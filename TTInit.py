from machine import *
from RMTTLib import *
from TTDefine import *

####################################################
#
#
#  初始化
#
#
####################################################
# 创建并初始化
led = RMTTLedCtrl()  # 定义LED的实用
led.start()  # LED开始工作
i2c = I2C(0, scl=Pin(26), sda=Pin(27), freq=400000)
matrix = RMTTMledCtrl(i2c)
uart1 = UART(1, baudrate=1000000, tx=18, rx=23)  # 创建串口通信
protocol = RMTTProtocol(uart1)  # RMTT通信协议
p34 = Pin(34, Pin.IN)
tof = RMTTToF(i2c)

# 修改主机Wifi,避免干扰
protocol.sendTelloCtrlMsg("wifi " + str("Victoria") + " " + str("Victoria2013"))

# 滚动显示反馈信息，调试用
def ShowInfo(Info):
    matrix.start()
    matrix.moveable_char("l", 2.5, Info, "r")
