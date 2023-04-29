import maya.cmds as cmds
import adv_scripting.rig_name as rig_name
import adv_scripting.matrix_tools as matrix_tools
import adv_scripting.rig.appendages.appendage as appendage
import adv_scripting.utilities as utils
import logging
logger = logging.getLogger(__name__)


class Root(appendage.Appendage):
    def __init__(self, appendage_name, start_joint, input_matrix=None):
        appendage.Appendage.__init__(self, appendage_name, start_joint, input_matrix)

    def setup(self):
        cmds.addAttr(self.output, longName='root_joint_matrix', attributeType='matrix')

    def build(self):
        # TODO: name should be more accessable.  The renaming utility is basing the rename on
        # the joint name and this does not work well in this case.  rigname should be:
        #            rn.RigName(
        #                    element='root',
        #                    rig_type='ctrl',
        #                    maya_type='transform'))
        self.root_ctrl = utils.create_fk_control(self.start_joint,
                                                 connect_output=f'{self.output}.root_joint_matrix')

    def connect_outputs(self):
        # Connect the start matrix on the output node to the skeleton
        cmds.connectAttr(f'{self.output}.root_joint_matrix', f'{self.start_joint}.offsetParentMatrix')

    def cleanup(self):
        # Parent the controls to the control group.
        cmds.parent(self.root_ctrl, self.controls_grp)
