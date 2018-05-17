#!python2
import thread
import time
import socket
import sys
import math

routingTable = {}
inNI = {} # In region node info
outNI = {} # Out region node info
radius = 5
currNode = 'A' # Current Node
currX = 0
currY = 0



def send_routing(HOST, PORT):
	
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
	addr = (HOST, PORT)

	while True:
			
		s.sendto(data, addr)

		time.sleep(0.1)
		
	s.close()  

def storeReceiveMsg(recvData):
	# Global Parameters
	# 
	data = recvData
	blockNum = len(data.split(';'))
	if data.split(';')[0] == 'Hello':
		seqNum = int(data.split(';')[1])

		sourceNodeStr = data.split(';')[2]
		node = data.split(';')[2].split(',')[0]
		nodeCoord = data.split(';')[2].split(',')[1]

		if blockNum > 3:
			inNeighborStr = data.split(';')[3]
			nodeInfo = nodeCoord + ';' + inNeighborStr
			state = addToInNI(node, seqNum, nodeInfo)
			if state == -1:
				return

			if blockNum > 4:
				outNeighborStr = data.split(';')[4]
				outPath = outNeighborStr.split(',')[0]
				outCost = outNeighborStr.split(',')[1]
				addToOutNI(outPath, outCost)


			


'''
			neighborNum = length(inNeighborStr.split('/')) - 1

			for i in range (0, neighborNum):
				nodeName = data.split('/')[i].split(',', 1)[0]
				posNeighbor = storeT.get(nodeName)
				# if posNeighbor == None:
				storeT[nodeName] = data.split('/')[i].split(',', 1)[1]
				# else:
'''
			
def findNodeInfo(node, num): # 0:Coord, 1:cost, 2:Path
	nodeInfo = rT.get(node)
	if nodeInfo != none:
		infoStr = rT[nodeInfo].split(';')
		return infoStr[num]

def addToInNI(node, seq, info):
	global inNI
	coord = info.split(';')[0]
	x = int(coord.split(' ')[0])
	y = int(coord.split(' ')[1])
	dist = math.sqrt((x - currX)^2 + (y - currY)^2)
	if dist <= radius:
		if inNI.get(node, 'None') != 'None':
			currSeq = int(inNI[node].split(';')[0])
			if seq > currSeq:
				if inNI.get('index', 'None') != 'None':
					inNI['index'] = inNI['index'] + ';' + node
				else:
					inNI['index'] = node
				inNI[node] = str(seq) + ';' + info
			else:
				return -1
		else:
			if inNI.get('index', 'None') != 'None':
					inNI['index'] = inNI['index'] + ';' + node
			else:
				inNI['index'] = node 
			inNI[node] = str(seq) + ';' + info
		return 0
	else:
		return -1


	
def addToOutNI(path, cost):
	global outNI
	if outNI.get('index', 'None') != 'None':
		outNI['index'] = outNI['index'] + ';' + path
	else:
		outNI['index'] = path
	outNI[path] = cost


def updateRoutingTable():
	global inNI
	length = len(inNI['index'].split(';'))
	if length > 0:
		node = inNI['index'].split(';')[0]

		if inNI.get(node, 'None') != 'None':
			dealInNIMsg(node)
			inNI.pop(node)
		if length == 1:
			inNI['index'] = ''
		else:
			inNI['index'] = inNI['index'].split(';',1)[1]



	return

def dealInNIMsg(node):

	return
'''
def updateNodeInfo(node, num):
	nodeInfo = rT.get(node)
	if 
'''

'''test'''
data = "Hello;2;B,3 0;C,1 0,5,C/D,5 5,10,D;AB,10"
storeReceiveMsg(data)
print inNI
print outNI

data = "Hello;1;D,3 0;C,1 0,5,C/E,5 5,10,E"
storeReceiveMsg(data)
print inNI
print outNI

data = "Hello;3;B,3 0;C,1 0,5,C/D,5 5,10,D;AB,20"
storeReceiveMsg(data)
print inNI
print outNI

updateRoutingTable()
print "1"
print inNI
updateRoutingTable()
print "2"
print inNI
updateRoutingTable()
print "3"
print inNI

'''MAIN'''
'''
HOST = ''
PORT = 8888

try:
	thread.start_new_thread( sendRouting, (HOST, PORT, ) )
	
except:
	print "Error: unable to start thread"

while 1:
	pass
'''