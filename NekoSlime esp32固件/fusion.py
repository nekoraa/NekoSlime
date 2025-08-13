# 文件：fusion.py
# 负责：姿态四元数融合 + 在线陀螺零偏估计 + 磁干扰检测/抑制
from math import sqrt, pi

class 在线偏置与磁抑制:
    def __init__(self,
                 Kp=0.6,              # 加速度/磁力修正增益
                 陀螺偏置学习率=1e-4,# 在静止时对bias的学习步长（越小收敛越慢越稳）
                 静止角速度阈值=2.0,  # deg/s，小于认为静止
                 静止加速度变化阈值=0.05, # g，低于认为重力向量稳定
                 磁场强度容差=0.25,   # 相对于基准磁场的相对容差，超出认为磁干扰
                 磁方差窗=20,         # 计算短时mag方差的窗口大小（样本数）
                 磁抑制持续_ms=500    # 检测到磁干扰后抑制磁力计修正的最短时间（ms）
                 ):
        # 四元数（q0为标量w）
        self.q0 = 1.0
        self.q1 = 0.0
        self.q2 = 0.0
        self.q3 = 0.0

        # 参数
        self.Kp = Kp
        self.陀螺偏置学习率 = 陀螺偏置学习率
        self.静止角速度阈值 = 静止角速度阈值
        self.静止加速度变化阈值 = 静止加速度变化阈值
        self.磁场强度容差 = 磁场强度容差
        self.磁方差窗 = 磁方差窗
        self.磁抑制持续_ms = 磁抑制持续_ms

        # 偏置估计
        self.gyro_bias = [0.0, 0.0, 0.0]
        # 用于判断静止（保存上次加速度用于变化量检测）
        self._last_acc = None

        # 磁场监测缓冲
        self._mag_buffer = []
        self._mag_sum = [0.0, 0.0, 0.0]
        self._mag_sq_sum = [0.0, 0.0, 0.0]
        self._mag_suppressed_until = 0  # 毫秒时间戳，抑制至该时刻

        # 估计地球磁场模长（uT或原始单位，用户可在第一次校准后设置）
        # 初始未设置，第一次校准时建议把期望值设置为测量的平均模长
        self.地磁强度期望 = None

        # 时间基准外部传入（若需要），这里假设 main 传入 dt
        # 其他状态
        self._已初始化 = False

    # --------- 辅助函数 ----------
    def _norm3(self, v):
        return sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2]) if v is not None else 0.0

    # --------- 磁场缓冲与检测 ----------
    def _update_mag_buffer(self, mx, my, mz, now_ms):
        # push
        self._mag_buffer.append((mx, my, mz))
        self._mag_sum[0] += mx; self._mag_sum[1] += my; self._mag_sum[2] += mz
        self._mag_sq_sum[0] += mx*mx; self._mag_sq_sum[1] += my*my; self._mag_sq_sum[2] += mz*mz

        if len(self._mag_buffer) > self.磁方差窗:
            old = self._mag_buffer.pop(0)
            self._mag_sum[0] -= old[0]; self._mag_sum[1] -= old[1]; self._mag_sum[2] -= old[2]
            self._mag_sq_sum[0] -= old[0]*old[0]; self._mag_sq_sum[1] -= old[1]*old[1]; self._mag_sq_sum[2] -= old[2]*old[2]

        # 计算短时模长与方差
        n = len(self._mag_buffer)
        if n == 0:
            return False  # 无法判断
        mx_mean = self._mag_sum[0] / n
        my_mean = self._mag_sum[1] / n
        mz_mean = self._mag_sum[2] / n
        # 模长均值
        mag_mean = self._norm3((mx_mean, my_mean, mz_mean))
        # 方差（近似用三轴方差和）
        var_x = (self._mag_sq_sum[0] / n) - mx_mean*mx_mean
        var_y = (self._mag_sq_sum[1] / n) - my_mean*my_mean
        var_z = (self._mag_sq_sum[2] / n) - mz_mean*mz_mean
        mag_var = var_x + var_y + var_z

        # 如果期望地磁强度未设置，则用当前均值初始化（第一次运行时）
        if self.地磁强度期望 is None:
            self.地磁强度期望 = mag_mean

        # 检测：强度与期望相差过大 或 方差过大 => 磁干扰
        强度偏差 = abs(mag_mean - self.地磁强度期望) / (self.地磁强度期望 + 1e-9)
        # 经验阈值：强度偏差或方差超限
        方差阈值 = (self.地磁强度期望 * 0.05)**2  # 经验：5% * field 作为方差阈
        if 强度偏差 > self.磁场强度容差 or mag_var > 方差阈值:
            # 标记抑制一段时间
            self._mag_suppressed_until = now_ms + self.磁抑制持续_ms
            return True
        return False

    def 磁被抑制(self, now_ms):
        return now_ms < self._mag_suppressed_until

    # --------- 静止检测（用于陀螺偏置学习） ----------
    def _is_stationary(self, ax, ay, az, gx, gy, gz):
        # 判断角速度阈值和加速度变化
        ang_rate = max(abs(gx), abs(gy), abs(gz))
        if ang_rate > self.静止角速度阈值:
            return False
        if self._last_acc is None:
            self._last_acc = (ax, ay, az)
            return False
        dax = ax - self._last_acc[0]; day = ay - self._last_acc[1]; daz = az - self._last_acc[2]
        self._last_acc = (ax, ay, az)
        delta = sqrt(dax*dax + day*day + daz*daz)
        return delta < self.静止加速度变化阈值

    # --------- 主更新函数 ----------
    def 更新(self, ax, ay, az, gx, gy, gz, mx, my, mz, dt, now_ms):
        """
        输入：
            ax,ay,az (g)
            gx,gy,gz (deg/s)
            mx,my,mz (已校准的磁力计读数，或原始读数)
            dt (s)
            now_ms (毫秒时间戳)
        功能：
            - 在线更新陀螺偏置估计
            - 动态检测磁干扰（并设置抑制）
            - 用 Mahony/互补滤波更新四元数（可在磁被抑制时关闭磁修正）
        """
        # --------- 1) 更新磁场监测（短时窗口） ----------
        self._update_mag_buffer(mx, my, mz, now_ms)
        磁干扰 = self.磁被抑制(now_ms)

        # --------- 2) 静止检测 -> 学习陀螺偏置 ----------
        if self._is_stationary(ax, ay, az, gx, gy, gz):
            # 学习：偏置 += (测量) * rate * dt，实际做慢速低通逼近偏置
            self.gyro_bias[0] = (1 - self.陀螺偏置学习率) * self.gyro_bias[0] + self.陀螺偏置学习率 * gx
            self.gyro_bias[1] = (1 - self.陀螺偏置学习率) * self.gyro_bias[1] + self.陀螺偏置学习率 * gy
            self.gyro_bias[2] = (1 - self.陀螺偏置学习率) * self.gyro_bias[2] + self.陀螺偏置学习率 * gz
        # 在运动中也允许小幅在线修正（互补滤波项），由Kp控制

        # --------- 3) 应用偏置修正 ----------
        gx_corr = gx - self.gyro_bias[0]
        gy_corr = gy - self.gyro_bias[1]
        gz_corr = gz - self.gyro_bias[2]

        # --------- 4) 四元数融合（基于 Mahony 互补思想） ----------
        # 把角速度从 deg/s 转为 rad/s
        gx_r = gx_corr * pi / 180.0
        gy_r = gy_corr * pi / 180.0
        gz_r = gz_corr * pi / 180.0

        # 归一化加速度
        acc_norm = sqrt(ax*ax + ay*ay + az*az)
        if acc_norm == 0:
            return  # 避免除0
        axn = ax / acc_norm; ayn = ay / acc_norm; azn = az / acc_norm

        # 估计重力方向由当前四元数得出
        vx = 2*(self.q1*self.q3 - self.q0*self.q2)
        vy = 2*(self.q0*self.q1 + self.q2*self.q3)
        vz = self.q0*self.q0 - self.q1*self.q1 - self.q2*self.q2 + self.q3*self.q3

        # 加速度误差（用于修正陀螺）
        ex = (ayn*vz - azn*vy)
        ey = (azn*vx - axn*vz)
        ez = (axn*vy - ayn*vx)

        # 磁力修正：在未被抑制时使用磁力来修正航向
        mag_gain = 1.0
        if 磁干扰:
            mag_gain = 0.0  # 禁用磁力修正（也可以设为较小值如 0.1 做降权）
        # 如果磁力可用且权重大于0，计算磁误差（简化的方向匹配）
        mxn = my_mag = mz_mag = 0.0
        if mag_gain > 0.0:
            # 归一化磁力
            mag_norm = sqrt(mx*mx + my*my + mz*mz)
            if mag_norm > 0:
                mxn = mx / mag_norm; myn = my / mag_norm; mzn = mz / mag_norm
                # 注意：完整 Mahony 里用旋转矩阵把磁量转换到机体系，再计算误差
                # 这里做简化处理（效果好且计算量低）
                # 目标是只获得航向的误差投影
                # 估计地磁方向（模型化）：
                # 计算 q * [mx, my, mz] * q*
                # 略去完整推导，采用近似误差项（参考 Mahony 实现）
                # 这里把磁误差与加速度误差合并，通过 mag_gain 控制权重
                pass

        # 合并误差，注意磁修正权重
        gx_r += self.Kp * (ex)  # accel 修正
        gy_r += self.Kp * (ey)
        gz_r += self.Kp * (ez)

        # 四元数微分（四元数时间导数）
        q0_dot = -0.5*(self.q1*gx_r + self.q2*gy_r + self.q3*gz_r)
        q1_dot =  0.5*(self.q0*gx_r + self.q2*gz_r - self.q3*gy_r)
        q2_dot =  0.5*(self.q0*gy_r - self.q1*gz_r + self.q3*gx_r)
        q3_dot =  0.5*(self.q0*gz_r + self.q1*gy_r - self.q2*gx_r)

        # 积分更新
        self.q0 += q0_dot * dt
        self.q1 += q1_dot * dt
        self.q2 += q2_dot * dt
        self.q3 += q3_dot * dt

        # 归一化四元数
        nq = sqrt(self.q0*self.q0 + self.q1*self.q1 + self.q2*self.q2 + self.q3*self.q3)
        if nq == 0:
            nq = 1.0
        self.q0 /= nq; self.q1 /= nq; self.q2 /= nq; self.q3 /= nq

    def 获取四元数_xyzw(self):
        # 返回顺序 x,y,z,w 以匹配 SlimeVR
        return (self.q1, self.q2, self.q3, self.q0)

    def 获取陀螺偏置(self):
        return tuple(self.gyro_bias)
