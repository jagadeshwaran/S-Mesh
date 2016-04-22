
# Use Synapse Evaluation Board definitions
from synapse.evalBase import *

redLEDPin = GPIO_6 

@setHook(HOOK_STARTUP)
def startupEvent():
    global FirstCounter
    FirstCounter = 0
    initProtoHw() # intialize the proto board    
    setPinDir(redLEDPin,True)   
    # Set each pin to a low value
    writePin(redLEDPin, False) 

# Disable UART, Increase Radio rate to 2Mbps by using setRadrate() inbuilt function
@setHook(HOOK_1MS)
def timer1msEvent():
    
    global FirstCounter
    global secondCounter
    
    FirstCounter = FirstCounter+1
    
    if(FirstCounter == 5):
        mcastRpc(1,2,"test",1,2,3,4)
        FirstCounter=0
        
    if secondCounter == 1:
        writePin(redLEDPin, True)
        secondCounter = 0
    else:
        writePin(redLEDPin, False)
        secondCounter=1
        


