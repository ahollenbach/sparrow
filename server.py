from __future__ import print_function

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
import threading
import json
import random
import re
import socket


# Inspired by: https://mafayyaz.wordpress.com/2013/02/08/writing-simple-http-server-in-python-with-rest-and-json/
class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if None != re.search('/sparrow/status', self.path):
            # API request
            # TODO Dummy response to be replaced with actual
            statuses = {
                "worker1" : random.randint(0,5),
                "worker2" : random.randint(0,5)
            }

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(statuses))
        elif None != re.search('/sparrow', self.path):
            # Send back webpage
            with open('web/index.html', 'r') as html_file:
                html = html_file.read()

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)
        elif None != re.search('web', self.path):
            # Resource request
            resource = self.path.split('/')[-1]
            with open("web/" + resource, 'r') as resource_file:
                res = resource_file.read()

            self.send_response(200)

            if "css" in self.path:
                type = "text/css"
            else:
                type = "text/html"

            self.send_header("Content-type", type)
            self.send_header("Content-Length", str(len(res)))
            self.end_headers()
            self.wfile.write(res)
        else:
            # Invalid request
            self.send_response(403)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = True

    def shutdown(self):
        self.socket.close()
        HTTPServer.shutdown(self)


class SimpleHttpServer():
    def __init__(self, ip, port):
        self.server = ThreadedHTTPServer((ip, port), HTTPRequestHandler)

    def start(self):
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def waitForThread(self):
        self.server_thread.join()

    def stop(self):
        self.server.shutdown()
        self.waitForThread()


if __name__ == '__main__':
    # parser = argparse.ArgumentParser(description='HTTP Server')
    # parser.add_argument('port', type=int, help='Listening port for HTTP Server', default=8901)
    # args = parser.parse_args()
    #
    # server = SimpleHttpServer(socket.gethostname(), args.port)
    HOST = socket.gethostname()
    PORT = 8901

    server = SimpleHttpServer(HOST, PORT)
    print('Starting server at %s:%d' % (HOST, PORT))
    # server.start()
    # server.waitForThread()
    server.server.serve_forever()