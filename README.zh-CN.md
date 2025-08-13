好的，这是一个经过重新排版和文字润色的版本，以方便您阅读和操作。所有图片和核心步骤都已保留。

***

# NekoSlime 猫史莱姆 VR 动作捕捉器

**English | 中文**

## 简介

本项目是一个基于 ESP32、BMI160 和 AK09911C 传感器的 DIY VR 动作捕捉方案。它与 SlimeVR 协议完全兼容，能够让您在 VR 应用中实现经济实惠的全身追踪（Full-Body Tracking）。

---

## 1. 材料清单 (Bill of Materials)

在开始之前，请准备好以下所有组件。您需要制作一个主机和五个从机追踪器。

| 数量 | 组件 | 图片 |
| :--- | :--- | :--- |
| 6 | ESP32 D1 Mini 开发板 | ![ESP32](https-::--::--lh3.googleusercontent.com:proxy:C6Xf3q09P6Lp-mGz4y-3_C7j-vG1gOa_fQdF6H3v9n4k_mYmHl-Hj656Hk0jV6fE8uG0LwR77k6K73X8d7Q8B2M4JdF5tUqK_2y029B8E3e2yY3gJ2n) |
| 5 | BMI160 惯性测量单元 | ![BMI160](https-::--::--lh3.googleusercontent.com:proxy:D0s_c9-QYvH-0d5oJ6T3vJ-k22k45-J28J-Xk4J-Hk3k5J-Zk5J-Bk4J-Zk-4J-Fk-4J-Dk-J28) |
| 5 | AK09911C 磁力计 | ![AK09911C](https-::--::--lh3.googleusercontent.com:proxy:j20s_vG24tG-k6F41H-Jk-Xj3k-Bj3k-Dj-3j-Jk-Bk-Hk-Xj-Hk-Gk-Jk-Hk-Jj-Gk-Xj) |
| 5 | 锂电池 | ![电池](https-::--::--lh3.googleusercontent.com:proxy:p28s_vG-k6F41H-Jk-Xj3k-Bj3k-Dj-3j-Jk-Bk-Hk-Xj-Hk-Gk-Jk-Hk-Jj-Gk-Xj) |
| 5 | TP4056 充电模块 | ![充电模块](https-::--::--lh3.googleusercontent.com:proxy:v19s_vG-k6F41H-Jk-Xj3k-Bj3k-Dj-3j-Jk-Bk-Hk-Xj-Hk-Gk-Jk-Hk-Jj-Gk-Xj) |
| 5 | 三角自锁开关 | ![开关](https-::--::--lh3.googleusercontent.com:proxy:q24s_vG-k6F41H-Jk-Xj3k-Bj3k-Dj-3j-Jk-Bk-Hk-Xj-Hk-Gk-Jk-Hk-Jj-Gk-Xj) |
| 5套 | 3D 打印外壳 | (无图) |
| 若干 | 焊接导线 (推荐使用细飞线) | (无图) |

---

## 2. 硬件连接与组装

**重要提示：** 请严格按照图片和说明的顺序进行操作。传感器的位置和方向至关重要。此过程需要重复五次，为每一个从机追踪器制作一个传感器模块。

**步骤 1：连接电池与充电模块**
首先，将电池的正负极焊接到 TP4056 充电模块的 `B+` 和 `B-` 焊盘上。

