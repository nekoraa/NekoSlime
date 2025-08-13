# pc_gateway.py (高频适配版)
import tkinter as tk
from tkinter import ttk, messagebox
import socket
import struct
import threading
import time

class SlimeVR_Multi_Gateway:
    def __init__(self, 窗口):
        self.窗口 = 窗口
        self.窗口.title("SlimeVR ESP32 多追踪器网关 (高频版)")
        self.窗口.protocol("WM_DELETE_WINDOW", self._关闭程序)

        self.slimevr套接字 = None
        self.esp监听套接字 = None
        self.服务器地址 = None
        self.已连接 = False
        self.全局包编号 = 0
        self.监听线程 = None
        self.gui更新任务ID = None

        # --- 多追踪器定义 ---
        # 【重要】请务必将这里的 mac 地址替换为您自己ESP32从机的真实MAC地址！
        self.追踪器 = {
            # ID: {name, slime_id, mac, quat, last_seen}
            0: {"名称": "腰部", "slime_id": 0, "mac": b'\xAA\xAA\xAA\xAA\xAA\x00', "quat": [0, 0, 0, 1], "last_seen": 0},
            1: {"名称": "左大腿", "slime_id": 1, "mac": b'\xAA\xAA\xAA\xAA\xAA\x01', "quat": [0, 0, 0, 1], "last_seen": 0},
            2: {"名称": "右大腿", "slime_id": 2, "mac": b'\xAA\xAA\xAA\xAA\xAA\x02', "quat": [0, 0, 0, 1], "last_seen": 0},
            3: {"名称": "左小腿", "slime_id": 3, "mac": b'\xAA\xAA\xAA\xAA\xAA\x03', "quat": [0, 0, 0, 1], "last_seen": 0},
            4: {"名称": "右小腿", "slime_id": 4, "mac": b'\xAA\xAA\xAA\xAA\xAA\x04', "quat": [0, 0, 0, 1], "last_seen": 0},
        }
        self.数据锁 = threading.Lock()
        self._创建界面()

    def _创建界面(self):
        主框架 = ttk.Frame(self.窗口, padding="10")
        主框架.grid(row=0, column=0, sticky="nsew")
        连接框架 = ttk.LabelFrame(主框架, text="网络连接")
        连接框架.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Label(连接框架, text="SlimeVR服务器IP:").grid(row=0, column=0, sticky="w", padx=5)
        self.IP输入框 = ttk.Entry(连接框架, width=15)
        self.IP输入框.insert(0, "127.0.0.1")
        self.IP输入框.grid(row=0, column=1, padx=5)
        self.连接按钮 = ttk.Button(连接框架, text="启动服务", command=self._启动服务)
        self.连接按钮.grid(row=0, column=2, padx=5)
        self.状态标签 = ttk.Label(连接框架, text="状态: 未启动", foreground="red")
        self.状态标签.grid(row=0, column=3, padx=10)
        数据框架 = ttk.LabelFrame(主框架, text="追踪器状态")
        数据框架.grid(row=1, column=0, padx=5, pady=10, sticky="nsew")
        self.追踪器标签 = {}
        for i, (tracker_id, info) in enumerate(self.追踪器.items()):
            名称标签 = ttk.Label(数据框架, text=f"{info['名称']} (ID:{tracker_id})")
            名称标签.grid(row=i, column=0, sticky="w", padx=5, pady=2)
            状态标签 = ttk.Label(数据框架, text="等待连接...", foreground="grey", font=("Courier", 10))
            状态标签.grid(row=i, column=1, sticky="w", padx=5, pady=2)
            self.追踪器标签[tracker_id] = 状态标签

    def _启动服务(self):
        if self.已连接: return
        try:
            slimevr_ip = self.IP输入框.get()
            self.服务器地址 = (slimevr_ip, 6969)
            self.slimevr套接字 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            for tracker_id, info in self.追踪器.items():
                print(f"正在注册 {info['名称']}...")
                # 注意：使用您原始的握手包格式
                握手包 = self._构建握手包(info["mac"], info['名称'])
                self.slimevr套接字.sendto(握手包, self.服务器地址)
                time.sleep(0.05)
                # 注意：使用您原始的传感器信息包格式
                传感器包 = self._构建传感器信息包(tracker_id, info['slime_id'])
                self.slimevr套接字.sendto(传感器包, self.服务器地址)
                time.sleep(0.05)
            self.esp监听套接字 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.esp监听套接字.bind(('', 12345))
            self.已连接 = True
            self.监听线程 = threading.Thread(target=self._esp_数据监听线程, daemon=True)
            self.监听线程.start()
            self.IP输入框.config(state=tk.DISABLED)
            self.连接按钮.config(state=tk.DISABLED)
            self.状态标签.config(text="状态: 运行中", foreground="green")
            self._更新GUI状态()
            messagebox.showinfo("成功", "服务已启动！")
        except Exception as e:
            messagebox.showerror("启动错误", f"服务启动失败: {e}")

    # 【【【核心修改】】】
    # 这个函数被修改以处理来自ESP32的独立、高频的数据包
    def _esp_数据监听线程(self):
        print("ESP主机监听线程已启动 (高频模式)...")
        while self.已连接:
            try:
                # 每次接收到的就是一个独立的17字节数据包
                单包, 地址 = self.esp监听套接字.recvfrom(1024)

                # 检查数据包长度是否是我们期望的17字节
                if len(单包) == 17:
                    # 直接在锁内解析并更新数据
                    with self.数据锁:
                        tracker_id, qx, qy, qz, qw = struct.unpack('>Bffff', 单包)
                        if tracker_id in self.追踪器:
                            self.追踪器[tracker_id]["quat"] = [qx, qy, qz, qw]
                            self.追踪器[tracker_id]["last_seen"] = time.time()
                # else:
                #    在高频模式下，为避免刷屏，可以忽略长度不符的包
                #    print(f"收到长度异常的数据包: {len(单包)}字节")

            except socket.error:
                # 当套接字被关闭时，这会触发，是正常的退出方式
                break
            except Exception as e:
                if self.已连接: print(f"监听线程错误: {e}")
                break
        print("ESP主机监听线程已停止。")

    # 这个函数保持原样，它负责将更新后的数据发送到SlimeVR
    def _更新GUI状态(self):
        """定期更新界面显示，并发送数据到SlimeVR"""
        if not self.已连接: return

        current_time = time.time()
        active_trackers = 0
        with self.数据锁:
            for tracker_id, info in self.追踪器.items():
                # 更新GUI
                if current_time - info["last_seen"] < 5.0:  # 5秒超时
                    qx, qy, qz, qw = info["quat"]
                    状态文本 = f"x={qx:+.2f}, y={qy:+.2f}, z={qz:+.2f}, w={qw:+.2f}"
                    self.追踪器标签[tracker_id].config(text=状态文本, foreground="black")
                    active_trackers += 1
                else:
                    self.追踪器标签[tracker_id].config(text="已断开", foreground="red")

                # 发送姿态数据到SlimeVR
                qx, qy, qz, qw = info["quat"]
                self.全局包编号 += 1
                数据包 = self._构建旋转包(self.全局包编号, info["slime_id"], qx, qy, qz, qw)
                self.slimevr套接字.sendto(数据包, self.服务器地址)

        self.状态标签.config(text=f"状态: 运行中 ({active_trackers}/{len(self.追踪器)} 已连接)")
        # 保持原有的刷新率逻辑
        self.gui更新任务ID = self.窗口.after(1, self._更新GUI状态)

    def _关闭程序(self):
        self.已连接 = False # 标志位置为False，让所有线程循环自然退出
        if self.gui更新任务ID: self.窗口.after_cancel(self.gui更新任务ID)
        if self.esp监听套接字: self.esp监听套接字.close() # 关闭套接字以中断阻塞的recvfrom
        if self.slimevr套接字: self.slimevr套接字.close()
        self.窗口.destroy()

    # 以下是您原始工作版的协议构建函数，保持不变
    @staticmethod
    def _构建握手包(mac地址, board_name):
        return struct.pack('>IQIII3IIB14s6s', 3, 0, 0, 0, 3, 0, 0, 0, 10, 14, board_name.encode('utf-8'), mac地址)

    @staticmethod
    def _构建传感器信息包(包编号, 传感器编号):
        return struct.pack('>IQBBB', 15, 包编号, 传感器编号, 1, 0)

    @staticmethod
    def _构建旋转包(包编号, 传感器编号, qx, qy, qz, qw):
        return struct.pack('>IQBBffffB', 17, 包编号, 传感器编号, 1, qx, qy, qz, qw, 0)

if __name__ == "__main__":
    根窗口 = tk.Tk()
    应用程序 = SlimeVR_Multi_Gateway(根窗口)
    根窗口.mainloop()