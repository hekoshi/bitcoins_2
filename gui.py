#!/usr/bin/env python3
from PyQt4 import QtCore, QtGui
from main_window_ui import *
from imports import *
from events import *
import sys

class Window(QtGui.QMainWindow):
    def __init__(self, events, commands, ticker, depth, trades, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.events = events
        self.commands = commands
        self.ticker = ticker
        self.depth = depth
        self.trades = trades
        self.last_depth_update = time.time()
        self.depth_interval = 1
        self.red_palette = QtGui.QPalette(self.palette())
        self.green_palette = QtGui.QPalette(self.palette())
        self.black_palette = QtGui.QPalette(self.palette())
        self.red_palette.setColor(self.red_palette.Text, QtGui.QColor(255,0,0))
        self.green_palette.setColor(self.green_palette.Text, QtGui.QColor(0,255,0))
        self.ui.commandEdit.setFocus()
        self.messages = []
        self.connect(self, QtCore.SIGNAL("setTicker"), self.setTickerText)
        self.connect(self, QtCore.SIGNAL('addTrade'), self.addTrade)
        self.connect(self, QtCore.SIGNAL('resetTrades'), self.resetTrades)
        self.connect(self, QtCore.SIGNAL('updateMessage'), self.updateMessage)
        self.connect(self, QtCore.SIGNAL('clearMessage'), self.clearMessage)
        self.connect(self, QtCore.SIGNAL('clearMessages'), self.clearMessages)
        self.connect(self, QtCore.SIGNAL('updateDepth'), self.updateDepth)
        self.connect(self, QtCore.SIGNAL('addMessage'), self.addMessage)
        self.connect(self, QtCore.SIGNAL('resetTickerColor'), self.resetTickerColor)
        self.connect(self.ui.actionFull_Update, QtCore.SIGNAL('triggered()'), self.full_update)
        self.connect(self.ui.actionClear_Messages, QtCore.SIGNAL('triggered()'), self.clearMessages)
        self.connect(self.ui.commandEdit, QtCore.SIGNAL('returnPressed()'), self.commandAction)

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
        split_command = command.split(' ')
        name = split_command[0][1:]
        args = split_command[1:]
        result = self.commands.command(name, args)
        if result is -1:
            self.addMessage('Error: command failed')
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

        self.ui.buyEdit.setText(str(self.ticker.buy))
        if change['buy'] > 0: self.ui.buyEdit.setPalette(self.green_palette)
        elif change['buy'] < 0: self.ui.buyEdit.setPalette(self.red_palette)

        self.ui.sellEdit.setText(str(self.ticker.sell))
        if change['sell'] > 0: self.ui.sellEdit.setPalette(self.green_palette)
        elif change['sell'] < 0: self.ui.sellEdit.setPalette(self.red_palette)

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
