from TTDefine import *

########################################################################
#
#             TT地图，属性宽度，高度，TT迷宫初级宽度3，高度4     高级 5*5
#             地图块坐标以左上角为起点
#
#
#                     前
#                                                              0,0    1,0    2,0    3,0    4,0
#             0,0    1,0    2,0                                0,1    1,1    2,1    3,1    4,1
#             0,1    1,1    2,1                                0,2    1,2    2,2    3,2    4,2
#    左       0,2    1,2    2,2      右                        0,3    1,3    2,3    3,3    4,3
#             0,3    1,3    2,3                                0,4    1,4    2,4    3,4    4,4
#
#                     后
#
########################################################################


class TTMap(object):
    def __init__(self, Width, Height):
        self.Width = Width
        self.Height = Height
        # 根据地图尺寸创建地图快，次数为一个大坑，在此跌倒过一次，Mark一下
        self.Blocks = [[None] * Height for i in range(Width)]

    # 将一个路径节点添加到地图中来
    # 添加时设置路径相关属性
    #!!!!!!!!!!!!!!!!!!!!!!!默认起点和终点都有墙，出入口为封闭状态，到达节点即完成任务
    def IncludeARNode(self, ARNode):
        self.Blocks[ARNode.MapX][ARNode.MapY] = ARNode
        # 根据节点，设置相邻节点的状态
        if (ARNode.HasWall_L == HW_Yes) and (ARNode.MapX > 0):
            if not (self.Blocks[ARNode.MapX - 1][ARNode.MapY] is None):
                self.Blocks[ARNode.MapX - 1][ARNode.MapY].HasWall_R = HW_Yes
        if (ARNode.HasWall_R == HW_Yes) and (ARNode.MapX < self.Width - 1):
            if not (self.Blocks[ARNode.MapX + 1][ARNode.MapY] is None):
                self.Blocks[ARNode.MapX + 1][ARNode.MapY].HasWall_L = HW_Yes
        if (ARNode.HasWall_F == HW_Yes) and (ARNode.MapY > 0):
            if not (self.Blocks[ARNode.MapX][ARNode.MapY - 1] is None):
                self.Blocks[ARNode.MapX][ARNode.MapY - 1].HasWall_B = HW_Yes
        if (ARNode.HasWall_B == HW_Yes) and (ARNode.MapY < self.Height - 1):
            if not (self.Blocks[ARNode.MapX][ARNode.MapY + 1] is None):
                self.Blocks[ARNode.MapX][ARNode.MapY + 1].HasWall_F = HW_Yes

        if ARNode.MapX == 0:  # 如果是最左边的位置，左边一定有墙
            ARNode.HasWall_L = HW_Yes

        if ARNode.MapX == (self.Width - 1):  # 如果是最右边的位置，右边一定有墙
            ARNode.HasWall_R = HW_Yes

        if ARNode.MapY == 0:  # 如果是最上面的节点，上面肯定有墙
            ARNode.HasWall_F = HW_Yes

        if ARNode.MapY == (self.Height - 1):  # 如果是最下面的节点
            ARNode.HasWall_B = HW_Yes

        # 根据相邻节点设置节点的墙
        if ARNode.MapX > 0:
            LN = self.Blocks[ARNode.MapX - 1][ARNode.MapY]
            if not (LN is None):
                ARNode.HasWall_L = LN.HasWall_R
        if ARNode.MapX < self.Width - 1:
            RN = self.Blocks[ARNode.MapX + 1][ARNode.MapY]
            if not (RN is None):
                ARNode.HasWall_R = RN.HasWall_L

        if ARNode.MapY > 0:
            FN = self.Blocks[ARNode.MapX][ARNode.MapY - 1]
            if not (FN is None):
                ARNode.HasWall_F = FN.HasWall_B
        if ARNode.MapY < self.Height - 1:
            BN = self.Blocks[ARNode.MapX][ARNode.MapY + 1]
            if not (BN is None):
                ARNode.HasWall_B = BN.HasWall_F

    # 取得地图上所有的路径节点，按照从左向右顺序
    def GetAllRNodes(self):
        Result = []
        for j in range(self.Height):
            for i in range(self.Width):
                if not (self.Blocks[i][j] is None):
                    Result.append(self.Blocks[i][j])
        return Result
