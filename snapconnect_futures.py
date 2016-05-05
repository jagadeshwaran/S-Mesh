import tornado
from snapconnect_futures import SnapConnectFutures
from snapconnect import snap
from tornado.gen import coroutine
import apy
import time

global FirstTime
FirstTime = True

def Ackknowledgement(x):
	print "Ackknowledgementreceived",x
	
def SampledData(x,y):
	print ("The sampled data of address %s is %s:" %(x,y))
	
# Required IO loop setup:
scheduler = apy.ioloop_scheduler.IOLoopScheduler.instance() # Create an apy IOLoopScheduler
comm = snap.Snap(scheduler=scheduler, funcs={'Ackknowledgement':Ackknowledgement, 'SampledData':SampledData }) # Create a SNAP Connect Instance that uses the apy scheduler
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
def McastTheSamplingRate():
	"""Each yielded callback_rpc() function here will not return until
	it gets a response back from the node."""
	#print "Probing the module..."
	#hw_type = yield scf.callback_rpc("aabbcc", "get_hardware_type",(hardware_id,))
	#print "Hardware type: ", hw_type
	#num_devices = yield scf.callback_rpc("aabbcc", "get_connected_devices", (arg1, arg2))
	#print "Connected devices: ", num_devices
	#measurement = yield scf.callback_rpc("aabbcc", "get_measurement")
	#print "Current measurement: ", measurement
	
	mcast_rpc_success = yield scf.mcast_rpc("SamplingRate", "S1", "S2", "S3", "S4","S5","S6","S7")# => True
	print "Is Mcast_rpc Sent: ", mcast_rpc_success
	
@coroutine
def ReportSampledValuesatThePeriod(x):
	""" X is given in Milliscends"""
	rpc_success = yield scf.rpc("5EC840", "ReportingPeriod", "x")
	print "Is Unicastrpc Sent: ", rpc_success
	
@coroutine
def main():
	global FirstTime
	if FirstTime == True:
		yield setup_serial() # Will wait here until serial connection completes
		yield McastTheSamplingRate() # Will wait here until all moduleinformation is returned
		yield ReportSampledValuesatThePeriod(16)
		FirstTime = False
		print "Done!"
	
while(True):	
	tornado.ioloop.IOLoop.current().run_sync(main)
	time.sleep(0.001)
