from TTRouteNode import *
from TTInit import *

####################################################
#
#
#   探索控制类
#
#
####################################################
class TTDiscover(object):
    def __init__(self, AMap, ATTESP32):
        self.Map = AMap
        self.TT = ATTESP32
        self.BeginNode = TTRouteNode(AMap, BeginX, BeginY)  # 创建头节点
        # 设置头节点的相关属性
        self.BeginNode.IsBeginNode = True  # 是开始节点
        self.EndNode = None

    def MisssionInit(self):
        self.TT.Init()
        self.TT.TakeOff()

    def MissionFinit(self):
        self.TT.Land()
        self.TT.FInit()

    # 一个空任务，测试机器状态用
    def EmptyMission(self):
        self.MisssionInit()
        self.TT.FlashLED()
        self.MissionFinit()

    # 原始走迷宫算法一路向右直到走到迷宫出口。需手动停止任务
    def AllGoRight(self):
        def TTMove():
            self.TT.Forward()
            self.TT.ShowTask()

        # 不断重复向右找出口的方法，默认无人机向地图前方
        while True:

            self.TT.TurnRight()
            if not self.TT.CanGoForward():
                self.TT.CorrectFDist()
                self.TT.TurnLeft()
                if not self.TT.CanGoForward():
                    self.TT.CorrectFDist()
                    self.TT.TurnLeft()
                    if not self.TT.CanGoForward():
                        self.TT.CorrectFDist()
                        self.TT.TurnLeft()
                        TTMove()
                    else:
                        TTMove()
                else:
                    TTMove()
            else:
                TTMove()

    # 精简路径
    # 将路径上方向相同的节点删除，仅保留两头的节点
    def GetSimplifyARoute(self, ARoute):
        Result = []
        LastN = None  # 最后一个节点
        SameXCnt = 0  # 相同的X坐标次数
        SameYCnt = 0  # 相同的Y坐标的次数
        for N in ARoute:
            if not (LastN is None):
                if LastN.MapX == N.MapX:  # 如果X坐标相等，则增加X相同次数
                    SameXCnt = SameXCnt + 1
                    if SameXCnt > 1:
                        Result.remove(LastN)
                        SameXCnt = SameXCnt - 1
                else:
                    SameXCnt = 0

                if LastN.MapY == N.MapY:
                    SameYCnt = SameYCnt + 1
                    if SameYCnt > 1:
                        Result.remove(LastN)
                        SameYCnt = SameYCnt - 1
                else:
                    SameYCnt = 0

            LastN = N
            Result.append(N)

        return Result

    # 沿着一个路径飞行,飞机默认在第一个节点上，路径必须是连续的
    def FallowRoute(self, ARoute):
        if not (self.TT.Facing == TTF_Front):
            self.TT.TurnToFront()

        if not (ARoute is None):
            # 取简化路径
            SRoute = self.GetSimplifyARoute(ARoute)
            LastNode = None
            for RNode in SRoute:
                if protocol.getTelloMsgInt("[TELLO] mid?", 1000) == 12:
                    self.TT.GoToANode(RNode)
                    LastNode = RNode
                else:
                    ###取需要移动的绝对X和Y，并进行移动
                    DistX = RNode.AbsX - LastNode.AbsX
                    DistY = RNode.AbsY - LastNode.AbsY

                    if DistX >= 0:
                        self.TT.Right(DistX)
                    else:
                        self.TT.Left(-1 * DistX)

                    if DistY >= 0:
                        self.TT.Forward(DistY)
                    else:
                        self.TT.Backward(-1 * DistY)

    # 探索一个节点的一面 !!!!!!!!!!!! 飞机必须已经飞行到此节点位置 !!!!!!!!!!!
    def DiscoverANodeSide(self, ANode):
        if not ANode is None:
            if not self.TT.CanGoForward():  # 如果飞机不能前进，根据飞机朝向标记墙面
                if self.TT.Facing == TTF_Front:
                    ANode.HasWall_F = HW_Yes
                elif self.TT.Facing == TTF_Left:
                    ANode.HasWall_L = HW_Yes
                elif self.TT.Facing == TTF_Right:
                    ANode.HasWall_R = HW_Yes
                elif self.TT.Facing == TTF_Back:
                    ANode.HasWall_B = HW_Yes
            else:  # 如果可以前进，准备前进的节点
                if self.TT.Facing == TTF_Front:
                    ANode.FPrepareANode()
                elif self.TT.Facing == TTF_Left:
                    ANode.LPrepareANode()
                elif self.TT.Facing == TTF_Right:
                    ANode.RPrepareANode()
                elif self.TT.Facing == TTF_Back:
                    ANode.BPrepareANode()
            # 更新Node自己的状态
            ANode.UpdateDisable()
            # 更新节点在地图中的状态
            self.TT.AMap.IncludeARNode(ANode)

    # 判断当前飞机是不是需要右转,如果当前飞机朝向的右侧如果有墙则不需要右转
    def TTCanGoRight(self, ANode):
        Result = False
        if not (ANode is None):
            Result = self.GetHasWallRight(ANode) == HW_No
        return Result

    # 判断飞机是否能向前进
    def TTCanGoForward(self, ANode):
        Result = False
        if not (ANode is None):
            Result = self.GetHasWallForward(ANode) == HW_No
        return Result

    # 判断飞机是否能向前进
    def TTCanGoLeft(self, ANode):
        Result = False
        if not (ANode is None):
            Result = self.GetHasWallLeft(ANode) == HW_No
        return Result

    def TTCanGoBack(self, ANode):
        Result = False
        if not (ANode is None):
            Result = self.GetHasWallBack(ANode) == HW_No
        return Result

    # 获取前进方向上的下一个节点
    def GetNextNode(self, ANode):
        Result = None
        if not (ANode is None):
            if self.TT.Facing == TTF_Front:
                Result = ANode.Node_F
            elif self.TT.Facing == TTF_Right:
                Result = ANode.Node_R
            elif self.TT.Facing == TTF_Back:
                Result = ANode.Node_B
            elif self.TT.Facing == TTF_Left:
                Result = ANode.Node_L
        return Result

    # 获取当前方向上右侧墙的状态
    def GetHasWallRight(self, ANode):
        Result = HW_Unknown
        if not (ANode is None):
            if self.TT.Facing == TTF_Front:
                Result = ANode.HasWall_R
            elif self.TT.Facing == TTF_Right:
                Result = ANode.HasWall_B
            elif self.TT.Facing == TTF_Back:
                Result = ANode.HasWall_L
            elif self.TT.Facing == TTF_Left:
                Result = ANode.HasWall_F
        return Result

    # 获取当前方向上后方墙的状态
    def GetHasWallBack(self, ANode):
        Result = HW_Unknown
        if not (ANode is None):
            if self.TT.Facing == TTF_Front:
                Result = ANode.HasWall_B
            elif self.TT.Facing == TTF_Right:
                Result = ANode.HasWall_L
            elif self.TT.Facing == TTF_Back:
                Result = ANode.HasWall_F
            elif self.TT.Facing == TTF_Left:
                Result = ANode.HasWall_R
        return Result

    # 获取当前前进方向上的墙的状态
    def GetHasWallForward(self, ANode):
        Result = HW_Unknown
        if not (ANode is None):
            if self.TT.Facing == TTF_Front:
                Result = ANode.HasWall_F
            elif self.TT.Facing == TTF_Right:
                Result = ANode.HasWall_R
            elif self.TT.Facing == TTF_Back:
                Result = ANode.HasWall_B
            elif self.TT.Facing == TTF_Left:
                Result = ANode.HasWall_L
        return Result

    # 获取当前左面的墙的状态
    def GetHasWallLeft(self, ANode):
        Result = HW_Unknown
        if not (ANode is None):
            if self.TT.Facing == TTF_Front:
                Result = ANode.HasWall_L
            elif self.TT.Facing == TTF_Right:
                Result = ANode.HasWall_F
            elif self.TT.Facing == TTF_Back:
                Result = ANode.HasWall_R
            elif self.TT.Facing == TTF_Left:
                Result = ANode.HasWall_B
        return Result

    # 右手优先算法一
    def DiscoverToEndRightFirst1(self, ANode):
        CurNode = ANode
        LastNode = ANode
        while not CurNode.IsEndNode:  # 如果没有找到最终节点

            LastNode.UpdateDisableArea()  # 节点更新状态
            # ShowInfo(str(LastNode.IsDeadEnd))
            if LastNode.IsDeadEnd:  # 如果是死胡同，则进行任务显示
                self.TT.ShowTask()
                self.TT.Forward()
            else:
                if protocol.getTelloMsgInt("[TELLO] mid?", 1000) == 12:
                    self.TT.GoToANode(CurNode)  # 飞到此节点上
                else:
                    self.TT.ShowTask()
                    self.TT.Forward()  # 如果识别到了挑战卡需要直接向前跑 ！！！！！！！！！！这里已然存在路径中存在其他挑战卡出现的问题需要从坐标系中进行规避！！！！！！！！！！！

            # 探测完任务后再飞到新节点上

            # 如果右侧墙面未知向右看一眼，如果能走就走，不能走就回来，相对的右侧！！！！！！！，不是绝对的右侧
            StartHWR = self.GetHasWallRight(CurNode)  # 刚进入地图块的右侧墙状态，前进方向右侧
            StartHWL = self.GetHasWallLeft(CurNode)  # 刚进入地图块的右侧墙状态，前进方向右侧
            StartHWF = self.GetHasWallForward(CurNode)  # 刚进入地图块的右侧墙状态，前进方向右侧
            StartHWB = self.GetHasWallBack(CurNode)

            # ShowInfo(str(CurNode.HasWall_F))

            # led.normal(255, 0, 255)
            if not (
                (StartHWR == HW_Unknown)
                or (StartHWL == HW_Unknown)
                or (StartHWF == HW_Unknown)
                or (StartHWB == HW_Unknown)
            ):
                if StartHWR == HW_No:
                    self.TT.TurnRight()
                    LastNode = CurNode
                    CurNode = self.GetNextNode(CurNode)
                    continue
                elif StartHWF == HW_No:
                    LastNode = CurNode
                    CurNode = self.GetNextNode(CurNode)
                    continue

                elif StartHWL == HW_No:
                    self.TT.TurnLeft()
                    LastNode = CurNode
                    CurNode = self.GetNextNode(CurNode)
                    continue

            self.DiscoverANodeSide(CurNode)
            if (
                StartHWR == HW_Unknown
            ):  ###############################################################################！！！！！！！！！！！！！！！
                led.normal(0, 255, 255)
                self.TT.TurnRight()
                self.DiscoverANodeSide(CurNode)
                if self.TTCanGoForward(CurNode):  # 如果能往右走就往右走
                    # led.normal(255, 0, 0)
                    LastNode = CurNode
                    CurNode = self.GetNextNode(CurNode)
                    continue
                elif self.TTCanGoLeft(CurNode):  # 注意，这里已经面朝右了，所以之前的前面在现在的左面，且已经探索过
                    # led.normal(0, 0, 255)
                    self.TT.TurnLeft()  # 左转，并前进
                    LastNode = CurNode
                    CurNode = self.GetNextNode(CurNode)
                    continue
                else:  # 再看现在的后方，也就是进入时的左边，现在时后面
                    # led.normal(0, 255, 0)
                    if self.TTCanGoBack(CurNode):  # 如果时有墙的，直接右转前进
                        self.TT.TurnRight()
                        LastNode = CurNode
                        CurNode = self.GetNextNode(CurNode)
                        continue
                    elif StartHWL == HW_Unknown:  # 未知则掉头，也就是转向进入时的左侧
                        self.TT.TurnBack()  # 回头并进行探测，结果只有两种，有，或者没有，如果有就左转前进，如果没有就继续前进
                        self.DiscoverANodeSide(CurNode)
                        if self.GetHasWallForward(CurNode) == HW_Unknown:  #
                            self.DiscoverANodeSide(CurNode)
                            if self.GetHasWallForward(CurNode) == HW_Yes:
                                self.TT.TurnLeft()
                            LastNode = CurNode
                            CurNode = self.GetNextNode(CurNode)
                            continue
                    else:  # 有墙直接右转离开
                        self.TT.TurnRight()
                        LastNode = CurNode
                        CurNode = self.GetNextNode(CurNode)
                        continue
            elif StartHWR == HW_No:  # 如果右侧没有墙，直接右转前进
                # led.normal(255, 255, 0)
                self.TT.TurnRight()
                LastNode = CurNode
                CurNode = self.GetNextNode(CurNode)
                continue
            else:  # 如果右侧有墙
                # led.normal(255, 255, 255)
                if self.TTCanGoForward(CurNode):  # 如果能前进，则前进，此时前面墙面在进入时已经探测过
                    LastNode = CurNode
                    CurNode = self.GetNextNode(CurNode)
                    continue

                if self.TTCanGoLeft(CurNode):  # 如果能够左转就左转，除此之外左侧墙面还有两种可能性，有墙或者未知
                    self.TT.TurnLeft()
                    LastNode = CurNode
                    CurNode = self.GetNextNode(CurNode)
                    continue
                elif self.GetHasWallLeft(CurNode) == HW_Yes:
                    self.TT.TurnBack()
                    LastNode = CurNode
                    CurNode = self.GetNextNode(CurNode)
                    continue
                else:  # 未知左侧是否有墙左转探测
                    self.TT.TurnLeft()
                    self.DiscoverANodeSide(CurNode)
                    if self.TTCanGoForward(CurNode):
                        LastNode = CurNode
                        CurNode = self.GetNextNode(CurNode)
                        continue
                    else:
                        self.TT.TurnLeft()
                        LastNode = CurNode
                        CurNode = self.GetNextNode(CurNode)
                        continue

        self.EndNode = CurNode
        self.TT.GoToANode(self.EndNode)
        if not (self.TT.Facing == TTF_Front):
            self.TT.TurnToFront()
        self.TT.FlashLED()

    # 探索直到找到出口
    def DiscoverToEnd(self, ANode):
        self.DiscoverToEndRightFirst1(ANode)

    # 飞回出发点
    def BackToBegin(self):
        # led.normal(0, 255, 255)
        Rout = self.EndNode.GetEnabledRouteTo(self.BeginNode)
        self.FallowRoute(Rout)
