# main.py (Tracker)  —— 保留你原有变量名
from machine import Pin, I2C
import time
from bmi160 import BMI160
from ak09911 import AK09911C
from fusion import 在线偏置与磁抑制
import gc
import network
import espnow
import struct

# --- 配置 ---
TRACKER_ID = 4  # 追踪器ID，改成0~4
HOST_MAC = b'\xec\xe3\x34\x46\x8f\xec'  # 主机MAC地址，确保准确

# --- 初始化WiFi和信道 ---
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.config(channel=11)  # 跟主机信道保持一致（你的主机是11）

# --- 初始化ESP-NOW ---
e = espnow.ESPNow()
e.active(True)
# 试着预先 add_peer，不成功也没关系
try:
    e.add_peer(HOST_MAC)
except Exception:
    pass
print(f"ESP-NOW 初始化完成, 追踪器ID: {TRACKER_ID}, 目标主机: {HOST_MAC.hex()}")

# 硬件与 I2C 初始化（GPIO21 SDA, GPIO22 SCL）
LED = Pin(2, Pin.OUT)
i2c = I2C(1, scl=Pin(22), sda=Pin(21))
imu = BMI160(i2c)
mag = AK09911C(i2c)

# 采样参数（可调）
目标频率 = 60.0
采样周期_s = 1.0 / 目标频率
采样周期_us = int(1e6 * 采样周期_s)

# 创建融合器
融合器 = 在线偏置与磁抑制(Kp=0.6, 陀螺偏置学习率=2e-4)

# LED 闪烁函数
def led闪(次数, 持续_ms):
    for _ in range(次数):
        LED.on()
        time.sleep_ms(持续_ms)
        LED.off()
        time.sleep_ms(持续_ms)

# --------- 1) 开机提示并进行陀螺静态校准（10s） ----------
led闪(2, 1000)
print("开始陀螺静态偏置采集 10s，请保持不动...")
gyro_sum = [0.0, 0.0, 0.0]
count = 0
start = time.ticks_ms()
while time.ticks_diff(time.ticks_ms(), start) < 10000:
    ax, ay, az, gx, gy, gz = imu.读取六轴()
    gyro_sum[0] += gx; gyro_sum[1] += gy; gyro_sum[2] += gz
    count += 1
    time.sleep_ms(10)
初始_bias = [gyro_sum[i]/count for i in range(3)]
# 将初始 bias 载入融合器为初值
融合器.gyro_bias = 初始_bias[:]
print("陀螺初始偏置:", 融合器.gyro_bias)

# --------- 2) 磁力计椭球/偏置快速采集（用户画8字 10s） ----------
led闪(3, 500)
print("开始磁力计快速采集 10s，请画8字旋转设备...")
mag_max = [-32768, -32768, -32768]
mag_min = [32767, 32767, 32767]
start = time.ticks_ms()
while time.ticks_diff(time.ticks_ms(), start) < 10000:
    mx, my, mz = mag.读取磁力()
    if mx > mag_max[0]: mag_max[0] = mx
    if my > mag_max[1]: mag_max[1] = my
    if mz > mag_max[2]: mag_max[2] = mz
    if mx < mag_min[0]: mag_min[0] = mx
    if my < mag_min[1]: mag_min[1] = my
    if mz < mag_min[2]: mag_min[2] = mz
    time.sleep_ms(20)

# 计算简化校准 (每轴 bias 和 scale)
mag_bias = [ (mag_max[i] + mag_min[i]) / 2.0 for i in range(3) ]
mag_scale = [ (mag_max[i] - mag_min[i]) / 2.0 for i in range(3) ]
avg = (mag_scale[0] + mag_scale[1] + mag_scale[2]) / 3.0
for i in range(3):
    if mag_scale[i] != 0:
        mag_scale[i] = avg / mag_scale[i]
    else:
        mag_scale[i] = 1.0

