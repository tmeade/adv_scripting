'''
two_bone_fkik.py

Builds FK/IK for two-bone joint chain.
'''

import maya.cmds as mc
import maya.api.OpenMaya as om
import adv_scripting.rig_name as rig_name
import adv_scripting.matrix_tools as matrix_tools
import adv_scripting.rig.appendages.appendage as appendage
import adv_scripting.pole_vector as pole_vector
import adv_scripting.utilities as utils

import logging
logger = logging.getLogger(__name__)

import importlib as il
il.reload(appendage)
il.reload(matrix_tools)
il.reload(pole_vector)
il.reload(rig_name)
il.reload(utils)


class TwoBoneFKIK(appendage.Appendage):
    def __init__(self,
                 appendage_name,
                 start_joint,
                 num_upperTwist_joint,
                 num_lowerTwist_joint,
                 input_matrix=None):
        self.num_upperTwist_joints = num_upperTwist_joint
        self.num_lowerTwist_joints = num_lowerTwist_joint
        self.side = None
        self.element = None
        appendage.Appendage.__init__(self, appendage_name, start_joint, input_matrix)

    def setup(self):
        # {'start_joint': lt_upArm_bnd_10, 'upTwist_01':lt_upArm_bnd_jnt_04, 'midle_joint': 'lt_loArm'}
        skeleton = mc.listRelatives(self.start_joint, ad=True)
        skeleton.reverse()

        # build dictionary of bind joints using the start joint and number of twist joints to
        # determine the position of each joint.
        self.bnd_joints = dict()
        self.bnd_joints['start_joint'] = self.start_joint
        if self.num_upperTwist_joints > 0:
            for index in range(self.num_upperTwist_joints):
                self.bnd_joints[f'up_twist_{index+1}'] = skeleton[index]
        self.bnd_joints['middle_joint'] = skeleton[self.num_upperTwist_joints]
        if self.num_lowerTwist_joints > 0:
            for index in range(self.num_lowerTwist_joints):
                self.bnd_joints[f'low_twist_{index+1}'] = skeleton[self.num_upperTwist_joints + index+1]
        self.bnd_joints['end_joint'] = skeleton[self.num_upperTwist_joints + self.num_lowerTwist_joints + 1]

        # Extract a control skeleton for the fk
        self.fk_skeleton = utils.create_control_joints_from_skeleton(self.bnd_joints['start_joint'],
                                                                self.bnd_joints['end_joint'],
                                                                rig_name.ControlType('fk'),
                                                                self.num_upperTwist_joints,
                                                                self.num_lowerTwist_joints)

        # Extract a control skeleton for the ik
        self.ik_skeleton = utils.create_control_joints_from_skeleton( self.bnd_joints['start_joint'],
                                                                self.bnd_joints['end_joint'],
                                                                rig_name.ControlType('ik'),
                                                                self.num_upperTwist_joints,
                                                                self.num_lowerTwist_joints)

        # Add a matrix attribute to represent each bnd joint on the output node
        for joint_name in self.bnd_joints.keys():
            mc.addAttr(self.output, longName=f'{joint_name}_matrix', attributeType='matrix')

    def build(self):
        #FK
        self.fk_arm_controls = list()
        for joint, joint_rn in self.fk_skeleton:
            name_fk_control = joint_rn.rename(rig_type='ctrl', maya_type='controller')
            fk_control = mc.createNode('transform', n=str(name_fk_control))
            matrix_tools.snap_offset_parent_matrix(fk_control, joint)
            matrix_tools.matrix_parent_constraint(fk_control, joint)

            mc.xform(joint, ro = [0, 0, 0], os=True)
            mc.setAttr(joint+'.jointOrient', 0,0,0)
            self.fk_arm_controls.append(fk_control)

        for index in range(len(self.fk_arm_controls)):
            if index != 0:
                mc.parent(self.fk_arm_controls[index], self.fk_arm_controls[index-1])
                matrix_tools.matrix_parent_constraint(self.fk_arm_controls[index-1], self.fk_arm_controls[index])

        #IK
        root, root_rn = self.ik_skeleton[0]
        mid, mid_rn =  self.ik_skeleton[1]
        end, end_rn =  self.ik_skeleton[2]
        self.side = str(root_rn.side)
        self.element = str(root_rn.element)
        name_ik_handle = rig_name.RigName(element=self.element, side=self.side,
            control_type='ik', rig_type='handle', maya_type='ikrpsolver')
        name_ik_control = rig_name.RigName(element=self.element, side=self.side,
            control_type='ik', rig_type='ctrl', maya_type='controller')

        #IK handle
        arm_ik_handle = mc.ikHandle(sj=root, ee=end, sol='ikRPsolver', n=str(name_ik_handle))[0]
        self.ik_control = mc.createNode('transform', n=str(name_ik_control))
        matrix_tools.snap_offset_parent_matrix(self.ik_control, arm_ik_handle)
        mc.parent(arm_ik_handle, self.ik_control)

        #pole vector
        name_pv = rig_name.RigName(element=self.element, side=self.side,
            control_type='ik', rig_type='pv', maya_type='controller')
        pv_position = pole_vector.calculate_pole_vector_position(root, mid, end)
        self.arm_pv_control = mc.createNode('transform', n=str(name_pv))
        # TODO: place pole vector with offsetParentMatrix
        mc.move(pv_position.x, pv_position.y, pv_position.z, self.arm_pv_control)
        mc.makeIdentity(self.arm_pv_control, apply=True, t=True, r=True, s=True)
        mc.poleVectorConstraint(self.arm_pv_control, arm_ik_handle)

        # Create blended output
        name_FKIK_switch = rig_name.RigName(element=self.element, side=self.side,
            control_type='switch', rig_type='grp')
        FKIK_switch = mc.createNode('transform', n=str(name_FKIK_switch))
        mc.addAttr(FKIK_switch, ln=('FKIK'), at='double', min=0, max=1, k=True)


        result_matricies = list()
        for fk, ik in zip(self.fk_skeleton, self.ik_skeleton):
            result_matricies.append(blend_skeleton(fk,
                                                   ik,
                                                   f'{FKIK_switch}.FKIK',
                                                   element=self.element,
                                                   side=self.side))


    def connect_outputs(self):
        # Connect the start matrix on the output node to the skeleton
        for key, joint_name in self.bnd_joints.items():
            mc.connectAttr(f'{self.output}.{key}_matrix', f'{joint_name}.offsetParentMatrix')

    def cleanup(self):
        # Parent the controls to the control group.
        mc.parent(self.fk_arm_controls[0], self.controls_grp)
        mc.parent(self.ik_control, self.controls_grp)
        mc.parent(self.arm_pv_control, self.controls_grp)
        mc.parent(self.fk_skeleton[0][0], self.controls_grp)
        mc.parent(self.ik_skeleton[0][0], self.controls_grp)


def blend_skeleton(fk_joint, ik_joint, switch_attribute, element=None, side=None):
    logger.debug('============BLEND SKELETON=============')

    fk, fk_rn = fk_joint
    ik, ik_rn = ik_joint
    blend_name = rig_name.RigName(element=f'{element}_fkik',
                                    side=side,
                                    rig_type='util',
                                    maya_type='blendcolors')
    logger.debug(blend_name.output())
    blender = mc.createNode('blendColors', n=str(blend_name))
    mc.connectAttr((ik + '.rotate'), (blender + '.color1'), f=True)
    mc.connectAttr((fk + '.rotate'), (blender + '.color2'), f=True)
    mc.connectAttr(switch_attribute, (blender + '.blender'), f=True)

    # compose matrix
    result_matrix = mc.createNode('composeMatrix')
    mc.connectAttr((blender + '.output'), (result_matrix + '.inputRotate'), f=True)

    return result_matrix


'''
import adv_scripting.rig.appendages.two_bone_fkik as twoB
il.reload(twoB)
arm = twoB.TwoBoneFKIK('arm', 'lt_upArm_bnd_jnt_01', 1, 1, 'lt')
'''
