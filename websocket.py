#!/usr/bin/env python3
import socket, ssl, codecs, random, struct, hashlib, threading, base64
from urllib.parse import urlparse

RESOURCE_CHARS = " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
PROTOCOL_CHARS = " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
LARGEST_INT = 4294967295
MAX_STRUCT_INT = 18446744073709551615
SOCKET_TIMEOUT = None
INSERT_CHARS = "'!\"#$%&\'()*+,-./:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~'"
CODE_CHARS = b"0123456789"
CAPITAL_LETTERS = b"ABCDEFGHIJKLMNOPQRSTUVWXYZ"
CONNECTION_LIMIT = 30
KEY_COMPARE = b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

class WebSocketError(Exception): pass

def websocket(url, protocol=None, autoconnect=True):
    """ Create websocket from url -> WebSocket  """
    parsed_url = urlparse(url)
    host = parsed_url.hostname
    resource_name = parsed_url.path
    if not resource_name: resource_name = '/'
    origin = '127.0.0.1'
    if parsed_url.scheme == 'ws': secure = False
    elif parsed_url.scheme == 'wss': secure = True
    else: raise WebSocketError("invalid websocket scheme")
    if parsed_url.port: port = parsed_url.port
    elif secure: port = 443
    else: port = 80
    return WebSocket(host, port, origin, secure,
                     resource_name, protocol,autoconnect)

class active(object):
    def __init__(self):
        self.websockets = []
        self.update_lock = threading.Lock()

    def __call__(self):
        """ Returns all active WebSocket objects -> list """
        self.update()
        return self.websockets

    def update(self):
        with self.update_lock:
            websockets = list(self.websockets)
            for websocket in websockets:
                if websocket.socket is None:
                    self.websockets.remove(websocket)

    def count(self, websocket):
        return self.get_hosts().count(websocket.host)

    def get_hosts(self):
        return [websocket.host for websocket in self.get_connecting()]

    def get_connecting(self):
        return [websocket for websocket in self.websockets if websocket.connected == False and websocket.socket is not None]

    def add(self, websocket):
        self.update()
        if self.count(websocket) > CONNECTION_LIMIT and CONNECTION_LIMIT > 0:
            raise WebSocketError("too many connection attemps to one host")
        else: self.websockets.append(websocket)

# init steps for module
_active = active()
active_websockets = _active.__call__
del active

