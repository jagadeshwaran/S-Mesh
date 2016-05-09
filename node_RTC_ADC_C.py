#Import the c stuff
import_c("ADC_C.c")
from synapse.hexSupportExt2 import *
from timers import *
# Use Synapse Evaluation Board definitions
from synapse.evalBase import *

redLEDPin = GPIO_6 

FirstCounter = 0
Millisecondscounter = 0
SecondsCounter = 0
MinutesCounter = 0
HoursCounter   = 0
days           = 0

# Define constant
MONTH = 0
DAY = 1
YEAR = 2
HOUR = 4
MINUTE = 5
SECOND = 6
DAYS_IN_MONTH = (0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
V = 0

h=0
m=0
se=0

# Global variables
START_TIME = "\x01\x01\x07\xD0\x18\x00\x00"
time_str = START_TIME
alarm_time = "\x00\x00\x00\x00\x00\x00\x00"
rtc_alarm = 0


#startup hook
@setHook(HOOK_STARTUP)
def startupEvent():
    global secondCounter
    secondCounter = 0
    timer_init(TMR5, WGM_FASTPWM16_TOP_ICR, CLK_FOSC_DIV1024, 0x3d09)
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
    #print "MinutesCounter:", MinutesCounter 
	
@setHook(HOOK_100MS)
def timer_100ms():
  clock_timer_100ms()

def clock_timer_100ms():
    """This function needs to be hooked into the 100ms hook"""
    global lastTime
    cTime = get_tmr_count(TMR5) >> 8
    if cTime < lastTime:
        clock_tick()
    lastTime = cTime

def McastRpc():
    global V
    add = GetLocalAddr()
    V +=1
    A = take_averaged_sample(2) # ADC sampled and averaged values
    mcastRpc(1,4,"SampledData",add,V, A)
    rtc_clear_alarm()
    rtc_set_time(1, 1, 2016, 24, 0, 0)
    rtc_set_alarm(1, 1, 2016, h, m, se)

def rtc_set_alarm(month, day, year, hour, minute, second):
    """Set the alarm time and date 0-24 hour"""
    global alarm_time
    alarm_time = chr(month) + chr(day) + chr(year >> 8) + chr(year & 0xFF) + chr(hour) + chr(minute) + chr(second)


def rtc_clear_alarm():
    global rtc_alarm
    rtc_alarm = 0


def check_alarms():
    """Check the time against the alarm time and call the event if match"""
    global rtc_alarm
    if time_str == alarm_time:
        rtc_alarm = 1
        McastRpc()
    return rtc_alarm


def rtc_set_time(month, day, year, hour, minute, second):
    """Set the current time and date 0-24 hour"""
    global time_str
    time_str = chr(month) + chr(day) + chr(year >> 8) + chr(year & 0xFF) + chr(hour) + chr(minute) + chr(second)

    # clear timers
    set_tmr_count(TMR5, 0)


def read_alarm():
    """Return the alarm time and date in printable ASCII"""
    return parse_time(alarm_time)


def read_time():
    """Return the current time and date in printable ASCII"""
    return parse_time(time_str)


def get_hours():
    """Return the current hours in printable ASCII"""
    time = time_str
    myStr = ''
    hour = ord(time[HOUR])
    if hour < 10:
        myStr += '0' + str(hour)
    else:
        myStr += str(hour)
    myStr += ':'

    minute = ord(time[MINUTE])
    if minute < 10:
        myStr += '0' + str(minute)
    else:
        myStr += str(minute)
    myStr += ':'

    second = ord(time[SECOND])
    if second < 10:
        myStr += '0' + str(second)
    else:
        myStr += str(second)
    return myStr


def get_date():
    """Convert the date string into printable ASCII"""
    time = time_str
    myStr = str(ord(time[MONTH])) + '/'
    myStr += str(ord(time[DAY])) + '/'
    year = ord(time[YEAR]) << 8 | ord(time[YEAR+1])
    myStr += str(year)
    return myStr


def parse_time(time):
    """Convert the time string into printable ASCII"""
    myStr = str(ord(time[MONTH])) + '/'
    myStr += str(ord(time[DAY])) + '/'
    year = ord(time[YEAR]) << 8 | ord(time[YEAR+1])
    myStr += str(year) + ' '

    hour = ord(time[HOUR])
    if hour < 10:
        myStr += '0' + str(hour)
    else:
        myStr += str(hour)
    myStr += ':'

    minute = ord(time[MINUTE])
    if minute < 10:
        myStr += '0' + str(minute)
    else:
        myStr += str(minute)
    myStr += ':'

    second = ord(time[SECOND])
    if second < 10:
        myStr += '0' + str(second)
    else:
        myStr += str(second)
    return myStr


def clock_tick():
    """This function is automatically called to increment the clock string"""
    global time_str

    # See if we have any impending alarms
    check_alarms()

    second = ord(time_str[SECOND])
    if second == 59:
        time_str = time_str[0:SECOND] + "\x00"
        minute = ord(time_str[MINUTE])
        if minute == 59:
            time_str = time_str[0:MINUTE] + "\x00" + time_str[SECOND]
            hour = ord(time_str[HOUR])
            if hour == 23:
                time_str = time_str[0:HOUR] + chr(24) + time_str[MINUTE:]
                month = ord(time_str[MONTH])
                day = ord(time_str[DAY])
                year = ord(time_str[YEAR]) << 8 | ord(time_str[YEAR+1])
                if day == get_days_in_month(month, year):
                    if month == 12:
                        year += 1
                        time_str = "\x01\x01" + chr(year >> 8) + chr(year & 0xFF) + time_str[HOUR:]
                    else:
                        month += 1
                        time_str = chr(month) + time_str[DAY:]
                else:
                    day += 1
                    time_str = time_str[0:DAY] + chr(day) + time_str[YEAR:]
            elif hour == 24:
                time_str = time_str[0:HOUR] + "\01" + time_str[MINUTE:]
            else:
                hour += 1
                time_str = time_str[0:HOUR] + chr(hour) + time_str[MINUTE:]
        else:
            minute += 1
            time_str = time_str[0:MINUTE] + chr(minute) + time_str[SECOND]
    else:
        second += 1
        time_str = time_str[0:SECOND] + chr(second)


def is_leap_year(year):
    """Determine whether the specified year is a leap year"""
    if year % 4 == 0:
        if year % 100 == 0:
            if year % 400 == 0:
                return 1
            else:
                return 0
        else:
            return 1
    else:
        return 0


def get_days_in_month(month, year):
    """Determine days in the month/year combination"""
    if month == 2:
        return DAYS_IN_MONTH[month] + is_leap_year(year)
    else:
        return DAYS_IN_MONTH[month]
		
		
def HextoBin(str):
    pktLen = len(str)
    i = 0
    binStr = ''
    while i < pktLen:
        val = ord(str[i])
        if 64 < val < 71:
            byte = (val - 55)<<4
        elif 47 < val < 58:
            byte = (val-48)<<4
        elif 96 < val < 103:
            byte = (val - 87)<<4
 
        val = ord(str[i+1])
        if 64 < val < 71:
            byte+= (val - 55)
        elif 47 < val < 58:
            byte+= (val-48)
        elif 96 < val < 103:
            byte+= (val - 87)
        binStr+= chr(byte)
        i+=2
    return binStr
     
@setHook(HOOK_10MS)
def timer10msEvent():
    
    global FirstCounter
    FirstCounter = FirstCounter + 1
    add = GetLocalAddr() 
    #rx(False)
    #if FirstCounter == 1000:
        #rx(True) # -- Not neccesary since the  RpC call itself will enable it and it is faster too
        #V = take_averaged_sample(2) # ADC sampled and averaged values
        #mcastRpc(1,4,"SampledData",add,V)
        #FirstCounter = 0
    
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

def ReportingPeriod(H,M,S):
    global h,m,se
    h = H
    m = M
    se = S
    rtc_clear_alarm()
    rtc_set_time(1, 1, 2016, 24, 0, 0)
    rtc_set_alarm(1, 1, 2016, h, m, se)
    return M

def ImGateway(x):
	addr0 = GetLocalAddr()
	#y = str(x)
	# Unicast would be good to do here, In that case Im gateway should carry the E20 Address
	# Use mcast --- unicast will be much useful when there is a single hop for a 6 or more node surrounded and after that 1 node
	mcastRpc(1,4,"MeshNodes",addr0)
	

