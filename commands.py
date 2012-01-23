#!/usr/bin/env python3
from imports import *
from events import *
from gui import *

class Commands(object):
    def __init__(self, events, caller, account, ticker, trades,  depth, commands=COMMANDS):
        self.events = events
        self.account = account
        self.window = None
        self.ticker = ticker
        self.trades = trades
        self.depth = depth
        self.commands = commands
        self.caller = caller

    def set_window(self, window):
        self.window = window

    def message(self, text):
        self.window.emit(QtCore.SIGNAL('addMessage'),text)

    def command(self, name, args):
        if not self.window: return
        if name in self.commands:
            return self.__getattribute__(name+'_command')(args)
        else:
            self.message('Error: command not found')

    def comment_command(self, args):
        self.window.emit(QtCore.SIGNAL('addMessage'), 'Comment: %s' % ' '.join(args))

    def quit_command(self, args):
        self.window.close()

    def clear_command(self, args):
        self.window.emit(QtCore.SIGNAL('clearMessages'))

    def connect_command(self, args):
        if len(args):
            use = args[0]
        elif USE_SOCKETIO:
            use = 'socketio'
        else:
            use = 'websocket'
        self.events += Event(CONNECT_REQUESTED, use=use)

    def disconnect_command(self, args):
        self.events += Event(DISCONNECT_REQUESTED)

    def reconnect_command(self, args):
        if len(args):
            use = args[0]
        elif USE_SOCKETIO:
            use = 'socketio'
        else:
            use = 'websocket'
        self.events += Event(RECONNECT_REQUESTED, use=use)

    def login_command(self, args):
        if not len(args):
            self.message('/login: no password provided')
            return
        if not os.path.exists(LOGIN_INFO_FILE):
            self.message('/login: no login information')
            return
        key = ' '.join(args)
        in_data = open(LOGIN_INFO_FILE,'rb').read().decode()
        output = encrypt.decodes(key,in_data)
        try:
            data = json.loads(output)
        except ValueError:
            self.message('/login: incorrect password or corrupt file')
        else:
            if 'key' not in data or 'secret' not in data:
                self.message('/login: incorrect file')
                return
            self.message('/login: account key unlocked')
            self.events += Event(API_KEY_UNLOCKED, key=data['key'], secret=data['secret'])

    def logout_command(self, args):
        self.message('/logout: logging out')
        self.account.logout()

    def trade_command(self, args):
        if not self.account.logged_in:
            self.message('/trade: account not logged in')
            return
        if len(args):
            if args[0] == 'cancel':
                if len(args) < 2:
                    self.message('/trade: incorrect arguments')
                    return
                orders = [int(x) for x in args[1:]]
                for order in orders:
                    if order >= len(self.account.orders):
                        self.message('/trade: incorrect order number')
                    else:
                        self.message('/trade: canceling order %s' % self.account.orders[order])
                        self.account.cancel(self.account.orders[order])
                return
        if len(args) < 2 or len(args) > 3:
            self.message('/trade: incorrect arguments')
            return
        trade_type = args[0]
        if trade_type  not in ('buy', 'sell'):
            self.message('/trade: incorrect trade type')
            return
        amount = args[1]
        if len(args) > 2: price = args[2]
        else:
            self.message('/trade: doing market order')
            price = None
        self.message('/trade: placing order')
        if trade_type == 'sell':
            success, status, oid = self.account.sell(amount,price)
        elif trade_type == 'buy':
            success, status, oid = self.account.buy(amount,price)
        if success:
            self.message('/trade: order placed')
            self.events += Event(ORDER_PLACED, oid=oid)
        else:
            self.message('/trade: order failed')

    def help_command(self, args):
        if not args:
            for command in COMMAND_HELP:
                for arg in COMMAND_HELP[command]:
                    if not arg:
                        self.message('/%s%s: %s' % (command,
                            (' '*int(bool(COMMAND_HELP[command][arg][0])))+COMMAND_HELP[command][arg][0],
                            COMMAND_HELP[command][arg][1]))
                    else:
                        self.message('/%s %s%s: %s' % (command, arg,
                            (' '*int(bool(COMMAND_HELP[command][arg][0])))+COMMAND_HELP[command][arg][0],
                            COMMAND_HELP[command][arg][1]))
        if args:
            name = args[0]
            string = ' '.join(args[1:])
            if name not in COMMAND_HELP: self.message('/help: command not found'); return
            if string not in COMMAND_HELP[name] and string != '': self.message('/help: command not found'); return
            if not string:
                for arg in COMMAND_HELP[name]:
                    if not arg:
                        self.message('/%s%s: %s' % (name,
                            (' '*int(bool(COMMAND_HELP[name][arg][0])))+COMMAND_HELP[name][arg][0],
                            COMMAND_HELP[name][arg][1]))
                    else:
                        self.message('/%s %s%s: %s' % (name, arg,
                            (' '*int(bool(COMMAND_HELP[name][arg][0])))+COMMAND_HELP[name][arg][0],
                            COMMAND_HELP[name][arg][1]))
            else: self.message('/%s %s%s: %s' % (name, string,
                      (' '*int(bool(COMMAND_HELP[name][arg][0])))+COMMAND_HELP[name][string][0],
                      COMMAND_HELP[name][string][1]))

    def update_command(self, args):
        if len(args) == 0: self.events += Event(FULL_UPDATE_REQUESTED)
        elif args[0] == 'frequency':
            try: frequency = int(args[1])
            except ValueError: return -1
            if frequency < 1: self.message('/update: Update frequency must be at least 1'); return
            self.events += Event(UPDATE_FREQUENCY_CHANGE, frequency=frequency)
            self.message('/update: Update frequency set to %s seconds' % frequency)
        else:
            updates = {}
            if 'account' in args:
                updates['account'] = True
            else: updates['account'] = False
            if 'ticker' in args:
                updates['ticker'] = True
            else: updates['ticker'] = False
            if 'depth' in args:
                updates['depth'] = True
            else: updates['depth'] = False
            if 'trades' in args:
                updates['trades'] = True
            else: updates['trades'] = False
            self.events += Event(PARTIAL_UPDATE_REQUESTED, update=updates)

    def account_command(self, args):
        if not self.account.logged_in:
            self.message('/account: not logged in')
        elif args[0] == 'info':
            messages = []
            messages.append('Login Name: %s' % self.account.login)
            messages.append('Login Created: %s' % time.asctime(time.gmtime(self.account.created)))
            messages.append('Last Login: %s' % time.asctime(time.gmtime(self.account.last_login)))
            messages.append('Language: %s' % self.account.language)
            messages.append('API Rights: %s' % ', '.join(self.account.rights))
            messages.append('Trade Free: %s%%' % self.account.trade_fee)
            messages.append('Open Orders: %s' % len(self.account.orders))
            messages.append('Funds: %s' % ' '.join([' '.join([str(self.account.wallets[x].balance), x]) for x in self.account.wallets]))
            for message in messages:
                self.message(message)
        elif args[0] == 'orders':
            if not self.account.orders:
                self.message('/account: no orders known')
                return
            for order in self.account.orders:
                self.message(str(order))
        elif args[0] == 'history':
            usd_history, btc_history = (True,True)
            if len(args) > 1:
                usd_history, btc_history = (False, False)
                if args[1].lower() == 'usd': usd_history = True
                elif args[1].lower() == 'btc': btc_history = True
                else: self.message('/account: incorrect history currency'); return
            if len(args) > 2:
                if args[2].lower() == 'usd': usd_history = True
                elif args[2].lower() == 'btc': btc_history = True
                else: self.message('/account: incorrect history currency'); return
            if btc_history:
                self.message('BTC History:')
                for item in self.account.history_btc:
                    self.message(str(item))
            if usd_history:
                self.message('USD History:')
                for item in self.account.history_usd:
                    self.message(str(item))
        elif args[0] == 'funds':
            self.message('Account Funds: %s' % ' '.join([' '.join([str(self.account.wallets[x].balance), x]) for x in self.account.wallets]))
        elif args[0] == 'update':
            full,funds,orders,history = (True,False,False,False)
            if len(args) > 1:
                full = False
                if args[1] == 'funds': funds = True
                elif args[1] == 'orders': orders = True
                elif args[1] == 'history': history = True
                else: self.message('/account: incorrect update name'); return
            if len(args) > 2:
                if args[2] == 'funds': funds = True
                elif args[2] == 'orders': orders = True
                elif args[2] == 'history': history = True
                else: self.message('/account: incorrect update name'); return
            if len(args) > 3:
                if args[3] == 'funds': funds = True
                elif args[3] == 'orders': orders = True
                elif args[3] == 'history': history = True
                else: self.message('/account: incorrect update name'); return
            if funds and orders and history:
                full,funds,orders,history = (True,False,False,False)
            self.events += Event(ACCOUNT_UPDATE_REQUESTED, full=full, funds=funds, orders=orders, history=history)

    def save_command(self, args):
        if not args: self.message('/save: no file specified'); return
        overwrite = False
        tstamp = False
        tstampfname = False
        if '-overwrite' in args:
            overwrite = True
            args.remove('-overwrite')
        if '-tstamp' in args:
            tstamp = True
            args.remove('-tstamp')
            self.message('/save: adding timestamp to file')
        if '-tstampfname' in args:
            tstampfname = True
            args.remove('-tstampfname')
            self.message('/save: adding timestamp to filename')
        path = args[0]
        head, tail = os.path.split(path)
        root, ext = os.path.splitext(tail)
        if tstampfname:
            root += (' %s' % time.strftime('%x')).replace(os.sep,'.')
        if head: path = head+os.sep+root+ext
        else: path = head+root+ext
        if os.path.exists(path) and not overwrite:
            self.message('/save: file already exists, use -overwrite to overwrite')
            return
        elif overwrite:
            self.message('/save: overwriting file \'%s\'' % path)
        else:
            self.message('/save: writing to file \'%s\'' % path)
        logfile = open(path,'w')
        if tstamp:
            logfile.write(time.asctime(time.localtime())+'\n\n')
        for line in self.window.messages:
            logfile.write(line+'\n')
        logfile.close()
        self.message('/save: wrote file')

    def call_command(self, args):
        call = self.caller.make_call()
        if call > 0:
            self.message('/call: current call is buy')
        elif call < 0:
            self.message('/call: current call is sell')
        else:
            self.message('/call: current call is mixed')
