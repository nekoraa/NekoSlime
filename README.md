好的，这是一个根据您的要求编写和完善的 `README.md` 文件内容。

---

# NekoSlime

English | [中文](README.zh-CN.md)

## Introduction

A VR motion capture solution based on ESP32 + BMI160 + AK09911C sensors, compatible with the SlimeVR protocol, suitable for full-body tracking and virtual reality interaction.

## Bill of Materials

*   ESP32 Mini Development Board * 6
*   Welding wires
*   BMI160 Sensor * 5
*   AK09911C Sensor * 5
*   3D Printed Case * 5
*   Battery * 5
*   Charging Module * 5

## Hardware Connection

**(这里将介绍 ESP32、BMI160、AK09911C、电池和充电模块之间的接线。)**

**图片插入方法说明：**

在 `README.md` 文件中插入图片非常简单。最常用的方法是：

1.  **在您的项目仓库中创建一个文件夹** (例如，`images` 或 `assets`)。
2.  **将您的图片上传到这个文件夹中。**
3.  **在 `README.md` 文件中，使用以下 Markdown 语法引用图片：**

    ```markdown
    ![图片描述](图片文件的路径)
    ```

    例如，如果您的图片名为 `hardware-connection.jpg` 并位于 `images` 文件夹中，您应该这样写：

    ```markdown
    ![Hardware Connection Diagram](images/hardware-connection.jpg)
    ```

    "图片描述" (Alt text) 是在图片无法加载时显示的替代文本。

## Firmware Installation

### 1. Flashing MicroPython with Thonny

To get started, you need to flash the MicroPython firmware onto all your ESP32 boards. We recommend using the Thonny IDE for this process.

**Detailed Steps:**

