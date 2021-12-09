from TTDefine import *
from TTInit import *


####################################################
#
#
#     TT无人机类
#
#
####################################################

# TT类
class TTESP32(object):
    def __init__(self, AMap, StartFacing=TTF_Front):
        self.AMap = AMap  # 飞机所在的地图
        self.Facing = TTF_Front  # 飞机朝向,起始朝向必须朝前，面向Y轴正方向！！！
        self.StartFacing = StartFacing
        self.TakeOffYaw = 0  # 起飞时的偏航角度，在起飞时会进行记录，用于角度校正
        self.LastYaw = 0  # 最后一次的偏航角度。每次取得新的偏航角度时会进行记录
        self.LastTaskNum = -1  # 最后一次挑战卡的编号

    def GetDistance(self):  # 获得当前正面距离
        return tof.read()

    # 在终点闪烁LED灯
    def FlashLED(self):
        for i in range(3):
            led.normal(255, 0, 0)
            time.sleep(0.5)
            if i == 2:  # 减少没有必要的等待
                break
            led.normal(0, 0, 0)
            time.sleep(0.5)
        led.normal(0, 255, 0)

    # 转向启动时的方向
    def TurnToStartFacing(self):
        if self.StartFacing == TTF_Left:
            self.TurnToLeft()
        elif self.StartFacing == TTF_Right:
            self.TurnToRight()
        elif self.StartFacing == TTF_Back:
            self.TurnToBack()

    # 起飞后等待识别到地图
    def TakeOffWaitMap(self):
        while protocol.getTelloMsgInt("[TELLO] mid?", 1000) == 1:
            time.sleep(0.10)

    # 起飞
    def TakeOff(self):
        matrix.normal(
            "000rr00000rppr000rppppr0rrrpprrr00rppr0000rppr0000rppr0000rrrr00"
        )  # 显示起飞图案
        self.TakeOffYaw = self.GetYaw()  # 记录起飞时的偏航角!!!!!!!!
        led.normal(0, 255, 0)
        protocol.sendTelloCtrlMsg("takeoff")
        self.TurnToStartFacing()  # 转向起始

    # 降落
    def Land(self):
        led.normal(0, 0, 255)
        protocol.sendTelloCtrlMsg("land")

    # 初始化无人机
    def Init(self):
        matrix.normal(
            "000000000rp00rp00rp00pp00rp00pb00bp0pp000bppp0000bpp000000000000"
        )  # 显示初始画面
        led.normal(0, 0, 255)
        while not (p34.value() == 0):  # 引脚34低电平有效,等待按键被按下
            time.sleep(0.1)
        led.normal(255, 0, 255)
        time.sleep(2)
        led.normal(255, 255, 0)
        while not (
            protocol.getTelloMsgString("[TELLO] command", 1000) == "ETT ok"
        ):  # 初始化主机通信，等待完成
            time.sleep(0.1)
        led.normal(0, 0, 255)
        protocol.sendTelloCtrlMsg("mon")  # 打开挑战卡监视
        # protocol.sendTelloCtrlMsg("mdirection 2") #设置监视范围向前和向下
        protocol.sendTelloCtrlMsg("speed " + str(TTSpeed))

    # 结束化无人机
    def FInit(self):
        pass

    # 停止动作并悬停
    def Stop(self):
        protocol.sendTelloCtrlMsg("stop")

    # 显示当前挑战卡
    def ShowTask(self, TryCount=10):
        TaskNum = -1
        for i in range(TryCount):
            if (self.LastTaskNum == TaskNum) or (TaskNum == -1):  # 等待检测到新的挑战卡
                TaskNum = protocol.getTelloMsgInt("[TELLO] mid?", 1000)
            else:
                break
            time.sleep(0.2)

        self.LastTaskNum = TaskNum  # 修改最后一次挑卡的编号
        if (self.LastTaskNum >= 1) and (self.LastTaskNum <= 8):
            matrix.static_char(str(self.LastTaskNum), "r")

    # 前进
    def Forward(self, Distance=MapBlockSize):
        protocol.sendTelloCtrlMsg("forward " + str(Distance))

    # 后退
    def Backward(self, Distance=MapBlockSize):
        protocol.sendTelloCtrlMsg("back " + str(Distance))

    # 左移
    def Left(self, Distance=MapBlockSize):
        protocol.sendTelloCtrlMsg("left " + str(Distance))

    # 右移
    def Right(self, Distance=MapBlockSize):
        protocol.sendTelloCtrlMsg("right " + str(Distance))

    # 顺时针旋转
    def CW(self, Angle=TTRAngle):
        protocol.sendTelloCtrlMsg("cw " + str(Angle))

    # 逆时针旋转
    def CCW(self, Angle=TTRAngle):
        protocol.sendTelloCtrlMsg("ccw " + str(Angle))

    # 飞到场地的坐标位置
    def GoToMapPosition(self, X, Y, Z=TTHight, Speed=TTSpeed, Map="m-1"):
        protocol.sendTelloCtrlMsg(
            "go "
            + str(int(X))
            + " "
            + str(int(Y))
            + " "
            + str(int(Z))
            + " "
            + str(int(Speed))
            + " "
            + Map
        )

    # 飞到一个节点的位置
    def GoToANode(self, ANode):
        if not (ANode is None):
            self.GoToMapPosition(ANode.AbsX, ANode.AbsY)

    # 飞到相对自己的坐标位置
    def FromSelfGoTo(self, X, Y, Z=0, Speed=TTSpeed):
        protocol.sendTelloCtrlMsg(
            "go "
            + str(int(X))
            + " "
            + str(int(Y))
            + " "
            + str(int(Z))
            + " "
            + str(int(Speed))
        )

    # 判断面前是否有障碍物
    def IsBlocked(self):
        Result = self.GetDistance() < MapBlockSize
        return Result

    # 获取前距离，以CM为单位
    def FDistance(self):
        return tof.read() // 10

    # 返回自己能否向前移动
    def CanGoForward(self):
        return self.FDistance() > MapBlockSize

    # 在当前地图格内矫正前后距离
    def CorrectFDist(self):
        FDist = self.FDistance()  # 读取tof前距离，并转换为CM
        if FDist < (MapBlockSize):  # 如果前端距离小于地图格尺寸 - 10,前面障碍物在一个格内
            MoveDist = FDist - (MapBlockSize // 2)
            if MoveDist > 10:
                # self.Forward(MoveDist + 10)
                self.Forward(20)
            elif MoveDist < -10:
                # self.Backward((-1 * MoveDist) + 10)
                self.Backward(20)

    # 设置无人机相对于地图的偏航角度
    def SetYaw(self, Angle, AMap="m-1"):
        protocol.sendTelloCtrlMsg("setyaw " + str(Angle) + " " + AMap)

    # 取得当前的偏航角度
    # 取得当前的偏航角度
    def GetYaw(self):
        Succ = False  # 命令处理的结果，避免异常
        while not Succ:
            try:
                S = protocol.getTelloMsgString("[TELLO] attitude?", 1000)
                self.LastYaw = int(S[S.rfind("yaw:") + 4 : S.rfind(";")])
                Succ = True
            except:
                pass
        return self.LastYaw

    # 转到指定的偏航角
    def TurnToYaw(self, AYaw):
        CurYaw = self.GetYaw()  # 取得当前的偏航角度

        # 校正角度
        if AYaw > 180:
            AYaw = AYaw - 360
        if AYaw < -180:
            AYaw = AYaw + 360

        # 计算需要旋转的角度
        AngleToTurn = 0  # 需要旋转的角度

        if AYaw >= 0:
            if CurYaw >= 0:
                AngleToTurn = AYaw - CurYaw
            else:
                TmpAngle = AYaw - CurYaw
                if TmpAngle <= 180:
                    AngleToTurn = TmpAngle
                else:
                    AngleToTurn = -1 * (360 - TmpAngle)
        else:
            if CurYaw < 0:
                AngleToTurn = AYaw - CurYaw
            else:
                TmpAngle = CurYaw - AYaw
                if TmpAngle <= 180:
                    AngleToTurn = -1 * TmpAngle
                else:
                    AngleToTurn = 360 - TmpAngle

        # 进行旋转
        if AngleToTurn > 0:
            self.CW(AngleToTurn)
        elif AngleToTurn < 0:
            self.CCW((-1 * AngleToTurn))

    # 转到起飞时的偏航角度
    def TurnToTakeOffYaw(self):
        self.TurnToYaw(self.TakeOffYaw)

    # 转向前
    def TurnToFront(self):
        self.Facing = TTF_Front
        ToAngle = 0 + self.TakeOffYaw
        self.TurnToYaw(ToAngle)

    # 转向左
    def TurnToLeft(self):
        self.Facing = TTF_Left
        ToAngle = -90 + self.TakeOffYaw
        self.TurnToYaw(ToAngle)

    # 转向右
    def TurnToRight(self):
        self.Facing = TTF_Right
        ToAngle = 90 + self.TakeOffYaw
        self.TurnToYaw(ToAngle)

    # 转向后
    def TurnToBack(self):
        self.Facing = TTF_Back
        ToAngle = 180 + self.TakeOffYaw
        self.TurnToYaw(ToAngle)

    # 向右转，结合偏航角，以及当前面对的方向进行计算
    def TurnRight(self):

        # 根据当前面向方向进行计算

        if self.Facing == TTF_Front:
            self.TurnToRight()
        elif self.Facing == TTF_Right:
            self.TurnToBack()
        elif self.Facing == TTF_Back:
            self.TurnToLeft()
        elif self.Facing == TTF_Left:
            self.TurnToFront()

    # 向右转，结合偏航角，以及当前面对的方向进行计算
    def TurnLeft(self):
        # 根据当前面向方向进行计算
        if self.Facing == TTF_Front:
            self.TurnToLeft()
        elif self.Facing == TTF_Right:
            self.TurnToFront()
        elif self.Facing == TTF_Back:
            self.TurnToRight()
        elif self.Facing == TTF_Left:
            self.TurnToBack()

    # U Turn 掉头，结合偏航角，以及当前面对的方向进行计算
    def TurnBack(self):
        # 根据当前面向方向进行计算
        if self.Facing == TTF_Front:
            self.TurnToBack()
        elif self.Facing == TTF_Right:
            self.TurnToLeft()
        elif self.Facing == TTF_Back:
            self.TurnToFront()
        elif self.Facing == TTF_Left:
            self.TurnToRight()
