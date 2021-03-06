#!/usr/bin/env python3
from imports import *
from events import *

class AccountError(Exception): pass

class Wallet(object):
    def __init__(self, currency, Balance,
                 Daily_Withdraw_Limit,
                 Max_Withdraw,
                 Monthly_Withdraw_Limit,
                 Operations):
        self.currency = currency
        self.balance = int(Balance['value_int'])/FACTORS[currency]
        self.daily_withdraw = int(Daily_Withdraw_Limit['value_int'])/FACTORS[currency]
        self.max_withdraw = int(Max_Withdraw['value_int'])/FACTORS[currency]
        if Monthly_Withdraw_Limit: self.monthly_withdraw = int(Monthly_Withdraw_Limit['value_int'])/FACTORS[currency]
        else: self.monthly_withdraw = None
        self.operations = Operations

    def __str__(self):
        return '%s %s' % (self.balance,self.currency)

    def __repr__(self):
        return self.__str__()

class HistoryItem(object):
    def __init__(self, index, date, type, info, value, balance):
        self.index = int(index)
        self.date = time.mktime(time.strptime(date, '"%Y-%m-%d %H:%M:%S"'))
        self.type = type
        self.info = info.strip('"')
        self.value = float(value)
        self.balance = float(balance)

    def __eq__(self, y):
        assert(isinstance(y,HistoryItem))
        return self.id == y.id

    def __gt__(self, y):
        assert(isinstance(y,HistoryItem))
        return self.index > y.index

    def __lt__(self, y):
        assert(isinstance(y,HistoryItem))
        return self.index < y.index

    def __ge__(self, y):
        assert(isinstance(y,HistoryItem))
        return self > y or self == y

    def __le__(self, y):
        assert(isinstance(y,HistoryItem))
        return self < y or self == y

    def __str__(self):
        return self.info

    def __repr__(self):
        return str(self)

class Order(object):
    def __init__(self, status, priority, price_int, item,
                 oid, real_status, dark, currency, amount_int,
                 date, type, **kwargs):
        self.item = item
        self.currency = currency
        self.status = status-1
        self.id = oid
        self.priority = int(priority)
        self.price = int(price_int)/FACTORS[currency]
        self.amount = int(amount_int)/FACTORS[item]
        self.dark = bool(dark)
        self.date = date,
        self.type = type

    def __str__(self):
        return 'order %s: %s %s at %s %s' % (self.id,self.amount,self.item,self.price,self.currency)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, y):
        if not(isinstance(y,Order)): return False
        if y.id == self.id: return True
        else: return False

