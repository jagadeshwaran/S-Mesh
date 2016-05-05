#Import the c stuff
import_c("ADC_C.c")
from synapse.hexSupportExt2 import *

# Use Synapse Evaluation Board definitions
from synapse.evalBase import *

redLEDPin = GPIO_6 

FirstCounter = 0
Millisecondscounter = 0
SecondsCounter = 0
MinutesCounter = 0
HoursCounter   = 0
days           = 0


#startup hook
@setHook(HOOK_STARTUP)
def startupEvent():
    global secondCounter
    secondCounter = 0
    #initProtoHw() # intialize the proto board    
    setPinDir(redLEDPin,True)   
    writePin(redLEDPin, False) # Set the pin to a low value 

def GetLocalAddr():
    myAddr = localAddr()
    addrAscii = convBinToStr(myAddr)
    #print "LocalAddr = ", addrAscii # Tell the MCU
    #mcastRpc(1,4, "LocalAddr ",addrAscii) #DEBUG ONLY
    return addrAscii
#------------------------------------------------------------
# TIMER REFERNCE
#------------------------------------------------------------
@setHook(HOOK_1MS)
def TimerRef():
    global Millisecondscounter, SecondsCounter, MinutesCounter, HoursCounter, days
    Millisecondscounter +=1
    if Millisecondscounter == 1000:
        Millisecondscounter = 0
        SecondsCounter +=1
    if SecondsCounter == 60:
        MinutesCounter+=1
        SecondsCounter=0
    if MinutesCounter == 60:
        MinutesCounter= 0
        HoursCounter +=1
    if HoursCounter == 24:
        HoursCounter=0
        days+=1
    if days == 7300: # its roughly 20 years
        days =0
    print "MinutesCounter:", MinutesCounter 
     
@setHook(HOOK_10MS)
def timer10msEvent():
    
    global FirstCounter
    FirstCounter = FirstCounter + 1
    add = GetLocalAddr() 
    if FirstCounter == 100:
        V = take_averaged_sample(2) # ADC sampled and averaged values
        mcastRpc(1,4,"SampledData",add,V)
        FirstCounter = 0
    
@c_function(api=["none"])
def startup():
    """ Clears all the buffers  """
    pass     
        
@c_function(api=["int", "int"])
def take_averaged_sample(channel):
    """ Takes samples of the specified channel at a time and stores it"""
    pass

@c_function(api=["none", "int"])
def take_averaged_sample_all_channels(samples):
    """ It takes the samples of all 7 different ADC channels at a single call"""
    pass

#-------------------------------------------------------------
# say channel 0 and 120, you will get the return values as the 
# zeroth channel ADCs last reading of 120th moment.
# Its periodicity is based on the peridiocity of take_averaged_sample()
#------------------------------------------------------------

@c_function(api=["int","int", "int"])
def GetADCSanmpledValues(channel,sampleNo):
    """ The last 130 values of 8 channels are stored sequentially, you can access
    any of it by just giving the channel no and Samplepoint which should be less than 130 """
    pass

@c_function(api=["none", "str", "int"])
def ReadADCdatachunks(s, count):
    pass

def ReadADCdatachunks1(data):
    s = ''
    i = 0
    # Construct a string as large as SNAPpy can handle to pass in.
    while i < 255:
        s += ' '
        i+= 1
    ReadADCdatachunks(s, data)
    return "ADC Chunk datas are: " + s
    