# 将初始地磁场期望设置为当前平均模长，便于动态检测
mx0 = (mag_max[0] + mag_min[0]) / 2.0
my0 = (mag_max[1] + mag_min[1]) / 2.0
mz0 = (mag_max[2] + mag_min[2]) / 2.0
地磁模长 = (mx0*mx0 + my0*my0 + mz0*mz0) ** 0.5
融合器.地磁强度期望 = 地磁模长

print("磁校准偏置:", mag_bias, "缩放:", mag_scale, "地磁模长:", 地磁模长)

# 校准完成，LED 熄灭
led闪(4, 500)
LED.off()
print("校准完成，开始主循环（{}Hz）".format(目标频率))

LED.on()

# ---- 握手与可靠发送参数（可调） ----
HELLO_INTERVAL_MS = 800    # 未连接时 HELLO 发送间隔
SEND_RETRY = 3             # 每帧最大重试次数
ACK_TIMEOUT_MS = 300       # 等待 ACK 超时（用于重发判定）
GC_EACH_FRAMES = 30        # 每多少帧执行一次 gc.collect()
MAX_PENDING = 8            # 最多缓存未被 ACK 的帧数，防止内存占满

# pending_frames: seq -> dict { 'payload': bytes, 'ts': ticks_ms, 'attempts': int }
pending_frames = {}

# 连接状态：当收到主机 OK 时设为 True
connected = False
last_hello_t = time.ticks_ms()

# 非阻塞接收并处理 ACK/OK（在主循环每帧调用）
def process_incoming():
    global connected
    try:
        r = e.recv(0)  # 非阻塞
    except Exception:
        return
    if not r:
        return
    # 兼容多返回格式 (mac, msg) 或 (mac, msg, rssi)
    if isinstance(r, (tuple, list)):
        if len(r) >= 2:
            peer = r[0]; msg = r[1]
        else:
            return
    else:
        return

    # 处理 OK（握手确认）
    if isinstance(msg, (bytes, bytearray)) and msg == b'OK' and peer == HOST_MAC:
        connected = True
        # 确保 peer 存在
        try:
            e.add_peer(HOST_MAC)
        except Exception:
            pass
        # 清旧 pending（可选保留）
        # pending_frames.clear()
        # print once
        print("收到主机 OK，连接建立")
        return

    # 处理 ACK (b'ACK' + seq)
    if isinstance(msg, (bytes, bytearray)) and msg.startswith(b'ACK') and peer == HOST_MAC:
        if len(msg) >= 5:
            try:
                ack_seq = struct.unpack('>H', msg[3:5])[0]
            except Exception:
                return
            if ack_seq in pending_frames:
                # 已确认，清除
                del pending_frames[ack_seq]
                # 可选: print("ACK", ack_seq)
        return

# 非阻塞发送函数：只将 payload 放入 pending 并尝试发送（不阻塞等待 ACK）
def enqueue_and_send(payload, seq):
    # 限制 pending 长度
    if len(pending_frames) >= MAX_PENDING:
        # 最简单策略：丢弃最老的一帧（按插入时间）
        oldest = min(pending_frames.items(), key=lambda x: x[1]['ts'])[0]
        del pending_frames[oldest]
    # 插入 pending
    pending_frames[seq] = { 'payload': payload, 'ts': time.ticks_ms(), 'attempts': 1 }
    # 尝试发送（立即）
    try:
        e.send(HOST_MAC, payload)
    except Exception:
        # 发送失败也保留在 pending，后续帧会重发
        pass

