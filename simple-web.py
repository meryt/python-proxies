#!/bin/env python

from termcolor import colored
from twisted.web import server, resource
from twisted.internet import reactor
import datetime

class Simple(resource.Resource):
    isLeaf = True
    numRequests = 0

    def logRequest(self, request):
        self.numRequests += 1
        print colored("[%s] - %s" % (str(datetime.datetime.utcnow()), str(request)), 'cyan', attrs=["bold"])
        print "%s %s from %s for %s" % (
            colored("    Request # %d" % (self.numRequests), 'red'),
            colored(request.method, 'white'),
            colored(request.getClientIP(), 'white', attrs=["bold"]), colored(request.getAllHeaders()['host'], 'yellow', attrs=["bold"]))
        headers = request.getAllHeaders()
        for key in headers:
            if key == 'via' or key == 'x-forwarded-for' or key == 'content-length':
                print colored('    ' + key + ": " + headers[key], 'blue')
        print colored(request.content.read(), "yellow")

    def render_GET(self, request):
        self.logRequest(request)

        request.setHeader("content-type", "text/plain")
        return "Processed request # " + str(self.numRequests) + "\n";

    def render_POST(self, request):
        self.logRequest(request)

        request.setHeader("content-type", "text/plain")

        #print colored('    Situation: %s' % (request.args["situation"][0]), 'green')
        #print request.args

        #return 'Processed request #%d\nYou submitted: %s' % (self.numRequests, request.args["situation"][0],)
        return 'Processed request #%d\n'


site = server.Site(Simple())
portNum = 7081
reactor.listenTCP(portNum, site)
print "Unprotected web server, Listening on port " + str(portNum) + "\n"
reactor.run()