1.  **Download and Install Thonny:** If you don't have it already, download and install Thonny from its [official website](https://thonny.org/).
2.  **Download MicroPython Firmware:**
    *   Go to the [MicroPython downloads page](https://micropython.org/download/).
    *   Select the firmware for the "ESP32" board. Download the latest stable `.bin` file.
3.  **Connect Your ESP32:** Connect one of your ESP32 boards to your computer via a USB cable.
4.  **Configure Thonny Interpreter:**
    *   In Thonny, go to `Tools` > `Options...`.
    *   Select the `Interpreter` tab.
    *   Choose "MicroPython (ESP32)" from the interpreter dropdown list.
    *   Select the COM port corresponding to your ESP32. If you don't see it, you may need to install the necessary drivers for your board.
5.  **Install the Firmware:**
    *   While still in the Interpreter settings, click on "Install or update MicroPython".
    *   In the new window, select the correct target port and browse for the `.bin` file you downloaded earlier.
    *   Click "Install" to begin flashing the firmware.
    *   Once the process is complete, you will see the MicroPython REPL prompt (`>>>`) in the Thonny shell.
6.  **Repeat for All Boards:** Repeat this process for all six of your ESP32 boards.

### 2. Host ESP32 Setup (1 board)

The host ESP32 is responsible for gathering data from all the trackers and sending it to your PC.

1.  **Open `host_main.py` in Thonny.**
2.  **Configure Network Settings:**
    *   Locate lines 36-37 (or the relevant configuration section) in `host_main.py`.
    *   You will need to fill in your Wi-Fi credentials and the IP address of the computer running the SlimeVR server.
        *   `WIFI_SSID`: Your Wi-Fi network name.
        *   `WIFI_PASSWORD`: Your Wi-Fi password.
        *   `PC_IP`: The local IP address of your computer.
        *   `PC_PORT`: The port number used by the NekoSlime receiver (default is `12345`).
3.  **Upload the file:** Save the modified `host_main.py` to the host ESP32.

### 3. Tracker ESP32 Setup (5 boards)

The tracker ESP32s read the sensor data and send it to the host.

1.  **Connect a tracker ESP32** to your computer.
2.  **Upload the following files** to the ESP32 using Thonny:
    *   `ak09911.py`
    *   `bim160.py`
    *   `boot.py`
    *   `fusion.py`
    *   `main.py`
3.  **Configure Tracker ID:**
    *   Open the `main.py` file.
    *   Locate the line `TRACKER_ID=x`.
    *   **Crucially, you must assign a unique ID to each tracker, from 0 to 4.** For the first tracker, set it to `TRACKER_ID=0`, for the second, `TRACKER_ID=1`, and so on.
4.  **Repeat:** Repeat these steps for all five tracker ESP32s, ensuring each has a unique `TRACKER_ID`.

## Software Installation

The PC-side software receives the tracking data from the host ESP32 and forwards it to SlimeVR.

1.  **Prerequisites:** Ensure you have Python installed on your PC if you wish to run the script directly.
2.  **Choose your method:**
    *   **Using the Python script:** Run `NekoSlime接收程序.py`.
    *   **Using the executable:** For ease of use, you can directly run `NekoSlime接收程序.exe` from the `dist` folder.
3.  **Integration with SlimeVR:** Make sure the SlimeVR server is running on your PC **before** you connect the NekoSlime receiver.

## Running the System

1.  **Power on** all your ESP32 trackers and the host ESP32.
2.  **Start the SlimeVR server** on your computer.
3.  **Run the NekoSlime receiver** (`.py` or `.exe`) on your computer and click "Connect".
4.  You should now see the trackers appear in SlimeVR, ready for full-body tracking in your VR applications.

---
---

# NekoSlime

[English](README.md) | 中文

## 简介

基于 ESP32 + BMI160 + AK09911C 传感器的 VR 动作捕捉方案，兼容 SlimeVR 协议，可用于全身追踪与虚拟现实互动。

## 材料清单准备

*   ESP32 迷你开发板 * 6
*   焊接用的导线
*   BMI160 传感器 * 5
*   AK09911C 传感器 * 5
*   3D 打印外壳 * 5
*   电池 * 5
*   充电模块 * 5

## 硬件连接

**(这里将介绍 ESP32、BMI160、AK09911C、电池和充电模块之间的接线。)**

**图片插入方法说明：**

在 `README.md` 文件中插入图片非常简单。最常用的方法是：

1.  **在您的项目仓库中创建一个文件夹** (例如，`images` 或 `assets`)。
2.  **将您的图片上传到这个文件夹中。**
3.  **在 `README.md` 文件中，使用以下 Markdown 语法引用图片：**

    ```markdown
    ![图片描述](图片文件的路径)
    ```

    例如，如果您的图片名为 `hardware-connection.jpg` 并位于 `images` 文件夹中，您应该这样写：

    ```markdown
    ![硬件连接图](images/hardware-connection.jpg)
    ```

    “图片描述” (Alt text) 是在图片无法加载时显示的替代文本。

## 固件安装

### 1. 使用 Thonny 刷入 MicroPython

首先，您需要为所有的 ESP32 开发板刷入 MicroPython 固件。我们推荐使用 Thonny IDE 来完成这个步骤。

**详细步骤：**

1.  **下载并安装 Thonny：** 如果您尚未安装，请从 [Thonny 官网](https://thonny.org/) 下载并安装。
2.  **下载 MicroPython 固件：**
    *   访问 [MicroPython 下载页面](https://micropython.org/download/)。
    *   选择 “ESP32” 开发板的固件。下载最新的稳定版 `.bin` 文件。
3.  **连接您的 ESP32：** 将您的一个 ESP32 开发板通过 USB 数据线连接到电脑。
4.  **配置 Thonny 解释器：**
    *   在 Thonny 中，转到 `工具` > `选项...`。
    *   选择 `解释器` 选项卡。
    *   从解释器下拉列表中选择 “MicroPython (ESP32)”。
    *   选择您的 ESP32 对应的 COM 端口。如果找不到，您可能需要为您的开发板安装必要的驱动程序。
5.  **安装固件：**
    *   仍在解释器设置中，点击“安装或更新 MicroPython”。
    *   在弹出的窗口中，选择正确的目标端口，并浏览选择您之前下载的 `.bin` 文件。
    *   点击“安装”开始刷写固件。
    *   当该过程完成后，您会在 Thonny 的 shell 中看到 MicroPython 的 REPL 提示符 (`>>>`)。
6.  **为所有开发板重复操作：** 为您的全部六个 ESP32 开发板重复此过程。

### 2. 主机 ESP32 设置 (1个)

主机 ESP32 负责从所有追踪器收集数据并将其发送到您的电脑。

1.  **在 Thonny 中打开 `host_main.py` 文件。**
2.  **配置网络设置：**
    *   在 `host_main.py` 中找到第 36-37 行（或相关的配置部分）。
    *   您需要填写您的 Wi-Fi 信息和运行 SlimeVR 服务器的电脑的 IP 地址。
        *   `WIFI_SSID`：您的 Wi-Fi 网络名称。
        *   `WIFI_PASSWORD`：您的 Wi-Fi 密码。
        *   `PC_IP`：您电脑的局域网 IP 地址。
        *   `PC_PORT`：NekoSlime 接收程序使用的端口号（默认为 `12345`）。
3.  **上传文件：** 将修改后的 `host_main.py` 保存到主机 ESP32。

### 3. 从机 ESP32 设置 (5个)

从机 ESP32 读取传感器数据并将其发送到主机。

1.  **连接一个从机 ESP32** 到您的电脑。
2.  **使用 Thonny 将以下文件上传**到 ESP32：
    *   `ak09911.py`
    *   `bim160.py`
    *   `boot.py`
    *   `fusion.py`
    *   `main.py`
3.  **配置追踪器 ID：**
    *   打开 `main.py` 文件。
    *   找到 `TRACKER_ID=x` 这一行。
    *   **关键一步：您必须为每个追踪器分配一个从 0 到 4 的唯一 ID。** 例如，第一个追踪器设置为 `TRACKER_ID=0`，第二个设置为 `TRACKER_ID=1`，以此类推。
4.  **重复操作：** 为所有五个从机 ESP32 重复这些步骤，确保每个都有唯一的 `TRACKER_ID`。

## 软件安装

PC 端的软件接收来自主机 ESP32 的追踪数据，并将其转发给 SlimeVR。

1.  **先决条件：** 如果您希望直接运行脚本，请确保您的 PC 上已安装 Python。
2.  **选择您的运行方式：**
    *   **使用 Python 脚本：** 运行 `NekoSlime接收程序.py`。
    *   **使用可执行文件：** 为了方便使用，您可以直接运行 `dist` 文件夹中的 `NekoSlime接收程序.exe`。
3.  **与 SlimeVR 的集成：** 在连接 NekoSlime 接收程序**之前**，请确保 SlimeVR 服务器正在您的 PC 上运行。

## 运行

1.  **打开**您所有的 ESP32 追踪器和主机 ESP32 的电源。
2.  在您的电脑上**启动 SlimeVR 服务器**。
3.  在您的电脑上**运行 NekoSlime 接收程序**（`.py` 或 `.exe`）并点击“连接”。
4.  现在您应该能在 SlimeVR 中看到追踪器出现，可以在您的 VR 应用中进行全身追踪了。
