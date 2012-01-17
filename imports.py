#!/usr/bin/env python3
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import hashlib, hmac, base64, json
import time, queue, threading, sys

API_0_URL = 'https://mtgox.com/api/0/'
API_1_URL = 'https://mtgox.com/api/1/'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
SOCKETIO_URL = 'socketio.mtgox.com/socket.io'
SOCKETIO_PATH = '/mtgox'
WEBSOCKET_URL = 'ws://websocket.mtgox.com/mtgox'

CHANNELS = {
    'dbf1dee9-4f2e-4a08-8cb7-748919a71b21': 'trades',
    'd5f06780-30a8-4a48-a2f8-7ed181b4a13f': 'ticker',
    '24e67e0d-1cad-4cc0-9e7a-f8523ef460fe': 'depth'
}

COMMANDS = [
    'comment',
    'quit',
    'update',
    'account',
    'help',
]

COMMAND_HELP = {
    'comment':{'':['','Useful for when your comment starts with a command.']},
    'quit':{'':['','Quit this application']},
    'update':{'':['','Runs full update'],
              'frequency':[' (seconds)','Sets update frequency']},
    'account':{'info':['','Returns account information']},
    'help':{'':['','Prints useful help information'],
            'command':[' [args]','Prints help about command']}
}

WEBSOCKET_CONNECTED = 0
UPDATE_THREAD_STARTED = 1
CHANNEL_SUBSCRIBED = 2
TICKER_UPDATE = 3
TRADE_UPDATE = 4
DEPTH_UPDATE = 5
ACCOUNT_UPDATED = 6
WEBSOCKET_DISCONNECTED = 7
QUIT_ORDERED = 8
GUI_STARTED = 9
TRADE_RESET = 10
FULL_UPDATE_REQUESTED = 11
RESET_DEPTH = 12
UPDATE_FREQUENCY_CHANGE = 13

BTC_FACTOR = 1E8
USD_FACTOR = 1E5
JPY_FACTOR = 1E3

FACTORS = {
    'BTC': BTC_FACTOR,
    'USD': USD_FACTOR,
    'JPY': JPY_FACTOR,
    'AUD': USD_FACTOR,
    'CAD': USD_FACTOR,
    'CHF': USD_FACTOR,
    'CNY': USD_FACTOR,
    'DKK': USD_FACTOR,
    'EUR': USD_FACTOR,
    'GBP': USD_FACTOR,
    'HKD': USD_FACTOR,
    'NZD': USD_FACTOR,
    'PLN': USD_FACTOR,
    'RUB': USD_FACTOR,
    'SEK': USD_FACTOR,
    'SGD': USD_FACTOR,
    'THB': USD_FACTOR,
    
}

URLS = {
    'ticker': 'BTCUSD/public/ticker?raw',
    'depth': 'BTCUSD/public/fulldepth?raw',
    'trades': 'BTCUSD/public/trades?raw'
}

ACCOUNT_URLS = {
    'info': 'info.php',
    'funds':'getFunds.php',
    'buy': 'buyBTC.php',
    'sell': 'sellBTC.php',
    'orders': 'getOrders.php',
    'cancel': 'cancelOrder.php',
    'redeem': 'redeemCode.php',
    'withdraw': 'withdraw.php',
    'btc_address': 'btcAddress.php',
    'history_usd': 'history_USD.csv',
    'history_btc': 'history_BTC.csv'}

POST_DATA = {
    'buy': ['amount','price','Currency'],
    'buy_optional': {'price':'a market order'},
    'sell': ['amount', 'price', 'Currency'],
    'sell_optional': {'price':'a market order'},
     'cancel': ['oid','type'],
    'redeem': ['code'],
    'withdraw': ['group1','btca','amount'],
    'btc_address': ['description'],
    'btc_address_optional': {'description':'description-less activity'}
    }
