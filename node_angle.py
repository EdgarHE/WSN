#!python2
import thread
import threading
import time
import socket
import sys
import math
import struct
import fcntl


def getip(ethname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0X8915, struct.pack('256s', ethname[:15]))[20:24])


alpha = 1
beta = 0.005
gamma = 1

routingTable = {}
inNI = {}  # In region node info
seqT = {}  # Sequence number
ipTable = {}
nodeMap = {}  # 'A':coord_A  coord_A = Coord(1,1)
radius = 3
currNode = 'B'  # Current Node
currX = 1
currY = 4
currSeq = 0
currEnergy = 100
currIP = getip('eth0')
print currIP

send_state = threading.Lock()
storeNI_state = threading.Lock()
storeRT_state = threading.Lock()
pktRecv_state = threading.Lock()


class Coord:
    def __init__(self, coordx, coordy):
        self.x = coordx
        self.y = coordy


def initial():
    global routingTable, inNI
    routingTable = {}
    inNI = {}  # In region node info

def sendRoutingTable(PORT):
    HOST = currIP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
		addr = (HOST, PORT)
		data = repr(routingTable)
		data = currNode + data
		s.sendto(data, addr)
		time.sleep(3)
    s.close()

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
        #print 'send: ' + data
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
        #print routingTable
        storeNI_state.release()


def storeReceiveMsg(recvData):
    # Global Parameters
    #
    data = recvData
    blockNum = len(data.split(';'))
    # print ("bnum%d"%blockNum)
    if data.split(';')[0] == 'Hello':
        seqNum = data.split(';')[1]

        sourceNodeStr = data.split(';')[2]
        node = data.split(';')[2].split(',')[0]

        if node == currNode:
            return
        #print 'recvdata   ' + data
        nodeCoord = data.split(';')[2].split(',')[1]

        nodeIP = data.split(';')[2].split(',')[2]
        if blockNum == 3:
            addToInNI(node, seqNum, nodeCoord, nodeIP)

        elif blockNum > 3:
            inNeighborStr = data.split(';')[3]
            nodeInfo = nodeCoord + ';' + inNeighborStr
            addToInNI(node, seqNum, nodeInfo, nodeIP)


def findNodeInfo(node, num):  # 0:Coord, 1:cost, 2:Path
    nodeInfo = rT.get(node)
    if nodeInfo != none:
        infoStr = rT[nodeInfo].split(';')
        return infoStr[num]


def addSeqNum(node, seq):
    global seqT
    if seqT.get(node, 'None') != 'None':
        if int(seqT[node].split(' ')[0]) < seq:
            seqT[node] = str(seq) + ' ' + str(currSeq)
    else:
        seqT[node] = str(seq) + ' ' + str(currSeq)


def addToInNI(node, seqTime, info, nodeIP):
    global inNI
    seq = int(seqTime.split(',')[0])
    time = seqTime.split(',')[1]
    coord = info.split(';')[0]
    x = int(coord.split(' ')[0])
    y = int(coord.split(' ')[1])
    dist = math.sqrt((x - currX) ** 2 + (y - currY) ** 2)
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
        time.sleep(0.5)


def dealInNIMsg(node):
    global routingTable
    nodeName = node
    nodeInfo = inNI[node]
    nodeCoord = inNI[node].split(';')[1]
    nodeTime = int(inNI[node].split(';')[0])
    nodeCost = calCost(nodeCoord, nodeTime)
    nodePath = nodeName
    updateNodeInfo(nodeName, nodeCoord, nodeCost, nodePath)
    # print (inNI[node])
    if len(inNI[node].split(';')) > 2:
        nodeNum = len(inNI[node].split(';')[2].split('/'))
        # print (nodeNum)
        for i in range(0, nodeNum):
            currNodeInfo = inNI[node].split(';')[2].split('/')[i]
            currNodeName = currNodeInfo.split(',')[0]

            if currNodeName != currNode:
                currCoord = currNodeInfo.split(',')[1]
                currNodeX = int(currCoord.split(' ')[0])
                currNodeY = int(currCoord.split(' ')[1])
                dist = math.sqrt((currNodeX - currX) ** 2 + (currNodeY - currY) ** 2)

                # print dist
                if dist <= radius:
                    nodeInRTInfo = routingTable.get(nodeName, 'None')
                    if nodeInRTInfo != 'None':
                        currCost = int(currNodeInfo.split(',')[2]) + int(nodeInRTInfo.split(';')[1])
                        tempPath = routingTable[nodeName].split(';')[2]
                        currPath = tempPath + currNodeInfo.split(',')[3]

                        isInRT = routingTable.get(currNodeName, 'None')
                        if isInRT != 'None':
                            routingCoord = isInRT.split(';')[0]
                            # print routingCoord + '-------------' + currCoord
                            if routingCoord == currCoord:
                                # print routingCoord + '-------------' + currCoord
                                updateNodeInfo(currNodeName, currCoord, currCost, currPath)


