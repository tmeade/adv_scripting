import maya.cmds as cmds
import maya.api.OpenMaya as om
import adv_scripting.rig_name as rn
import adv_scripting.matrix_tools as matrix_tools
import adv_scripting.rig.appendages.appendage as rap
import adv_scripting.utilities as utils
import logging
import pymel.core as pm
logger = logging.getLogger(__name__)

import importlib as il
il.reload(rap)
il.reload(matrix_tools)
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
        # TODO: Add support for neck twist joints!
        self.neck_control = utils.create_fk_control(self.bnd_joints['start_joint'],
                                                    connect_output=f'{self.output}.start_joint_matrix')
        self.head_ctrl = utils.create_fk_control(self.bnd_joints['head_joint'],
                                                connect_output=f'{self.output}.head_joint_matrix',
                                                parent_control=self.neck_control)


    def connect_outputs(self):
        # Connect the start matrix on the output node to the skeleton
        for key, joint_name in self.bnd_joints.items():
            cmds.connectAttr(f'{self.output}.{key}_matrix', f'{joint_name}.offsetParentMatrix')
            cmds.setAttr(joint_name+'.jointOrient', 0,0,0)
            matrix_tools.make_identity(joint_name)


    def cleanup(self):
        # Parent the controls to the control group.
        cmds.parent(self.neck_control, self.controls_grp)
