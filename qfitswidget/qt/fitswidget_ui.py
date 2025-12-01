# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'fitswidget.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractSpinBox, QApplication, QCheckBox, QComboBox,
    QDoubleSpinBox, QFrame, QHBoxLayout, QLabel,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)
from . import resources.rc_rc

class Ui_FitsWidget(object):
    def setupUi(self, FitsWidget):
        if not FitsWidget.objectName():
            FitsWidget.setObjectName(u"FitsWidget")
        FitsWidget.resize(896, 553)
        self.verticalLayout = QVBoxLayout(FitsWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.widget_2 = QWidget(FitsWidget)
        self.widget_2.setObjectName(u"widget_2")
        self.horizontalLayout_6 = QHBoxLayout(self.widget_2)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(-1, 1, -1, 1)
        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_4)

        self.widgetTools = QWidget(self.widget_2)
        self.widgetTools.setObjectName(u"widgetTools")
        self.verticalLayout_4 = QVBoxLayout(self.widgetTools)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)

        self.horizontalLayout_6.addWidget(self.widgetTools)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_5)


        self.verticalLayout.addWidget(self.widget_2)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.widgetCanvas = QWidget(FitsWidget)
        self.widgetCanvas.setObjectName(u"widgetCanvas")
        self.verticalLayout_3 = QVBoxLayout(self.widgetCanvas)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)

        self.horizontalLayout_2.addWidget(self.widgetCanvas)

        self.labelColorbar = QLabel(FitsWidget)
        self.labelColorbar.setObjectName(u"labelColorbar")
        self.labelColorbar.setMinimumSize(QSize(30, 0))
        self.labelColorbar.setMaximumSize(QSize(30, 16777215))
        self.labelColorbar.setScaledContents(True)

        self.horizontalLayout_2.addWidget(self.labelColorbar)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

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

        self.horizontalSpacer = QSpacerItem(5, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.labelStretch = QLabel(self.frame)
        self.labelStretch.setObjectName(u"labelStretch")
        self.labelStretch.setEnabled(False)

        self.horizontalLayout_3.addWidget(self.labelStretch)

        self.comboStretch = QComboBox(self.frame)
        self.comboStretch.setObjectName(u"comboStretch")
        self.comboStretch.setEnabled(False)

        self.horizontalLayout_3.addWidget(self.comboStretch)

        self.horizontalSpacer_2 = QSpacerItem(5, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

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

        self.horizontalSpacer_3 = QSpacerItem(5, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)

        self.checkTrimSec = QCheckBox(self.frame)
        self.checkTrimSec.setObjectName(u"checkTrimSec")
        self.checkTrimSec.setEnabled(False)
        self.checkTrimSec.setChecked(True)

        self.horizontalLayout_3.addWidget(self.checkTrimSec)


        self.verticalLayout.addWidget(self.frame)

        self.verticalLayout.setStretch(1, 1)

        self.retranslateUi(FitsWidget)

        QMetaObject.connectSlotsByName(FitsWidget)
    # setupUi

    def retranslateUi(self, FitsWidget):
        FitsWidget.setWindowTitle(QCoreApplication.translate("FitsWidget", u"Form", None))
        self.labelColorbar.setText("")
        self.labelCuts.setText(QCoreApplication.translate("FitsWidget", u"Cuts:", None))
        self.labelStretch.setText(QCoreApplication.translate("FitsWidget", u"Stretch:", None))
        self.labelColormap.setText(QCoreApplication.translate("FitsWidget", u"Colormap:", None))
        self.checkColormapReverse.setText(QCoreApplication.translate("FitsWidget", u"reversed", None))
        self.checkTrimSec.setText(QCoreApplication.translate("FitsWidget", u"trimsec", None))
    # retranslateUi

