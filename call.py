#!/usr/bin/env python3
from imports import *

class Caller(object):
    def __init__(self, events, account, ticker, depth, trades):
        self.events = events
        self.account = account
        self.ticker = ticker
        self.depth = depth
        self.trades = trades

    def make_call(self):
        if self.ticker['last'] > self.ticker['vwap']:
            if (self.ticker['last']/self.ticker['vwap'])-1 > 1: return 1
            else: return (self.ticker['last']/self.ticker['vwap'])-1
        elif self.ticker['last'] < self.ticker['vwap']:
            if (self.ticker['vwap']/self.ticker['last'])-1 > 1: return -1
            else: return -((self.ticker['last']/self.ticker['vwap'])-1)
        else: return 0
