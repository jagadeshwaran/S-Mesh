
from snapconnect import snap
global comm
comm = snap.Snap(funcs=rpcFuncs)
# ist of Datas
SensorData = [ [1,2],["S1Val"],["S2Val"],["S3Val"],["S4Val"],["S5Val"] ]

#------------------------------------------------------------#
# node    - Identity of the node, can be said as an address
# sensor  - Type of sensor
# data    - sensor data  
#-----------------------------------------------------------#
# datas from different sensors has not been taken care - which has to be fixed #
def SensorValues(nodeId, sensor, data ):
	SensorData[nodeId].append(data)

#--------------------------------------------------------#
# Need for fn: when all the nodes have to work with same configuration
#--------------------------------------------------------#
def PushConfigurationToAllNodes(nodeId, sensorCfg, S1T, S2T, S3T, S4T, S5T, S6T):
	comm.mcast_rpc( 1, 2, "PushConfigurationToAllNodes", nodeId, sensorCfg, S1T, S2T, S3T, S4T, S5T, S6T) #mcast the configuration data

#--------------------------------------------------------#
# Need for fn : when each node have to work with different configuration
# node address - address of the node for which configuration has to be pushed
# nodeId       - X
# sensorCfg    - I binary multiples Transmitted say 1
						# 000001 - Enables sensor 1
						# 000010 - Enables sensor 2
						# 000100 - Enables sensor 3
						# 001000 - Enables sensor 4
						# 010000 - Enables sensor 5
						# 100000 - Enables sensor 6
						# 111111 - Enables all the 6 sensors
#S1T, S2T, S3T, S4T, S5T, S6T are sensors reporting timings						
#--------------------------------------------------------#
def PushConfigurationToSingleNode(nodeAddress, nodeId, sensorCfg, S1T, S2T, S3T, S4T, S5T, S6T):
	comm.rpc("PushConfigurationToSingleNode", nodeId, sensorCfg, S1T, S2T, S3T, S4T, S5T, S6T)
	
def server_auth(realm, username):
	"""
	An example server authentication function
	Returns the password for the specified username in the realm
	realm : This server's realm
	username : The username specified by the remote server
	"""
if username == "public":
	return "public"
if __name__ == '__main__':
	import logging
	logging.basicConfig(level=logging.DEBUG, format='%(asctime)s:%(msecs)03d %(levelname)-8s %(name)-8s %(message)s', datefmt='%H:%M:%S')
	funcdir = { # You CHOOSE what you want to provide RPC access to...
	'SensorValues' : SensorValues,
    }
	# Make us accessible over TCP/IP
	com.accept_tcp(server_auth)
	# Make us accessible over our internal SNAP Engine
	com.open_serial(1, '/dev/ttyS1')
	# Configure some example settings
	# No encryption
	com.save_nv_param(snap.NV_AES128_ENABLE_ID, False)
	# Lock down our routes (we are a stationary device)
	com.save_nv_param(snap.NV_MESH_ROUTE_AGE_MAX_TIMEOUT_ID, 0)
	# Don't allow others to change our NV Parameters
	com.save_nv_param(snap.NV_LOCKDOWN_FLAGS_ID, 0x2)

# Run SNAP Connect until shutdown	
while True:
	com.poll()
	com.stop_accepting_tcp()
