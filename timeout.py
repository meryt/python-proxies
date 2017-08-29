#!/usr/bin/env python

'''
Listens on specified port (or 8888) but never sends data.
Useful for simulating Connection timed out states.
'''

import socket
import sys

port = 8888
if (len(sys.argv) > 1):
    port = int(sys.argv[1])


print("Timeout Server -- accepts connections on specified port but never responds.")
print("                  Useful for simulating Connection Timed Out.")
print "                  Exits when client goes away."

print("Listening on port {0} ".format(port))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('localhost', port))
s.listen(1)
(clientsocket, address) = s.accept()

while 1:
    data = clientsocket.recv(1024)
    if not data:
        print("Client went away")
        break



