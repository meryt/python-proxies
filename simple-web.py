#!/bin/env python

from termcolor import colored
from twisted.web import server, resource
from twisted.internet import reactor
import datetime

class Simple(resource.Resource):
    isLeaf = True
    numRequests = 0
    
    def render_GET(self, request):
        self.numRequests += 1
        print colored("[%s] - %s" % (str(datetime.datetime.utcnow()), str(request)), 'cyan', attrs=["bold"])

        print "%s from %s for %s (user: %s pass: %s)" % (
            colored("Request # %d" % (self.numRequests), 'red'), colored(request.getClientIP(), 'white', attrs=["bold"]), colored(request.getAllHeaders()['host'], 'yellow', attrs=["bold"]), request.getUser(), request.getPassword())

        for key in request.getAllHeaders():
            print(key + ": " + request.getAllHeaders()[key])

        request.setHeader("content-type", "text/plain")
        return "Processed request # " + str(self.numRequests) + "\n";

site = server.Site(Simple())
portNum = 7081
reactor.listenTCP(portNum, site) 
print "Unprotected web server, Listening on port " + str(portNum) + "\n"
reactor.run()


