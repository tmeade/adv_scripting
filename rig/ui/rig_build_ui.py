import pathlib
import os
from PySide2 import QtUiTools, QtWidgets, QtCore
import shiboken2
import logging
logger = logging.getLogger(__name__)

try:
    from maya import OpenMayaUI as omui
except Exception as e:
    logger.error(e)


def get_main_window():
    try:
        mayaMainWindowPtr = omui.MQtUtil.mainWindow()
        mayaMainWindow = shiboken2.wrapInstance(int(mayaMainWindowPtr), QtWidgets.QMainWindow)
        logger.info(f'Wrapped maya UI instance: {mayaMainWindow}' )
    except Exception:
        mayaMainWindow = None
    return mayaMainWindow


class RigBuildUI(QtWidgets.QDialog):
    def __init__(self, parent=get_main_window(), rig_data=None):
        QtWidgets.QDialog.__init__(self, parent)

        # Get parent directory to load .ui file from
        package_dir =  str(pathlib.Path(__file__).parent)
        self.ui_file_path = os.path.join(package_dir, 'build.ui')
        print ('self.ui_file_path', self.ui_file_path)
        # Instanciate data object
        self.rig_data = rig_data

        # Setup main UI and layout
        self.windowTitle = 'Rig Builder'
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.create_ui()


    def create_ui(self):

        self.ui = QtUiTools.QUiLoader().load(self.ui_file_path)
        self.main_layout.addWidget(self.ui)
        self.ui.build_BUT.clicked.connect(self.slot_build_clicked)
        self.ui.close_BUT.clicked.connect(self.slot_close)

        if self.rig_data:
            self.ui.root_start_joint_LE.setText(self.rig_data.root_start_joint)
            self.ui.spine_start_joint_LE.setText(self.rig_data.spine_start_joint)
            self.ui.spine_num_spine_joints_LE.setText(str(self.rig_data.spine_num_spine_joints))
            self.ui.head_start_joint_LE.setText(self.rig_data.head_start_joint)
            self.ui.head_num_twist_joints_LE.setText(str(self.rig_data.head_num_twist_joints))
            self.ui.arm_start_joint_LE.setText(self.rig_data.arm_start_joint)
            self.ui.arm_num_up_joints_LE.setText(str(self.rig_data.arm_num_upperTwist_joints))
            self.ui.arm_num_low_joints_LE.setText(str(self.rig_data.arm_num_lowerTwist_joints))
            self.ui.leg_start_joint_LE.setText(self.rig_data.leg_start_joint)
            self.ui.leg_num_up_joints_LE.setText(str(self.rig_data.leg_num_upperTwist_joints))
            self.ui.leg_num_low_joints_LE.setText(str(self.rig_data.leg_num_lowerTwist_joints))
            self.ui.hand_start_joint_LE.setText(self.rig_data.hand_start_joint)


    def slot_build_clicked(self):
        print (self.rig_data)
        #go_publish(self.publish_data)

    def slot_close(self):
        self.close()