# return


def calCost(coord, nodeTime):
    coordX = int(coord.split(' ')[0])
    coordY = int(coord.split(' ')[1])
    timehr = time.localtime(time.time()).tm_hour
    timemin = time.localtime(time.time()).tm_min
    timesec = time.localtime(time.time()).tm_sec
    currTime = 3600 * timehr + 60 * timemin + timesec
    dTime = currTime - nodeTime
    cost = int(alpha * (2 ** (math.sqrt((coordX - currX) ** 2) + (coordY - currY) ** 2)) + beta * dTime)
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
        if routingCoord != coord and path.count(currNode) < 1:
            routingTable[node] = coord + ';' + str(cost) + ';' + path
        if routingCost > cost and path.count(currNode) < 1:
            routingTable[node] = coord + ';' + str(cost) + ';' + path

    return


def genHelloMsg():
    global currSeq
    timehr = time.localtime(time.time()).tm_hour
    timemin = time.localtime(time.time()).tm_min
    timesec = time.localtime(time.time()).tm_sec
    currTime = 3600 * timehr + 60 * timemin + timesec
    currSeq += 1
    data = "Hello;" + str(currSeq) + ',' + str(currTime) + ';' + currNode + ',' + str(currX) + ' ' + str(
        currY) + ',' + currIP
    if len(routingTable) > 0:
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
        # print ipTable
        if (currSeq - int(seqT[key].split(' ')[1])) > 5:
            for node in routingTable:
                if routingTable[node].find(key) != -1:
                    nodes.append(node)
            for element in nodes:
                if routingTable.get(element, 'None') != 'None':
                    routingTable.pop(element)
                    if ipTable.get(element, 'None') != 'None':
                        ipTable.pop(element)
            seqT[key] = str(0) + ' ' + str(currSeq)

'''
# Projection
def getEdge(coordS, coordD):  # destination_node is a node outside the range (i.e. final destination)
    vector1X = coordD.x - coordS.x  # vector_X from source to destination
    vector1Y = coordD.y - coordS.y  # vector_Y from source to destination
    product = -1000
    if len(routingTable) > 0:
        for node in routingTable:
            location = routingTable[node].split(';')[0]
            locationX = float(location.split(' ')[0])
            locationY = float(location.split(' ')[1])
            vector2X = locationX - coordS.x  # vector_X from source to neighbor
            vector2Y = locationY - coordD.y  # vector_Y from source to neighbor
            newproduct = vector1X * vector2X + vector1Y * vector2Y
            if newproduct > product:  # record the max_product
                product = newproduct
                edge = node
        return edge
    else:
        return 'None'
'''


# Angle
def getEdge(coordS, coordD):  # destination_node is a node outside the range (i.e. final destination)
    vector1X = coordD.x - coordS.x  # vector_X from source to destination
    vector1Y = coordD.y - coordS.y  # vector_Y from source to destination
    cosvalue = -1000
    if len(routingTable) > 0:
        for node in routingTable:
            location = routingTable[node].split(';')[0]
            locationX = float(location.split(' ')[0])
            locationY = float(location.split(' ')[1])
            vector2X = locationX - coordS.x  # vector_X from source to neighbor
            vector2Y = locationY - coordS.y  # vector_Y from source to neighbor
            newproduct = vector1X * vector2X + vector1Y * vector2Y
            norme1 = math.sqrt(vector1X * vector1X + vector1Y * vector1Y)
            norme2 = math.sqrt(vector2X * vector2X + vector2Y * vector2Y)
            newcosvalue = newproduct / (norme1 * norme2)
            if newcosvalue > cosvalue:  # record the max_cosvalue
                cosvalue = newcosvalue
                edge = node
        return edge
    else:
        return 'None'


