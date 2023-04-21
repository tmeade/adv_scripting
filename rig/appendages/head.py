import maya.cmds as cmds
import maya.api.OpenMaya as om
import adv_scripting.rig.name as rn
import adv_scripting.martix_tools as mt
import adv_scripting.rig.appendages.appendage as rap
import adv_scripting.pole_vector as pv
import logging
import pymel.core as pm
logger = logging.getLogger(__name__)

import importlib as il
il.reload(rap)
il.reload(mt)
il.reload(pv)


class Root(rap.Appendage):
    def __init__(   self,
                    appendage_name,
                    start_joint,
                    num_lowerTwist_joint,
                    num_upperTwist_joint,
                    input_matrix=None):
        rap.Appendage.__init__(self, appendage_name, start_joint, input_matrix)
        self.num_lowerTwist_joint = num_lowerTwist_joint;
        self.num_upperTwist_joint = num_upperTwist_joint;


    def setup(self):
        ### Select root first ###

        def create_head_control():
            head_ctrl = cmds.createNode('transform', n="head_ctrl")
            target = cmds.ls(sl=True)[0]
            if not target:
                cmds.warning("Please select a target root joint.")

            mt.snap_offset_parent_matrix(head_ctrl, target)
            mt.matrix_parent_constraint(head_ctrl, target)


        def create_neck_control():
            neck_ctrl = cmds.createNode('transform', n="neck_ctrl")
            target = cmds.ls(sl=True)[0]
            if not target:
                cmds.warning("Please select a target root joint.")

            mt.snap_offset_parent_matrix(neck_ctrl, target)
            mt.matrix_parent_constraint(neck_ctrl, target)




    def build(self):
        # Create a root control, place its offsetParentMatrix to the root joint and connect the
        # resulting matrix constraint to the start_matrix attribute on the output node.
        self.root_ctrl = mc.createNode('transform', name=rn.RigName(
                                                            element='root',
                                                            rig_type='ctrl',
                                                            maya_type='transform'))
        mt.snap_offset_parent_matrix(self.root_ctrl, self.start_joint)
        mt.martix_parent_constraint(self.root_ctrl,
                                    self.start_joint,
                                    connect_output=f'{self.output}.start_matrix')



    def connect_outputs(self):
        # Connect the start matrix on the output node to the skeleton
        mc.connectAttr(f'{self.output}.start_matrix', f'{self.start_joint}.offsetParentMatrix')

    def cleanup(self):
        # Parent the controls to the control group.
        mc.parent(self.root_ctrl, self.control_grp)
