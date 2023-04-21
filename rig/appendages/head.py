import maya.cmds as cmds
import maya.api.OpenMaya as om
import adv_scripting.rig_name as rn
import adv_scripting.matrix_tools as mt
import adv_scripting.rig.appendages.appendage as rap
import adv_scripting.pole_vector as pv
import adv_scripting.utilities as utils
import logging
import pymel.core as pm
logger = logging.getLogger(__name__)

import importlib as il
il.reload(rap)
il.reload(mt)
il.reload(pv)
il.reload(utils)




class Head(rap.Appendage):
    def __init__(   self,
                    appendage_name,
                    start_joint,
                    num_neck_joints,
                    input_matrix=None):
        self.num_neck_joints = num_neck_joints
        rap.Appendage.__init__(self, appendage_name, start_joint, input_matrix)

    def setup(self):
        self.bnd_joints = dict()
        self.bnd_joints['start_joint'] = self.start_joint
        if self.num_neck_joints > 0:
            for index in range(self.num_neck_joints):
                self.bnd_joints[f'neck_{index+1}'] = self.skeleton[index]

        self.bnd_joints['head_joint'] = self.skeleton[self.num_neck_joints + 1]

        # Add a matrix attribute to represent each bnd joint on the output node
        for joint_name in self.bnd_joints.keys():
            cmds.addAttr(self.output, longName=f'{joint_name}_matrix', attributeType='matrix')

        logger.debug('self.bnd_joints: {} '.format(self.bnd_joints))

    def build(self):
        # Create a root control, place its offsetParentMatrix to the root joint and connect the
        # resulting matrix constraint to the start_matrix attribute on the output node.
        self.neck_control = utils.create_fk_control(self.bnd_joints['start_joint'], f'{self.output}.start_joint_matrix')
        self.head_ctrl = utils.create_fk_control(self.bnd_joints['head_joint'], f'{self.output}.head_joint_matrix')

        cmds.parent(self.head_ctrl, self.neck_control)
        #TODO: fix parent_inverse_matrix for head control?
        # matrix_tools.matrix_parent_constraint(self.neck_control, self.head_ctrl)

    def connect_outputs(self):
        # Connect the start matrix on the output node to the skeleton
        for key, joint_name in self.bnd_joints.items():
            cmds.connectAttr(f'{self.output}.{key}_matrix', f'{joint_name}.offsetParentMatrix')

    def cleanup(self):
        # Parent the controls to the control group.
        # cmds.parent(self.head_ctrl, self.neck_control)
        cmds.parent(self.neck_control, self.controls_grp)
