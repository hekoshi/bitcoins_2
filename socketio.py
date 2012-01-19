from urllib.request import urlopen
from websocket import *
import json, ssl, socket, time, threading

class SocketIONotImplementedError(NotImplementedError): pass

class SocketIO(object):
    def __init__(self, host, path):
        self.host = host
        self.connected = False
        self.heartbeat_interval = None
        self.id = None
        self.websocket = None
        self.keepalive_thread = None
        self.path = path

    def __keepalive(self):
        while self.connected:
            try: self.websocket.send(b'2::')
            except WebSocketError: self.connected = False; return
            except AttributeError: self.connected = False; return
            time.sleep(self.heartbeat_interval)

    def connect(self):
        request = urlopen('https://' + self.host + '/1')
        data = request.read()
        raw = data.split(b':')
        self.heartbeat_interval = int(raw[1])
        if b'websocket' not in raw[3].split(b','):
            raise SocketIONotImplementedError("only websocket transport layer supported")
        self.id = raw[0].decode()
        self.connected = True
        url = 'wss://'+self.host+'/1/websocket/'+self.id
        self.websocket = websocket(url)
        self.websocket.send(b'1::'+self.path.encode())
        self.keepalive_thread = threading.Thread(target=self.__keepalive)
        self.keepalive_thread.setDaemon(True)
        self.keepalive_thread.start()

    def close(self, hard=False):
        self.connected = False
        self.websocket.close(hard)
        self.websocket = None
        self.keepalive_thread.join()
        self.keepalive_thread = None
        self.id = None
        self.heartbeat_interval = None

    def send(self, data):
        assert(isinstance(data, bytes))
        self.websocket.send(b'4::'+self.path.encode()+b':'+data)

    def recv(self):
        message = self.websocket.recv()
        while message is not None:
            if message[:10] == b'4::'+self.path.encode()+b':':
                return message[10:]
            message = self.websocket.recv()
