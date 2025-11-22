# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settings.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from qtpy.QtCore import QCoreApplication, QMetaObject
from qtpy.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QToolButton,
)
from . import resources_rc


class Ui_DialogSettings(object):
    def setupUi(self, DialogSettings):
        if not DialogSettings.objectName():
            DialogSettings.setObjectName("DialogSettings")
        DialogSettings.resize(409, 230)
        self.gridLayout = QGridLayout(DialogSettings)
        self.gridLayout.setObjectName("gridLayout")
        self.groupBox_3 = QGroupBox(DialogSettings)
        self.groupBox_3.setObjectName("groupBox_3")
        self.formLayout_3 = QFormLayout(self.groupBox_3)
        self.formLayout_3.setObjectName("formLayout_3")
        self.checkTextOverlayVisible = QCheckBox(self.groupBox_3)
        self.checkTextOverlayVisible.setObjectName("checkTextOverlayVisible")

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.SpanningRole, self.checkTextOverlayVisible)

        self.label_5 = QLabel(self.groupBox_3)
        self.label_5.setObjectName("label_5")

        self.formLayout_3.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_5)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.labelTextOverlayColor = QFrame(self.groupBox_3)
        self.labelTextOverlayColor.setObjectName("labelTextOverlayColor")
        self.labelTextOverlayColor.setFrameShape(QFrame.Shape.StyledPanel)
        self.labelTextOverlayColor.setFrameShadow(QFrame.Shadow.Raised)

        self.horizontalLayout_3.addWidget(self.labelTextOverlayColor)

        self.buttonTextOverlayColor = QToolButton(self.groupBox_3)
        self.buttonTextOverlayColor.setObjectName("buttonTextOverlayColor")

        self.horizontalLayout_3.addWidget(self.buttonTextOverlayColor)

        self.horizontalLayout_3.setStretch(0, 1)

        self.formLayout_3.setLayout(1, QFormLayout.ItemRole.FieldRole, self.horizontalLayout_3)

        self.gridLayout.addWidget(self.groupBox_3, 0, 0, 1, 1)

        self.groupBox_2 = QGroupBox(DialogSettings)
        self.groupBox_2.setObjectName("groupBox_2")
        self.formLayout_2 = QFormLayout(self.groupBox_2)
        self.formLayout_2.setObjectName("formLayout_2")
        self.label_3 = QLabel(self.groupBox_2)
        self.label_3.setObjectName("label_3")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_3)

        self.comboCenterStyle = QComboBox(self.groupBox_2)
        self.comboCenterStyle.setObjectName("comboCenterStyle")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.comboCenterStyle)

        self.label_2 = QLabel(self.groupBox_2)
        self.label_2.setObjectName("label_2")

        self.formLayout_2.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.labelCenterColor = QFrame(self.groupBox_2)
        self.labelCenterColor.setObjectName("labelCenterColor")
        self.labelCenterColor.setFrameShape(QFrame.Shape.StyledPanel)
        self.labelCenterColor.setFrameShadow(QFrame.Shadow.Raised)

        self.horizontalLayout_2.addWidget(self.labelCenterColor)

        self.buttonCenterColor = QToolButton(self.groupBox_2)
        self.buttonCenterColor.setObjectName("buttonCenterColor")

        self.horizontalLayout_2.addWidget(self.buttonCenterColor)

        self.horizontalLayout_2.setStretch(0, 1)

        self.formLayout_2.setLayout(3, QFormLayout.ItemRole.FieldRole, self.horizontalLayout_2)

        self.checkCenterVisible = QCheckBox(self.groupBox_2)
        self.checkCenterVisible.setObjectName("checkCenterVisible")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.SpanningRole, self.checkCenterVisible)

        self.label_4 = QLabel(self.groupBox_2)
        self.label_4.setObjectName("label_4")

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_4)

        self.spinCenterSize = QSpinBox(self.groupBox_2)
        self.spinCenterSize.setObjectName("spinCenterSize")
        self.spinCenterSize.setMinimum(1)
        self.spinCenterSize.setMaximum(999)

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spinCenterSize)

        self.gridLayout.addWidget(self.groupBox_2, 0, 1, 2, 1)

        self.groupBox_4 = QGroupBox(DialogSettings)
        self.groupBox_4.setObjectName("groupBox_4")
        self.formLayout_4 = QFormLayout(self.groupBox_4)
        self.formLayout_4.setObjectName("formLayout_4")
        self.checkZoomVisible = QCheckBox(self.groupBox_4)
        self.checkZoomVisible.setObjectName("checkZoomVisible")

        self.formLayout_4.setWidget(0, QFormLayout.ItemRole.SpanningRole, self.checkZoomVisible)

        self.gridLayout.addWidget(self.groupBox_4, 0, 2, 1, 1)

        self.groupBox = QGroupBox(DialogSettings)
        self.groupBox.setObjectName("groupBox")
        self.formLayout = QFormLayout(self.groupBox)
        self.formLayout.setObjectName("formLayout")
        self.checkDirectionsVisible = QCheckBox(self.groupBox)
        self.checkDirectionsVisible.setObjectName("checkDirectionsVisible")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.SpanningRole, self.checkDirectionsVisible)

        self.label = QLabel(self.groupBox)
        self.label.setObjectName("label")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.labelDirectionsColor = QFrame(self.groupBox)
        self.labelDirectionsColor.setObjectName("labelDirectionsColor")
        self.labelDirectionsColor.setFrameShape(QFrame.Shape.StyledPanel)
        self.labelDirectionsColor.setFrameShadow(QFrame.Shadow.Raised)

        self.horizontalLayout.addWidget(self.labelDirectionsColor)

        self.buttonDirectionsColor = QToolButton(self.groupBox)
        self.buttonDirectionsColor.setObjectName("buttonDirectionsColor")

        self.horizontalLayout.addWidget(self.buttonDirectionsColor)

        self.horizontalLayout.setStretch(0, 1)

        self.formLayout.setLayout(1, QFormLayout.ItemRole.FieldRole, self.horizontalLayout)

        self.gridLayout.addWidget(self.groupBox, 1, 0, 1, 1)

        self.retranslateUi(DialogSettings)

        QMetaObject.connectSlotsByName(DialogSettings)

    # setupUi

    def retranslateUi(self, DialogSettings):
        DialogSettings.setWindowTitle(QCoreApplication.translate("DialogSettings", "Settings", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("DialogSettings", "Text overlay", None))
        self.checkTextOverlayVisible.setText(QCoreApplication.translate("DialogSettings", "Visible", None))
        self.label_5.setText(QCoreApplication.translate("DialogSettings", "Color:", None))
        self.buttonTextOverlayColor.setText(QCoreApplication.translate("DialogSettings", "...", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("DialogSettings", "Center mark", None))
        self.label_3.setText(QCoreApplication.translate("DialogSettings", "Style:", None))
        self.label_2.setText(QCoreApplication.translate("DialogSettings", "Color:", None))
        self.buttonCenterColor.setText(QCoreApplication.translate("DialogSettings", "...", None))
        self.checkCenterVisible.setText(QCoreApplication.translate("DialogSettings", "Visible", None))
        self.label_4.setText(QCoreApplication.translate("DialogSettings", "Size:", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("DialogSettings", "Zoom", None))
        self.checkZoomVisible.setText(QCoreApplication.translate("DialogSettings", "Visible", None))
        self.groupBox.setTitle(QCoreApplication.translate("DialogSettings", "N/E directions", None))
        self.checkDirectionsVisible.setText(QCoreApplication.translate("DialogSettings", "Visible", None))
        self.label.setText(QCoreApplication.translate("DialogSettings", "Color:", None))
        self.buttonDirectionsColor.setText(QCoreApplication.translate("DialogSettings", "...", None))

    # retranslateUi
