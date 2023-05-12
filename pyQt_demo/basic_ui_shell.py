from PySide2 import QtUiTools, QtWidgets, QtUiTools

class BasicDialog(QtWidgets.QDialog):
    def __init__(self):
        QtWidgets.QDialog.__init__(self)

        self.ui = QtUiTools.QUiLoader().load('/Users/tmeade/Documents/python/maya/adv_scripting/pyQt_demo/basic_template.ui')

app = QtWidgets.QApplication()
win = BasicDialog()
win.ui.show()
app.exec_()
