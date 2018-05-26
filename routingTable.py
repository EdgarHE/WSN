#!python2
import thread
import time
import socket
import sys


def recvHello(PORT):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    s.bind(('', PORT))

    while True:
		data, addr = s.recvfrom(1000)
		currNode = data[0]
		routingTable = eval(data[1:])
		print ''
		print '----- Routing Table of Node ' + currNode + ' -----'
		print 'Node Name   Coordinate   Cost   Path'
		for key in routingTable:
			node = key
			coord = routingTable[node].split(';')[0]
			x = coord.split(' ')[0]
			y = coord.split(' ')[1]
			cost = routingTable[node].split(';')[1]
			path = routingTable[node].split(';')[2]
			print '    ' + key + '         (' + x +' , ' + y + ')     ' + cost + '      '+ path
		print ''
		print ''
		
PORT_SENDRT = 23444
recvHello(PORT_SENDRT)

