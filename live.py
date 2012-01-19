#!/usr/bin/env python3
from imports import *
from socketio import *
from websocket import *
from events import *
from trade import *
from ticker import *
from depth import *

class Updater(object):
    def __init__(self, events, ticker, depth, trades):
        self.ticker = ticker
        self.depth = depth
        self.trades = trades
        self.events = events
        self.socket = None
        self.update_thread = None
        self.stop = True
        self.use_socketio = USE_SOCKETIO

    def __run(self):
        while not self.stop:
            try: data_raw = self.socket.recv()
            except:
                self.events += Event(WEBSOCKET_DISCONNECTED, reconnect=True)
                return
            if data_raw is None:
                self.events += Event(WEBSOCKET_DISCONNECTED, reconnect=True)
                return
            try: data = json.loads(data_raw.decode())
            except ValueError: continue
            else:
                if data['op'] == 'subscribe':
                    self.events += Event(CHANNEL_SUBSCRIBED, channel=data['channel'])
                elif data['op'] == 'remark':
                    self.events += Event(REMARK_MESSAGE, message=data['message'])
                elif data['op'] == 'private':
                    if data['private'] == 'ticker':
                        change, total_change = self.ticker.update(data['ticker'])
                        if total_change: self.events += Event(TICKER_UPDATE,change=change)
                    elif data['private'] == 'trade':
                        trade = Trade(**data['trade'])
                        self.trades += trade
                        self.events += Event(TRADE_UPDATE, trade=trade)
                    elif data['private'] == 'depth':
                        self.depth += data['depth']
                        if int(data['depth']['volume_int']): self.events += Event(DEPTH_UPDATE, change=data['depth'])

    def connect(self):
        try:
            if self.use_socketio:
                self.socket = SocketIO(SOCKETIO_URL, SOCKETIO_PATH)
                self.socket.connect()
            else:
                self.socket = websocket(WEBSOCKET_URL)
            self.events += Event(WEBSOCKET_CONNECTED)
            self.update_thread = threading.Thread(target=self.__run)
            self.stop = False
            self.update_thread.start()
            self.events += Event(UPDATE_THREAD_STARTED)
        except:
            self.events += Event(WEBSOCKET_DISCONNECTED, reconnect=True)
            return

    def disconnect(self, reconnect=False):
        # the reason for the following split is that other threads send "disconnected" events before we have a chance to send ours
        if not reconnect: self.events += Event(WEBSOCKET_DISCONNECTED, reconnect=False)
        self.socket.close(True)
        if reconnect: self.events += Event(WEBSOCKET_DISCONNECTED, reconnect=True)
