# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/tmeade/Documents/python/maya/adv_scripting/pyQt_demo/rig_build_win.ui',
# licensing of '/Users/tmeade/Documents/python/maya/adv_scripting/pyQt_demo/rig_build_win.ui' applies.
#
# Created: Sat May 20 10:25:55 2023
#      by: pyside2-uic  running on PySide2 5.14.2
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(780, 710)
        self.main_layout_VL = QtWidgets.QVBoxLayout(Dialog)
        self.main_layout_VL.setObjectName("main_layout_VL")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        spacerItem = QtWidgets.QSpacerItem(55, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.start_joint_TEDIT = QtWidgets.QTextEdit(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.start_joint_TEDIT.sizePolicy().hasHeightForWidth())
        self.start_joint_TEDIT.setSizePolicy(sizePolicy)
        self.start_joint_TEDIT.setMaximumSize(QtCore.QSize(16777215, 25))
        self.start_joint_TEDIT.setObjectName("start_joint_TEDIT")
        self.horizontalLayout.addWidget(self.start_joint_TEDIT)
        self.main_layout_VL.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.twistJoints_TEDIT = QtWidgets.QTextEdit(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.twistJoints_TEDIT.sizePolicy().hasHeightForWidth())
        self.twistJoints_TEDIT.setSizePolicy(sizePolicy)
        self.twistJoints_TEDIT.setMaximumSize(QtCore.QSize(16777215, 25))
        self.twistJoints_TEDIT.setObjectName("twistJoints_TEDIT")
        self.horizontalLayout_2.addWidget(self.twistJoints_TEDIT)
        self.main_layout_VL.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.build_BUT = QtWidgets.QPushButton(Dialog)
        self.build_BUT.setObjectName("build_BUT")
        self.horizontalLayout_3.addWidget(self.build_BUT)
        self.apply_BUT = QtWidgets.QPushButton(Dialog)
        self.apply_BUT.setObjectName("apply_BUT")
        self.horizontalLayout_3.addWidget(self.apply_BUT)
        self.close_BUT = QtWidgets.QPushButton(Dialog)
        self.close_BUT.setObjectName("close_BUT")
        self.horizontalLayout_3.addWidget(self.close_BUT)
        self.main_layout_VL.addLayout(self.horizontalLayout_3)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.main_layout_VL.addItem(spacerItem1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtWidgets.QApplication.translate("Dialog", "Dialog", None, -1))
        self.label.setText(QtWidgets.QApplication.translate("Dialog", "start_joint", None, -1))
        self.label_2.setText(QtWidgets.QApplication.translate("Dialog", "Number twist jonits", None, -1))
        self.build_BUT.setText(QtWidgets.QApplication.translate("Dialog", "Build", None, -1))
        self.apply_BUT.setText(QtWidgets.QApplication.translate("Dialog", "Apply", None, -1))
        self.close_BUT.setText(QtWidgets.QApplication.translate("Dialog", "Close", None, -1))

