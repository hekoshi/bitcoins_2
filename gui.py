#!/usr/bin/env python3
from PyQt4 import QtCore, QtGui
from main_window_ui import *
from imports import *
from events import *
import sys

import save_log_ui, info_ui, login_ui
import api_key_ui, preferences_ui
import order_ui, cancel_order_ui

class CancelOrderDialog(QtGui.QDialog):
    def __init__(self, account, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = cancel_order_ui.Ui_Dialog()
        self.ui.setupUi(self)
        self.account = account

    def update_orders(self):
        self.ui.orderList.clear()
        if not self.account.logged_in: return
        if self.account.orders is None: return
        for order in self.account.orders:
            self.ui.orderList.addItem(str(order))

class OrderDialog(QtGui.QDialog):
    def __init__(self, ticker, caller, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = order_ui.Ui_Dialog()
        self.ui.setupUi(self)
        self.ticker = ticker
        self.caller = caller
        self.primary = 'amount'
        self.ignore_total_change = 0
        self.ignore_amount_change = 0
        self.ui.marketOrderBox.setChecked(True)
        self.connect(self.ui.orderGroup, QtCore.SIGNAL('buttonClicked(int)'), self.update_price_box)
        self.connect(self.ui.marketOrderBox, QtCore.SIGNAL('clicked()'), self.update_price_box)
        self.connect(self.ui.totalSpinBox, QtCore.SIGNAL('valueChanged(double)'), self.total_change)
        self.connect(self.ui.amountSpinBox, QtCore.SIGNAL('valueChanged(double)'), self.amount_change)
        self.connect(self.ui.priceSpinBox, QtCore.SIGNAL('valueChanged(double)'), self.price_change)

    def total_change(self):
        if self.ignore_total_change:
            self.ignore_total_change -= 1
            return
        self.primary = 'total'
        self.ignore_amount_change += 1
        if self.ui.priceSpinBox.value():
            self.ui.amountSpinBox.setValue(self.ui.totalSpinBox.value()/self.ui.priceSpinBox.value())
        else:
            self.ui.amountSpinBox.setValue(0.0)

    def amount_change(self):
        if self.ignore_amount_change:
            self.ignore_amount_change -= 1
            return
        self.primary = 'amount'
        self.ignore_total_change += 1
        self.ui.totalSpinBox.setValue(self.ui.amountSpinBox.value()*self.ui.priceSpinBox.value())

    def price_change(self):
        if self.primary == 'total': self.total_change()
        elif self.primary == 'amount': self.amount_change()

    def update_price_box(self):
        if self.ui.marketOrderBox.isChecked():
            if self.ui.buyButton.isChecked():
                self.ui.priceSpinBox.setValue(self.ticker['sell'])
            elif self.ui.sellButton.isChecked():
                self.ui.priceSpinBox.setValue(self.ticker['buy'])
            else:
                self.ui.priceSpinBox.setValue(0.0)
        if self.caller.make_call()*1000 > 100:
            self.ui.callSlider.setValue(100.0)
        elif self.caller.make_call()*1000 < -100:
            self.ui.callSlider.setValue(-100.0)
        else:
            self.ui.callSlider.setValue(self.caller.make_call()*1000)

class PreferencesDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = preferences_ui.Ui_Dialog()
        self.ui.setupUi(self)
        self.update_seconds = self.ui.updateFrequency.value()
        self.connect(self, QtCore.SIGNAL('rejected()'), self.reset_values)
        self.connect(self, QtCore.SIGNAL('accepted()'), self.set_values)

    def reset_values(self):
        self.ui.updateFrequency.setValue(self.update_seconds)

    def set_values(self):
        self.update_seconds = self.ui.updateFrequency.value()

    def update_preferences(self, update_seconds):
        self.ui.updateFrequency.setValue(update_seconds)

class ApiKeyDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = api_key_ui.Ui_Dialog()
        self.ui.setupUi(self)
        self.connect(self, QtCore.SIGNAL('rejected()'), self.clear_everything)

    def clear_everything(self):
        self.ui.keyEdit.clear()
        self.ui.secretEdit.clear()
        self.ui.passwordEdit.clear()

class LoginDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = login_ui.Ui_Dialog()
        self.ui.setupUi(self)
        self.connect(self, QtCore.SIGNAL('rejected()'), self.clear_everything)

    def clear_everything(self):
        self.ui.passwordEdit.clear()

class SaveLog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = save_log_ui.Ui_Dialog()
        self.ui.setupUi(self)
        self.connect(self.ui.browseButton, QtCore.SIGNAL('clicked()'), self.file_browse)
        self.connect(self, QtCore.SIGNAL('rejected()'), self.clear_everything)

    def file_browse(self):
        filename = QtGui.QFileDialog.getSaveFileName(self, "Save Log", "./", "*.*")
        self.ui.fileEdit.setText(filename)

    def clear_everything(self):
        self.ui.fileEdit.clear()
        self.ui.overwrite.setChecked(False)
        self.ui.timeStamp.setChecked(False)
        self.ui.timeStampFileName.setChecked(False)

class InfoBox(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self,parent)
        self.ui = info_ui.Ui_Dialog()
        self.ui.setupUi(self)

    def change_message(self, message):
        self.ui.label.setText(message)

    def __call__(self, message):
        self.change_message(message)
        self.show()

class Window(QtGui.QMainWindow):
    def __init__(self, events, caller, account, commands, ticker, depth, trades, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.events = events
        self.commands = commands
        self.ticker = ticker
        self.depth = depth
        self.trades = trades
        self.caller = caller
        self.account = account
        self.last_depth_update = time.time()
        self.depth_interval = 1
        self.red_palette = QtGui.QPalette(self.palette())
        self.green_palette = QtGui.QPalette(self.palette())
        self.black_palette = QtGui.QPalette(self.palette())
        self.red_palette.setColor(self.red_palette.Text, QtGui.QColor(255,0,0))
        self.green_palette.setColor(self.green_palette.Text, QtGui.QColor(0,255,0))
        self.ui.commandEdit.setFocus()
        self.messages = []

        self.save_log_ui = SaveLog(self)
        self.connect(self.save_log_ui, QtCore.SIGNAL('accepted()'), self.save_log)
        self.info_box = InfoBox(self)
        self.login_dialog = LoginDialog(self)
        self.connect(self.login_dialog, QtCore.SIGNAL('accepted()'), self.login)
        self.api_key = ApiKeyDialog(self)
        self.connect(self.api_key, QtCore.SIGNAL('accepted()'), self.save_api_key)
        self.preferences_dialog = PreferencesDialog(self)
        self.connect(self.preferences_dialog, QtCore.SIGNAL('accepted()'), self.update_preferences)
        self.order_dialog = OrderDialog(self.ticker, self.caller, self)
        self.connect(self.order_dialog, QtCore.SIGNAL('accepted()'), self.place_order)
        self.cancel_order_dialog = CancelOrderDialog(self.account, self)
        self.connect(self.cancel_order_dialog, QtCore.SIGNAL('accepted()'), self.cancel_order)

        self.connect(self, QtCore.SIGNAL("setTicker"), self.setTickerText)
        self.connect(self, QtCore.SIGNAL('addTrade'), self.addTrade)
        self.connect(self, QtCore.SIGNAL('resetTrades'), self.resetTrades)
        self.connect(self, QtCore.SIGNAL('updateMessage'), self.updateMessage)
        self.connect(self, QtCore.SIGNAL('clearMessage'), self.clearMessage)
        self.connect(self, QtCore.SIGNAL('clearMessages'), self.clearMessages)
        self.connect(self, QtCore.SIGNAL('updateDepth'), self.updateDepth)
        self.connect(self, QtCore.SIGNAL('addMessage'), self.addMessage)
        self.connect(self, QtCore.SIGNAL('resetTickerColor'), self.resetTickerColor)
        self.connect(self, QtCore.SIGNAL('setPreferences'), self.set_preferences)
        self.connect(self, QtCore.SIGNAL('setOrderPrice'), self.set_order_price)
        self.connect(self, QtCore.SIGNAL('setOrderList'), self.set_order_list)

        self.connect(self.ui.commandEdit, QtCore.SIGNAL('returnPressed()'), self.commandAction)
        self.connect(self.ui.actionClear_Messages, QtCore.SIGNAL('triggered()'), self.clearMessages)
        self.connect(self.ui.actionSave_Log, QtCore.SIGNAL('triggered()'), self.save_log_ui.show)
        self.connect(self.ui.actionLogin, QtCore.SIGNAL('triggered()'), self.login_dialog.show)
        self.connect(self.ui.actionChange_API_Key, QtCore.SIGNAL('triggered()'), self.api_key.show)
        self.connect(self.ui.actionPreferences, QtCore.SIGNAL('triggered()'), self.preferences_dialog.show)
        self.connect(self.ui.actionUpdateAll, QtCore.SIGNAL('triggered()'), self.full_update)
        self.connect(self.ui.actionAccount, QtCore.SIGNAL('triggered()'), self.update_account)
        self.connect(self.ui.actionTicker, QtCore.SIGNAL('triggered()'), self.update_ticker)
        self.connect(self.ui.actionDepth, QtCore.SIGNAL('triggered()'), self.update_depth)
        self.connect(self.ui.actionTrades, QtCore.SIGNAL('triggered()'), self.update_trades)
        self.connect(self.ui.actionLogout, QtCore.SIGNAL('triggered()'), self.logout)
        self.connect(self.ui.actionPlace_Order, QtCore.SIGNAL('triggered()'), self.order_dialog.show)
        self.connect(self.ui.actionCall, QtCore.SIGNAL('triggered()'), self.call)
        self.connect(self.ui.actionAuto_Trade, QtCore.SIGNAL('triggered()'), self.auto_trade)
        self.connect(self.ui.actionCancel_Order, QtCore.SIGNAL('triggered()'), self.cancel_order_dialog.show)
        self.connect(self.ui.actionUpdate_AllAccount, QtCore.SIGNAL('triggered()'), self.update_all_account)
        self.connect(self.ui.actionUpdate_History, QtCore.SIGNAL('triggered()'), self.update_history_account)
        self.connect(self.ui.actionUpdate_Funds, QtCore.SIGNAL('triggered()'), self.update_funds_account)
        self.connect(self.ui.actionUpdate_Orders, QtCore.SIGNAL('triggered()'), self.update_orders_account)
        self.connect(self.ui.actionLogInfo, QtCore.SIGNAL('triggered()'), self.log_account_info)
        self.connect(self.ui.actionLogHistory, QtCore.SIGNAL('triggered()'), self.log_account_history)
        self.connect(self.ui.actionLogOrders, QtCore.SIGNAL('triggered()'), self.log_account_orders)
        self.connect(self.ui.actionLogFunds, QtCore.SIGNAL('triggered()'), self.log_account_funds)
        self.connect(self.ui.actionDisconnect, QtCore.SIGNAL('triggered()'), self.disconnect)
        self.connect(self.ui.actionConnectCurrent, QtCore.SIGNAL('triggered()'), self.connect_current)
        self.connect(self.ui.actionConnectWebSocket, QtCore.SIGNAL('triggered()'), self.connect_websocket)
        self.connect(self.ui.actionConnectSocket_IO, QtCore.SIGNAL('triggered()'), self.connect_socketio)
        self.connect(self.ui.actionReconnectCurrent, QtCore.SIGNAL('triggered()'), self.reconnect_current)
        self.connect(self.ui.actionReconnectWebSocket, QtCore.SIGNAL('triggered()'), self.reconnect_websocket)
        self.connect(self.ui.actionReconnectSocket_IO, QtCore.SIGNAL('triggered()'), self.reconnect_socketio)

    def reconnect_socketio(self):
        self.commands.reconnect_command(['socketio'])

    def reconnect_websocket(self):
        self.commands.reconnect_command(['websocket'])

    def reconnect_current(self):
        self.commands.reconnect_command([])

    def connect_socketio(self):
        self.commands.connect_command(['socketio'])

    def connect_websocket(self):
        self.commands.connect_command(['websocket'])

    def connect_current(self):
        self.commands.connect_command([])

    def disconnect(self):
        self.commands.disconnect_command([])

    def log_account_funds(self):
        self.commands.account_command(['funds'])

    def log_account_orders(self):
        self.commands.account_command(['orders'])

    def log_account_history(self):
        self.commands.account_command(['history'])

    def log_account_info(self):
        self.commands.account_command(['info'])

    def update_orders_account(self):
        self.commands.account_command(['update','orders'])

    def update_funds_account(self):
        self.commands.account_command(['update','funds'])

    def update_history_account(self):
        self.commands.account_command(['update','history'])

    def update_all_account(self):
        self.commands.account_command(['update'])

    def cancel_order(self):
        index = self.cancel_order_dialog.ui.orderList.currentRow()
        self.commands.trade_command(['cancel',str(index)])
        self.commands.account_command(['update','orders'])

    def set_order_list(self):
        self.cancel_order_dialog.update_orders()

    def set_order_price(self):
        self.order_dialog.update_price_box()

    def call(self):
        self.commands.call_command([])

    def auto_trade(self):
        # not implemented yet
        pass

    def place_order(self):
        if self.order_dialog.ui.marketOrderBox.isChecked():
            price = None
        else:
            price = self.order_dialog.ui.priceSpinBox.value()
        amount = self.order_dialog.ui.amountSpinBox.value()
        if self.order_dialog.ui.buyButton.isChecked():
            order_type = 'buy'
        elif self.order_dialog.ui.sellButton.isChecked():
            order_type = 'sell'
        else: return
        if price is not None:
            self.commands.trade_command([order_type,str(amount),str(price)])
        else:
            self.commands.trade_command([order_type,str(amount)])

    def update_account(self):
        self.events += Event(PARTIAL_UPDATE_REQUESTED, update={'account':True,'ticker':False,'depth':False,'trades':False})

    def update_ticker(self):
        self.events += Event(PARTIAL_UPDATE_REQUESTED, update={'account':False,'ticker':True,'depth':False,'trades':False})

    def update_depth(self):
        self.events += Event(PARTIAL_UPDATE_REQUESTED, update={'account':False,'ticker':False,'depth':True,'trades':False})

    def update_trades(self):
        self.events += Event(PARTIAL_UPDATE_REQUESTED, update={'account':False,'ticker':False,'depth':False,'trades':True})

    def set_preferences(self, update_frequency):
        self.preferences_dialog.update_preferences(update_frequency)

    def update_preferences(self):
        self.events += Event(UPDATE_FREQUENCY_CHANGE, frequency=self.preferences_dialog.ui.updateFrequency.value())
        self.addMessage('Set update frequency to %s' % self.preferences_dialog.ui.updateFrequency.value())

    def save_log(self):
        filename = self.save_log_ui.ui.fileEdit.text()
        overwrite = self.save_log_ui.ui.overwrite.isChecked()
        tstamp = self.save_log_ui.ui.timeStamp.isChecked()
        tstampfname = self.save_log_ui.ui.timeStampFileName.isChecked()
        args = [filename]
        if overwrite: args.append('-overwrite')
        if tstamp: args.append('-tstamp')
        if tstampfname: args.append('-tstampfname')
        self.commands.save_command(args)
        self.save_log_ui.clear_everything()

    def login(self):
        password = self.login_dialog.ui.passwordEdit.text()
        self.commands.login_command([password])
        self.login_dialog.clear_everything()

    def logout(self):
        self.commands.logout_command([])

    def save_api_key(self):
        key = self.api_key.ui.keyEdit.toPlainText()
        secret = self.api_key.ui.secretEdit.toPlainText()
        password = self.api_key.ui.passwordEdit.text()
        key_dict = {'key':key,'secret':secret}
        to_encode = json.dumps(key_dict)
        encoded = encrypt.encodes(password, to_encode).encode()
        open('login_info.enc','wb').write(encoded)
        self.addMessage('API Key updated')
        self.commands.login_command([password])
        self.api_key.clear_everything()

    def full_update(self):
        if self.events:
            self.events += Event(FULL_UPDATE_REQUESTED)

    def updateMessage(self, text, msecs=0):
        self.ui.statusbar.showMessage(text, msecs)

    def clearMessage(self):
        self.ui.statusbar.clearMessage()

    def clearMessages(self):
        self.messages = []
        self.ui.messageList.clear()

    def commandAction(self):
        command = self.ui.commandEdit.text()
        if not command: return
        if command[0] != '/':
            self.addMessage('Comment: %s' % command)
            self.ui.commandEdit.clear()
            return
        split_command = []
        in_quotes = False
        current_part = ''
        for char in command:
            if char == '/': pass
            elif char  == '"':
                in_quotes = not in_quotes
            elif char == ' ':
                if not in_quotes:
                    if current_part: split_command.append(current_part)
                    current_part = ''
                else: current_part += char
            else: current_part += char
        if current_part: split_command.append(current_part)
        name = split_command[0]
        args = split_command[1:]
        try: result = self.commands.command(name, args)
        except Exception as e: self.addMessage('Error: command failed (%s)' % e)
        else:
            if result is -1: self.addMessage('Error: command failed')
        self.ui.commandEdit.clear()

    def resetTickerColor(self):
        self.ui.highEdit.setPalette(self.black_palette)
        self.ui.lowEdit.setPalette(self.black_palette)
        self.ui.averageEdit.setPalette(self.black_palette)
        self.ui.vwapEdit.setPalette(self.black_palette)
        self.ui.volumeEdit.setPalette(self.black_palette)
        self.ui.lastEdit.setPalette(self.black_palette)
        self.ui.buyEdit.setPalette(self.black_palette)
        self.ui.sellEdit.setPalette(self.black_palette)

    def setTickerText(self, change):
        self.ui.highEdit.setText(str(self.ticker.high))
        if change['high'] > 0: self.ui.highEdit.setPalette(self.green_palette)
        elif change['high'] < 0: self.ui.highEdit.setPalette(self.red_palette)

        self.ui.lowEdit.setText(str(self.ticker.low))
        if change['low'] > 0: self.ui.lowEdit.setPalette(self.green_palette)
        elif change['low'] < 0: self.ui.lowEdit.setPalette(self.red_palette)

        self.ui.averageEdit.setText(str(self.ticker.average))
        if change['average'] > 0: self.ui.averageEdit.setPalette(self.green_palette)
        elif change['average'] < 0: self.ui.averageEdit.setPalette(self.red_palette)

        self.ui.vwapEdit.setText(str(self.ticker.vwap))
        if change['vwap'] > 0: self.ui.vwapEdit.setPalette(self.green_palette)
        elif change['vwap'] < 0: self.ui.vwapEdit.setPalette(self.red_palette)

        self.ui.volumeEdit.setText(str(self.ticker.volume))
        if change['volume'] > 0: self.ui.volumeEdit.setPalette(self.green_palette)
        elif change['volume'] < 0: self.ui.volumeEdit.setPalette(self.red_palette)

        self.ui.lastEdit.setText(str(self.ticker.last))
        if change['last'] > 0: self.ui.lastEdit.setPalette(self.green_palette)
        elif change['last'] < 0: self.ui.lastEdit.setPalette(self.red_palette)

        self.ui.buyEdit.setText(str(self.ticker.sell))
        if change['sell'] > 0: self.ui.buyEdit.setPalette(self.green_palette)
        elif change['sell'] < 0: self.ui.buyEdit.setPalette(self.red_palette)

        self.ui.sellEdit.setText(str(self.ticker.buy))
        if change['buy'] > 0: self.ui.sellEdit.setPalette(self.green_palette)
        elif change['buy'] < 0: self.ui.sellEdit.setPalette(self.red_palette)

    def addTrade(self, trade):
        if trade.currency == 'USD':
            QtGui.QTreeWidgetItem(self.ui.tradeList, [trade.type,str(trade.price),str(trade.amount)])
        while self.ui.tradeList.topLevelItemCount() > 100:
            self.ui.tradeList.takeTopLevelItem(0)
        self.ui.tradeList.scrollToItem(self.ui.tradeList.topLevelItem(self.ui.tradeList.topLevelItemCount()-1))

    def resetTrades(self):
        self.ui.tradeList.clear()
        for trade in self.trades[-100:]:
            if trade.currency == 'USD':
                QtGui.QTreeWidgetItem(self.ui.tradeList, [trade.type,str(trade.price),str(trade.amount)])
        while self.ui.tradeList.topLevelItemCount() > 100:
            self.ui.tradeList.takeTopLevelItem(0)
        self.ui.tradeList.scrollToItem(self.ui.tradeList.topLevelItem(self.ui.tradeList.topLevelItemCount()-1))

    def updateDepth(self, change):
        QtGui.QTreeWidgetItem(self.ui.depthList, [change['type_str'],change['price'],change['volume']])
        while self.ui.depthList.topLevelItemCount() > 50:
            self.ui.depthList.takeTopLevelItem(0)
        self.ui.depthList.scrollToItem(self.ui.depthList.topLevelItem(self.ui.depthList.topLevelItemCount()-1))

    def addMessage(self, message):
        QtGui.QTreeWidgetItem(self.ui.messageList, [time.strftime('%H:%M:%S'),message])
        self.messages.append('%s\t%s' % (time.strftime('%H:%M:%S'),message))
        self.ui.messageList.scrollToItem(self.ui.messageList.topLevelItem(self.ui.messageList.topLevelItemCount()-1))

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = Window(None)
    window.show()
    sys.exit(app.exec_())
