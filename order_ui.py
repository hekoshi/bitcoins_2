# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'order.ui'
#
# Created: Sun Jan 22 19:29:58 2012
#      by: PyQt4 UI code generator 4.9
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(400, 273)
        self.formLayoutWidget = QtGui.QWidget(Dialog)
        self.formLayoutWidget.setGeometry(QtCore.QRect(10, 9, 381, 284))
        self.formLayoutWidget.setObjectName(_fromUtf8("formLayoutWidget"))
        self.formLayout = QtGui.QFormLayout(self.formLayoutWidget)
        self.formLayout.setMargin(0)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(self.formLayoutWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.buyButton = QtGui.QRadioButton(self.formLayoutWidget)
        self.buyButton.setObjectName(_fromUtf8("buyButton"))
        self.orderGroup = QtGui.QButtonGroup(Dialog)
        self.orderGroup.setObjectName(_fromUtf8("orderGroup"))
        self.orderGroup.addButton(self.buyButton)
        self.verticalLayout.addWidget(self.buyButton)
        self.sellButton = QtGui.QRadioButton(self.formLayoutWidget)
        self.sellButton.setObjectName(_fromUtf8("sellButton"))
        self.orderGroup.addButton(self.sellButton)
        self.verticalLayout.addWidget(self.sellButton)
        self.formLayout.setLayout(1, QtGui.QFormLayout.FieldRole, self.verticalLayout)
        self.label_2 = QtGui.QLabel(self.formLayoutWidget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_2)
        self.amountSpinBox = QtGui.QDoubleSpinBox(self.formLayoutWidget)
        self.amountSpinBox.setDecimals(8)
        self.amountSpinBox.setObjectName(_fromUtf8("amountSpinBox"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.amountSpinBox)
        self.label_3 = QtGui.QLabel(self.formLayoutWidget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_3)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.priceSpinBox = QtGui.QDoubleSpinBox(self.formLayoutWidget)
        self.priceSpinBox.setDecimals(5)
        self.priceSpinBox.setObjectName(_fromUtf8("priceSpinBox"))
        self.verticalLayout_2.addWidget(self.priceSpinBox)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.marketOrderBox = QtGui.QCheckBox(self.formLayoutWidget)
        self.marketOrderBox.setObjectName(_fromUtf8("marketOrderBox"))
        self.horizontalLayout_2.addWidget(self.marketOrderBox)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.formLayout.setLayout(3, QtGui.QFormLayout.FieldRole, self.verticalLayout_2)
        self.label_4 = QtGui.QLabel(self.formLayoutWidget)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.label_4)
        self.totalSpinBox = QtGui.QDoubleSpinBox(self.formLayoutWidget)
        self.totalSpinBox.setDecimals(5)
        self.totalSpinBox.setObjectName(_fromUtf8("totalSpinBox"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.totalSpinBox)
        self.buttonBox = QtGui.QDialogButtonBox(self.formLayoutWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.FieldRole, self.buttonBox)
        self.label_5 = QtGui.QLabel(self.formLayoutWidget)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_5)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_7 = QtGui.QLabel(self.formLayoutWidget)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.horizontalLayout.addWidget(self.label_7)
        self.callSlider = QtGui.QSlider(self.formLayoutWidget)
        self.callSlider.setEnabled(False)
        self.callSlider.setMinimum(-100)
        self.callSlider.setMaximum(100)
        self.callSlider.setSingleStep(0)
        self.callSlider.setProperty("value", 0)
        self.callSlider.setTracking(True)
        self.callSlider.setOrientation(QtCore.Qt.Horizontal)
        self.callSlider.setInvertedAppearance(False)
        self.callSlider.setInvertedControls(False)
        self.callSlider.setTickPosition(QtGui.QSlider.TicksBelow)
        self.callSlider.setTickInterval(50)
        self.callSlider.setObjectName(_fromUtf8("callSlider"))
        self.horizontalLayout.addWidget(self.callSlider)
        self.label_6 = QtGui.QLabel(self.formLayoutWidget)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.horizontalLayout.addWidget(self.label_6)
        self.formLayout.setLayout(0, QtGui.QFormLayout.FieldRole, self.horizontalLayout)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QObject.connect(self.marketOrderBox, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.priceSpinBox.setDisabled)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Order", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Order Type:", None, QtGui.QApplication.UnicodeUTF8))
        self.buyButton.setText(QtGui.QApplication.translate("Dialog", "Buy", None, QtGui.QApplication.UnicodeUTF8))
        self.sellButton.setText(QtGui.QApplication.translate("Dialog", "Sell", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Amount:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "Price:", None, QtGui.QApplication.UnicodeUTF8))
        self.marketOrderBox.setText(QtGui.QApplication.translate("Dialog", "Market Order", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Dialog", "Total:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("Dialog", "Current Call:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("Dialog", "Sell", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("Dialog", "Buy", None, QtGui.QApplication.UnicodeUTF8))

