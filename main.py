from TTDefine import *
from TTInit import *
from TTMap import *
from TTESP32 import *
from TTDiscover import *

#############################################################
#
#     ##     ##
#     ###   ###
#     #### ####
#     #########
#     ## ### ##
#     ##  #  ##
#     ##     ##          2021
#    ####   ####
#
#
#
#    主程序
#
############################################################


def main():
    AMap = TTMap(3, 4)
    ATT = TTESP32(AMap, StartFacing=TTStartFacing)
    ADiscover = TTDiscover(AMap, ATT)
    ATT.Init()
    ATT.TakeOff()
    # ATT.TakeOffWaitMap()
    # ADiscover.DiscoverToEnd(ADiscover.BeginNode)
    # ADiscover.BackToBegin()
    ATT.TurnLeft()
    ATT.TurnLeft()
    ATT.TurnLeft()
    ATT.TurnLeft()

    ATT.Land()


################################################
#
#   主程序入口，并进行异常捕获
#
################################################

try:
    main()
    matrix.normal("000000000pppppp00rrrrrb00r0r0rb00r0r0rb00r0r0rb00r0r0rb000000000")
except Exception as e:
    ShowInfo(str(e) + "<")
    ATT.Land()
