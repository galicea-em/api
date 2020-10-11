# pip install requests
# requests>=2.5.0

import threading
import requests
from pprint import pprint
import http.server as SimpleHTTPServer
import socketserver

api_port=5000
auth_url='http://127.0.0.1:5000/oauth/authorize'

server_port=3000
#redirect_url='http://127.0.0.1:3000'
redirect_uri='http%3A%2F%2F127.0.0.1%3A3000'
client_id=1

url=auth_url+('?redirect_uri=%s&client_id=%s' % (redirect_uri,client_id))+'&response_type=code&state=state_test&response_mode=query' 


class Handler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def do_GET(self):
        request_path = self.path
        print('Request:')
        pprint(request_path)
        if not request_path.find('state=state_test'):
            message='error: state=state_test'
        else:
            i=request_path.find('code=')
            if i>0:
                message=request_path[i:]
            else:
                message = 'error: code'
        print('Message=%s' % message)
        self.send_response(200)
        self.end_headers()


class Server(socketserver.TCPServer):
    def server_bind(self):
        import socket
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)


def start_httpd(port, server_class=Server, handler_class=Handler):
    with server_class(('', port), handler_class) as server:
        server.serve_forever()

def server_thread():
    start_httpd(server_port)

try:
    thread_type = threading.Thread(target=server_thread)
    thread_type.start()
    thread_type.join(4)
    demo_login = {"user": "demo", "password": "demo"}
    session = requests.Session()
    login = session.post('http://localhost:%d/login' % api_port, None, demo_login)
    cookies=session.cookies.get_dict()
    response=session.get(url, cookies=cookies)
    print('koniec testu')
    print('Naciśnij ^C')
except Exception as e:
    print("Error: %s" % e)
