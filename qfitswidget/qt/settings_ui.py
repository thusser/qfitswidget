# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settings.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
    QFormLayout, QFrame, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QSizePolicy, QSpinBox,
    QToolButton, QWidget)
from . import resources_rc

class Ui_DialogSettings(object):
    def setupUi(self, DialogSettings):
        if not DialogSettings.objectName():
            DialogSettings.setObjectName(u"DialogSettings")
        DialogSettings.resize(409, 230)
        self.gridLayout = QGridLayout(DialogSettings)
        self.gridLayout.setObjectName(u"gridLayout")
        self.groupBox_3 = QGroupBox(DialogSettings)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.formLayout_3 = QFormLayout(self.groupBox_3)
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.checkTextOverlayVisible = QCheckBox(self.groupBox_3)
        self.checkTextOverlayVisible.setObjectName(u"checkTextOverlayVisible")

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.SpanningRole, self.checkTextOverlayVisible)

        self.label_5 = QLabel(self.groupBox_3)
        self.label_5.setObjectName(u"label_5")

        self.formLayout_3.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_5)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.labelTextOverlayColor = QFrame(self.groupBox_3)
        self.labelTextOverlayColor.setObjectName(u"labelTextOverlayColor")
        self.labelTextOverlayColor.setFrameShape(QFrame.Shape.StyledPanel)
        self.labelTextOverlayColor.setFrameShadow(QFrame.Shadow.Raised)

        self.horizontalLayout_3.addWidget(self.labelTextOverlayColor)

        self.buttonTextOverlayColor = QToolButton(self.groupBox_3)
        self.buttonTextOverlayColor.setObjectName(u"buttonTextOverlayColor")

        self.horizontalLayout_3.addWidget(self.buttonTextOverlayColor)

        self.horizontalLayout_3.setStretch(0, 1)

        self.formLayout_3.setLayout(1, QFormLayout.ItemRole.FieldRole, self.horizontalLayout_3)


        self.gridLayout.addWidget(self.groupBox_3, 0, 0, 1, 1)

        self.groupBox_2 = QGroupBox(DialogSettings)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.formLayout_2 = QFormLayout(self.groupBox_2)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.label_3 = QLabel(self.groupBox_2)
        self.label_3.setObjectName(u"label_3")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_3)

        self.comboCenterStyle = QComboBox(self.groupBox_2)
        self.comboCenterStyle.setObjectName(u"comboCenterStyle")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.comboCenterStyle)

        self.label_2 = QLabel(self.groupBox_2)
        self.label_2.setObjectName(u"label_2")

        self.formLayout_2.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.labelCenterColor = QFrame(self.groupBox_2)
        self.labelCenterColor.setObjectName(u"labelCenterColor")
        self.labelCenterColor.setFrameShape(QFrame.Shape.StyledPanel)
        self.labelCenterColor.setFrameShadow(QFrame.Shadow.Raised)

        self.horizontalLayout_2.addWidget(self.labelCenterColor)

        self.buttonCenterColor = QToolButton(self.groupBox_2)
        self.buttonCenterColor.setObjectName(u"buttonCenterColor")

        self.horizontalLayout_2.addWidget(self.buttonCenterColor)

        self.horizontalLayout_2.setStretch(0, 1)

        self.formLayout_2.setLayout(3, QFormLayout.ItemRole.FieldRole, self.horizontalLayout_2)

        self.checkCenterVisible = QCheckBox(self.groupBox_2)
        self.checkCenterVisible.setObjectName(u"checkCenterVisible")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.SpanningRole, self.checkCenterVisible)

        self.label_4 = QLabel(self.groupBox_2)
        self.label_4.setObjectName(u"label_4")

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_4)

        self.spinCenterSize = QSpinBox(self.groupBox_2)
        self.spinCenterSize.setObjectName(u"spinCenterSize")
        self.spinCenterSize.setMinimum(1)
        self.spinCenterSize.setMaximum(999)

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spinCenterSize)


        self.gridLayout.addWidget(self.groupBox_2, 0, 1, 2, 1)

        self.groupBox_4 = QGroupBox(DialogSettings)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.formLayout_4 = QFormLayout(self.groupBox_4)
        self.formLayout_4.setObjectName(u"formLayout_4")
        self.checkZoomVisible = QCheckBox(self.groupBox_4)
        self.checkZoomVisible.setObjectName(u"checkZoomVisible")

        self.formLayout_4.setWidget(0, QFormLayout.ItemRole.SpanningRole, self.checkZoomVisible)


        self.gridLayout.addWidget(self.groupBox_4, 0, 2, 1, 1)

        self.groupBox = QGroupBox(DialogSettings)
        self.groupBox.setObjectName(u"groupBox")
        self.formLayout = QFormLayout(self.groupBox)
        self.formLayout.setObjectName(u"formLayout")
        self.checkDirectionsVisible = QCheckBox(self.groupBox)
        self.checkDirectionsVisible.setObjectName(u"checkDirectionsVisible")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.SpanningRole, self.checkDirectionsVisible)

        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.labelDirectionsColor = QFrame(self.groupBox)
        self.labelDirectionsColor.setObjectName(u"labelDirectionsColor")
        self.labelDirectionsColor.setFrameShape(QFrame.Shape.StyledPanel)
        self.labelDirectionsColor.setFrameShadow(QFrame.Shadow.Raised)

        self.horizontalLayout.addWidget(self.labelDirectionsColor)

        self.buttonDirectionsColor = QToolButton(self.groupBox)
        self.buttonDirectionsColor.setObjectName(u"buttonDirectionsColor")

        self.horizontalLayout.addWidget(self.buttonDirectionsColor)

        self.horizontalLayout.setStretch(0, 1)

        self.formLayout.setLayout(1, QFormLayout.ItemRole.FieldRole, self.horizontalLayout)


        self.gridLayout.addWidget(self.groupBox, 1, 0, 1, 1)


        self.retranslateUi(DialogSettings)

        QMetaObject.connectSlotsByName(DialogSettings)
    # setupUi

    def retranslateUi(self, DialogSettings):
        DialogSettings.setWindowTitle(QCoreApplication.translate("DialogSettings", u"Settings", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("DialogSettings", u"Text overlay", None))
        self.checkTextOverlayVisible.setText(QCoreApplication.translate("DialogSettings", u"Visible", None))
        self.label_5.setText(QCoreApplication.translate("DialogSettings", u"Color:", None))
        self.buttonTextOverlayColor.setText(QCoreApplication.translate("DialogSettings", u"...", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("DialogSettings", u"Center mark", None))
        self.label_3.setText(QCoreApplication.translate("DialogSettings", u"Style:", None))
        self.label_2.setText(QCoreApplication.translate("DialogSettings", u"Color:", None))
        self.buttonCenterColor.setText(QCoreApplication.translate("DialogSettings", u"...", None))
        self.checkCenterVisible.setText(QCoreApplication.translate("DialogSettings", u"Visible", None))
        self.label_4.setText(QCoreApplication.translate("DialogSettings", u"Size:", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("DialogSettings", u"Zoom", None))
        self.checkZoomVisible.setText(QCoreApplication.translate("DialogSettings", u"Visible", None))
        self.groupBox.setTitle(QCoreApplication.translate("DialogSettings", u"N/E directions", None))
        self.checkDirectionsVisible.setText(QCoreApplication.translate("DialogSettings", u"Visible", None))
        self.label.setText(QCoreApplication.translate("DialogSettings", u"Color:", None))
        self.buttonDirectionsColor.setText(QCoreApplication.translate("DialogSettings", u"...", None))
    # retranslateUi