class WebSocket(object):
    """ Object representing the connection to a remote websocket """
    def __init__(self, host, port, origin, secure,
                 resource_name, protocol=None,
                 autoconnect=True):
        """ Use websocket.websocket(url, [protocol]) instead """
        # convert hostname to punycode
        self.encoder = codecs.getencoder('punycode')
        host_raw = self.encoder(host)
        self.host = host_raw[0][:host_raw[1]].decode()

        # init general values
        self.port = port
        self.origin = origin
        self.origin.lower()

        # verify resource name
        if resource_name[0] != '/':
            raise ValueError("resource name must start with \"/\"")
        for char in resource_name:
            if char not in RESOURCE_CHARS:
                raise ValueError("unacceptable character in resource name.")

        # verify protocol name
        if protocol is not None:
            for char in protocol:
                if char not in PROTOCOL_CHARS:
                    raise ValueError("unacceptable character in protocol.")

        # init rest of general values
        self.resource_name = resource_name
        self.protocol = protocol
        self.secure = secure
        self.socket = None
        self.connected = False
        self.closing = False

        # handle autoconnect
        if autoconnect: self.connect()

    # internal functions
    def __insert(self, string_1, string_2, position):
        part_1 = string_1[:position]
        part_2 = string_1[position:]
        return part_1 + string_2 + part_2

    def __construct_url(self, host, port, resource_name, secure):
        url = ''
        if secure: url += 'wss://'
        else: url += 'ws://'
        url += host
        if (not secure and port != 80) or (secure and port != 443):
            url += ':' + str(port)
        url += resource_name
        return url

    def __fail(self, message=None):
        if self.socket: self.socket.close()
        raise WebSocketError(message)

    # general functions
    def connect(self):
        # version 00 of connection handshake
        # make sure we aren't connecting twice
        if self.socket is not None: return

        # register with active websocket tracker
        _active.add(self)

        # skipping proxy (use system-wide settings)

        # create socket and connect to host
        self.socket = socket.socket()
        self.socket.connect((self.host,self.port))
        self.socket.settimeout(SOCKET_TIMEOUT)
        if self.secure:
            # handle ssl connections
            self.socket = ssl.wrap_socket(self.socket)

        # send request
        self.socket.send(b"GET ")
        self.socket.send(self.resource_name.encode())
        self.socket.send(b" HTTP/1.1")
        self.socket.send(b"\r\n")

        # prepare headers
        fields = []
        fields.append("Upgrade: WebSocket")
        fields.append("Connection: Upgrade")
        # handle possible unusual port request
        hostport = ""
        host = self.host.lower()
        hostport += host
        if not self.secure and self.port != 80 or\
                self.secure and self.port != 443:
            hostport += ":" + str(self.port)
        # add rest of headers
        fields.append("Host: " + hostport)
        fields.append("Origin: " + self.origin)
        if self.protocol is not None:
            fields.append("Sec-WebSocket-Protocol: " + self.protocol)
        # skipping cookies
        # generate server challenge keys
        spaces_1 = random.randint(1,12)
        spaces_2 = random.randint(1,12)
        max_1 = int(LARGEST_INT/spaces_1)
        max_2 = int(LARGEST_INT/spaces_2)
        number_1 = random.randint(0,max_1)
        number_2 = random.randint(0,max_2)
        product_1 = number_1 * spaces_1
        product_2 = number_2 * spaces_2
        key_1 = str(product_1)
        key_2 = str(product_2)
        for i in range(random.randint(1,12)):
            key_1 = self.__insert(key_1,random.choice(INSERT_CHARS),
                           random.randrange(len(key_1)))
        for i in range(random.randint(1,12)):
            key_2 = self.__insert(key_2,random.choice(INSERT_CHARS),
                           random.randrange(len(key_2)))
        for i in range(spaces_1):
            key_1 = self.__insert(key_1,' ',random.randrange(1,len(key_1)-1))
        for i in range(spaces_2):
            key_2 = self.__insert(key_2,' ',random.randrange(1,len(key_2)-1))
        # add challenge keys to headers
        fields.append("Sec-WebSocket-Key1: " + key_1)
        fields.append("Sec-WebSocket-Key2: " + key_2)

        # fire off headers in random order
        while len(fields):
            self.socket.send(fields.pop(random.randrange(len(fields))).encode()+b'\r\n')
        self.socket.send(b'\r\n')
        # generate random challenge string
        key_3 = struct.pack("!Q", random.randint(0,MAX_STRUCT_INT))
        # send random challenge string
        self.socket.send(key_3)

        # recieve response
        field = b""
        while True:
            char = self.socket.recv(1)
            if not char: break
            field += char
            if char == b"\n": break
        # check for weird response
        if len(field) < 7 or field[-2:] != b"\r\n" or\
                field.count(b' ') < 2:
            self.__fail("invalid response")
        # check for weird response code
        code = field[field.index(b' ')+1:field.index(b' ',field.index(b' ')+1)]
        for char in code:
            if char not in CODE_CHARS:
                self.__fail("unacceptable character in response code")
        if code == b'101': pass
        elif code == b'407':
            self.__fail("proxy authentication required")
        else:
            self.__fail("unknown response code")

        # prepare to recieve headers
        fields = {}
        name = ""
        value = ""

        # recieve headers
        while True:
            # outer while loop is for name
            char = self.socket.recv(1)
            if not char: self.__fail("connection closed during handshake")
            elif char == b'\r':
                if len(name) == 0: break
                else: self.__fail("malformed headers")
            elif char == b'\n':
                self.__fail("malformed headers")
            elif char == b':':
                count = 0
                while True:
                    # inner while loop is for value
                    char = self.socket.recv(1)
                    count += 1
                    if not char: self.__fail("connection closed during handshake")
                    elif char == b' ' and count == 1: continue
                    elif char == b'\r': break
                    elif char == b'\n': self.__fail("malformed headers")
                    else: value += char.decode()
                char = self.socket.recv(1)
                if char != b'\n': self.__fail("malformed headers")
                # add name and value pair to header list
                fields[name] = value
                name = ""; value = ""
            elif char in CAPITAL_LETTERS:
                name += char.lower().decode()
            else: name += char.decode()
        # recieve additional \n byte to finish headers
        char = self.socket.recv(1)
        if char != b'\n': self.__fail("malformed headers")

        # check header names
        # for missing/empty/malformed/duplicate headers
        keys = list(fields.keys())
        if keys.count('upgrade') != 1 or\
                keys.count('connection') != 1 or\
                keys.count('sec-websocket-origin') != 1 or\
                keys.count('sec-websocket-location') != 1 or\
                (self.protocol is not None and keys.count('sec-websocket-protocol') != 1) or\
                keys.count('') > 0:
            self.__fail("malformed headers")
        del char,keys

        # check header values
        for name in fields:
            if name == 'upgrade':
                if fields[name].lower() != 'websocket': self.__fail("invalid upgrade header")
            if name == 'connection':
                if fields[name].lower() != 'upgrade': self.__fail("invalid connection header")
            if name == 'sec-websocket-origin':
                if fields[name] != self.origin: self.__fail("invalid origin header (warning! possible XSS attack)")
            if name == 'sec-websocket-location':
                if fields[name] != self.__construct_url(self.host, self.port, self.resource_name, self.secure):
                    self.__fail("invalid location header (warning! possible XSS attack)")
            if name == 'sec-websocket-protocol':
                if self.protocol is not None and fields[name] != self.protocol:
                    self.__fail("invalid protocol header")
            # not handling cookies here

        # calculate expected challenge
        challenge = struct.pack("!II",number_1,number_2) + key_3
        expected = hashlib.md5(challenge).digest()
        reply = self.socket.recv(16)
        if len(reply) < 16: self.__fail("invalid challenge")
        if expected != reply: self.__fail("invalid challenge")
        
        # success!
        self.connected = True

    def recv(self):
        if self.closing: return
        if self.socket is None: self.__fail("not connected")
        # get frame type
        frame_type = self.socket.recv(1)
        error = False
        if not frame_type: self.close(); return
        elif frame_type[0] & 128 == 128:
            # check for closing handshake
            length = 0
            while True:
                b = self.socket.recv(1)
                b_v = b[0] & 127
                length *= 128
                length += b_v
                if b[0] & 128 == 128: continue
                else: break
            self.socket.recv(length) # discard data
            if frame_type == b'\xff' and length == 0:
                # closing handshake detected
                self.close()
                return
            else: error = True
        elif frame_type[0] & 128 == 0:
            # recieve data
            raw_data = b""
            while True:
                b = self.socket.recv(1)
                if b != b'\xff': raw_data += b
                else: break
            data = raw_data
            if frame_type == b'\x00':
                return data
            else: error = True
        else: error = True
        if error: self.__fail("invalid frame type")

    def send(self, data):
        """ Send packet of data to websocket -> None """
        if self.closing: return
        if self.socket is None: self.__fail("not connected")
        assert(type(data) == bytes)
        self.socket.send(b'\x00')
        self.socket.send(data)
        self.socket.send(b'\xff')

    def close(self):
        """ Closes the websocket -> None """
        if self.closing: return
        if self.socket is None: self.__fail("not connected")
        self.closing = True
        self.socket.send(b'\xff')
        self.socket.send(b'\x00')
        while True:
            b = self.socket.recv(1)
            if not b:
                self.socket = None
                self.closing = False
                self.connected = False
                break
            elif b == '\xff':
                b = self.socket.recv(1)
                if not b or b == '\xff':
                    self.socket = None
                    self.closing = False
                    self.connected = False
                    break

__all__ = ['websocket', 'active_websockets', 'WebSocket', 'WebSocketError']
