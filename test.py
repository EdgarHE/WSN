#!python2
import thread
import time
import socket
import sys


def sendHello(PORT):
	
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
	s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

	while True:
		network = '<broadcast>'
		addr = (network, PORT)
		data = 'aaa'
		s.sendto(data, addr)
		print 'send' + data

		time.sleep(1)
		
	s.close()  

def recvHello(PORT):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
	s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	
	s.bind(('', PORT))
	
	while True:
		data, addr = s.recvfrom(100)
		print 'recv' + data

'''MAIN'''

HOST = ''
PORT = 8888

#send_routing(PORT)
try:
	thread.start_new_thread( sendHello, (PORT, ) )
	thread.start_new_thread( recvHello, (PORT, ) )
# except:
# 	print "Error: unable to start thread"

# while 1:
# 	pass
