from TTDefine import *

#############################################################
#
#            定义路径节点，前后左右表示是否有相同的路径
#            MapX,MapY 表示在地图上的块坐标，注意！这里不是cm坐标
#
#
###############################################################


class TTRouteNode(object):
    def __init__(
        self, Map, MapX, MapY, Node_L=None, Node_R=None, Node_F=None, Node_B=None
    ):
        self.Map = Map
        self.MapX = MapX
        self.MapY = MapY
        self.AbsX = 0  # 路径节点中心在地图上的绝对坐标值 X
        self.AbsY = 0  # 路径节点中心在地图上的绝对坐标值 Y
        self.Node_L = Node_L
        self.Node_R = Node_R
        self.Node_F = Node_F
        self.Node_B = Node_B
        self.LConnect(Node_L)
        self.RConnect(Node_R)
        self.FConnect(Node_F)
        self.BConnect(Node_B)

        self.CaculateAbsLoca()  # 计算在地图上的绝对坐标位置

        self.IsDeadEnd = False  # 标记是否为死胡同终点 ！！！隐藏任务的常见位置 ！！！
        self.IsDisable = False  # 标记是否为无效路径

        # 是否为头尾结点
        self.IsBeginNode = (MapX == BeginX) and (MapY == BeginY)  # 是否为头节点，默认False
        self.IsEndNode = (MapX == EndX) and (MapY == EndY)  # 是否为尾节点，默认False

        # 各方向上是否有墙，默认未知状态
        self.HasWall_L = HW_Unknown  # 左面是否有墙
        self.HasWall_R = HW_Unknown  # 右面是否有墙
        self.HasWall_F = HW_Unknown  # 前面是否有墙
        self.HasWall_B = HW_Unknown  # 后面是否有墙

        # 将节点添加到地图中去
        self.Map.IncludeARNode(self)

    # 向左连接一个节点
    def LConnect(self, ANode):
        if not (ANode is None):
            self.Node_L = ANode
            self.HasWall_L = HW_No  # 设置自己左边界没有墙
            ANode.Node_R = self
            ANode.HasWall_R = HW_No  # 设置节点有边界没有墙

    # 向右连接一个节点
    def RConnect(self, ANode):
        if not (ANode is None):
            self.Node_R = ANode
            self.HasWall_R = HW_No
            ANode.Node_L = self
            ANode.HasWall_L = HW_No

    # 向前连接一个节点
    def FConnect(self, ANode):
        if not (ANode is None):
            self.Node_F = ANode
            self.HasWall_F = HW_No
            ANode.Node_B = self
            ANode.HasWall_B = HW_No

    # 向后连接一个节点
    def BConnect(self, ANode):
        if not (ANode is None):
            self.Node_B = ANode
            self.HasWall_B = HW_No
            ANode.Node_F = self
            ANode.HasWall_F = HW_No

    # 判断两个节点是否相连接
    def IsConnectWith(self, ANode):
        return (
            (self.Node_L == ANode)
            or (self.Node_R == ANode)
            or (self.Node_F == ANode)
            or (self.Node_B == ANode)
        )

    # 返回一个！！！已经连接！！！的节点相对于自己的方位

    def NodeConnToMy(self, ANode):
        Result = NS_None
        if not ANode is None:
            if self.Node_L == ANode:
                Result = NS_Left
            elif self.Node_R == ANode:
                Result = NS_Right
            elif self.Node_F == ANode:
                Result = NS_Front
            elif self.Node_B == ANode:
                Result = NS_Back
        return Result

    # 向左准备一个路径节点，如果不存在则创建一个路径节点,并进行连接
    # 同时修改对应节点的地图块坐标，并返回，所有方向相同
    def LPrepareANode(self):
        if self.Node_L is None:  # 避免重复创建
            self.LConnect(TTRouteNode(self.Map, self.MapX - 1, self.MapY))
        return self.Node_L

    def RPrepareANode(self):
        if self.Node_R is None:  # 避免重复创建
            self.RConnect(TTRouteNode(self.Map, self.MapX + 1, self.MapY))
        return self.Node_R

    def FPrepareANode(self):
        if self.Node_F is None:  # 避免重复创建
            self.FConnect(TTRouteNode(self.Map, self.MapX, self.MapY - 1))
        return self.Node_F

    def BPrepareANode(self):
        if self.Node_B is None:  # 避免重复创建
            self.BConnect(TTRouteNode(self.Map, self.MapX, self.MapY + 1))
        return self.Node_B

    # 取得所有和自己连接的节点列表
    def NodesConn(self):
        Result = []
        if not (self.Node_L is None):
            Result.append(self.Node_L)
        if not (self.Node_R is None):
            Result.append(self.Node_R)
        if not (self.Node_F is None):
            Result.append(self.Node_F)
        if not (self.Node_B is None):
            Result.append(self.Node_B)
        return Result

    # 计算在地图上的绝对坐标位置
    def CaculateAbsLoca(self):
        self.AbsX = (
            (self.MapX * MapBlockSize)
            - ((self.Map.Width * MapBlockSize) // 2)
            + (MapBlockSize // 2)
        )
        self.AbsY = -1 * (
            (self.MapY * MapBlockSize) - ((self.Map.Height * MapBlockSize) // 2)
        ) - (MapBlockSize // 2)

    # 更新自己的Disable状态,如果墙面总数，加上周围Disable节点的总数大于等于3，则此节点为无效节点
    def UpdateDisable(self):
        # 如果是终点或者起点不用计算
        if not (self.IsBeginNode or self.IsEndNode):
            # 计数
            Cnt = 0
            WallCnt = 0

            if self.HasWall_F == HW_Yes:
                Cnt = Cnt + 1
                WallCnt = WallCnt + 1  # 增加墙面计数，用于标记死点
            elif self.HasWall_F == HW_No:
                if not (self.Node_F is None):
                    if self.Node_F.IsDisable:
                        Cnt = Cnt + 1

            if self.HasWall_L == HW_Yes:
                Cnt = Cnt + 1
                WallCnt = WallCnt + 1
            elif self.HasWall_L == HW_No:
                if not (self.Node_L is None):
                    if self.Node_L.IsDisable:
                        Cnt = Cnt + 1

            if self.HasWall_R == HW_Yes:
                Cnt = Cnt + 1
                WallCnt = WallCnt + 1
            elif self.HasWall_R == HW_No:
                if not (self.Node_R is None):
                    if self.Node_R.IsDisable:
                        Cnt = Cnt + 1

            if self.HasWall_B == HW_Yes:
                Cnt = Cnt + 1
                WallCnt = WallCnt + 1
            elif self.HasWall_B == HW_No:
                if not (self.Node_B is None):
                    if self.Node_B.IsDisable:
                        Cnt = Cnt + 1

            self.IsDisable = Cnt >= 3
            self.IsDeadEnd = WallCnt >= 3

    # 根据自己的状态更新自己周边的节点的状态

    def UpdateDisableArea(self):
        self.UpdateDisable()
        if not (self.Node_L is None):
            self.Node_L.UpdateDisable()
        if not (self.Node_R is None):
            self.Node_R.UpdateDisable()
        if not (self.Node_B is None):
            self.Node_B.UpdateDisable()
        if not (self.Node_F is None):
            self.Node_F.UpdateDisable()

    #
    # 到一个节点的最短路径,计算最短路径算法
    # ANode 需要到达的节点
    # RoutePassed 已经经过的路径节点
    #
    # 返回值 ：如果能到达则返回包含重点的节点列表，如果不能到达，则返回None
    # 由于递归层级限制，放弃实用递归。在标记点的时候只取第一个有效节点开始进行
    #     算法要点：
    #             一路沿着有效节点走。
    #
    #
    def GetEnabledRouteTo(self, ANode):
        Result = [self]
        if not (ANode) is None:

            TempNode = self

            while not (TempNode is None):  # 判断是不是已经走到头了，或者已经找到了节点
                # led.normal(255, 255, 0)
                if TempNode == ANode:
                    break

                if not (TempNode.Node_L is None):
                    TempNode.Node_L.UpdateDisableArea()
                    if (not TempNode.Node_L.IsDisable) and (
                        TempNode.HasWall_L == HW_No
                    ):
                        if not (TempNode.Node_L in Result):
                            TempNode = TempNode.Node_L
                            Result.append(TempNode)
                            continue
                if not (TempNode.Node_R is None):
                    TempNode.Node_R.UpdateDisableArea()
                    if (not TempNode.Node_R.IsDisable) and (
                        TempNode.HasWall_R == HW_No
                    ):
                        if not (TempNode.Node_R in Result):
                            TempNode = TempNode.Node_R
                            Result.append(TempNode)
                            continue
                if not (TempNode.Node_F is None):
                    TempNode.Node_F.UpdateDisableArea()
                    if (not TempNode.Node_F.IsDisable) and (
                        TempNode.HasWall_F == HW_No
                    ):
                        if not (TempNode.Node_F in Result):
                            TempNode = TempNode.Node_F
                            Result.append(TempNode)
                            continue
                if not (TempNode.Node_B is None):
                    TempNode.Node_B.UpdateDisableArea()
                    if (not TempNode.Node_B.IsDisable) and (
                        TempNode.HasWall_B == HW_No
                    ):
                        if not (TempNode.Node_B in Result):
                            TempNode = TempNode.Node_B
                            Result.append(TempNode)
                            continue
                TempNode = None

        return Result
