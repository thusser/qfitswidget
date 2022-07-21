# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'settings.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DialogSettings(object):
    def setupUi(self, DialogSettings):
        DialogSettings.setObjectName("DialogSettings")
        DialogSettings.resize(320, 194)
        self.gridLayout = QtWidgets.QGridLayout(DialogSettings)
        self.gridLayout.setObjectName("gridLayout")
        self.groupBox = QtWidgets.QGroupBox(DialogSettings)
        self.groupBox.setObjectName("groupBox")
        self.formLayout = QtWidgets.QFormLayout(self.groupBox)
        self.formLayout.setObjectName("formLayout")
        self.checkDirectionsVisible = QtWidgets.QCheckBox(self.groupBox)
        self.checkDirectionsVisible.setObjectName("checkDirectionsVisible")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.SpanningRole, self.checkDirectionsVisible)
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.labelDirectionsColor = QtWidgets.QFrame(self.groupBox)
        self.labelDirectionsColor.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.labelDirectionsColor.setFrameShadow(QtWidgets.QFrame.Raised)
        self.labelDirectionsColor.setObjectName("labelDirectionsColor")
        self.horizontalLayout.addWidget(self.labelDirectionsColor)
        self.buttonDirectionsColor = QtWidgets.QToolButton(self.groupBox)
        self.buttonDirectionsColor.setObjectName("buttonDirectionsColor")
        self.horizontalLayout.addWidget(self.buttonDirectionsColor)
        self.horizontalLayout.setStretch(0, 1)
        self.formLayout.setLayout(1, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)
        self.groupBox_2 = QtWidgets.QGroupBox(DialogSettings)
        self.groupBox_2.setObjectName("groupBox_2")
        self.formLayout_2 = QtWidgets.QFormLayout(self.groupBox_2)
        self.formLayout_2.setObjectName("formLayout_2")
        self.label_3 = QtWidgets.QLabel(self.groupBox_2)
        self.label_3.setObjectName("label_3")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.comboCenterStyle = QtWidgets.QComboBox(self.groupBox_2)
        self.comboCenterStyle.setObjectName("comboCenterStyle")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.comboCenterStyle)
        self.label_2 = QtWidgets.QLabel(self.groupBox_2)
        self.label_2.setObjectName("label_2")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.labelCenterColor = QtWidgets.QFrame(self.groupBox_2)
        self.labelCenterColor.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.labelCenterColor.setFrameShadow(QtWidgets.QFrame.Raised)
        self.labelCenterColor.setObjectName("labelCenterColor")
        self.horizontalLayout_2.addWidget(self.labelCenterColor)
        self.buttonCenterColor = QtWidgets.QToolButton(self.groupBox_2)
        self.buttonCenterColor.setObjectName("buttonCenterColor")
        self.horizontalLayout_2.addWidget(self.buttonCenterColor)
        self.horizontalLayout_2.setStretch(0, 1)
        self.formLayout_2.setLayout(3, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_2)
        self.checkCenterVisible = QtWidgets.QCheckBox(self.groupBox_2)
        self.checkCenterVisible.setObjectName("checkCenterVisible")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.SpanningRole, self.checkCenterVisible)
        self.label_4 = QtWidgets.QLabel(self.groupBox_2)
        self.label_4.setObjectName("label_4")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.spinCenterSize = QtWidgets.QSpinBox(self.groupBox_2)
        self.spinCenterSize.setMinimum(1)
        self.spinCenterSize.setMaximum(999)
        self.spinCenterSize.setObjectName("spinCenterSize")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.spinCenterSize)
        self.gridLayout.addWidget(self.groupBox_2, 0, 1, 1, 1)

        self.retranslateUi(DialogSettings)
        QtCore.QMetaObject.connectSlotsByName(DialogSettings)

    def retranslateUi(self, DialogSettings):
        _translate = QtCore.QCoreApplication.translate
        DialogSettings.setWindowTitle(_translate("DialogSettings", "Settings"))
        self.groupBox.setTitle(_translate("DialogSettings", "N/E directions"))
        self.checkDirectionsVisible.setText(_translate("DialogSettings", "Visible"))
        self.label.setText(_translate("DialogSettings", "Color:"))
        self.buttonDirectionsColor.setText(_translate("DialogSettings", "..."))
        self.groupBox_2.setTitle(_translate("DialogSettings", "Center mark"))
        self.label_3.setText(_translate("DialogSettings", "Style:"))
        self.label_2.setText(_translate("DialogSettings", "Color:"))
        self.buttonCenterColor.setText(_translate("DialogSettings", "..."))
        self.checkCenterVisible.setText(_translate("DialogSettings", "Visible"))
        self.label_4.setText(_translate("DialogSettings", "Size:"))