# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/tmeade/Documents/python/maya/tools/pubilsh_window.ui',
# licensing of '/Users/tmeade/Documents/python/maya/tools/pubilsh_window.ui' applies.
#
# Created: Fri Apr 24 22:21:04 2020
#      by: pyside2-uic  running on PySide2 5.12.5
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_publish_dialog(object):
    def setupUi(self, publish_dialog):
        publish_dialog.setObjectName("publish_dialog")
        publish_dialog.resize(688, 370)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(publish_dialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.main_publish_layout = QtWidgets.QVBoxLayout()
        self.main_publish_layout.setObjectName("main_publish_layout")
        self.context_hz_layout = QtWidgets.QHBoxLayout()
        self.context_hz_layout.setObjectName("context_hz_layout")
        self.project_lbl = QtWidgets.QLabel(publish_dialog)
        self.project_lbl.setObjectName("project_lbl")
        self.context_hz_layout.addWidget(self.project_lbl)
        self.project_le = QtWidgets.QLineEdit(publish_dialog)
        self.project_le.setObjectName("project_le")
        self.context_hz_layout.addWidget(self.project_le)
        self.scene_lbl = QtWidgets.QLabel(publish_dialog)
        self.scene_lbl.setObjectName("scene_lbl")
        self.context_hz_layout.addWidget(self.scene_lbl)
        self.scene_le = QtWidgets.QLineEdit(publish_dialog)
        self.scene_le.setObjectName("scene_le")
        self.context_hz_layout.addWidget(self.scene_le)
        self.shot_lbl = QtWidgets.QLabel(publish_dialog)
        self.shot_lbl.setObjectName("shot_lbl")
        self.context_hz_layout.addWidget(self.shot_lbl)
        self.shot_le = QtWidgets.QLineEdit(publish_dialog)
        self.shot_le.setObjectName("shot_le")
        self.context_hz_layout.addWidget(self.shot_le)
        self.main_publish_layout.addLayout(self.context_hz_layout)
        self.char_lw = QtWidgets.QListWidget(publish_dialog)
        self.char_lw.setObjectName("char_lw")
        self.main_publish_layout.addWidget(self.char_lw)
        self.buttons_hz_layout = QtWidgets.QHBoxLayout()
        self.buttons_hz_layout.setObjectName("buttons_hz_layout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.buttons_hz_layout.addItem(spacerItem)
        self.pushButton = QtWidgets.QPushButton(publish_dialog)
        self.pushButton.setObjectName("pushButton")
        self.buttons_hz_layout.addWidget(self.pushButton)
        self.pushButton_3 = QtWidgets.QPushButton(publish_dialog)
        self.pushButton_3.setObjectName("pushButton_3")
        self.buttons_hz_layout.addWidget(self.pushButton_3)
        self.main_publish_layout.addLayout(self.buttons_hz_layout)
        self.verticalLayout_2.addLayout(self.main_publish_layout)

        self.retranslateUi(publish_dialog)
        QtCore.QMetaObject.connectSlotsByName(publish_dialog)

    def retranslateUi(self, publish_dialog):
        publish_dialog.setWindowTitle(QtWidgets.QApplication.translate("publish_dialog", "Publish Items", None, -1))
        self.project_lbl.setText(QtWidgets.QApplication.translate("publish_dialog", "Project:", None, -1))
        self.scene_lbl.setText(QtWidgets.QApplication.translate("publish_dialog", "Scene", None, -1))
        self.shot_lbl.setText(QtWidgets.QApplication.translate("publish_dialog", "Shot:", None, -1))
        self.pushButton.setText(QtWidgets.QApplication.translate("publish_dialog", "Close", None, -1))
        self.pushButton_3.setText(QtWidgets.QApplication.translate("publish_dialog", "Publish", None, -1))