def createPath(destination):  # destination_node is a node in the range (i.e. edge node)
    storeNI_state.acquire()
    path_string = routingTable[destination].split(';')[2]
    storeNI_state.release()
    count = len(path_string) - 1
    path = []
    while count >= 0:
        path.append(path_string[count])
        count = count - 1
    return path


def genPkt(source_node, coordS_x, coordS_y, destination_node, coordD_x, coordD_y,
           current_node, coordC, content):  # destination_node is a node outside the range (i.e. final destination)
    packet = {}
    packet.update(source=source_node)
    packet.update(coordSource_x=coordS_x)
    packet.update(coordSource_y=coordS_y)
    packet.update(destination=destination_node)
    packet.update(coordDestination_x=coordD_x)
    packet.update(coordDestination_y=coordD_y)
    coordD = Coord(coordD_x, coordD_y)
    if destination_node in routingTable:
        packet.update(edge=destination_node)
        packet.update(pathToEdge=createPath(destination_node))
    else:
        packet.update(edge=getEdge(coordC, coordD))  # Edge is a node at the edge of the range
        packet.update(pathToEdge=createPath(getEdge(coordC, coordD)))
    # Content = input("Input something funny: ")
    packet.update(content=content)
    packet.update(routingPath=[])
    return packet


def transPkt(source_node, coordS_x, coordS_y, destination_node, coordD_x, coordD_y,
             current_node, coordC):  # destination_node is a node outside the range (i.e. final destination)
    packet = {}
    packet.update(source=source_node)
    packet.update(coordSource_x=coordS_x)
    packet.update(coordSource_y=coordS_y)
    packet.update(destination=destination_node)
    packet.update(coordDestination_x=coordD_x)
    packet.update(coordDestination_y=coordD_y)
    coordD = Coord(coordD_x, coordD_y)
    if destination_node in routingTable:
        packet.update(edge=destination_node)
        packet.update(pathToEdge=createPath(destination_node))
    else:
        packet.update(edge=getEdge(coordC, coordD))  # Edge is a node at the edge of the range
        packet.update(pathToEdge=createPath(getEdge(coordC, coordD)))
    #packet.update(edge=getEdge(coordC, coordD))  # Edge is a node at the edge of the range
    packet.update(content="I am a cute packet from " + source_node + " to " + destination_node)
    #packet.update(pathToEdge=createPath(getEdge(coordC, coordD)))
    packet.update(routingPath=[])
    return packet


def recvAndTreatPkt():  # receive, check, print or route/send the packet

    HOST = ipTable[currNode]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((HOST, PORT_RECV))
    # s.listen(1)
    while True:
        # conn, addr = s.accept()
        # print'Connected by', addr
        data = s.recv(10024)
        # if len(data.strip()) == 0:
        # conn.sendall('Done.')
        # else:
        packet = eval(data)  # retrive the dictionary from string, packet is a dictionary
        if currNode == packet['destination']:  # current node is the destination, print the detail about the packet
            print("******** I received a packet from " + packet['source'] + "********")
            print("Packet contains:" + str(packet['content']))
            print("Routing path is: ")
	    print (packet['routingPath'])
        elif currNode == packet['edge']:  # current node is the edge so calculate new route path in the range
            currentC = Coord(currX, currY)
            newpacket = transPkt(packet['source'], packet['coordSource_x'], packet['coordSource_y'],packet['destination'],
                                 packet['coordDestination_x'], packet['coordDestination_y'], currNode, currentC)
            newpacket['content'] = packet['content']
            temphop = newpacket['pathToEdge'].pop()
            prevroute = packet['routingPath'].pop()
            if newpacket['edge'] != 'None' and temphop != prevroute:
                newpacket['pathToEdge'].append(temphop)
                packet['routingPath'].append(prevroute)
                newpacket['routingPath'] = packet['routingPath']
                newpacket['routingPath'].append(currNode)
                nextHop = newpacket['pathToEdge'].pop()
                sendPkt(nextHop, newpacket)
            else:
                print("routing table is empty!")
        else:  # current is a node in the range, route the packet to genPktthe next hop
            try:
                nextHop = packet['pathToEdge'].pop()
            except:
                print("The pathToEdge term is empty, nothing to be popped")
            packet['routingPath'].append(currNode)
            sendPkt(nextHop, packet)


