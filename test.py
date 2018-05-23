#!python2
import thread
import time
import socket
import sys
import math


def send_routing(PORT):
	
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
	s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

	while True:
		network = '<broadcast>'
		addr = (network, PORT)
		data = 'aaa'
		s.sendto(data, addr)
		print data

		time.sleep(1)
		
	s.close()  



'''MAIN'''

HOST = ''
PORT = 8888

send_routing(PORT)
# try:
# 	thread.start_new_thread( sendRouting, (HOST, PORT, ) )
	
# except:
# 	print "Error: unable to start thread"

# while 1:
# 	pass
