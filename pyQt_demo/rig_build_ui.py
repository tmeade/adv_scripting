from PySide2 import QtUiTools, QtWidgets, QtCore
import maya.OpenMayaUI as omui
import shiboken2

def get_main_maya_window():
    maya_main_window_ptr = omui.MQtUtil.mainWindow()
    wrapped_ptr = shiboken2.wrapInstance(maya_main_window_ptr, QtWidgets.QMainWindow)
    return wrapped_ptr


class RigBuildWindow(QtWidgets.QDialog):
    def __init__(self, parent=get_main_maya_window()):
        QtWidgets.QDialog.__init__(self, parent)
        self.setObjectName('Rig Builder')
        # self.windowTitle('Rig Builder')

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        # Create main layout
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.setup_ui()

    def setup_ui(self):
        # Load ui file and parent to main layout
        self.ui = QtUiTools.QUiLoader().load('/Users/tmeade/Documents/python/maya/adv_scripting/pyQt_demo/rig_build_win.ui')
        self.main_layout.addWidget(self.ui)

        # Signals
        self.ui.build_BUT.clicked.connect(self.slot_build)
        self.ui.apply_BUT.clicked.connect(self.slot_apply)
        self.ui.close_BUT.clicked.connect(self.slot_close)

    def slot_build(self):
        print('slot_build')
        start_joint_text = self.ui.start_joint_TEDIT.toPlainText()
        print (start_joint_text)
        self.ui.twistJoints_TEDIT.setText(start_joint_text)
        self.slot_close()

    def slot_close(self):
        self.close()

    def slot_apply(self):
        start_joint_text = self.ui.start_joint_TEDIT.toPlainText()
        print (start_joint_text)
        self.ui.twistJoints_TEDIT.setText(start_joint_text)

# app = QtWidgets.QApplication()
win = RigBuildWindow()
win.show()
# app.exec_()
