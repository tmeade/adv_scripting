# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/tmeade/Documents/python/maya/adv_scripting/pyQt_demo/basic_template.ui',
# licensing of '/Users/tmeade/Documents/python/maya/adv_scripting/pyQt_demo/basic_template.ui' applies.
#
# Created: Fri May 19 12:51:15 2023
#      by: pyside2-uic  running on PySide2 5.14.2
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_mian_dialog(object):
    def setupUi(self, mian_dialog):
        mian_dialog.setObjectName("mian_dialog")
        mian_dialog.setWindowModality(QtCore.Qt.WindowModal)
        mian_dialog.resize(740, 521)
        mian_dialog.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(mian_dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.startJoin_HL = QtWidgets.QHBoxLayout()
        self.startJoin_HL.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.startJoin_HL.setObjectName("startJoin_HL")
        self.label_startJoint = QtWidgets.QLabel(mian_dialog)
        self.label_startJoint.setObjectName("label_startJoint")
        self.startJoin_HL.addWidget(self.label_startJoint)
        self.startJoint_lineEdit = QtWidgets.QLineEdit(mian_dialog)
        self.startJoint_lineEdit.setText("")
        self.startJoint_lineEdit.setObjectName("startJoint_lineEdit")
        self.startJoin_HL.addWidget(self.startJoint_lineEdit)
        self.verticalLayout.addLayout(self.startJoin_HL)
        self.startJoin_HL_2 = QtWidgets.QHBoxLayout()
        self.startJoin_HL_2.setObjectName("startJoin_HL_2")
        self.label_startJoint_2 = QtWidgets.QLabel(mian_dialog)
        self.label_startJoint_2.setObjectName("label_startJoint_2")
        self.startJoin_HL_2.addWidget(self.label_startJoint_2)
        self.startJoint_lineEdit_2 = QtWidgets.QLineEdit(mian_dialog)
        self.startJoint_lineEdit_2.setText("")
        self.startJoint_lineEdit_2.setObjectName("startJoint_lineEdit_2")
        self.startJoin_HL_2.addWidget(self.startJoint_lineEdit_2)
        self.verticalLayout.addLayout(self.startJoin_HL_2)
        self.print_name_PB = QtWidgets.QPushButton(mian_dialog)
        self.print_name_PB.setObjectName("print_name_PB")
        self.verticalLayout.addWidget(self.print_name_PB)
        self.close_PB = QtWidgets.QPushButton(mian_dialog)
        self.close_PB.setObjectName("close_PB")
        self.verticalLayout.addWidget(self.close_PB)

        self.retranslateUi(mian_dialog)
        QtCore.QMetaObject.connectSlotsByName(mian_dialog)

    def retranslateUi(self, mian_dialog):
        mian_dialog.setWindowTitle(QtWidgets.QApplication.translate("mian_dialog", "our test", None, -1))
        self.label_startJoint.setText(QtWidgets.QApplication.translate("mian_dialog", "Start Joint", None, -1))
        self.label_startJoint_2.setText(QtWidgets.QApplication.translate("mian_dialog", "Number of Upper Twist joints", None, -1))
        self.print_name_PB.setText(QtWidgets.QApplication.translate("mian_dialog", "print", None, -1))
        self.close_PB.setText(QtWidgets.QApplication.translate("mian_dialog", "Close", None, -1))

