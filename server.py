#  coding: utf-8 
import socketserver
import os
# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class msgParser():
    def getRequestAddr(self, defaultStr):
        tokenList = defaultStr.split(' ')[:2]
        httpMethod = tokenList[0]
        route = tokenList[1]
        if route:
            return httpMethod, route
    
    def getRespond(self, httpMethod, endPoint):
        if httpMethod != 'GET':
            return self.formatResponse('', None, 405)

        response = None
        fileType = None
        path = os.getcwd()

        if endPoint[0:4] != '/www':
            path = path + '/www'
        path += endPoint
        path = os.path.normpath(path)

        if endPoint[-1] != '/' and endPoint[-4:] != '.css':
            response = self.formatResponse('http://127.0.0.1:8080' + endPoint + '/', None, 301)
        elif os.path.exists(path) and os.getcwd() in path:
            if not os.path.isfile(path):
                fileType = 'html'
                path = os.path.join(path, 'index.html')
            else:
                if path[-4:] == 'html':
                    fileType = 'html'
                else:
                    fileType = 'css'
            f = open(path, 'r')
            content = f.read()
            f.close()
            response = self.formatResponse(content, fileType, 200)
        else:
            response = self.formatResponse('', None, 404)
        return response

    def formatResponse(self, content, fileType, statusCode):
        header = ''
        if statusCode == 200:
            header = "HTTP/1.1 200 OK\n"
            if (fileType == 'html'):
                header += "Content-Type: text/html\n\n"
            elif (fileType == 'css'):
                header += "Content-Type: text/css\n\n"
        elif statusCode == 405:
            content = "HTTP/1.1 405 Method Not Allowed\n"
        elif statusCode == 404:
            content = "HTTP/1.1 404 Page Not Found\n"
        elif statusCode == 301:
            header = "HTTP/1.1 301 Moved Permanently\n"
            content = "Location: " + content + "\n\n"

        finalRes = header + content
        return finalRes

class MyWebServer(socketserver.BaseRequestHandler):
    # initialize string parser
    def handle(self):
        self.data = self.request.recv(1024).decode('utf8')
        print ("Got a request of: %s\n" % self.data)

        newMsgParser = msgParser()
        httpMethod, route = newMsgParser.getRequestAddr(self.data)

        response = newMsgParser.getRespond(httpMethod, route)

        if not response:
            return
        else:
            self.request.sendall(bytearray(response,'utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
