import maya.cmds as mc
import adv_scripting.rig_name as rn
import adv_scripting.matrix_tools as mt
import adv_scripting.rig.appendages.appendage as rap
import logging
logger = logging.getLogger(__name__)

import importlib as il
il.reload(rap)
il.reload(mt)


class Root(rap.Appendage):
    def __init__(self, appendage_name, start_joint, input_matrix=None):
        rap.Appendage.__init__(self, appendage_name, start_joint, input_matrix)

    def setup(self):
        # No additional setup needed for setup()
        return

    def build(self):
        # Create a root control, place its offsetParentMatrix to the root joint and connect the
        # resulting matrix contraint to the start_matrix attribute on the output node.
        self.root_ctrl = mc.createNode('transform', name=rn.RigName(
                                                                element='root',
                                                                rig_type='ctrl',
                                                                maya_type='transform'))
        mt.snap_offset_parent_matrix(self.root_ctrl, self.start_joint)
        mt.matrix_parent_constraint(self.root_ctrl,
                                    self.start_joint,
                                    connect_output=f'{self.output}.start_joint_matrix')

    def connect_outputs(self):
        # Connect the start matrix on the output node to the skeleton
        mc.connectAttr(f'{self.output}.start_joint_matrix', f'{self.start_joint}.offsetParentMatrix')

    def cleanup(self):
        # Parent the controls to the control group.
        mc.parent(self.root_ctrl, self.controls_grp)
