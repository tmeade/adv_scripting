'''
two_bone_fkik.py

Builds FK/IK for two-bone joint chain.
'''

import maya.cmds as cmds
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
                 side,
                 rotate_axis = 'rz',
                 axis_orient = 1,
                 control_to_local_orient=False,
                 input_matrix=None):
        self.num_upperTwist_joints = num_upperTwist_joint
        self.num_lowerTwist_joints = num_lowerTwist_joint
        self.rotate_axis = rotate_axis
        self.axis_orient = axis_orient
        self.control_to_local_orient = control_to_local_orient
        self.side = side
        self.appendage_name = appendage_name
        appendage.Appendage.__init__(self, appendage_name, start_joint, input_matrix)

    def setup(self):
        # {'start_joint': lt_upArm_bnd_10, 'upTwist_01':lt_upArm_bnd_jnt_04, 'midle_joint': 'lt_loArm'}
        skeleton = cmds.listRelatives(self.start_joint, ad=True)
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
            cmds.addAttr(self.output, longName=f'{joint_name}_matrix', attributeType='matrix')

    def build(self):
        #FK setup
        self.fk_controls = fk_setup(self.fk_skeleton)

        #IK setup
        self.ik_controls = ik_setup(self.ik_skeleton,
                                    self.rotate_axis,
                                    self.axis_orient,
                                    self.control_to_local_orient)

        # Create blended output
         #TODO : twist joint blending
        name_FKIK_switch = rig_name.RigName(element=self.appendage_name, side=self.side,
            control_type='switch', rig_type='grp')
        self.FKIK_switch = cmds.createNode('transform', n=str(name_FKIK_switch))
        cmds.addAttr(self.FKIK_switch, ln=('FKIK'), at='double', min=0, max=1, k=True)


        result_matricies = list()
        for fk, ik in zip(self.fk_skeleton, self.ik_skeleton):
            result_matricies.append(blend_skeleton(fk,
                                                   ik,
                                                   f'{self.FKIK_switch}.FKIK',
                                                   element=self.appendage_name,
                                                   side=self.side))

        bnd_joints_list = [self.bnd_joints['start_joint'],self.bnd_joints['middle_joint'],self.bnd_joints['end_joint']]

        for mult_matrix_node, bnd_jnt in zip(result_matricies,bnd_joints_list):
            parent = cmds.listRelatives(bnd_jnt, parent=True)
            cmds.connectAttr(f'{parent[0]}.worldInverseMatrix[0]', f'{mult_matrix_node}.matrixIn[1]')
            key = get_keys_from_value(self.bnd_joints, bnd_jnt)
            cmds.connectAttr(mult_matrix_node + '.matrixSum', f'{self.output}.{key[0]}_matrix')
            cmds.xform(bnd_jnt, t = [0, 0, 0], os=True)

    def connect_inputs(self):
        '''
        Connect the input matricies from the input node to the root control of the appendage.
        '''
        return

    def connect_outputs(self):
        # Connect the start matrix on the output node to the skeleton
        for key, joint_name in self.bnd_joints.items():
            cmds.connectAttr(f'{self.output}.{key}_matrix', f'{joint_name}.offsetParentMatrix')
            cmds.setAttr(f'{joint_name}.jointOrient', 0,0,0)
            matrix_tools.make_identity(joint_name)

    def cleanup(self):
        # Parent the controls to the control group.
        cmds.parent(self.fk_controls[0], self.controls_grp)
        cmds.parent(self.ik_controls[0], self.controls_grp)
        cmds.parent(self.ik_controls[1], self.controls_grp)
        cmds.parent(self.fk_skeleton[0][0], self.controls_grp)
        cmds.parent(self.ik_skeleton[0][0], self.controls_grp)
        cmds.parent(self.FKIK_switch, self.controls_grp)


