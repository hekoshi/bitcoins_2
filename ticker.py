#!/usr/bin/env python3
from imports import *

class Ticker(object):
    ITEMS = {'high':'high','low':'low',
             'avg':'average','vwap':'vwap',
             'vol':'volume','last':'last',
             'buy':'buy','sell':'sell'}

    def __init__(self):
        self.high = None
        self.low = None
        self.average = None
        self.vwap = None
        self.volume = None
        self.last = None
        self.buy = None
        self.sell = None

    def __getitem__(self, name):
        if name in self.ITEMS:
            return self.__getattribute__(self.ITEMS[name])
        else: return ValueError('name not found')

    def __setitem__(self, name, value):
        if name in self.ITEMS:
            self.__setattr__(self.ITEMS[name], value)
        else: return ValueError('name not found')

    def update(self, data=None):
        if data is None:
            req = urlopen(API_1_URL+URLS['ticker'])
            data = json.loads(req.read().decode())
        change = {}; total_change = False
        for item in data:
            if item in self.ITEMS:
                new = int(data[item]['value_int'])/FACTORS[data[item]['currency']]
                if self[item] != new and self[item] is not None:
                    change[self.ITEMS[item]] = self[item]-new
                    total_change = True
                else: change[self.ITEMS[item]] = 0
                self[item] = new
        return change, total_change
