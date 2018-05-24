#!python2
import thread
import threading
import time
import socket
import sys
import math
import struct
import fcntl
#import nextHop_test

def getip(ethname):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0X8915, struct.pack('256s', ethname[:15]))[20:24])


alpha = 1
beta = 0.005
gamma = 1

routingTable = {}
inNI = {} # In region node info
seqT = {} #Sequence number
ipTable = {}
radius = 5
currNode = 'A' # Current Node
currX = 0
currY = 0
currSeq = 0
currEnergy = 100
currIP = getip('eth0')
print currIP

send_state = threading.Lock()
storeNI_state = threading.Lock()
storeRT_state = threading.Lock()
pktRecv_state = threading.Lock()


def sendHello(PORT):
	
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
	s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

	while True:
		data = ''
		network = '<broadcast>'
		addr = (network, PORT)
		data = genHelloMsg()
		s.sendto(data, addr)
		storeNI_state.acquire()
		print 'send: ' + data
		storeNI_state.release()
		time.sleep(1)
		
	s.close()   
	
def recvHello(PORT):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
	s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	
	s.bind(('', PORT))
	
	while True:
		data, addr = s.recvfrom(100)
		storeNI_state.acquire()
		storeReceiveMsg(data)
		print routingTable
		storeNI_state.release()
		
		

def storeReceiveMsg(recvData):
	# Global Parameters
	# 
	data = recvData
	blockNum = len(data.split(';'))
	#print ("bnum%d"%blockNum)
	if data.split(';')[0] == 'Hello':
		seqNum = data.split(';')[1]

		sourceNodeStr = data.split(';')[2]
		node = data.split(';')[2].split(',')[0]
		
		if node == currNode:
			return
		print 'data   ' + data
		nodeCoord = data.split(';')[2].split(',')[1]
		nodeIP = data.split(';')[2].split(',')[2]
		if blockNum == 3:
			addToInNI(node, seqNum, nodeCoord, nodeIP)

		elif blockNum > 3:
			inNeighborStr = data.split(';')[3]
			nodeInfo = nodeCoord + ';' + inNeighborStr
			addToInNI(node, seqNum, nodeInfo, nodeIP)
			


			
def findNodeInfo(node, num): # 0:Coord, 1:cost, 2:Path
	nodeInfo = rT.get(node)
	if nodeInfo != none:
		infoStr = rT[nodeInfo].split(';')
		return infoStr[num]

def addSeqNum(node, seq):
	global seqT
	if seqT.get(node, 'None') != 'None':
		if int(seqT[node].split(' ')[0]) < seq:
			seqT[node] = str(seq) + ' ' + str(currSeq)
	else :
		seqT[node] = str(seq) + ' ' + str(currSeq)
	

def addToInNI(node, seqTime, info, nodeIP):
	global inNI
	seq = int(seqTime.split(',')[0])
	time = seqTime.split(',')[1]
	coord = info.split(';')[0]
	x = int(coord.split(' ')[0])
	y = int(coord.split(' ')[1])
	dist = math.sqrt((x - currX)**2 + (y - currY)**2)
	if dist <= radius:
		if inNI.get(node, 'None') != 'None':
			nodeSeq = int(seqT[node].split(' ')[0])
			if seq > nodeSeq:
				inNI[node] = time + ";" + info
				addSeqNum(node, seq)
				addIP(node, nodeIP)
			
		else:
			inNI[node] = time + ";" + info
			addSeqNum(node, seq)
			addIP(node, nodeIP)
		
def addIP(node, nodeIP):
	global ipTable
	ipTable[node] = nodeIP



def updateRoutingTable():
	global inNI
	
	while True:
		storeNI_state.acquire()
		
		tmp = []
		for key in inNI:
			tmp.append(key)
		
		for key2 in tmp:
		
			dealInNIMsg(key2)
			inNI.pop(key2)
		scanSeq()
		storeNI_state.release()
		time.sleep(1)
		


def dealInNIMsg(node):
	global routingTable
	nodeName = node
	nodeInfo = inNI[node]
	nodeCoord = inNI[node].split(';')[1]
	nodeTime = int(inNI[node].split(';')[0])
	nodeCost = calCost(nodeCoord, nodeTime)
	nodePath = nodeName
	updateNodeInfo(nodeName, nodeCoord, nodeCost, nodePath)
	#print (inNI[node])
	if len(inNI[node].split(';'))>2:
		nodeNum = len(inNI[node].split(';')[2].split('/'))
		#print (nodeNum)
		for i in range(0, nodeNum):
			currNodeInfo = inNI[node].split(';')[2].split('/')[i]
			currNodeName = currNodeInfo.split(',')[0]
			
			if currNodeName != currNode:
				currCoord = currNodeInfo.split(',')[1]
				currNodeX = int(currCoord.split(' ')[0])
				currNodeY = int(currCoord.split(' ')[1])
				dist = math.sqrt((currNodeX - currX)**2 + (currNodeY - currY)**2)
				
				#print dist
				if dist <= radius:
					nodeInRTInfo = routingTable.get(nodeName, 'None')
					if nodeInRTInfo!='None':
						currCost = int(currNodeInfo.split(',')[2]) + int(nodeInRTInfo.split(';')[1])
						currPath = nodeName + currNodeInfo.split(',')[3]
						updateNodeInfo(currNodeName, currCoord, currCost, currPath)
	#return