def blend_skeleton(fk_joint, ik_joint, switch_attribute, element=None, side=None):
    logger.debug('============BLEND SKELETON=============')

    fk, fk_rn = fk_joint
    ik, ik_rn = ik_joint
    blend_name = rig_name.RigName(element=f'{element}_fkik',
                                    side=side,
                                    rig_type='util',
                                    maya_type='blendMatrix')
    logger.debug(blend_name.output())
    blender = cmds.createNode('blendMatrix', n=str(blend_name))
    cmds.connectAttr((fk + '.worldMatrix'), (blender + '.inputMatrix'), f=True)
    cmds.connectAttr((ik + '.worldMatrix'), (blender + '.target[0].targetMatrix'), f=True)
    cmds.connectAttr(switch_attribute, (blender + '.envelope'), f=True)

    # compose matrix
    result_matrix = cmds.createNode('multMatrix')
    cmds.connectAttr((blender + '.outputMatrix'), (result_matrix +'.matrixIn[0]'), f=True)

    return result_matrix

def get_keys_from_value(dictionary, val):
    return [k for k, v in dictionary.items() if v == val]

def fk_setup(fk_skeleton):

    fk_controls = list()
    for joint, joint_rn in fk_skeleton:
        side = str(joint_rn.side)
        element = str(joint_rn.element)
        region = str(joint_rn.region)
        name_fk_control = rig_name.RigName(element=element, side=side, region=region,  control_type='fk', rig_type='ctrl', maya_type='transform').output()
        fk_control = utils.create_fk_control(joint)

        fk_controls.append(fk_control)

    for index in range(len(fk_controls)):
        if index != 0:
            cmds.parent(fk_controls[index], fk_controls[index-1])
            matrix_tools.matrix_parent_constraint(fk_controls[index-1], fk_controls[index])

    return fk_controls


def ik_setup(ik_skeleton, rotate_axis, axis_orient= 1, control_to_local_orient = False):

    root, root_rn = ik_skeleton[0]
    mid, mid_rn =  ik_skeleton[1]
    end, end_rn =  ik_skeleton[2]
    side = str(root_rn.side)
    element = str(root_rn.element)

    #pole vector
    cmds.setAttr(f'{mid}.{rotate_axis}', 20 * axis_orient)
    name_pv = rig_name.RigName(element=element, side=side,
        control_type='ik', rig_type='pv', maya_type='transform').output()
    pv_position = pole_vector.calculate_pole_vector_position(root, mid, end)
    pv_control = cmds.createNode('transform', n=str(name_pv))
    # TODO: place pole vector with offsetParentMatrix
    cmds.move(pv_position.x, pv_position.y, pv_position.z, pv_control)
    cmds.makeIdentity(pv_control, apply=True, t=True, r=True, s=True)
    cmds.setAttr(f'{mid}.{rotate_axis}',0)

    name_ik_handle = rig_name.RigName(element=element, side=side,
        control_type='ik', rig_type='handle', maya_type='ikrpsolver')
    name_ik_control = rig_name.RigName(element=element, side=side,
        control_type='ik', rig_type='ctrl', maya_type='controller')


    #IK handle
    ik_handle = cmds.ikHandle(sj=root, ee=end, sol='ikRPsolver', n=str(name_ik_handle))[0]
    ik_control = cmds.createNode('transform', n=str(name_ik_control))
    cmds.poleVectorConstraint(pv_control, ik_handle)

    # Orient the control to the local joint.
    # hrmmm??
    if control_to_local_orient == 1:
        matrix_tools.snap_offset_parent_matrix(ik_handle, end)

    matrix_tools.snap_offset_parent_matrix(ik_control, ik_handle)
    cmds.parent(ik_handle, ik_control)
    #matrix_tools.matrix_parent_constraint(ik_control, end)



    return ik_control, pv_control

'''
import adv_scripting.rig.appendages.two_bone_fkik as twoB
il.reload(twoB)
arm = twoB.TwoBoneFKIK('arm', 'lt_upArm_bnd_jnt_01', 1, 1, 'lt')
'''
