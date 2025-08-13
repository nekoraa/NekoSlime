# host_main.py (高频版)
import network, espnow, socket, time, gc, struct
import machine

# 【优化1】将CPU频率提升到240MHz以获得最大性能
machine.freq(240000000)
print(f"CPU 主频已设置为: {machine.freq() / 1000000} MHz")

# --- 初始化ESP-NOW ---
wlan_sta = network.WLAN(network.STA_IF)
wlan_sta.active(True)
e = espnow.ESPNow()
e.active(True)
print("ESP-NOW 初始化完成，等待从机数据...")

# --- 初始化WiFi和UDP ---
def 连接WiFi(ssid, password, 尝试次数=10):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print(f"正在连接 WiFi: {ssid} ...")
        wlan.connect(ssid, password)
        for _ in range(尝试次数 * 10):
            if wlan.isconnected():
                print("WiFi 已连接:", wlan.ifconfig())
                return True
            time.sleep(0.1)
        print("WiFi 连接失败")
        return False
    else:
        print("WiFi 已连接:", wlan.ifconfig())
        return True

WIFI_SSID='NEKORAAA'
WIFI_PASSWORD='xxxxxxx'  
PC_IP='192.168.10.3'
PC_PORT=12345

if not 连接WiFi(WIFI_SSID, WIFI_PASSWORD):
    while True: time.sleep(1)

目标地址 = (PC_IP, int(PC_PORT))
udp套接字 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

追踪器数据 = {}
追踪器时间 = {}
gc.collect()

TRACKER_TIMEOUT_MS = 2000
CLEAN_INTERVAL_MS = 1000 # 清理周期可以放宽一些
KNOWN_PEERS_LIMIT = 128
known_peers = set()
_last_clean = time.ticks_ms()

def safe_recv_nonblocking():
    try:
        r = e.recv(0)
    except Exception: return None, None
    if not r: return None, None
    if isinstance(r, (tuple, list)) and len(r) >= 2: return r[0], r[1]
    return None, None

print("\n初始化完成，开始高频转发数据...")

# --- 主循环 ---
while True:
    try:
        host, msg = safe_recv_nonblocking()
        if msg:
            # 自动添加Peer的逻辑保持不变
            if host not in known_peers:
                try:
                    e.add_peer(host)
                    known_peers.add(host)
                    print("已添加新 peer:", host.hex())
                except Exception: pass
            
            # 数据处理
            if isinstance(msg, (bytes, bytearray)) and len(msg) >= 17:
                # 【优化2】不再存储和排序，收到数据立即转发
                # 统一裁剪为17字节，确保格式纯净
                udp_payload = msg[:17]
                try:
                    # 直接发送这个独立的、17字节的数据包
                    udp套接字.sendto(udp_payload, 目标地址)
                except Exception as ex:
                    # 在高频下，只在第一次出现错误时打印，避免刷屏
                    print(f"UDP 转发异常: {ex}")

                # 更新时间戳用于超时检测（这个操作很快，可以保留）
                追踪器时间[host] = time.ticks_ms()

                # 如果是新格式，仍然回送ACK，不影响转发
                if len(msg) >= 19:
                    try:
                        seq = struct.unpack('>H', msg[17:19])[0]
                        ack = b'ACK' + struct.pack('>H', seq)
                        e.send(host, ack)
                    except Exception: pass
        
        # --- 超时清理（与数据转发解耦）---
        now = time.ticks_ms()
        if time.ticks_diff(now, _last_clean) >= CLEAN_INTERVAL_MS:
            _last_clean = now
            stale_hosts = [h for h, ts in 追踪器时间.items() if time.ticks_diff(now, ts) > TRACKER_TIMEOUT_MS]
            if stale_hosts:
                for h in stale_hosts:
                    if h in 追踪器时间: del 追踪器时间[h]
                print("清理超时追踪器 (MAC):", [h.hex() for h in stale_hosts])
                # 【优化4】只在低频的清理任务中执行垃圾回收
                gc.collect()

        # 【优化3】移除主循环中的 sleep，让CPU全力运行
        # time.sleep_ms(0) # 或者直接移除

    except Exception as main_ex:
        print("主循环异常:", main_ex)
        time.sleep_ms(200)

