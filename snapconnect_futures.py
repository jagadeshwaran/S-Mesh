import tornado
from snapconnect_futures import SnapConnectFutures
from snapconnect import snap
from tornado.gen import coroutine
import apy
import time
import datetime
import sqlite3 # for database

#global FirstTime
FirstTime = True
NoOfNodesCounter = 0

conn = sqlite3.connect('SensorDatas.db') # ***** should happen only once
c = conn.cursor() # create a cursor

NodeAddress = [ ]
def MeshNodes(x):
	global NoOfNodesCounter
	NoOfNodesCounter +=1
	NodeAddress.append(x)
	print "The No of nodes added to the List are:", NoOfNodesCounter
#------------------------------------------------------------#
# Sesensor timing config
#-----------------------------------------------------------#

#------------------------------------------------------------#
# SensorDatas: database holds the all sensor datas 
#-----------------------------------------------------------#
def sqliteDatabase():
	# ****time stamp of the datas collected with dates has to be added 
	# ******** It should be able to check, when there is one already, it should skip creating one ---- It has to be added
	c.execute('''create table SensorDatas(nodeAddress integer, sensor1 integer, sensor2 integer, sensor3 integer, sensor4 integer, sensor5 integer, sensor6 integer)''')
	
def AdddataTosqliteDatabase(nodeId, S1T, S2T, S3T, S4T, S5T, S6T):
	# Datas can be on the same table it need not be organized, since data can be read based on time and recents with search 
	c.execute('insert into SensorDatas values(?, ?, ?, ?, ?, ?, ?)',(nodeId, S1T, S2T, S3T, S4T, S5T, S6T))
	# Save (commit) the changes
	conn.commit()
	# We can also close the connection if we are done with it.
	# Just be sure 

def Ackknowledgement(x):
	print "Ackknowledgementreceived",x
	
def SampledData(x,y,v):
	now = datetime.datetime.now()
	print "Current date and time using str method of datetime object:"
	print str(now)
	print ("The sampled ADC data of address %s is %s No %s:" %(x,v,y))
	AdddataTosqliteDatabase(x, v, y, 9, 9, 9, 9)
	
# Required IO loop setup:
scheduler = apy.ioloop_scheduler.IOLoopScheduler.instance() # Create an apy IOLoopScheduler
comm = snap.Snap(scheduler=scheduler, funcs={'Ackknowledgement':Ackknowledgement, 'SampledData':SampledData, 'MeshNodes':MeshNodes }) # Create a SNAP Connect Instance that uses the apy scheduler
tornado.ioloop.PeriodicCallback(comm.poll_internals, 5).start() #Setup tornado's IO loop by scheduling calls to SNAP Connect's poll_internals method
# Create an SCF instanallbacks automatically:
scf = SnapConnectFutures(comm)

@coroutine
def setup_serial():
	"""This function won't return until the serial connection is
	established."""
	print "Connecting to serial..."
	com_port =  '/dev/snap1' # Since Windows counts from COM1, 0 is COM1, 1 is COM2, etc. On Linux/OS X, use something like "/dev/ttyS1"
	bridge_addr = yield scf.open_serial(snap.SERIAL_TYPE_RS232, com_port)
	print "Connected to: ", bridge_addr
	
@coroutine
def McastTheAddress():
	"""Each yielded callback_rpc() function here will not return until
	it gets a response back from the node."""
	#print "Probing the module..."
	#hw_type = yield scf.callback_rpc("aabbcc", "get_hardware_type",(hardware_id,))
	#print "Hardware type: ", hw_type
	#num_devices = yield scf.callback_rpc("aabbcc", "get_connected_devices", (arg1, arg2))
	#print "Connected devices: ", num_devices
	#measurement = yield scf.callback_rpc("aabbcc", "get_measurement")
	#print "Current measurement: ", measurement
	addr = comm.load_nv_param(2) # retsurns 16 characters, that is 8 bytes each char takes 4 bits
	addr1 = HexAddyToStr( addr )
	mcast_rpc_success = yield scf.mcast_rpc("ImGateway", (addr1) )# => True
	print "Is Mcast_rpc Sent: ", mcast_rpc_success
	
@coroutine
def ReportSampledValuesatThePeriod(H,M,S):
	""" X is given in Milliscends"""
	#rpc_success = yield scf.rpc("5ec840", "ReportingPeriod", x) # RPC
	callback_rpc_success = yield scf.callback_rpc("5ec840", "ReportingPeriod",(H,M,S)) #call back RPC , return TRUE from node and check 	
	#rpc_result = yield scf.callback_rpc("aabbcc", "test_func", (1, 2, 3))
# => ("value",)

	print "Is callback Unicastrpc Sent: ", callback_rpc_success
	
def HexAddyToStr( beaconAddrHexStr ):
    hexStr = "0123456789ABCDEF"
    beaconAddrPrintStr = ''
    
    # Convert something of the form \x00\x86\xF1 to '00.86.F1' in ASCII
    count = len(beaconAddrHexStr)
    index = 0
    for index in range(5,8):
        byte = ord(beaconAddrHexStr[index])
        hexNibble1 = byte >> 4
        hexNibble2 = byte
        hexChar1 = hexStr[hexNibble1 & 0xF]
        hexChar2 = hexStr[hexNibble2 & 0xF]
        
        beaconAddrPrintStr = beaconAddrPrintStr + hexChar1 + hexChar2
        #index += 1
        #if index < count:
        #   beaconAddrPrintStr += '.' 
    print "count",count
    return beaconAddrPrintStr	
	
@coroutine
def main():
	global FirstTime
	if FirstTime == True:
		yield setup_serial() # Will wait here until serial connection completes
		yield McastTheAddress() # Will wait here until all moduleinformation is returned
		yield ReportSampledValuesatThePeriod(24,1,0)
		#LocallAddress = snap.NV_MAC_ADDR_ID
		#print "The address is:" , addr1
		#print "The Local address is: ", LocallAddress
		#print "The Local address is: %02X.%02X.%02X" % (ord(addr[-3]), ord(addr[-2]), ord(addr[-1]))
		FirstTime = False
		print "Done!"
	
while(True):	
	tornado.ioloop.IOLoop.current().run_sync(main)
	time.sleep(0.001)
