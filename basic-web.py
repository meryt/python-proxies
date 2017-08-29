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
from twisted.web.guard import HTTPAuthSessionWrapper, BasicCredentialFactory
from twisted.python import log
import sys

class LoggingAuthSessionResource(HTTPAuthSessionWrapper):

    def _loginFailed(self, result):
        if result.type == UnhandledCredentials:
            print colored("BASIC [%s] - No credentials supplied, requesting auth" % (str(datetime.datetime.utcnow())), "red")
        elif result.type ==  UnauthorizedLogin:
            print colored("BASIC [%s] - Incorrect credentials" % (str(datetime.datetime.utcnow())), "red")
        else:
            print colored("BASIC [%s] - %s" % (str(datetime.datetime.utcnow()), result.getErrorMessage()), "red")
        return super(LoggingAuthSessionResource, self)._loginFailed(result)

    def _login(self, credentials):
        print colored("BASIC [%s] - Attempting login for %s" % (str(datetime.datetime.utcnow()), str(credentials)), "green")
        return super(LoggingAuthSessionResource, self)._login(credentials)

    def render_POST(self, request):
        print "%s from %s for %s (user: %s pass: %s)" % (
            colored("BASIC Request # %d" % (self.numRequests), 'red'), colored(request.getClientIP(), 'white', attrs=["bold"]), colored(request.getAllHeaders()['host'], 'yellow', attrs=["bold"]), request.getUser(), request.getPassword())
        print colored(request.content.read(), "yellow")
        return super(HTTPAuthSessionWrapper, self).render(request)

    def render(self, request):
        print "%s from %s for %s (user: %s pass: %s)" % (
            colored("BASIC Request # %d" % (self.numRequests), 'red'), colored(request.getClientIP(), 'white', attrs=["bold"]), colored(request.getAllHeaders()['host'], 'yellow', attrs=["bold"]), request.getUser(), request.getPassword())
        print colored(request.content.read(), "yellow")
        return super(HTTPAuthSessionWrapper, self).render(request)

class PublicHTMLRealm(object):
    implements(IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        print colored("BASIC [%s] - serving to authorized user %s" % (str(datetime.datetime.utcnow()), str(avatarId)), 'cyan', attrs=["bold"])

        if IResource in interfaces:
            return (IResource, File("/shome/jenny/web/public_html"), lambda: None)
        print  colored("BASIC [%s] - Could not find user" % (str(datetime.datetime.utcnow())), "red")
        raise NotImplementedError()


portal = Portal(PublicHTMLRealm(), [InMemoryUsernamePasswordDatabaseDontUse(jenny='secret',bobo='this is a very long (password) with extra chars##==')])
credentialFactory = BasicCredentialFactory("lugh.localdomain")

resource = LoggingAuthSessionResource(portal, [credentialFactory])

site = server.Site(resource)
portNum = 7083
print colored("Web server using Basic auth starting up on port %d " % (portNum), 'green', attrs=["bold"])
log.startLogging(sys.stdout)
reactor.listenTCP(portNum, site)
reactor.run()