def calCost(coord, nodeTime):
	coordX = int(coord.split(' ')[0])
	coordY = int(coord.split(' ')[1])
	timehr = time.localtime(time.time()).tm_hour 
	timemin = time.localtime(time.time()).tm_min
	timesec = time.localtime(time.time()).tm_sec
	currTime = 3600*timehr + 60*timemin + timesec
	dTime = currTime - nodeTime
	cost = int(alpha * (2**(math.sqrt((coordX - currX)**2) + (coordY - currY)**2)) + beta * dTime)
	return cost


def updateNodeInfo(node, coord, cost, path):
	global routingTable
	isInRT = routingTable.get(node, 'None')
	if isInRT == 'None':
		routingTable[node] = coord + ';' + str(cost) + ';' + path
	else:
		routingCost = int(isInRT.split(';')[1])
		routingCoord = isInRT.split(';')[0]
		# print('cost:' + str(cost))
		# print('routingCost:' + path + str(routingCost))
		if routingCoord != coord:

			routingTable[node] = coord + ';' + str(cost) + ';' + path
		if routingCost > cost:
			routingTable[node] = coord + ';' + str(cost) + ';' + path

	return 

def genHelloMsg():
	global currSeq
	timehr = time.localtime(time.time()).tm_hour 
	timemin = time.localtime(time.time()).tm_min
	timesec = time.localtime(time.time()).tm_sec
	currTime = 3600*timehr + 60*timemin + timesec
	currSeq += 1
	data = "Hello;" + str(currSeq) +',' + str(currTime) + ';' + currNode + ',' + str(currX) + ' ' + str(currY) + ',' + currIP
	if len(routingTable)>0:
		data = data + ';'
	for key in routingTable:
		coord = routingTable[key].split(';')[0]
		cost = routingTable[key].split(';')[1]
		path = routingTable[key].split(';')[2]
		data = data + key + ',' + coord + ',' + cost + ',' + path + '/'
	data = data.rstrip('/')
	return data

def scanSeq():
	global routingTable
	global ipTable
	for key in seqT:
		nodes = []
		if (currSeq - int(seqT[key].split(' ')[1])) > 5:
			for node in routingTable:
				if routingTable[node].find(key) != -1:
					nodes.append(node)
			for element in nodes:
				if routingTable.get(element, 'None') != 'None':
					routingTable.pop(element)
					ipTable.pop(element)
			seqT[key] = str(0) + ' ' + str(currSeq)
			'''
			if routingTable.get(key, 'None') != 'None':
				routingTable.pop(key)
				ipTable.pop(key)
			'''
			
def Projection_NextHop(coord): # coord = x y

	coordX = float(coord.split(' ', 1)[0])
	coordY = float(coord.split(' ', 1)[1])
	vector1X = coordX - currX # vector_X from source to destination
	vector1Y = coordY - currY # vector_Y from source to destination
	product = -10000 # means negative infinity
	nexthop = ''
	if len(routingTable) > 0:
		for node in routingTable:
			location = routingTable[node].split(';')[0]
			locationX = float(location.split(' ')[0])
			locationY = float(location.split(' ')[1])
			vector2X = locationX - currX # vector_X from source to neighbor
			vector2Y = locationY - currY # vector_Y from source to neighbor
			newproduct = vector1X*vector2X + vector1Y*vector2Y
			if newproduct > product: # record the max_product
				product = newproduct
				nexthop = node
		return nexthop
	else:
		return 'None'

def nextH():
	while True:
		pktRecv_state.acquire()
		a = Projection_NextHop('20 10')
		print a
		pktRecv_state.release()
		time.sleep(2)

def changeVariable():
	global currX, currY
	while True:
		data = raw_input()
		if data.find('coord:') != -1:
			coord = data.split(':')[1]
			if coord.find(' ') != -1:
				x = coord.split(' ')[0]
				y = coord.split(' ')[1]
				if x.isdigit() and y.isdigit() :
					currX = int(x)
					currY = int(y)
				else:
					print 'Invalid Input'
			else:
				print 'Invalid Input'
		else:
			print 'Invalid Input'
			
			

'''test'''
'''
#data = "Hello;1,200;B,3 0;C,10 0,5,C/D,1 2,10,D"
data = "Hello;1,200;B,1 1"
storeReceiveMsg(data)
# print outNI
# print seqT
updateRoutingTable()

# print "ud1"
# print (inNI)
#print (routingTable)

#data = "Hello;1,500;D,1 2;C,10 0,5,C/E,5 5,10,E"
data = "Hello;1,500;C,1 1;B,1 1,1000,B"
storeReceiveMsg(data)
#print (inNI)
# print outNI
# print seqT





# print outNI

updateRoutingTable()
# # print "ud2"
#print (routingTable)
currSeq = 10

data = "Hello;10,400;D,1 0;B,1 1,1,B"
storeReceiveMsg(data)
# # print outNI
updateRoutingTable()
print routingTable


scanSeq()

print routingTable

data = "Hello;10,200;B,1 1;D,1 0,1,D"

storeReceiveMsg(data)
# # print outNI
updateRoutingTable()
print routingTable

# print "ud3"
# print (inNI)
'''
'''MAIN'''

HOST = ''
PORT = 8888
try:
	thread.start_new_thread( sendHello, (PORT, ) )
	thread.start_new_thread( recvHello, (PORT, ) )
	thread.start_new_thread( updateRoutingTable, ( ) )
	thread.start_new_thread( nextH, ( ) )
	thread.start_new_thread( changeVariable, ( ) )
except:
	print "Error: unable to start thread"
while 1:
	pass

