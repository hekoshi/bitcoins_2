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
        #self.socket = SocketIO(SOCKETIO_URL, SOCKETIO_PATH)
        self.socket = None
        self.update_thread = None
        self.stop = True

    def __run(self):
        while not self.stop:
            data_raw = self.socket.recv()
            if data_raw is None:
                self.events += Event(WEBSOCKET_DISCONNECTED)
                return
            data = json.loads(data_raw.decode())
            if data['op'] == 'subscribe':
                self.events += Event(CHANNEL_SUBSCRIBED, channel=data['channel'])
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
            self.socket = websocket(WEBSOCKET_URL)
            self.events += Event(WEBSOCKET_CONNECTED)
            self.update_thread = threading.Thread(target=self.__run)
            self.stop = False
            self.update_thread.start()
            self.events += Event(UPDATE_THREAD_STARTED)
        except:
            self.events += Event(WEBSOCKET_DISCONNECTED)
            return
