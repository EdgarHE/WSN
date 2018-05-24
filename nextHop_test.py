import math
currX = 0
currY = 0
routingTable = {"A":"1 1;64;BCD", "B":"2 -1;32;ACF", "C":"1 0.5;22;Q", "D":"10 9;77;FRD"}

def Projection_NextHop(coord): # coord = x y
	global routingTable
	coordX = float(coord.split(' ', 1)[0])
	coordY = float(coord.split(' ', 1)[1])
	vector1X = coordX - currX # vector_X from source to destination
	vector1Y = coordY - currY # vector_Y from source to destination
	product = -10000 # means negative infinity
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

def Angle_NextHop(coord):
	global routingTable
	coordX = float(coord.split(' ', 1)[0])
	coordY = float(coord.split(' ', 1)[1])
	vector1X = coordX - currX # vector_X from source to destination
	vector1Y = coordY - currY # vector_Y from source to destination
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
			nexthop = node
	return nexthop

projectnode = Projection_NextHop("1 0")
anglenode = Angle_NextHop("1 0")
print(projectnode)
print(anglenode)
