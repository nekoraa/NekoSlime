# 文件：bmi160.py
from machine import I2C
from time import sleep_ms

class BMI160:
    # BMI160 I2C 地址
    地址 = 0x69
    # 寄存器和命令定义
    寄存器_设备ID = 0x00    # WHO_AM_I 寄存器
    寄存器_命令 = 0x7E    # 命令寄存器
    命令_软复位 = 0xB6
    命令_加速度正常模式 = 0x11
    命令_陀螺正常模式 = 0x15
    寄存器_陀螺_X低位 = 0x0C
    寄存器_加速度_X低位 = 0x12

    def __init__(self, i2c: I2C):
        self.i2c = i2c
        self.地址 = BMI160.地址
        # 检查设备 ID 是否匹配
        who = self.i2c.readfrom_mem(self.地址, BMI160.寄存器_设备ID, 1)
        if who[0] != 0xD1:
            raise OSError("未检测到 BMI160 设备")
        # 软复位
        self.i2c.writeto_mem(self.地址, BMI160.寄存器_命令, bytes([BMI160.命令_软复位]))
        sleep_ms(50)
        # 设置加速度计为正常模式
        self.i2c.writeto_mem(self.地址, BMI160.寄存器_命令, bytes([BMI160.命令_加速度正常模式]))
        sleep_ms(100)
        # 设置陀螺仪为正常模式
        self.i2c.writeto_mem(self.地址, BMI160.寄存器_命令, bytes([BMI160.命令_陀螺正常模式]))
        sleep_ms(100)

    def 读取六轴(self):
        """
        读取加速度计和陀螺仪数据（单位：g和度/秒）。
        返回元组：(ax, ay, az, gx, gy, gz)。
        """
        # 读取加速度 (连续读取 6 字节)
        acc_bytes = self.i2c.readfrom_mem(self.地址, BMI160.寄存器_加速度_X低位, 6)
        # 读取陀螺仪
        gyro_bytes = self.i2c.readfrom_mem(self.地址, BMI160.寄存器_陀螺_X低位, 6)
        # 合并并转换为有符号 16 位整数
        def _conv(lsb, msb):
            raw = lsb | (msb << 8)
            return raw - 65536 if raw & 0x8000 else raw
        ax = _conv(acc_bytes[0], acc_bytes[1]) / 16384.0  # 默认量程 ±2g => LSB/g
        ay = _conv(acc_bytes[2], acc_bytes[3]) / 16384.0
        az = _conv(acc_bytes[4], acc_bytes[5]) / 16384.0
        gx = _conv(gyro_bytes[0], gyro_bytes[1]) / 16.4    # 默认量程 ±2000°/s => LSB/°/s
        gy = _conv(gyro_bytes[2], gyro_bytes[3]) / 16.4
        gz = _conv(gyro_bytes[4], gyro_bytes[5]) / 16.4
        return ax, ay, az, gx, gy, gz
