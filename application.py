#!/usr/bin/env python3
from imports import *
from socketio import *
from websocket import *
from account import *
from live import *
from events import *
from gui import *
from commands import *

API_KEY = '3a77f9a2-ab3a-44c4-a9a5-9e1c432aeb34'
API_SECRET = 'tbO8HZBKGbDAS5+D23fbMKTLg2oqr4/xM6FkXCiXlRxziWK1ZXA8dCx1L7DmfjPSYVZU9PqiSfzsLIyGue1c/A=='

class Application(object):
    def __init__(self):
        self.events = Events()
        self.ticker = Ticker()
        self.depth = Depth()
        self.trades = Trades()
        self.account = Account(API_KEY,API_SECRET)
        self.updater = Updater(self.events, self.ticker, self.depth, self.trades)
        self.commands = Commands(self.events, self.account, self.ticker, self.trades, self.depth)
        self.update_frequency = 300
        self.last_update = 0
        self.last_ticker_color_change = None
        self.ticker_color_seconds = 1
        self.run_thread = None
        self.gui_thread = None
        self.gui_window = None
        self.quit = False
        self.empty_ticker = {'high':0,'low':0,'average':0,'vwap':0,'volume':0,'last':0,'buy':0,'sell':0}

    def full_update(self):
        if time.time()-self.last_update < self.update_frequency: return
        self.__statusbar('running full update', 0)
        self.__message('running full update')
        self.__statusbar('running full update (account)',0)
        self.account.update()
        self.events += Event(ACCOUNT_UPDATED)
        self.__statusbar('running full update (ticker)',0)
        self.ticker.update()
        self.events += Event(TICKER_UPDATE, change=self.empty_ticker)
        self.__statusbar('running full update (depth)', 0)
        self.depth.update()
        self.events += Event(RESET_DEPTH)
        self.__statusbar('running full update (trades)', 0)
        self.trades.update()
        self.events += Event(TRADE_RESET)
        self.last_update = time.time()
        self.__statusbar()

    def __gui_thread(self):
        app = QtGui.QApplication(sys.argv)
        self.gui_window = Window(self.events,self.commands,self.ticker,self.depth,self.trades)
        self.gui_window.show()
        self.commands.set_window(self.gui_window)
        self.events += Event(GUI_STARTED)
        app.exec_()
        self.events += Event(QUIT_ORDERED)

    def run(self):
        self.gui_thread = threading.Thread(target=self.__gui_thread)
        self.gui_thread.daemon = True
        self.gui_thread.start()
        self.run_thread = threading.Thread(target=self.__run)
        self.run_thread.daemon = True
        self.run_thread.start()
        while not self.quit:
            time.sleep(1)

    def __wait_for_gui(self):
        while True:
            for event in self.events:
                if event.type == GUI_STARTED: return
            time.sleep(1/60)

    def __statusbar(self, text=None, msecs=0):
        if text: self.gui_window.emit(QtCore.SIGNAL('updateMessage'),text,msecs)
        else: self.gui_window.emit(QtCore.SIGNAL('clearMessage'))

    def __message(self, message):
        self.gui_window.emit(QtCore.SIGNAL('addMessage'),message)

    def __run(self):
        self.__wait_for_gui()
        self.__statusbar('starting', 0)
        self.__message('starting')
        self.full_update()
        self.__statusbar('connecting', 0)
        self.__message('connecting')
        self.updater.connect()
        self.__statusbar()
        while True:
            time.sleep(1/60)
            for event in self.events:
                if event.type == WEBSOCKET_CONNECTED:
                    self.__message('websocket connected')
                elif event.type == WEBSOCKET_DISCONNECTED:
                    self.__message('websocket disconnected, reconnecting')
                    self.updater.connect()
                elif event.type == UPDATE_THREAD_STARTED:
                    self.__message('update thread started')
                elif event.type == ACCOUNT_UPDATED:
                    #self.__message('Current Funds: %s %s' % (self.account.wallets['BTC'],self.account.wallets['USD']))
                    pass
                elif event.type == CHANNEL_SUBSCRIBED:
                    self.__message('subscribed to \'%s\' channel' % CHANNELS[event.channel])
                elif event.type == TICKER_UPDATE:
                    self.gui_window.emit(QtCore.SIGNAL('setTicker'),event.change)
                    self.last_ticker_color_change = time.time()
                elif event.type == TRADE_UPDATE:
                    self.gui_window.emit(QtCore.SIGNAL('addTrade'),event.trade)
                elif event.type == DEPTH_UPDATE:
                    self.gui_window.emit(QtCore.SIGNAL('updateDepth'), event.change)
                elif event.type == RESET_DEPTH:
                    pass
                elif event.type == QUIT_ORDERED:
                    self.__statusbar('Quitting')
                    self.quit = True
                    sys.exit()
                elif event.type == TRADE_RESET:
                    self.gui_window.emit(QtCore.SIGNAL('resetTrades'))
                elif event.type == FULL_UPDATE_REQUESTED:
                    self.last_update = 0
                    self.full_update()
                elif event.type == UPDATE_FREQUENCY_CHANGE:
                    self.update_frequency = event.frequency

            self.full_update()
            if self.last_ticker_color_change is not None:
                if time.time() - self.ticker_color_seconds >= self.last_ticker_color_change:
                    self.gui_window.emit(QtCore.SIGNAL('resetTickerColor'))
                    self.last_ticker_color_change = None
