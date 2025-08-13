# **NekoSlime VR Motion Capture Solution**

[中文](README.zh.md) | English

---

## **1. Project Overview**

This project is based on **ESP32 + BMI160 + AK09911C** sensors, compatible with the **SlimeVR protocol**, enabling full-body tracking and interaction in virtual reality.

---

## **2. Bill of Materials**

| Item                  | Qty | Image                                                        |
| --------------------- | --- | ------------------------------------------------------------ |
| ESP32 mini dev board  | 6   | <img src="过程图片/1755057795491--2065557247.jpg" width="250"> |
| Wires for soldering   | —   | -                                                            |
| BMI160 sensor         | 5   | <img src="过程图片/1755057784713--292283426.jpg" width="250">  |
| AK09911C sensor       | 5   | <img src="过程图片/1755057856647-945560983.jpg" width="250">   |
| 3D printed case       | 5   | -                                                            |
| Battery               | 5   | <img src="过程图片/1755057841558-2007191268.jpg" width="250">  |
| Charging module       | 5   | <img src="过程图片/1755057807326-1714342055.jpg" width="250">  |
| Switch (triangle)     | 5   | <img src="过程图片/20250812_201414.jpg" width="250">           |

---

## **3. Hardware Assembly Steps**

> ⚠ **Note**: Sensors must be precisely aligned and positioned as shown in the example. Make sure all orientations are consistent. Use thin jumper wires for easier routing.

### **3.1 Battery & Charging Module**

<img src="过程图片/20250812_193749.jpg" width="350">

---

### **3.2 Sensor Placement**

* Attach the **BMI160** sensor to the **upper back side** of the ESP32 (use double-sided tape).
* Ensure sensors are neatly aligned.

  <img src="过程图片/20250812_194011.jpg" width="350">

---

### **3.3 Sensor Wiring**

1. **Connect BMI160 VCC**

   <img src="过程图片/20250812_194359.jpg" width="350">

2. **Connect BMI160 GND**

   <img src="过程图片/20250812_194558.jpg" width="350">

3. **Connect BMI160 SCL**

   <img src="过程图片/20250812_195447.jpg" width="350">

4. **Connect BMI160 SDA**

   <img src="过程图片/20250812_195646.jpg" width="350">

5. **Connect AK09911C GND**

   <img src="过程图片/20250812_195816.jpg" width="350">

6. **Connect SCL & SDA to ESP32 GPIO21 (SCL) and GPIO22 (SDA)**

   <img src="过程图片/20250812_200127.jpg" width="350">

7. **Connect AK09911C VCC**

   <img src="过程图片/20250812_200301.jpg" width="350">

8. **Connect AK09911C RST to ESP32 3.3V** (Important: Without this, the sensor will not work)

   <img src="过程图片/20250812_200525.jpg" width="350">

---

### **3.4 Final Assembly Check**

<img src="过程图片/20250812_200603.jpg" width="350">

---

### **3.5 Switch & Battery Wiring**

* Connect according to the diagram

  <img src="过程图片/20250812_201024.jpg" width="350">

---

### **3.6 Board Mounting**

* Mount the board flat and secure with hot glue as shown

  <img src="过程图片/20250812_201235.jpg" width="350">

---

### **3.7 Charging Module**

<img src="过程图片/20250812_201307.jpg" width="350">

---

### **3.8 Switch**

<img src="过程图片/20250812_201414.jpg" width="350">

---

### **3.9 Red & Blue Wire Routing**

1. Pass red and blue wires through the case

   <img src="过程图片/20250812_201417.jpg" width="350">

2. Blue wire → GND

   <img src="过程图片/20250812_201513.jpg" width="350">

3. Red wire → VCC

   <img src="过程图片/20250812_201616.jpg" width="350">

---

### **3.10 One Completed Unit**

* Make **6 sets** in total (1 host + 5 clients)

  <img src="过程图片/wx_camera_1755004415247.jpg" width="350">

---

## **4. Firmware Installation**

### **4.1 Install MicroPython**

1. **Download and install [Thonny IDE](https://thonny.org/)**
2. **Download MicroPython firmware** ([Download page](https://micropython.org/download/))

   * Choose the **ESP32** version and get the latest stable `.bin`
3. **Connect ESP32 to PC**
4. **Configure Thonny Interpreter**

   * Tools → Options → Interpreter → Select “MicroPython (ESP32)”
   * Choose the correct COM port
5. **Flash firmware**

   * Click “Install or update MicroPython”
   * Select `.bin` and flash
6. **Repeat for all 6 ESP32 boards**

---

### **4.2 Host ESP32 Setup**

1. Open `host_main.py`
2. Edit Wi-Fi and PC receiver settings:

```python
WIFI_SSID = "YourWiFiName"
WIFI_PASSWORD = "YourWiFiPassword"
PC_IP = "YourPC_LAN_IP"
PC_PORT = 12345
```

3. Upload `host_main.py` to the host ESP32

---

### **4.3 Client ESP32 Setup**

1. Upload the following files to each client:

```
ak09911.py
bmi160.py
boot.py
fusion.py
main.py
```

2. Edit `main.py` and set a unique `TRACKER_ID` (0–4 for each client)

---

## **5. PC Software Installation & Usage**

1. Ensure **Python** is installed on your PC
2. Run one of the following:

   * **Script**: `NekoSlimeReceiver.py`
   * **Executable**: `dist/NekoSlimeReceiver.exe`
3. **Startup order**:

   1. Power on all ESP32 boards
   2. Start the SlimeVR server
   3. Run NekoSlime Receiver and click “Connect”
   4. Check if trackers appear in SlimeVR

---
