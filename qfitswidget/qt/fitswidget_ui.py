# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'fitswidget.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)
from . import resources_rc

class Ui_FitsWidget(object):
    def setupUi(self, FitsWidget):
        if not FitsWidget.objectName():
            FitsWidget.setObjectName(u"FitsWidget")
        FitsWidget.resize(890, 551)
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

        self.verticalLayout.setStretch(1, 1)

        self.retranslateUi(FitsWidget)

        QMetaObject.connectSlotsByName(FitsWidget)
    # setupUi

    def retranslateUi(self, FitsWidget):
        FitsWidget.setWindowTitle(QCoreApplication.translate("FitsWidget", u"Form", None))
        self.labelColorbar.setText("")
    # retranslateUi