# s.close()

def sendPkt(destination, packet):  # send packet to the next hop, packet is a dictionary
    global currNode
    global ipTable
    global PORT_SEND
    HOST = ipTable[destination]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr = (HOST, PORT_SEND)
    # s.connect((HOST, PORT_SEND))
    s.sendto(repr(packet), addr)
    s.close()


def createInput():
    global currX, currY, radius
    while True:
        data = raw_input()
        if data.find('coord:') != -1:
            coord = data.split(':')[1]
            if coord.find(' ') != -1:
                x = coord.split(' ')[0]
                y = coord.split(' ')[1]
                if x.isdigit() and y.isdigit():
                    currX = int(x)
                    currY = int(y)
                    initial()
                    print 'Change the coordinate of node ' + currNode + ' to (' + str(currX) + ',' + str(currY) + ')'
                else:
                    print 'Invalid Input'
            else:
                print 'Invalid Input'
        elif data.find('radius:') != -1:
            tempRadius = data.split(':')[1]
            if tempRadius.isdigit() :
                tempRadius = int(tempRadius)
                if int(tempRadius) > 0:
                    radius = int(tempRadius)
                    print 'Change the radius of node ' + currNode + ' to ' + str(radius)
                else:
					print 'Radius should greater than 0'
            else:
                print 'Invalid Input'

        elif data.find('pkt;') != -1:  # pkt;P 0 1:xxxxxx
            if data.find(':') != -1:
                destInfo = data.split(':')[0].split(';', 1)[1]
                if destInfo.find(' ') != -1:
                    tempNode = destInfo.split(' ')[0]
                    if tempNode.isupper():
                        destNode = tempNode
                        tempCoord = destInfo.split(' ', 1)[1]
                        if tempCoord.find(' ') != -1:
                            x = tempCoord.split(' ')[0]
                            y = tempCoord.split(' ')[1]
                            if x.isdigit() and y.isdigit():
                                destX = int(x)
                                destY = int(y)
                                sendMsg = data.split(':')[1]
                                if len(sendMsg) != 0:
									pkt = genPkt(currNode, currX, currY, destNode, destX, destY,
												 currNode, Coord(currX, currY), sendMsg)
									nexthop = pkt['pathToEdge'].pop()
									pkt['routingPath'].append(currNode)
									sendPkt(nexthop, pkt)
									print 'Send a packet to ' + destNode + ':' + sendMsg
                                else:
                                    print 'Nothing to send'
                            else:
                                print 'Invalid input'
                        else:
                            print 'Invalid input'
                    else:
                        print 'Invalid input'
                else:
                    print 'Invalid input'
            else:
                print 'Invalid input'


        else:
            print 'Invalid Input'


'''MAIN'''

HOST = ''
PORT = 8888  # routing table

PORT_SEND = 23333  # packet
PORT_RECV = 23333
PORT_SENDRT = 23444

ipTable[currNode] = currIP
try:
    thread.start_new_thread(sendHello, (PORT,))
    thread.start_new_thread(recvHello, (PORT,))
    thread.start_new_thread(updateRoutingTable, ( ))
    thread.start_new_thread(createInput, ( ))
    thread.start_new_thread(recvAndTreatPkt, ( ))
    thread.start_new_thread(sendRoutingTable, (PORT_SENDRT,))
except:
    print "Error: unable to start thread"
while 1:
    pass
