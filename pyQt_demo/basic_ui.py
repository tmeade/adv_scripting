from PySide2 import QtUiTools, QtWidgets, QtUiTools, QtCore
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

import shiboken2
import logging

try:
    from maya import OpenMayaUI as omui
except Exception as e:
    logging.error(e)

def get_main_window():
    mayaMainWindowPtr = omui.MQtUtil.mainWindow()
    return shiboken2.wrapInstance(int(mayaMainWindowPtr), QtWidgets.QMainWindow)


class BasicDialog(MayaQWidgetDockableMixin, QtWidgets.QDialog):
    def __init__(self, parent=get_main_window()):
        QtWidgets.QDialog.__init__(self, parent)

        self.setObjectName('testWin')
        print(parent)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.ui = QtUiTools.QUiLoader().load('/Users/tmeade/Documents/python/maya/adv_scripting/pyQt_demo/basic_template.ui')
        self.main_layout.addWidget(self.ui)


# app = QtWidgets.QApplication()
# win = BasicDialog()
# win.ui.show()
# app.exec_()