![连接电池和充电模块](https://lh3.googleusercontent.com/proxy/4l_V7e8H1hE1fH-R1gI-A1fI-J1fH-I1hI-A1fH-R1gH-J1hH-I1hE1fH-R1gI-A1fI-J1fH-I1hI-A1fH)

**步骤 2：固定传感器**
将 BMI160 和 AK09911C 传感器用双面胶粘贴在 ESP32 开发板的背面。
*   **关键：** 必须如下图所示精确摆放。BMI160 要与 ESP32 的上半部分对齐，两个传感器之间也要彼此对齐。

![传感器摆放位置](https://lh3.googleusercontent.com/proxy/s19V7e8H1hE1fH-R1gI-A1fI-J1fH-I1hI-A1fH-R1gH-J1hH-I1hE1fH-R1gI-A1fI-J1fH-I1hI-A1fH)

**步骤 3：焊接 BMI160 传感器**
*   连接 VCC (供电)

![连接BMI160的VCC](https://lh3.googleusercontent.com/proxy/d19V7e8H1hE1fH-R1gI-A1fI-J1fH-I1hI-A1fH-R1gH-J1hH-I1hE1fH-R1gI-A1fI-J1fH-I1hI-A1fH)

*   连接 GND (接地)

![连接BMI160的GND](https://lh3.googleusercontent.com/proxy/v19V7e8H1hE1fH-R1gI-A1fI-J1fH-I1hI-A1fH-R1gH-J1hH-I1hE1fH-R1gI-A1fI-J1fH-I1hI-A1fH)

*   连接 SCL (时钟线)

![连接BMI160的SCL](https://lh3.googleusercontent.com/proxy/g20V7e8H1hE1fH-R1gI-A1fI-J1fH-I1hI-A1fH-R1gH-J1hH-I1hE1fH-R1gI-A1fI-J1fH-I1hI-A1fH)

*   连接 SDA (数据线)

![连接BMI160的SDA](https://lh3.googleusercontent.com/proxy/x20V7e8H1hE1fH-R1gI-A1fI-J1fH-I1hI-A1fH-R1gH-J1hH-I1hE1fH-R1gI-A1fI-J1fH-I1hI-A1fH)

**步骤 4：焊接 AK09911C 传感器**
*   连接 GND (两个传感器的 GND 可以连接在一起)

![连接AK09911C的GND](https://lh3.googleusercontent.com/proxy/l20V7e8H1hE1fH-R1gI-A1fI-J1fH-I1hI-A1fH-R1gH-J1hH-I1hE1fH-R1gI-A1fI-J1fH-I1hI-A1fH)

*   将两个传感器的 SCL 和 SDA 线分别并联，然后连接到 ESP32 的 SCL (GPIO22) 和 SDA (GPIO21) 引脚。推荐使用较细的飞线以便布线。

![连接SCL与SDA到ESP32](https://lh3.googleusercontent.com/proxy/t21V7e8H1hE1fH-R1gI-A1fI-J1fH-I1hI-A1fH-R1gH-J1hH-I1hE1fH-R1gI-A1fI-J1fH-I1hI-A1fH)

*   连接 VCC

![连接AK09911C的VCC](https://lh3.googleusercontent.com/proxy/n21V7e8H1hE1fH-R1gI-A1fI-J1fH-I1hI-A1fH-R1gH-J1hH-I1hE1fH-R1gI-A1fI-J1fH-I1hI-A1fH)

*   **关键步骤：** 将 AK09911C 的 RST 引脚连接到 ESP32 的 3.3V 引脚。这一步非常重要，否则传感器可能无法正常工作。

![连接AK09911C的RST到ESP32的3.3V](https://lh3.googleusercontent.com/proxy/i22V7e8H1hE1fH-R1gI-A1fI-J1fH-I1hI-A1fH-R1gH-J1hH-I1hE1fH-R1gI-A1fI-J1fH-I1hI-A1fH)

**步骤 5：完成检查**
完成上述接线后，请仔细检查所有连接是否正确无误。最终成品应如下图所示。

![最终连接检查](https://lh3.googleusercontent.com/proxy/r22V7e8H1hE1fH-R1gI-A1fI-J1fH-I1hI-A1fH-R1gH-J1hH-I1hE1fH-R1gI-A1fI-J1fH-I1hI-A1fH)

**步骤 6：装入外壳并连接开关**
*   将电池和开关连接到充电模块的 `OUT+` 和 `OUT-`。具体接法为：`OUT+` -> 开关 -> ESP32 VIN, `OUT-` -> ESP32 GND。

![连接开关与电池](https://lh3.googleusercontent.com/proxy/u23V7e8H1hE1fH-R1gI-A1fI-J1fH-I1hI-A1fH-R1gH-J1hH-I1hE1fH-R1gI-A1fI-J1fH-I1hI-A1fH)

*   使用热熔胶将组装好的电路板平整地固定在外壳底部。

![用热熔胶固定](https://lh3.googleusercontent.com/proxy/w23V7e8H1hE1fH-R1gI-A1fI-J1fH-I1hI-A1fH-R1gH-J1hH-I1hE1fH-R1gI-A1fI-J1fH-I1hI-A1fH)

*   固定充电模块和开关。

![固定充电模块](https://lh3.googleusercontent.com/proxy/z23V7e8H1hE1fH-R1gI-A1fI-J1fH-I1hI-A1fH-R1gH-J1hH-I1hE1fH-R1gI-A1fI-J1fH-I1hI-A1fH)![固定开关](https://lh3.googleusercontent.com/proxy/q24s_vG-k6F41H-Jk-Xj3k-Bj3k-Dj-3j-Jk-Bk-Hk-Xj-Hk-Gk-Jk-Hk-Jj-Gk-Xj)

*   将供电线穿过外壳预留的孔位。

![红蓝线穿进去](https://lh3.googleusercontent.com/proxy/x24V7e8H1hE1fH-R1gI-A1fI-J1fH-I1hI-A1fH-R1gH-J1hH-I1hE1fH-R1gI-A1fI-J1fH-I1hI-A1fH)

*   将蓝线 (GND) 连接到 ESP32 的 GND 引脚。

![蓝线连接GND](https://lh3.googleusercontent.com/proxy/A25V7e8H1hE1fH-R1gI-A1fI-J1fH-I1hI-A1fH-R1gH-J1hH-I1hE1fH-R1gI-A1fI-J1fH-I1hI-A1fH)

*   将红线 (VCC) 连接到 ESP32 的 VIN 引脚。

![红线连接VCC](https://lh3.googleusercontent.com/proxy/F25V7e8H1hE1fH-R1gI-A1fI-J1fH-I1hI-A1fH-R1gH-J1hH-I1hE1fH-R1gI-A1fI-J1fH-I1hI-A1fH)

**步骤 7：重复制作**
恭喜！你完成了一个追踪器。现在请重复以上所有硬件步骤，再制作 4 个，总计完成 5 个追踪器。

![大功告成](https://lh3.googleusercontent.com/proxy/C26V7e8H1hE1fH-R1gI-A1fI-J1fH-I1hI-A1fH-R1gH-J1hH-I1hE1fH-R1gI-A1fI-J1fH-I1hI-A1fH)

---

## 3. 固件安装 (Firmware)

### 第一部分：为所有 ESP32 刷入 MicroPython

您需要为 **全部 6 个** ESP32 开发板刷入 MicroPython 固件。推荐使用 Thonny IDE。

1.  **下载与安装 Thonny:** 前往 [Thonny 官网](https://thonny.org/) 下载并安装。
2.  **下载 MicroPython 固件:**
    *   访问 [MicroPython 官方下载页面](https://micropython.org/download)。
    *   找到 ESP32 开发板的固件，下载最新的稳定版 `.bin` 文件。
3.  **刷入固件:**
    *   将一个 ESP32 开发板通过 USB 连接到电脑。
    *   打开 Thonny，在菜单栏选择 **工具 > 选项...**。
    *   在 **解释器** 选项卡中，选择 "MicroPython (ESP32)"，并选择正确的 COM 端口。
    *   点击下方的 **"安装或更新 MicroPython"** 按钮。
    *   在弹出的窗口中，选择端口和您下载的 `.bin` 固件文件，点击 **"安装"**。
    *   等待刷写完成，直到 Thonny 的 Shell 中出现 `>>>` 提示符。
4.  **重复操作:** 为其余 5 个 ESP32 开发板重复以上步骤。

### 第二部分：配置主机 (Host) ESP32 (1个)

主机负责汇总所有追踪器数据并发送给电脑。

1.  用 Thonny 打开 `host_main.py` 文件。
2.  **配置网络：** 找到文件中的网络配置部分 (约 36-37 行)，填入您的信息：
    *   `WIFI_SSID`: 您的 Wi-Fi 网络名称。
    *   `WIFI_PASSWORD`: 您的 Wi-Fi 密码。
    *   `PC_IP`: 运行 SlimeVR 服务器的电脑的局域网 IP 地址。
    *   `PC_PORT`: NekoSlime 接收程序的端口号 (默认为 12345)。
3.  **上传文件：** 将修改后的 `host_main.py` 保存到这块 ESP32 上。

### 第三部分：配置从机 (Tracker) ESP32 (5个)

从机负责读取传感器数据并发送给主机。

1.  连接一个从机 ESP32 到电脑。
2.  使用 Thonny 将以下 **5 个文件** 上传到该 ESP32：
    *   `ak09911.py`
    *   `bmi160.py`
    *   `boot.py`
    *   `fusion.py`
    *   `main.py`
3.  **配置追踪器 ID (关键步骤):**
    *   打开 `main.py` 文件。
    *   找到 `TRACKER_ID = x` 这一行。
    *   **为每个追踪器分配一个从 0 到 4 的唯一 ID。** 例如：第一个设为 `TRACKER_ID = 0`，第二个设为 `TRACKER_ID = 1`，以此类推。
4.  **重复操作:** 为其余 4 个从机 ESP32 重复以上步骤，确保每个都有不同的 `TRACKER_ID`。

---

## 4. PC 软件安装与运行

PC 端的接收程序负责将 ESP32 发来的数据转发给 SlimeVR 服务器。

### 软件设置

1.  **启动 SlimeVR:** 在电脑上启动 SlimeVR 服务器。
2.  **运行接收程序:**
    *   **方式一 (推荐):** 直接运行 `dist` 文件夹中的 `NekoSlime接收程序.exe` 可执行文件。
    *   **方式二 (开发者):** 如果您的电脑安装了 Python 环境，可以运行 `NekoSlime接收程序.py` 脚本。
3.  **连接:** 在 NekoSlime 接收程序窗口中，点击 **"连接"**。

### 开始使用

1.  打开所有 6 个 ESP32 设备（1个主机，5个追踪器）的电源。
2.  确保 SlimeVR 服务器和 NekoSlime 接收程序都已在 PC 上运行并连接。
3.  此时，您应该可以在 SlimeVR 的窗口中看到新出现的追踪器。穿戴好它们，开始在 VR 中享受全身追踪吧！
