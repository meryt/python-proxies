#!/usr/bin/python
import time
import BaseHTTPServer
from pprint import pprint
import base64
import json
import cgi
import urllib2

HOST_NAME = '10.2.1.84' # !!!REMEMBER TO CHANGE THIS!!!
PORT_NUMBER = 9000      # You may want to change this
server = '%s:%s' % (HOST_NAME, PORT_NUMBER)
xapp_form = 'http://10.2.1.84:8888/reapi/2013-12-01/engines/Castle/Invasion/events'
xapp_user = 'bobo:gorilla'

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_HEAD(self):
            global numRequests
            numRequests += 1
            self.send_response(200, "OK")
            self.send_header("Content-type", "text/html")
            self.end_headers()

    def do_AUTHHEAD(self):

            self.send_response(401, "Authentication required")
            self.send_header('WWW-Authenticate', 'Basic realm=\"invasion-webserver.py\"')
            self.send_header('Content-type', 'text/html')
            self.end_headers()

    def do_GET(self):
        global numRequests
        numRequests += 1
        print '-----------------------------------------------------------'

        if not self.is_auth_required() or self.auth_succeeds():
            """Respond to a GET request."""
            self.send_response(200, "OK")
            self.send_header("Content-type", "text/html")
            self.end_headers()

            if self.path.startswith("/restricted/invasion"):
                self.wfile.write("<html><head><title>Announce an Invasion.</title></head><body>")
                self.wfile.write('''
                        <form action='.' method='POST'>
                        <h2>Castle Invasion Integration</h2>
                        <label for='type'>Type of Invader</label>
                        <input name='type' id='type' value='Viking' /><br/>
                        <h4>Status Callback</h4>
                        <label for='status_user'>User</label>
                        <input name='status_user' id='status_user' value='jenny' />
                        <label for='status_pass'>Password</label>
                        <input name='status_pass' id='status_pass' value='secret' />
                        <h4>Delivery Status Callback</h4>
                        <label for='delivery_user'>User</label>
                        <input name='delivery_user' id='delivery_user' value='jenny' />
                        <label for='delivery_pass'>Password</label>
                        <input name='delivery_pass' id='delivery_pass' value='secret' />
                        <h4>Response Callback</h4>
                        <label for='response_user'>User</label>
                        <input name='response_user' id='response_user' value='jenny' />
                        <label for='response_pass'>Password</label>
                        <input name='response_pass' id='response_pass' value='secret' />

                        <br/><br />
                        <input type='submit' value="Announce Invasion!" />
                        </form>
                ''')
                # If someone went to "http://something.somewhere.net/foo/bar/",
                # then self.path equals "/foo/bar/".
                self.wfile.write("</body></html>")

            else:
                self.wfile.write("<p>GET: You accessed path: %s</p>" % self.path)
                self.wfile.write("<p><a href='/restricted/invasion/'>Announce an invasion</a></p>")


    def do_POST(self):
        global numRequests
        numRequests += 1
        print '-----------------------------------------------------------'

        if not self.is_auth_required() or self.auth_succeeds():
            length = int(self.headers['Content-length'])
            content = self.rfile.read(length)
            print "POST Content=%s" % (content)

            self.send_response(200, "OK")
            self.send_header("Content-type", "text/html")
            self.end_headers()

            if self.path.startswith("/restricted/invasion"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

                if ctype == 'multipart/form-data':
                    postvars = cgi.parse_multipart(self.rfile, pdict)
                    self.submit_to_xapp(postvars)
                    return
                elif ctype == 'application/x-www-form-urlencoded':
                    length = int(self.headers.getheader('content-length'))
                    postvars = cgi.parse_qs(content, keep_blank_values=1)
                    self.submit_to_xapp(postvars)
                    return
                else:
                    self.wfile.write("<html><head><title>Thank you.</title></head><body>")
                    self.wfile.write("<p>Thank you for your submission.</p></body></html>")

                if "type" not in postvars.keys:
                    self.wfile.write("<html><head><title>Invalid form.</title></head><body>")
                    self.wfile.write("<p>Unable to parse POST vars in your submission.</p></body></html>")
                    return

            else:
                self.wfile.write("<html><head><title>Thank you.</title></head><body>")
                self.wfile.write("<p>Thank you for your submission.</p></body></html>")


    def submit_to_xapp(self, form):
        global server, xapp_form, xapp_user

        json = '''
{
  "properties": {
    "Type":"%s"
  },
 "recipients": [
    {"targetName": "aottema"}
  ],
  "callbacks": [
    {"url":"http://%s/restricted/eventStatus", "type":"status", "authType": "basic", "authUserName": "%s", "authPassword": "%s"},
    {"url":"http://%s/response", "type":"response", "authType": "basic", "authUserName": "%s", "authPassword": "%s"},
    {"url":"http://%s/restricted/deliveryStatus", "type":"deliveryStatus", "authType": "basic", "authUserName": "%s", "authPassword": "%s"}
  ]
}
        '''

        json = json % (form["type"][0], server, form["status_user"][0], form["status_pass"][0], server, form["response_user"][0], form["response_pass"][0], server, form["delivery_user"][0], form["delivery_pass"][0])

        self.wfile.write("<html><head><title>Success!</title></head><body>")
        self.wfile.write("<p>Posting to %s</p>" % xapp_form)
        self.wfile.write("<pre>%s</pre>" % json)
        self.wfile.write("<p><a href='/restricted/invasion/'>Post another</a></p>")
        self.wfile.write("</body></html>")

        req = urllib2.Request(xapp_form)
        req.add_header('Authorization', 'Basic %s' % (base64.b64encode(xapp_user)))
        req.add_header('Content-type', 'application/json')
        req.get_method = lambda: 'POST'
        response = urllib2.urlopen(req, json)


    def is_auth_required(self):
        global numRequests
        if not self.path.startswith('/restricted'):
            print "Request %d No authentication required" % numRequests
            return False
        else:
            return True

    def auth_succeeds(self):
        global numRequests

        if self.headers.getheader('Authorization') == None:
            print "Request %d Authentication required" % numRequests
            self.do_AUTHHEAD()
            self.wfile.write("<html><head><title>Authentication required.</title></head>")
            return False
        elif self.is_valid_user(self.headers.getheader('Authorization')):
            username, password = self.get_auth_credentials(self.headers.getheader('Authorization'))
            print "Request %d Authentication succeeded for user %s with password %s" % (numRequests, username, password)
            return True
        else:
            username, password = self.get_auth_credentials(self.headers.getheader('Authorization'))
            print "Request %d Authentication failed for user %s with password %s " % (numRequests, username, password)
            self.do_AUTHHEAD()
            self.wfile.write("<html><head><title>Authentication failed.</title></head>")
            return False

    def is_valid_user(self, authorization_header):
        users = [
            'jenny:secret',
            'bobo:gorilla',
        ]
        authorization_header = authorization_header.replace('Basic ', '')
        return (base64.b64decode(authorization_header) in users)

    def get_auth_credentials(self, authorization_header):
        basic, _, encoded = authorization_header.partition(' ')
        username, _, password = base64.b64decode(encoded).partition(':')
        return [username, password]


if __name__ == '__main__':
        numRequests = 0
        server_class = BaseHTTPServer.HTTPServer
        httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
        print time.asctime(), "Server starting at %s:%s" % (HOST_NAME, PORT_NUMBER)
        try:
                httpd.serve_forever()
        except KeyboardInterrupt:
                pass
        httpd.server_close()