class Account(object):
    def __init__(self, events, key, secret):
        if key: self.__key = key
        if secret: self.__secret = base64.b64decode(secret.encode())
        self.events = events
        self.login = None
        self.created = None
        self.index = None
        self.last_login = None
        self.language = None
        self.rights = None
        self.trade_fee = None
        self.orders = None
        self.wallets = None
        self.history_usd = None
        self.history_btc = None
        if key and secret: self.logged_in = True
        else: self.logged_in = False

    def __get_nonce(self):
        return int(time.time() * 1E5)

    def __sign_data(self, data):
        hmac_data = hmac.new(self.__secret, data.encode(), hashlib.sha512).digest()
        return base64.b64encode(hmac_data)

    def __build_query(self, req):
        req['nonce'] = self.__get_nonce()
        post_data = urlencode(req)
        headers = {'User-Agent' : 'python-urlopen',
                   'Rest-Key' : self.__key,
                   'Rest-Sign' : self.__sign_data(post_data)
        }
        return post_data, headers

    def update_login_info(self, key, secret):
        self.__key = key
        self.__secret = base64.b64decode(secret.encode())
        self.logged_in = True

    def logout(self):
        self.__key = None
        self.__secret = None
        self.login = None
        self.created = None
        self.index = None
        self.last_login = None
        self.language = None
        self.rights = None
        self.trade_fee = None
        self.orders = None
        self.wallets = None
        self.history_btc = None
        self.history_usd = None
        self.logged_in = False

    def perform(self, name, use_json=True, **args):
        if not self.logged_in:
            raise AccountError('not logged in')
        url = ACCOUNT_URLS[name]
        if name in POST_DATA:
            for arg in POST_DATA[name]:
                if arg not in args:
                    if name+'_optional' in POST_DATA:
                        if arg not in POST_DATA[name+'_optional']:
                            raise NameError('required argument missing: %s' % arg)
        data, headers = self.__build_query(args)
        req = Request(API_0_URL+url, data, headers)
        res = urlopen(req, data.encode())
        if use_json: jdata = json.loads(res.read().decode())
        else: jdata = res.read().decode()
        return jdata

    def __convert_time(self, string):
        return time.mktime(time.strptime(string, DATE_FORMAT))

    def update_funds(self):
        funds = self.perform('funds')
        if 'error' in funds:
            raise AccountError(funds['error'])
        for wallet in funds:
            self.wallets[wallet[:3].upper()].balance = float(funds[wallet])

    def update_orders(self):
        orders = self.perform('orders')
        if 'error' in orders:
            raise AccountError(orders['error'])
        if self.orders: old_orders = list(self.orders)
        else: old_orders = []
        self.orders = [Order(**order) for order in orders['orders']]
        for order in old_orders:
            if order not in self.orders:
                self.events += Event(TRADE_PERFORMED,order=order)
        for item in orders:
            if item[:4] != 'new_' and item != 'orders':
                self.wallets[item[:3].upper()].balance = float(orders[item])

    def update_history(self):
        btc_ret = self.perform('history_btc',False)
        usd_ret = self.perform('history_usd',False)
        try:
            btc_jdata = json.loads(btc_ret)
            if 'error' in btc_jdata: raise AccountError(btc_jdata['error'])
        except ValueError: pass
        try:
            usd_jdata = json.loads(usd_ret)
            if 'error' in usd_jdata: raise AccountError(usd_jdata['error'])
        except ValueError: pass
        history_btc = [x.split(',') for x in btc_ret.split('\n')]
        history_usd = [x.split(',') for x in usd_ret.split('\n')]
        self.history_btc, self.history_usd = [[],[]]
        for i, row in enumerate(history_btc):
            if i: self.history_btc.append(HistoryItem(*row))
        for i, row in enumerate(history_usd):
            if i: self.history_usd.append(HistoryItem(*row))
        self.history_btc.sort(); self.history_usd.sort()

    def sell(self, amount, price=None, currency='USD'):
        if price is None:
            out = self.perform('sell', amount=amount, Currency=currency)
        else:
            out = self.perform('sell', amount=amount, price=price, Currency=currency)
        if 'error' in out:
            return False, None, None
        if self.orders: old_orders = list(self.orders)
        else: old_orders = []
        self.orders = [Order(**order) for order in out['orders']]
        for order in old_orders:
            if order not in self.orders:
                self.events += Event(TRADE_PERFORMED,order=order)
        self.events += Event(ORDER_PLACED,status=out['status'],oid=out['oid'])
        return True,out['status'],out['oid']

    def buy(self, amount, price=None, currency='USD'):
        if price is None:
            out = self.perform('buy', amount=amount, Currency=currency)
        else:
            out = self.perform('buy', amount=amount, price=price, Currency=currency)
        if 'error' in out:
            return False, None, None
        if self.orders: old_orders = list(self.orders)
        else: old_orders = []
        self.orders = [Order(**order) for order in out['orders']]
        for order in old_orders:
            if order not in self.orders:
                self.events += Event(TRADE_PERFORMED,order=order)
        self.events += Event(ORDER_PLACED,status=out['status'],oid=out['oid'])
        return True,out['status'],out['oid']

    def cancel(self, order):
        self.perform('cancel', oid=order.id, type=order.type)
        self.orders.remove(order)

    def update(self):
        if not self.logged_in: return
        info = self.perform('info')
        orders = self.perform('orders')
        history_btc = [x.split(',') for x in self.perform('history_btc', False).split('\n') if len(x)>1]
        history_usd = [x.split(',') for x in self.perform('history_usd', False).split('\n') if len(x)>1]
        if 'error' in info:
            raise AccountError(info['error'])
        if 'error' in orders:
            raise AccountError(orders['error'])
        self.login = info['Login']
        self.created = self.__convert_time(info['Created'])
        self.index = info['Index']
        self.last_login = self.__convert_time(info['Last_Login'])
        self.language = info['Language']
        self.rights = info['Rights']
        self.trade_fee = info['Trade_Fee']
        self.wallets = {}
        for wallet in info['Wallets']:
            self.wallets[wallet] = Wallet(wallet, **info['Wallets'][wallet])
        if self.orders: old_orders = list(self.orders)
        else: old_orders = []
        self.orders = [Order(**order) for order in orders['orders']]
        for order in old_orders:
            if order not in self.orders:
                self.events += Event(TRADE_PERFORMED,order=order)
        self.history_btc, self.history_usd = [[],[]]
        for i, row in enumerate(history_btc):
            if i: self.history_btc.append(HistoryItem(*row))
        for i, row in enumerate(history_usd):
            if i: self.history_usd.append(HistoryItem(*row))
        self.history_btc.sort(); self.history_usd.sort()
