# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'fitswidget.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from .qimageview import QImageView


class Ui_FitsWidget(object):
    def setupUi(self, FitsWidget):
        if not FitsWidget.objectName():
            FitsWidget.setObjectName(u"FitsWidget")
        FitsWidget.resize(896, 553)
        self.verticalLayout_2 = QVBoxLayout(FitsWidget)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupInfo = QFrame(FitsWidget)
        self.groupInfo.setObjectName(u"groupInfo")
        self.horizontalLayout_5 = QHBoxLayout(self.groupInfo)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_2 = QLabel(self.groupInfo)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_5.addWidget(self.label_2)

        self.textImageX = QLineEdit(self.groupInfo)
        self.textImageX.setObjectName(u"textImageX")
        self.textImageX.setAlignment(Qt.AlignCenter)
        self.textImageX.setReadOnly(True)

        self.horizontalLayout_5.addWidget(self.textImageX)

        self.label_3 = QLabel(self.groupInfo)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_5.addWidget(self.label_3)

        self.textImageY = QLineEdit(self.groupInfo)
        self.textImageY.setObjectName(u"textImageY")
        self.textImageY.setAlignment(Qt.AlignCenter)
        self.textImageY.setReadOnly(True)

        self.horizontalLayout_5.addWidget(self.textImageY)

        self.label_4 = QLabel(self.groupInfo)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_5.addWidget(self.label_4)

        self.textWorldRA = QLineEdit(self.groupInfo)
        self.textWorldRA.setObjectName(u"textWorldRA")
        self.textWorldRA.setAlignment(Qt.AlignCenter)
        self.textWorldRA.setReadOnly(True)

        self.horizontalLayout_5.addWidget(self.textWorldRA)

        self.label_5 = QLabel(self.groupInfo)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout_5.addWidget(self.label_5)

        self.textWorldDec = QLineEdit(self.groupInfo)
        self.textWorldDec.setObjectName(u"textWorldDec")
        self.textWorldDec.setAlignment(Qt.AlignCenter)
        self.textWorldDec.setReadOnly(True)

        self.horizontalLayout_5.addWidget(self.textWorldDec)

        self.verticalLayout.addWidget(self.groupInfo)

        self.frame_2 = QFrame(FitsWidget)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.NoFrame)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame_2)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_7 = QLabel(self.frame_2)
        self.label_7.setObjectName(u"label_7")

        self.horizontalLayout.addWidget(self.label_7)

        self.textPixelValue = QLineEdit(self.frame_2)
        self.textPixelValue.setObjectName(u"textPixelValue")
        self.textPixelValue.setAlignment(Qt.AlignCenter)
        self.textPixelValue.setReadOnly(True)

        self.horizontalLayout.addWidget(self.textPixelValue)

        self.label_11 = QLabel(self.frame_2)
        self.label_11.setObjectName(u"label_11")

        self.horizontalLayout.addWidget(self.label_11)

        self.textAreaMean = QLineEdit(self.frame_2)
        self.textAreaMean.setObjectName(u"textAreaMean")
        self.textAreaMean.setAlignment(Qt.AlignCenter)
        self.textAreaMean.setReadOnly(True)

        self.horizontalLayout.addWidget(self.textAreaMean)

        self.label_12 = QLabel(self.frame_2)
        self.label_12.setObjectName(u"label_12")

        self.horizontalLayout.addWidget(self.label_12)

        self.textAreaMax = QLineEdit(self.frame_2)
        self.textAreaMax.setObjectName(u"textAreaMax")
        self.textAreaMax.setAlignment(Qt.AlignCenter)
        self.textAreaMax.setReadOnly(True)

        self.horizontalLayout.addWidget(self.textAreaMax)

        self.verticalLayout.addWidget(self.frame_2)

        self.horizontalLayout_4.addLayout(self.verticalLayout)

        self.labelZoom = QLabel(FitsWidget)
        self.labelZoom.setObjectName(u"labelZoom")
        self.labelZoom.setMinimumSize(QSize(101, 101))
        self.labelZoom.setMaximumSize(QSize(101, 101))
        self.labelZoom.setFrameShape(QFrame.StyledPanel)
        self.labelZoom.setFrameShadow(QFrame.Raised)
        self.labelZoom.setScaledContents(True)

        self.horizontalLayout_4.addWidget(self.labelZoom)

        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.imageView = QImageView(FitsWidget)
        self.imageView.setObjectName(u"imageView")

        self.horizontalLayout_2.addWidget(self.imageView)

        self.labelColorbar = QLabel(FitsWidget)
        self.labelColorbar.setObjectName(u"labelColorbar")
        self.labelColorbar.setMinimumSize(QSize(30, 0))
        self.labelColorbar.setMaximumSize(QSize(30, 16777215))
        self.labelColorbar.setScaledContents(True)

        self.horizontalLayout_2.addWidget(self.labelColorbar)

        self.horizontalLayout_2.setStretch(0, 1)

        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.frame = QFrame(FitsWidget)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.NoFrame)
        self.frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.labelCuts = QLabel(self.frame)
        self.labelCuts.setObjectName(u"labelCuts")
        self.labelCuts.setEnabled(False)

        self.horizontalLayout_3.addWidget(self.labelCuts)

        self.comboCuts = QComboBox(self.frame)
        self.comboCuts.setObjectName(u"comboCuts")
        self.comboCuts.setEnabled(False)

        self.horizontalLayout_3.addWidget(self.comboCuts)

        self.spinLoCut = QDoubleSpinBox(self.frame)
        self.spinLoCut.setObjectName(u"spinLoCut")
        self.spinLoCut.setEnabled(False)
        self.spinLoCut.setButtonSymbols(QAbstractSpinBox.UpDownArrows)
        self.spinLoCut.setMinimum(-99999.000000000000000)
        self.spinLoCut.setMaximum(99999.000000000000000)

        self.horizontalLayout_3.addWidget(self.spinLoCut)

        self.spinHiCut = QDoubleSpinBox(self.frame)
        self.spinHiCut.setObjectName(u"spinHiCut")
        self.spinHiCut.setEnabled(False)
        self.spinHiCut.setMinimum(-99999.000000000000000)
        self.spinHiCut.setMaximum(99999.000000000000000)

        self.horizontalLayout_3.addWidget(self.spinHiCut)

        self.horizontalSpacer = QSpacerItem(
            5, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.labelStretch = QLabel(self.frame)
        self.labelStretch.setObjectName(u"labelStretch")
        self.labelStretch.setEnabled(False)

        self.horizontalLayout_3.addWidget(self.labelStretch)

        self.comboStretch = QComboBox(self.frame)
        self.comboStretch.setObjectName(u"comboStretch")
        self.comboStretch.setEnabled(False)

        self.horizontalLayout_3.addWidget(self.comboStretch)

        self.horizontalSpacer_2 = QSpacerItem(
            5, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)

        self.labelColormap = QLabel(self.frame)
        self.labelColormap.setObjectName(u"labelColormap")
        self.labelColormap.setEnabled(False)

        self.horizontalLayout_3.addWidget(self.labelColormap)

        self.comboColormap = QComboBox(self.frame)
        self.comboColormap.setObjectName(u"comboColormap")
        self.comboColormap.setEnabled(False)

        self.horizontalLayout_3.addWidget(self.comboColormap)

        self.checkColormapReverse = QCheckBox(self.frame)
        self.checkColormapReverse.setObjectName(u"checkColormapReverse")
        self.checkColormapReverse.setEnabled(False)

        self.horizontalLayout_3.addWidget(self.checkColormapReverse)

        self.horizontalSpacer_3 = QSpacerItem(
            5, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)

        self.checkTrimSec = QCheckBox(self.frame)
        self.checkTrimSec.setObjectName(u"checkTrimSec")
        self.checkTrimSec.setEnabled(False)
        self.checkTrimSec.setChecked(True)

        self.horizontalLayout_3.addWidget(self.checkTrimSec)

        self.verticalLayout_2.addWidget(self.frame)

        self.verticalLayout_2.setStretch(1, 1)

        self.retranslateUi(FitsWidget)

        QMetaObject.connectSlotsByName(FitsWidget)

    # setupUi

    def retranslateUi(self, FitsWidget):
        FitsWidget.setWindowTitle(
            QCoreApplication.translate("FitsWidget", u"Form", None)
        )
        self.label_2.setText(QCoreApplication.translate("FitsWidget", u"X:", None))
        self.label_3.setText(QCoreApplication.translate("FitsWidget", u"Y:", None))
        self.label_4.setText(QCoreApplication.translate("FitsWidget", u"RA:", None))
        self.label_5.setText(QCoreApplication.translate("FitsWidget", u"Dec:", None))
        self.label_7.setText(QCoreApplication.translate("FitsWidget", u"Value:", None))
        self.label_11.setText(QCoreApplication.translate("FitsWidget", u"Mean:", None))
        self.label_12.setText(QCoreApplication.translate("FitsWidget", u"Max:", None))
        self.labelZoom.setText("")
        self.labelColorbar.setText("")
        self.labelCuts.setText(QCoreApplication.translate("FitsWidget", u"Cuts:", None))
        self.labelStretch.setText(
            QCoreApplication.translate("FitsWidget", u"Stretch:", None)
        )
        self.labelColormap.setText(
            QCoreApplication.translate("FitsWidget", u"Colormap:", None)
        )
        self.checkColormapReverse.setText(
            QCoreApplication.translate("FitsWidget", u"reversed", None)
        )
        self.checkTrimSec.setText(
            QCoreApplication.translate("FitsWidget", u"trimsec", None)
        )

    # retranslateUi
