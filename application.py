#!/usr/bin/env python3
from imports import *
from socketio import *
from websocket import *
from account import *
from live import *
from events import *
from gui import *
from commands import *
from call import *

class Application(object):
    def __init__(self):
        self.events = Events()
        self.ticker = Ticker()
        self.depth = Depth()
        self.trades = Trades()
        self.account = Account(self.events,None,None)
        self.caller = Caller(self.events, self.account, self.ticker, self.depth, self.trades)
        self.updater = Updater(self.events, self.ticker, self.depth, self.trades)
        self.commands = Commands(self.events, self.caller, self.account, self.ticker, self.trades, self.depth)
        self.update_frequency = UPDATE_FREQUENCY
        self.last_update = 0
        self.last_ticker_color_change = None
        self.ticker_color_seconds = TICKER_COLOR_SECONDS
        self.run_thread = None
        self.gui_thread = None
        self.gui_window = None
        self.connected = False
        self.disconnect_event_lock = threading.Lock()
        self.quit = False
        self.empty_ticker = {'high':0,'low':0,'average':0,'vwap':0,'volume':0,'last':0,'buy':0,'sell':0}

    def full_update(self):
        if time.time()-self.last_update < self.update_frequency: return
        self.__statusbar('running full update', 0)
        self.__message('running full update')
        if self.account.logged_in:
            self.__statusbar('running full update (account)',0)
            try: self.account.update()
            except AccountError as e: self.__message('account update failed: %s' % e)
            else: self.events += Event(ACCOUNT_UPDATED)
        else:
            self.__message('Account not logged in, log in with /login (password)')
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

    def update(self, account, ticker, depth, trades):
        if account and self.account.logged_in:
            self.__statusbar('updating account',0)
            self.__message('updating account')
            try: self.account.update()
            except AccountError as e: self.__message('account update failed: %s' % e)
            else: self.events += Event(ACCOUNT_UPDATED)
        elif not self.account.logged_in:
            self.__message('Account not logged in, log in with /login (password)')
        if ticker:
            self.__statusbar('updating ticker',0)
            self.__message('updating ticker')
            self.ticker.update()
            self.events += Event(TICKER_UPDATE, change=self.empty_ticker)
        if depth:
            self.__statusbar('updating depth',0)
            self.__message('updating depth')
            self.depth.update()
            self.events += Event(RESET_DEPTH)
        if trades:
            self.__statusbar('updating trades',0)
            self.__message('updating trades')
            self.trades.update()
            self.events += Event(TRADE_RESET)
        self.__statusbar()

    def __gui_thread(self):
        app = QtGui.QApplication(sys.argv)
        self.gui_window = Window(self.events,self.caller,self.account,self.commands,self.ticker,self.depth,self.trades)
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
        self.gui_window.emit(QtCore.SIGNAL('setPreferences'),self.update_frequency)
        self.__message('type /help for a list of possible commands')
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
                    self.connected = True
                    self.__message('websocket connected')
                elif event.type == WEBSOCKET_DISCONNECTED:
                    with self.disconnect_event_lock:
                        if event.reconnect and self.connected:
                            self.__message('websocket disconnected, reconnecting')
                            self.updater.connect()
                        else:
                            self.__message('websocket disconnected')
                        self.connected = False
                elif event.type == UPDATE_THREAD_STARTED:
                    self.__message('update thread started')
                elif event.type == ACCOUNT_UPDATED:
                    self.gui_window.emit(QtCore.SIGNAL('setOrderList'))
                elif event.type == CHANNEL_SUBSCRIBED:
                    self.__message('subscribed to \'%s\' channel' % CHANNELS[event.channel])
                elif event.type == REMARK_MESSAGE:
                    self.__message('Remark: %s' % event.message)
                elif event.type == TICKER_UPDATE:
                    self.gui_window.emit(QtCore.SIGNAL('setTicker'),event.change)
                    self.gui_window.emit(QtCore.SIGNAL('setOrderPrice'))
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
                    self.gui_window.emit(QtCore.SIGNAL('setPreferences'),self.update_frequency)
                elif event.type == PARTIAL_UPDATE_REQUESTED:
                    self.update(**event.update)
                elif event.type == CONNECT_REQUESTED:
                    if not self.connected:
                        self.__statusbar('connecting',0)
                        self.__message('connecting')
                        if event.use == 'socketio': self.updater.use_socketio = True
                        elif event.use == 'websocket': self.updater.use_socketio = False
                        else: self.__message('unexpected protocol, using default')
                        self.updater.connect()
                        self.__statusbar()
                    else: pass
                elif event.type == DISCONNECT_REQUESTED:
                    if self.connected:
                        self.__message('disconnecting')
                        self.updater.disconnect(False)
                    else: pass
                elif event.type == RECONNECT_REQUESTED:
                    if self.connected:
                        self.__message('disconnecting')
                        self.updater.disconnect(False)
                        self.__statusbar('reconnecting',0)
                        self.__message('connecting')
                        if event.use == 'socketio': self.updater.use_socketio = True
                        elif event.use == 'websocket': self.updater.use_socketio = False
                        else: self.__message('unexpected protocol, using default')
                        self.updater.connect()
                        self.__statusbar()
                    else: pass
                elif event.type == API_KEY_UNLOCKED:
                    self.account.update_login_info(event.key,event.secret)
                    self.__message('updating account')
                    self.__statusbar('updating account',0)
                    try: self.account.update()
                    except AccountError as e: self.__message('account update failed: %s' % e)
                    else: self.events += Event(ACCOUNT_UPDATED)
                    self.__statusbar()
                elif event.type == ORDER_PLACED:
                    self.__message('updating account')
                    self.__statusbar('updating account',0)
                    try: self.account.update()
                    except AccountError as e: self.__message('account update failed: %s' % e)
                    else: self.events += Event(ACCOUNT_UPDATED)
                    self.__statusbar()
                elif event.type == TRADE_PERFORMED:
                    self.__message('Trade performed: %s %s at %s %s' % (event.order.amount,event.order.item,
                                                                        event.order.price,event.order.currency))
                elif event.type == ACCOUNT_UPDATE_REQUESTED:
                    if event.full:
                        self.__message('updating account')
                        self.__statusbar('updating account',0)
                        try: self.account.update()
                        except AccountError as e: self.__message('account update failed: %s' % e)
                        else: self.events += Event(ACCOUNT_UPDATED)
                        self.__statusbar()
                    else:
                        if event.funds:
                            self.__message('updating account funds')
                            self.__statusbar('updating account funds')
                            try: self.account.update_funds()
                            except AccountError as e: self.__message('account update failed: %s' % e)
                            else: self.events += Event(ACCOUNT_UPDATED)
                            self.__statusbar()
                        if event.orders:
                            self.__message('updating account orders')
                            self.__statusbar('updating account orders')
                            try: self.account.update_funds()
                            except AccountError as e: self.__message('account update failed: %s' % e)
                            else: self.events += Event(ACCOUNT_UPDATED)
                            self.__statusbar()
                        if event.history:
                            self.__message('updating account history')
                            self.__statusbar('updating account history')
                            try: self.account.update_funds()
                            except AccountError as e: self.__message('account update failed: %s' % e)
                            else: self.events += Event(ACCOUNT_UPDATED)
                            self.__statusbar()

            self.full_update()
            if self.last_ticker_color_change is not None:
                if time.time() - self.ticker_color_seconds >= self.last_ticker_color_change:
                    self.gui_window.emit(QtCore.SIGNAL('resetTickerColor'))
                    self.last_ticker_color_change = None
