####################################################
#
#
#   基础定义
#
#
####################################################


MapBlockSize = 60  # 定义地图块的大小默认 60CM

TTHight = 90  # 定义TT的飞行高度，场地框架边长60，90为上层框架的中间高度
TTSpeed = 100  # 定义TT的飞行速度
TTRAngle = 90  # 定义TT默认旋转角度 为90°

# 机头方向
TTF_Left = 0  # 面向左
TTF_Right = 1  # 面向右
TTF_Front = 2  # 面向前
TTF_Back = 3  # 面向后


# 路径节点的相对方位  TTNodeSide
NS_None = 0
NS_Left = 1
NS_Right = 2
NS_Front = 3
NS_Back = 4


# 路径对应方向上是否有墙
HW_Unknown = 0  # 未知
HW_Yes = 1  # 有墙
HW_No = 2  # 没有墙


# 起点坐标
BeginX = 1
BeginY = 0

# 终点坐标
EndX = 1
EndY = 3

# 起飞时面向的方向  ！！！必须和实际方向一致
TTStartFacing = TTF_Back
