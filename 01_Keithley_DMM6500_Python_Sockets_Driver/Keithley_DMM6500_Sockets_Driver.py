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

    def SetFunction_Temperature(self, *args):
        # This function can be used to set up to three different measurement
        # function attributes, but they are expected to be in a certain
        # order....
        #   For simple front/rear terminal measurements:
        #       1. Transducer (TC/RTD/Thermistor)
        #       2. Transducer type
        #   For channel scan measurements:
        #       1. Channel string
        #       2. Transducer
        #       3. Transducer type
        if (type(args[0]) != str):
            print("dmm.measure.func = dmm.FUNC_TEMPERATURE")
        else:
            setStr = "channel.setdmm(\"{}\", ".format(args[0])
            print("{}dmm.ATTR_MEAS_FUNCTION, dmm.FUNC_TEMPERATURE)".format(setStr))
            if(len(args) > 1):
                if(args[1] == self.Transducer.TC):
                   xStr = "dmm.TRANS_THERMOCOUPLE"
                   xStr2 = "dmm.ATTR_MEAS_THERMOCOUPLE"
                elif(args[1] == self.Transducer.RTD4):
                   xStr = "dmm.TRANS_FOUR_RTD"
                   xStr2 = "dmm.ATTR_MEAS_FOUR_RTD"
                elif(args[1] == self.Transducer.RTD3):
                   xStr = "dmm.TRANS_THREE_RTD"
                   xStr2 = "dmm.ATTR_MEAS_THREE_RTD"
                elif(args[1] == self.Transducer.THERM):
                   xStr = "dmm.TRANS_THERMISTOR"
                   xStr2 = "dmm.ATTR_MEAS_THERMISTOR"
                sndBuffer = "{}dmm.ATTR_MEAS_TRANSDUCER, {})".format(setStr, xStr)
                self.SendCmd(sndBuffer)
            if(len(args) > 2):
                if(args[1] == self.Transducer.TC):
                    if(args[2] == self.TCType.K):
                       xType = "dmm.THERMOCOUPLE_K"
                    elif(args[2] == self.TCType.J):
                       xType = "dmm.THERMOCOUPLE_J"
                    elif(args[2] == self.TCType.N):
                       xType = "dmm.THERMOCOUPLE_N" 
                    #print("{}dmm.ATTR_MEAS_THERMOCOUPLE, {})".format(setStr, xType))
                    sndBuffer = "{}dmm.ATTR_MEAS_THERMOCOUPLE, {})".format(setStr, xType)
                    self.SendCmd(sndBuffer)
                elif((args[1] == self.Transducer.RTD4) or (args[1] == self.Transducer.RTD3)):
                    if(args[2] == self.RTDType.PT100):
                       rtdType = "dmm.RTD_PT100"
                    elif(args[2] == self.RTDType.PT385):
                       rtdType = "dmm.RTD_PT385"
                    elif(args[2] == self.RTDType.PT3916):
                       rtdType = "dmm.RTD_PT3916"
                    elif(args[2] == self.RTDType.D100):
                       rtdType = "dmm.RTD_F100"
                    elif(args[2] == self.RTDType.F100):
                       rtdType = "dmm.RTD_D100"
                    elif(args[2] == self.RTDType.USER):
                       rtdType = "dmm.RTD_USER"
                    #print("{}{}, {})".format(setStr, xStr2, rtdType))
                    sndBuffer = "{}{}, {})".format(setStr, xStr2, rtdType)
                    self.SendCmd(sndBuffer)
                if(args[1] == self.Transducer.THERM):
                    if(args[2] == self.ThermType.TH2252):
                       thrmType = "dmm.THERM_2252"
                    elif(args[2] == self.ThermType.PT385):
                       thrmType = "dmm.THERM_5000"
                    elif(args[2] == self.ThermType.PT3916):
                       thrmType = "dmm.THERM_10000"
                    #print("{}{}, {})".format(setStr, xStr2, thrmType))
                    sndBuffer = "{}{}, {})".format(setStr, xStr2, thrmType)
                    self.SendCmd(sndBuffer)
        return
    
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

    class Transducer(Enum):
        TC = 0
        RTD4 = 1
        RTD3 = 2
        THERM = 3

    class TCType(Enum):
        K = 0
        J = 1
        N = 2
        
    class RTDType(Enum):
        PT100 = 0
        PT385 = 1
        PT3916 = 2
        D100 = 3
        F100 = 4
        USER = 5

    class ThermType(Enum):
        TH2252 = 0
        TH5K = 1
        TH10K = 2
