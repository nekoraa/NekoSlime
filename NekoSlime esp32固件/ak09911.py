# 文件：ak09911.py
from machine import I2C
from time import sleep_ms

class AK09911C:
    # AK09911C I2C 地址（常见为 0x0C）
    地址 = 0xd
    # 寄存器定义
    寄存器_WIA1 = 0x00  # 公司ID
    寄存器_WIA2 = 0x01  # 设备ID
    寄存器_ST1  = 0x10  # 状态寄存器1
    寄存器_HXL  = 0x11  # 磁力计数据起始寄存器
    寄存器_ST2  = 0x18  # 状态寄存器2
    寄存器_CNTL2 = 0x31 # 控制2寄存器

    模式_10Hz = 0x02  # 连续测量模式1: 10Hz
    模式_100Hz = 0x08 # 连续测量模式4: 100Hz

    def __init__(self, i2c: I2C):
        self.i2c = i2c
        self.地址 = AK09911C.地址
        # 可选：检查设备ID
        who1 = self.i2c.readfrom_mem(self.地址, AK09911C.寄存器_WIA1, 1)[0]
        who2 = self.i2c.readfrom_mem(self.地址, AK09911C.寄存器_WIA2, 1)[0]
        # 参考手册 WIA1 = 0x48, WIA2 = 0x05 for AK09911C
        # 视实际情况可注释或调整：
        if who2 != 0x05:
            # 不是期望的设备ID时可抛错或提示
            raise OSError("未检测到 AK09911C 磁力计")
        # 进入连续测量模式（100Hz）
        self.i2c.writeto_mem(self.地址, AK09911C.寄存器_CNTL2, bytes([AK09911C.模式_100Hz]))
        sleep_ms(1)  # 等待模式切换

    def 读取磁力(self):
        """
        读取磁力计 (x,y,z) 三轴数据（单位：原始值）。
        返回元组：(mx, my, mz)。
        """
        # 等待数据准备(DRDY 位)
        while True:
            st1 = self.i2c.readfrom_mem(self.地址, AK09911C.寄存器_ST1, 1)[0]
            if st1 & 0x01:  # DRDY = 1 表示数据就绪
                break
        # 读取磁力计数据寄存器 HXL~HZH（6 字节）
        mag_bytes = self.i2c.readfrom_mem(self.地址, AK09911C.寄存器_HXL, 6)
        # 读取状态寄存器2 清除数据读取标志
        self.i2c.readfrom_mem(self.地址, AK09911C.寄存器_ST2, 1)
        # 合并并转换为有符号整数
        def _conv(lo, hi):
            raw = lo | (hi << 8)
            return raw - 65536 if raw & 0x8000 else raw
        mx = _conv(mag_bytes[0], mag_bytes[1])
        my = _conv(mag_bytes[2], mag_bytes[3])
        mz = _conv(mag_bytes[4], mag_bytes[5])
        return mx, my, mz
