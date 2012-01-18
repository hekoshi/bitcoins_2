#!/usr/bin/env python3
from imports import *

class Depth(object):
    def __init__(self):
        self.add_lock = threading.Lock()
        self.asks = {}
        self.bids = {}

    def __add__(self, x):
        with self.add_lock:
            if x['type_str'] == 'ask':
                price = int(x['price_int'])/FACTORS[x['currency']]
                if price not in self.asks: self.asks[price] = 0
                volume = int(x['volume_int'])/FACTORS[x['item']]
                self.asks[price] += volume
                if self.asks[price] <= 0: del self.asks[price]
            if x['type_str'] == 'bid':
                price = int(x['price_int'])/FACTORS[x['currency']]
                if price not in self.bids: self.bids[price] = 0
                volume = int(x['volume_int'])/FACTORS[x['item']]
                self.bids[price] += volume
                if self.bids[price] <= 0: del self.bids[price]
            return self

    def __getitem__(self, name):
        if name == 'asks': return self.asks
        elif name == 'bids': return self.bids
        else: raise NameError('name not found')

    def update(self):
        with self.add_lock:
            req = urlopen(API_1_URL+URLS['depth'])
            data = json.loads(req.read().decode())
            self.asks = {}
            self.bids = {}
            for item in data['asks']:
                price = int(item['price_int'])/FACTORS['USD']
                amount = int(item['amount_int'])/FACTORS['BTC']
                self.asks[price] = amount
            for item in data['bids']:
                price = int(item['price_int'])/FACTORS['USD']
                amount = int(item['amount_int'])/FACTORS['BTC']
                self.bids[price] = amount
