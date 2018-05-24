import socket
import math

routingTable = {'A':"1 1;64;BCD", 'B':"2 -1;32;ACF", 'C':"1 0.5;22;Q", 'D':"10 9;77;FRD"}

class Coord:
    def __init__(self, coordx, coordy):
        self.x = coordx
        self.y = coordy

coord_A = Coord(1,1)
coord_B = Coord(2,1)
coord_C = Coord(4,1)
coord_D = Coord(1,5)
coord_E = Coord(3,2)
coord_F = Coord(4,7)

nodeMap = {'A':coord_A,
       'B':coord_B,
       'C':coord_C,
       'D':coord_D,
       'E':coord_E,
       'F':coord_E}

PORT_SEND = 23333
PORT_RECV = 23334
########################################################################################################################
'''
class Packet:
    def __init__(self, source_node, destination_node): # destination_node is a node outside the range (i.e. final destination)
        self.source = source_node
        self.destination = destination_node
        self.edge = self.getEdge() # Edge is a node at the edge of the range
        self.content = self.inputContent()
        self.pathToEdge = self.createPath() # path is a stack which stores the route to edge

    def getEdge(self):  # coord = x y
        #global routingTable
        vector1X = nodeMap[self.destination].x - nodeMap[self.source].x  # vector_X from source to destination
        vector1Y = nodeMap[self.destination].y - nodeMap[self.source].y  # vector_Y from source to destination
        product = -10000  # means negative infinity
        for node in routingTable:
            location = routingTable[node].split(';')[0]
            locationX = float(location.split(' ')[0])
            locationY = float(location.split(' ')[1])
            vector2X = locationX - nodeMap[self.source].x  # vector_X from source to neighbor
            vector2Y = locationY - nodeMap[self.source].y  # vector_Y from source to neighbor
            newproduct = vector1X * vector2X + vector1Y * vector2Y
            if newproduct > product:  # record the max_product
                product = newproduct
                edge = node
        return edge

    def createPath(self):
        path_string = routingTable[self.destination].split(';')[2]
        count = len(path_string) - 1
        path = []
        while count >= 0:
            path.push(path_string[count])
            count = count - 1
        return path

    def inputContent(self):
        content = input("Please input a cute message: ")
        return content
'''
########################################################################################################################
# metric: projection
def getEdge(source, destination): # destination_node is a node outside the range (i.e. final destination)
    #global routingTable
    vector1X = nodeMap[destination].x - nodeMap[source].x  # vector_X from source to destination
    vector1Y = nodeMap[destination].y - nodeMap[source].y  # vector_Y from source to destination
    product = -10000  # means negative infinity
    for node in routingTable:
        location = routingTable[node].split(';')[0]
        locationX = float(location.split(' ')[0])
        locationY = float(location.split(' ')[1])
        vector2X = locationX - nodeMap[source].x  # vector_X from source to neighbor
        vector2Y = locationY - nodeMap[source].y  # vector_Y from source to neighbor
        newproduct = vector1X * vector2X + vector1Y * vector2Y
        if newproduct > product:  # record the max_product
            product = newproduct
            edge = node
    return edge
'''
# metric: angle
def Angle_NextHop(source, destination): # coord = x y
	#global routingTable
    vector1X = nodeMap[destination].x - nodeMap[source].x  # vector_X from source to destination
    vector1Y = nodeMap[destination].y - nodeMap[source].y  # vector_Y from source to destination
	cosvalue = -10000
	for node in routingTable:
		location = routingTable[node].split(';')[0]
		locationX = float(location.split(' ')[0])
		locationY = float(location.split(' ')[1])
		vector2X = locationX - currX # vector_X from source to neighbor
		vector2Y = locationY - currY # vector_Y from source to neighbor
		newproduct = vector1X*vector2X + vector1Y*vector2Y
		norme1 = math.sqrt(vector1X*vector1X+vector1Y*vector1Y)
		norme2 = math.sqrt(vector2X*vector2X+vector2Y*vector2Y)
		newcosvalue = newproduct / (norme1 * norme2)
		if newcosvalue > cosvalue:
			cosvalue = newcosvalue
			edge = node
	return edge
'''
def createPath(destination): # destination_node is a node in the range (i.e. edge node)
    path_string = routingTable[destination].split(';')[2]
    count = len(path_string) - 1
    path = []
    while count >= 0:
        path.append(path_string[count])
        count = count - 1
    return path

def genPkt(source_node, destination_node, current_node): # destination_node is a node outside the range (i.e. final destination)
    packet = {}
    packet.update(source = source_node)
    packet.update(destination = destination_node)
    packet.update(edge = getEdge(current_node, destination_node)) # Edge is a node at the edge of the range
    packet.update(content = "I am a cute packet from " + source_node + " to " + destination_node)
    packet.update(pathToEdge = createPath(destination_node))
    return packet

def recvAndTreatPkt(): # receive, check, print or route/send the packet
    global currNode
    global PORT_RECV
    HOST = ipTable[currNode]
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT_RECV))
    s.listen(1)
    while True:
        conn, addr = s.accept()
        print'Connected by', addr
        data = conn.recv(10024)
        if len(data.strip()) == 0:
            conn.sendall('Done.')
        else:
            packet = eval(data) # retrive the dictionary from string, packet is a dictionary
            if currNode == packet['destination']: # current node is the destination, print the detail about the packet
                print("I received a packet from " + packet['source'])
                print("Packet contains:")
                print(packet['content'])
            elif currNode == packet['edge']: # current node is the edge so calculate new route path in the range
                newpacket = genPkt(packet['source'],packet['destination'], currNode)
                nextHop = packet['pathToEdge'].pop()
                sendPkt(nextHop, packet)
            else: # current is a node in the range, route the packet to the next hop
                try:
                    nextHop = packet['pathToEdge'].pop()
                except:
                    print("The pathToEdge term is empty, nothing to be popped")
                sendPkt(nextHop, packet)

        conn.close()

def sendPkt(destination, packet): # send packet to the next hop, packet is a dictionary
    global currNode
    global ipTable
    global PORT_SEND
    HOST = ipTable[destination]
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT_SEND))
    s.sendall(repr(packet))
    s.close()
