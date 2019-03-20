import socket
import struct
import math
import time
from enum import Enum

# ======================================================================
#      DEFINE THE DMM CLASS INSTANCE HERE
# ======================================================================
class DMM6500:
    def __init__(self):
        self.echoCmd = 1
        self.mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    # ======================================================================
    #      DEFINE INSTRUMENT CONNECTION AND COMMUNICATIONS FUNCTIONS HERE
    # ======================================================================
    def Connect(self, myAddress, myPort, timeOut, doReset, doIdQuery):
        self.mySocket.connect((myAddress, myPort)) # input to connect must be a tuple
        self.mySocket.settimeout(timeOut)
        if doReset == 1:
            self.Reset()
            self.SendCmd("waitcomplete()")
        if doIdQuery == 1:
            tmpId = self.IDQuery()

        if doIdQuery == 1:
            return tmpId
        else:
            return

    def Disconnect(self):
        self.mySocket.close()
        return

    def SendCmd(self, cmd):
        if self.echoCmd == 1:
            print(cmd)
        cmd = "{0}\n".format(cmd)
        self.mySocket.send(cmd.encode())
        return

    def QueryCmd(self, cmd, rcvSize):
        self.SendCmd(cmd)
        time.sleep(0.1)
        return self.mySocket.recv(rcvSize).decode()

    # ======================================================================
    #      DEFINE BASIC FUNCTIONS HERE
    # ======================================================================        
    def Reset(self):
        sndBuffer = "reset()"
        self.SendCmd(sndBuffer)
        
    def IDQuery(self):
        sndBuffer = "*IDN?"
        return self.QueryCmd(sndBuffer, 64)

    def LoadScriptFile(self, filePathAndName):
        # This function opens the functions.lua file in the same directory as
        # the Python script and trasfers its contents to the DMM7510's internal
        # memory. All the functions defined in the file are callable by the
        # controlling program. 
        func_file = open(filePathAndName, "r")
        contents = func_file.read()
        func_file.close()

        cmd = "if loadfuncs ~= nil then script.delete('loadfuncs') end"
        self.SendCmd(cmd)

        cmd = "loadscript loadfuncs\n{0}\nendscript".format(contents)
        self.SendCmd(cmd)
        cmd = "loadfuncs()"
        print(self.QueryCmd(cmd, 32))
        return

    # ======================================================================
    #      DEFINE MEASUREMENT FUNCTIONS HERE
    # ======================================================================
    def SetMeasure_Function(self, myFunc):
        if myFunc == self.MeasFunc.DCV:
            funcStr = "dmm.FUNC_DC_VOLTAGE"
        elif myFunc == self.MeasFunc.DCI:
            funcStr = "dmm.FUNC_DC_CURRENT"
        sndBuffer = "dmm.measure.func =  {}".format(funcStr)
        self.SendCmd(sndBuffer)
        return

    def SetMeasure_Range(self, rng):
        sndBuffer = "dmm.measure.range = {}".format(rng)
        self.SendCmd(sndBuffer)
        return

    def SetMeasure_NPLC(self, nplc):
        sndBuffer = "dmm.measure.nplc = {}".format(nplc)
        self.SendCmd(sndBuffer)
        return

    def SetMeasure_InputImpedance(self, myZ):
        if myZ == self.InputZ.Z_AUTO:
            funcStr = "dmm.IMPEDANCE_AUTO"
        elif myZ == self.InputZ.Z_10M:
            funcStr = "dmm.IMPEDANCE_10M"
            
        sndBuffer = "dmm.measure.inputimpedance = {}".format(funcStr)
        self.SendCmd(sndBuffer)
        return

    def SetMeasure_AutoZero(self, myState):
        if myState == self.DmmState.OFF:
            funcStr = "dmm.OFF"
        elif myState == self.DmmState.ON:
            funcStr = "dmm.ON"
            
        sndBuffer = "dmm.measure.autozero.enable = {}".format(funcStr)
        self.SendCmd(sndBuffer)
        return

    def SetMeasure_FilterType(self, myFilter):
        if myFilter == self.FilterType.REP:
            funcStr = "dmm.FILTER_REPEAT_AVG"
        elif myFilter == self.FilterType.MOV:
            funcStr = "dmm.FILTER_MOVING_AVG"
            
        sndBuffer = "dmm.measure.filter.type = {}".format(funcStr)
        self.SendCmd(sndBuffer)
        return

    def SetMeasure_FilterCount(self, count):
        sndBuffer = "dmm.measure.filter.count = {}".format(count)
        self.SendCmd(sndBuffer)
        return

    def SetMeasure_FilterState(self, myState):
        if myState == self.DmmState.OFF:
            funcStr = "dmm.OFF"
        elif myState == self.DmmState.ON:
            funcStr = "dmm.ON"
            
        sndBuffer = "dmm.measure.filter.enable = {}".format(funcStr)
        self.SendCmd(sndBuffer)
        return
    
    def Measure(self, count):
        sndBuffer = "print(dmm.measure.read())"
        return self.QueryCmd(sndBuffer, 32)
    
    class MeasFunc(Enum):
        DCV = 0
        DCI = 1

    class InputZ(Enum):
        Z_AUTO = 0
        Z_10M = 1

    class DmmState(Enum):
        OFF = 0
        ON = 1

    class FilterType(Enum):
        REP = 0
        MOV = 1
    
