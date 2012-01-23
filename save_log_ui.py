# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'save_log.ui'
#
# Created: Sun Jan 22 13:32:34 2012
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
        Dialog.resize(399, 200)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        self.formLayoutWidget = QtGui.QWidget(Dialog)
        self.formLayoutWidget.setGeometry(QtCore.QRect(10, 10, 381, 183))
        self.formLayoutWidget.setObjectName(_fromUtf8("formLayoutWidget"))
        self.formLayout = QtGui.QFormLayout(self.formLayoutWidget)
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setMargin(0)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(self.formLayoutWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.browseButton = QtGui.QPushButton(self.formLayoutWidget)
        self.browseButton.setObjectName(_fromUtf8("browseButton"))
        self.horizontalLayout.addWidget(self.browseButton)
        self.formLayout.setLayout(1, QtGui.QFormLayout.FieldRole, self.horizontalLayout)
        self.label_2 = QtGui.QLabel(self.formLayoutWidget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_2)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.overwrite = QtGui.QCheckBox(self.formLayoutWidget)
        self.overwrite.setObjectName(_fromUtf8("overwrite"))
        self.verticalLayout.addWidget(self.overwrite)
        self.timeStamp = QtGui.QCheckBox(self.formLayoutWidget)
        self.timeStamp.setObjectName(_fromUtf8("timeStamp"))
        self.verticalLayout.addWidget(self.timeStamp)
        self.timeStampFileName = QtGui.QCheckBox(self.formLayoutWidget)
        self.timeStampFileName.setObjectName(_fromUtf8("timeStampFileName"))
        self.verticalLayout.addWidget(self.timeStampFileName)
        self.formLayout.setLayout(2, QtGui.QFormLayout.FieldRole, self.verticalLayout)
        self.buttonBox = QtGui.QDialogButtonBox(self.formLayoutWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.buttonBox)
        self.fileEdit = QtGui.QLineEdit(self.formLayoutWidget)
        self.fileEdit.setObjectName(_fromUtf8("fileEdit"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.fileEdit)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Save Log", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "File:", None, QtGui.QApplication.UnicodeUTF8))
        self.browseButton.setText(QtGui.QApplication.translate("Dialog", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Options:", None, QtGui.QApplication.UnicodeUTF8))
        self.overwrite.setText(QtGui.QApplication.translate("Dialog", "Overwrite", None, QtGui.QApplication.UnicodeUTF8))
        self.timeStamp.setText(QtGui.QApplication.translate("Dialog", "Time Stamp", None, QtGui.QApplication.UnicodeUTF8))
        self.timeStampFileName.setText(QtGui.QApplication.translate("Dialog", "Time Stamp File Name", None, QtGui.QApplication.UnicodeUTF8))