# 周期性重发检查（在主循环每帧调用）
def pending_check_and_resend():
    now = time.ticks_ms()
    to_resend = []
    for seq, info in list(pending_frames.items()):
        # 若超时则重发（并增加 attempts）
        if time.ticks_diff(now, info['ts']) >= ACK_TIMEOUT_MS:
            if info['attempts'] < SEND_RETRY:
                to_resend.append(seq)
            else:
                # 达到最大重试次数，删掉以免无限增长（可选记录日志）
                # print("丢弃帧 seq", seq, "尝试次数", info['attempts'])
                try:
                    del pending_frames[seq]
                except KeyError:
                    pass
    # 执行重发
    for seq in to_resend:
        info = pending_frames.get(seq)
        if not info:
            continue
        try:
            e.send(HOST_MAC, info['payload'])
            pending_frames[seq]['attempts'] += 1
            pending_frames[seq]['ts'] = time.ticks_ms()
        except Exception:
            # 发送失败，下次再试
            pending_frames[seq]['attempts'] += 1
            pending_frames[seq]['ts'] = time.ticks_ms()

# 初始握手不阻塞：在正式主循环前先发送几次 HELLO（快速触达）
for _ in range(3):
    try:
        e.send(HOST_MAC, b'HELLO' + bytes([TRACKER_ID]))
    except Exception:
        pass
    time.sleep_ms(50)

# --------- 主循环：60Hz 读取 -> 校正 -> 融合 -> 打包并入队发送（非阻塞） ----------
next_us = time.ticks_us()
seq = 0
frame_count = 0

while True:
    # 计算到下一帧剩余时间（微秒）
    now_us = time.ticks_us()
    dt_us = time.ticks_diff(next_us, now_us)
    if dt_us > 0:
        # 如果剩余时间大于 2000us，先 sleep 大部分，最后再微调
        if dt_us > 3000:
            time.sleep_ms((dt_us - 1000) // 1000)  # 保守地睡到接近点
        # 精确等待到时刻
        while time.ticks_diff(next_us, time.ticks_us()) > 0:
            # 少量 busy wait，避免占用太多 CPU
            pass

    # 更新下一帧时间点（避免累计误差）
    next_us = time.ticks_add(next_us, 采样周期_us)

    # 处理可能的入站消息（ACK/OK）尽早处理
    process_incoming()

    # 若未连接且到达 HELLO 发送间隔，则发送 HELLO（不阻塞）
    if not connected and time.ticks_diff(time.ticks_ms(), last_hello_t) >= HELLO_INTERVAL_MS:
        try:
            e.send(HOST_MAC, b'HELLO' + bytes([TRACKER_ID]))
        except Exception:
            pass
        last_hello_t = time.ticks_ms()

    # 读取传感器 (I2C 操作)
    ax, ay, az, gx, gy, gz = imu.读取六轴()
    mx_raw, my_raw, mz_raw = mag.读取磁力()

    # 应用磁校准（保留在 Python 层，尽量保持简单）
    mx = (mx_raw - mag_bias[0]) * mag_scale[0]
    my = (my_raw - mag_bias[1]) * mag_scale[1]
    mz = (mz_raw - mag_bias[2]) * mag_scale[2]

    # 获取当前毫秒时间戳
    now_ms = time.ticks_ms()

    # 更新融合器（内部自动做陀螺偏置学习与磁干扰抑制）
    融合器.更新(ax, ay, az, gx, gy, gz, mx, my, mz, 采样周期_s, now_ms)

    # 输出四元数 xyzw
    qx, qy, qz, qw = 融合器.获取四元数_xyzw()

    # 打包数据（带序号）
    seq = (seq + 1) & 0xFFFF
    payload = struct.pack('>BffffH', TRACKER_ID, qx, qy, qz, qw, seq)

    # 入队并立即尝试发送（非阻塞）
    enqueue_and_send(payload, seq)

    # 每帧检查 pending（重发逻辑）与处理入站（ACK）
    process_incoming()
    pending_check_and_resend()

    # 每 GC_EACH_FRAMES 帧执行一次 gc.collect()
    frame_count += 1
    if frame_count >= GC_EACH_FRAMES:
        frame_count = 0
        gc.collect()

    # tiny yield，释放线程片段（必要时可注释）
    # time.sleep_ms(0)

# end of file
