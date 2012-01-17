#!/usr/bin/env python3
from imports import *
from events import *
from gui import *

class Commands(object):
    def __init__(self, events, account, ticker, trades,  depth, commands=COMMANDS):
        self.events = events
        self.account = account
        self.window = None
        self.ticker = ticker
        self.trades = trades
        self.depth = depth
        self.commands = commands

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

    def help_command(self, args):
        if not args:
            for command in COMMAND_HELP:
                for arg in COMMAND_HELP[command]:
                    if not arg:
                        self.message('/%s%s: %s' % (command, COMMAND_HELP[command][arg][0], COMMAND_HELP[command][arg][1]))
                    else:
                        self.message('/%s %s%s: %s' % (command, arg, COMMAND_HELP[command][arg][0], COMMAND_HELP[command][arg][1]))
        if args:
            name = args[0]
            string = ' '.join(args[1:])
            if name not in COMMAND_HELP: self.message('/help: command not found'); return
            if string not in COMMAND_HELP[name] and string != '': self.message('/help: command not found'); return
            if not string:
                for arg in COMMAND_HELP[name]:
                    if not arg:
                        self.message('/%s%s: %s' % (name, COMMAND_HELP[name][arg][0], COMMAND_HELP[name][arg][1]))
                    else:
                        self.message('/%s %s%s: %s' % (name, arg, COMMAND_HELP[name][arg][0], COMMAND_HELP[name][arg][1]))
            else: self.message('/%s %s%s: %s' % (name, string, COMMAND_HELP[name][string][0], COMMAND_HELP[name][string][1]))

    def update_command(self, args):
        if len(args) == 0: self.events += Event(FULL_UPDATE_REQUESTED)
        elif args[0] == 'frequency':
            try: frequency = int(args[1])
            except ValueError: return -1
            if frequency < 1: return -1
            self.events += Event(UPDATE_FREQUENCY_CHANGE, frequency=frequency)
            self.message('Update frequency set to %s seconds' % frequency)

    def account_command(self, args):
        if args[0] == 'info':
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
