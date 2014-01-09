#!/bin/env python

from zope.interface import implements
from termcolor import colored
import datetime

from twisted.cred.error import UnhandledCredentials
from twisted.cred.error import UnauthorizedLogin
from twisted.cred.portal import IRealm, Portal
from twisted.cred.checkers import InMemoryUsernamePasswordDatabaseDontUse
from twisted.web.static import File
from twisted.web.resource import IResource
from twisted.web import server, resource
from twisted.internet import reactor
from twisted.web.guard import HTTPAuthSessionWrapper, DigestCredentialFactory

class LoggingAuthSessionResource(HTTPAuthSessionWrapper):

    def _loginFailed(self, result):
        if result.type == UnhandledCredentials:
            print colored("DIGEST [%s] - No credentials supplied, requesting auth" % (str(datetime.datetime.utcnow())), "red")
        elif result.type ==  UnauthorizedLogin:
            print colored("DIGEST [%s] - Incorrect credentials" % (str(datetime.datetime.utcnow())), "red")
        else:
            print colored("DIGEST [%s] - %s" % (str(datetime.datetime.utcnow()), result.getErrorMessage()), "red")
        return super(LoggingAuthSessionResource, self)._loginFailed(result)

    def render(self, request):
        print "%s from %s for %s (user: %s pass: %s)" % (
            colored("Request # %d" % (self.numRequests), 'red'), colored(request.getClientIP(), 'white', attrs=["bold"]), colored(request.getAllHeaders()['host'], 'yellow', attrs=["bold"]), request.getUser(), request.getPassword())
        return super(HTTPAuthSessionWrapper, self).render(request)

class PublicHTMLRealm(object):
    implements(IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        print colored("DIGEST [%s] - serving to authorized user %s" % (str(datetime.datetime.utcnow()), str(avatarId)), 'cyan', attrs=["bold"])

        if IResource in interfaces:
            return (IResource, File("/shome/jenny/web/public_html"), lambda: None)
        raise NotImplementedError()


portal = Portal(PublicHTMLRealm(), [InMemoryUsernamePasswordDatabaseDontUse(jenny='secret')])
credentialFactory = DigestCredentialFactory("md5", "localhost:7082")

resource = LoggingAuthSessionResource(portal, [credentialFactory])


site = server.Site(resource)
portNum = 7082
print colored("Web server using Digest auth starting up on port %d " % (portNum), 'green', attrs=["bold"])
reactor.listenTCP(portNum, site) 
reactor.run()
