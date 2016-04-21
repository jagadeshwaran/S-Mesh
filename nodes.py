from synapse.switchboard import *
from synapse.evalBase import *

UARTtestPin = GPIO_17
UARTtestpingnd = GPIO_18
toggle = 0

yourPortalAddr = "\x00\x00\x01"
@setHook(HOOK_STARTUP) 
def startupEvent():     
    
    setPinDir(UARTtestPin,True) # configure the pin as output
    writePin(UARTtestPin, False) # Set the pin high to power the device
    setPinDir(UARTtestpingnd,True) # configure the pin as output
    writePin(UARTtestpingnd, False) # Set the pin high to power the device
    
    initUart(1, 9600)
    flowControl(1, False)
    stdinMode(1, False)     
    crossConnect(DS_UART1, DS_STDIO)
    '''uniConnect(DS_STDIO,DS_UART1) # From UART0 to STDIN
    uniConnect(DS_TRANSPARENT, DS_STDIO) #From STDOUT to Datamode/Portal 
    ucastSerial(yourPortalAddr) #<= Add your address here'''

@setHook(HOOK_STDIN)    
def stdinEvent(data):
    data = "def"
    print data
    global toggle
    if(toggle ==1):
        writePin(UARTtestPin, False) 
        toggle=0
    else:
        writePin(UARTtestPin, True) 
        toggle=1
        
@setHook(HOOK_1S)
def eventlogger():
    print " test: The working of intercepter"