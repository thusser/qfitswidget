# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'fitswidget.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_FitsWidget(object):
    def setupUi(self, FitsWidget):
        FitsWidget.setObjectName("FitsWidget")
        FitsWidget.resize(896, 553)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(FitsWidget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupInfo = QtWidgets.QFrame(FitsWidget)
        self.groupInfo.setObjectName("groupInfo")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.groupInfo)
        self.horizontalLayout_5.setContentsMargins(-1, 1, -1, 1)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_2 = QtWidgets.QLabel(self.groupInfo)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_5.addWidget(self.label_2)
        self.textImageX = QtWidgets.QLineEdit(self.groupInfo)
        self.textImageX.setAlignment(QtCore.Qt.AlignCenter)
        self.textImageX.setReadOnly(True)
        self.textImageX.setObjectName("textImageX")
        self.horizontalLayout_5.addWidget(self.textImageX)
        self.label_3 = QtWidgets.QLabel(self.groupInfo)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_5.addWidget(self.label_3)
        self.textImageY = QtWidgets.QLineEdit(self.groupInfo)
        self.textImageY.setAlignment(QtCore.Qt.AlignCenter)
        self.textImageY.setReadOnly(True)
        self.textImageY.setObjectName("textImageY")
        self.horizontalLayout_5.addWidget(self.textImageY)
        self.label_4 = QtWidgets.QLabel(self.groupInfo)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_5.addWidget(self.label_4)
        self.textWorldRA = QtWidgets.QLineEdit(self.groupInfo)
        self.textWorldRA.setAlignment(QtCore.Qt.AlignCenter)
        self.textWorldRA.setReadOnly(True)
        self.textWorldRA.setObjectName("textWorldRA")
        self.horizontalLayout_5.addWidget(self.textWorldRA)
        self.label_5 = QtWidgets.QLabel(self.groupInfo)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_5.addWidget(self.label_5)
        self.textWorldDec = QtWidgets.QLineEdit(self.groupInfo)
        self.textWorldDec.setAlignment(QtCore.Qt.AlignCenter)
        self.textWorldDec.setReadOnly(True)
        self.textWorldDec.setObjectName("textWorldDec")
        self.horizontalLayout_5.addWidget(self.textWorldDec)
        self.verticalLayout.addWidget(self.groupInfo)
        self.frame_2 = QtWidgets.QFrame(FitsWidget)
        self.frame_2.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout.setContentsMargins(-1, 1, -1, 1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_7 = QtWidgets.QLabel(self.frame_2)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout.addWidget(self.label_7)
        self.textPixelValue = QtWidgets.QLineEdit(self.frame_2)
        self.textPixelValue.setAlignment(QtCore.Qt.AlignCenter)
        self.textPixelValue.setReadOnly(True)
        self.textPixelValue.setObjectName("textPixelValue")
        self.horizontalLayout.addWidget(self.textPixelValue)
        self.label_11 = QtWidgets.QLabel(self.frame_2)
        self.label_11.setObjectName("label_11")
        self.horizontalLayout.addWidget(self.label_11)
        self.textAreaMean = QtWidgets.QLineEdit(self.frame_2)
        self.textAreaMean.setAlignment(QtCore.Qt.AlignCenter)
        self.textAreaMean.setReadOnly(True)
        self.textAreaMean.setObjectName("textAreaMean")
        self.horizontalLayout.addWidget(self.textAreaMean)
        self.label_12 = QtWidgets.QLabel(self.frame_2)
        self.label_12.setObjectName("label_12")
        self.horizontalLayout.addWidget(self.label_12)
        self.textAreaMax = QtWidgets.QLineEdit(self.frame_2)
        self.textAreaMax.setAlignment(QtCore.Qt.AlignCenter)
        self.textAreaMax.setReadOnly(True)
        self.textAreaMax.setObjectName("textAreaMax")
        self.horizontalLayout.addWidget(self.textAreaMax)
        self.verticalLayout.addWidget(self.frame_2)
        self.widget_2 = QtWidgets.QWidget(FitsWidget)
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.widget_2)
        self.horizontalLayout_6.setContentsMargins(-1, 1, -1, 1)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem)
        self.widgetTools = QtWidgets.QWidget(self.widget_2)
        self.widgetTools.setObjectName("widgetTools")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.widgetTools)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_6.addWidget(self.widgetTools)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem1)
        self.verticalLayout.addWidget(self.widget_2)
        self.horizontalLayout_4.addLayout(self.verticalLayout)
        self.labelZoom = QtWidgets.QLabel(FitsWidget)
        self.labelZoom.setMinimumSize(QtCore.QSize(101, 101))
        self.labelZoom.setMaximumSize(QtCore.QSize(101, 101))
        self.labelZoom.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.labelZoom.setFrameShadow(QtWidgets.QFrame.Raised)
        self.labelZoom.setText("")
        self.labelZoom.setScaledContents(True)
        self.labelZoom.setObjectName("labelZoom")
        self.horizontalLayout_4.addWidget(self.labelZoom)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.widgetCanvas = QtWidgets.QWidget(FitsWidget)
        self.widgetCanvas.setObjectName("widgetCanvas")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.widgetCanvas)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_2.addWidget(self.widgetCanvas)
        self.labelColorbar = QtWidgets.QLabel(FitsWidget)
        self.labelColorbar.setMinimumSize(QtCore.QSize(30, 0))
        self.labelColorbar.setMaximumSize(QtCore.QSize(30, 16777215))
        self.labelColorbar.setText("")
        self.labelColorbar.setScaledContents(True)
        self.labelColorbar.setObjectName("labelColorbar")
        self.horizontalLayout_2.addWidget(self.labelColorbar)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.frame = QtWidgets.QFrame(FitsWidget)
        self.frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.labelCuts = QtWidgets.QLabel(self.frame)
        self.labelCuts.setEnabled(False)
        self.labelCuts.setObjectName("labelCuts")
        self.horizontalLayout_3.addWidget(self.labelCuts)
        self.comboCuts = QtWidgets.QComboBox(self.frame)
        self.comboCuts.setEnabled(False)
        self.comboCuts.setObjectName("comboCuts")
        self.horizontalLayout_3.addWidget(self.comboCuts)
        self.spinLoCut = QtWidgets.QDoubleSpinBox(self.frame)
        self.spinLoCut.setEnabled(False)
        self.spinLoCut.setButtonSymbols(QtWidgets.QAbstractSpinBox.UpDownArrows)
        self.spinLoCut.setMinimum(-99999.0)
        self.spinLoCut.setMaximum(99999.0)
        self.spinLoCut.setObjectName("spinLoCut")
        self.horizontalLayout_3.addWidget(self.spinLoCut)
        self.spinHiCut = QtWidgets.QDoubleSpinBox(self.frame)
        self.spinHiCut.setEnabled(False)
        self.spinHiCut.setMinimum(-99999.0)
        self.spinHiCut.setMaximum(99999.0)
        self.spinHiCut.setObjectName("spinHiCut")
        self.horizontalLayout_3.addWidget(self.spinHiCut)
        spacerItem2 = QtWidgets.QSpacerItem(5, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.labelStretch = QtWidgets.QLabel(self.frame)
        self.labelStretch.setEnabled(False)
        self.labelStretch.setObjectName("labelStretch")
        self.horizontalLayout_3.addWidget(self.labelStretch)
        self.comboStretch = QtWidgets.QComboBox(self.frame)
        self.comboStretch.setEnabled(False)
        self.comboStretch.setObjectName("comboStretch")
        self.horizontalLayout_3.addWidget(self.comboStretch)
        spacerItem3 = QtWidgets.QSpacerItem(5, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem3)
        self.labelColormap = QtWidgets.QLabel(self.frame)
        self.labelColormap.setEnabled(False)
        self.labelColormap.setObjectName("labelColormap")
        self.horizontalLayout_3.addWidget(self.labelColormap)
        self.comboColormap = QtWidgets.QComboBox(self.frame)
        self.comboColormap.setEnabled(False)
        self.comboColormap.setObjectName("comboColormap")
        self.horizontalLayout_3.addWidget(self.comboColormap)
        self.checkColormapReverse = QtWidgets.QCheckBox(self.frame)
        self.checkColormapReverse.setEnabled(False)
        self.checkColormapReverse.setObjectName("checkColormapReverse")
        self.horizontalLayout_3.addWidget(self.checkColormapReverse)
        spacerItem4 = QtWidgets.QSpacerItem(5, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem4)
        self.checkTrimSec = QtWidgets.QCheckBox(self.frame)
        self.checkTrimSec.setEnabled(False)
        self.checkTrimSec.setChecked(True)
        self.checkTrimSec.setObjectName("checkTrimSec")
        self.horizontalLayout_3.addWidget(self.checkTrimSec)
        self.verticalLayout_2.addWidget(self.frame)
        self.verticalLayout_2.setStretch(1, 1)

        self.retranslateUi(FitsWidget)
        QtCore.QMetaObject.connectSlotsByName(FitsWidget)

    def retranslateUi(self, FitsWidget):
        _translate = QtCore.QCoreApplication.translate
        FitsWidget.setWindowTitle(_translate("FitsWidget", "Form"))
        self.label_2.setText(_translate("FitsWidget", "X:"))
        self.label_3.setText(_translate("FitsWidget", "Y:"))
        self.label_4.setText(_translate("FitsWidget", "RA:"))
        self.label_5.setText(_translate("FitsWidget", "Dec:"))
        self.label_7.setText(_translate("FitsWidget", "Value:"))
        self.label_11.setText(_translate("FitsWidget", "Mean:"))
        self.label_12.setText(_translate("FitsWidget", "Max:"))
        self.labelCuts.setText(_translate("FitsWidget", "Cuts:"))
        self.labelStretch.setText(_translate("FitsWidget", "Stretch:"))
        self.labelColormap.setText(_translate("FitsWidget", "Colormap:"))
        self.checkColormapReverse.setText(_translate("FitsWidget", "reversed"))
        self.checkTrimSec.setText(_translate("FitsWidget", "trimsec"))
