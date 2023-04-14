import maya.cmds as mc
import maya.api.OpenMaya as om
import adv_scripting.rig_name as rn
import adv_scripting.matrix_tools as mt
import adv_scripting.rig.appendages.appendage as rap
import adv_scripting.pole_vector as pv
import adv_scripting.utilities as utils

import logging
logger = logging.getLogger(__name__)

import importlib as il
il.reload(rap)
il.reload(mt)
il.reload(pv)
il.reload(rn)
il.reload(utils)



class TwoBoneFKIK(rap.Appendage):
    def __init__(   self,
                    appendage_name,
                    start_joint,
                    num_upperTwist_joint,
                    num_lowerTwist_joint,
                    side,
                    input_matrix=None):
        self.num_upperTwist_joints = num_upperTwist_joint
        self.num_lowerTwist_joints = num_lowerTwist_joint
        self.side = side
        rap.Appendage.__init__(self, appendage_name, start_joint, input_matrix)

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
        self.fk_skeleton = utils.create_control_joints_from_skeleton( self.bnd_joints['start_joint'],
                                                                self.bnd_joints['end_joint'],
                                                                rn.ControlType('fk'),
                                                                self.num_upperTwist_joints,
                                                                self.num_lowerTwist_joints)

        # Extract a control skeleton for the ik
        self.ik_skeleton = utils.create_control_joints_from_skeleton( self.bnd_joints['start_joint'],
                                                                self.bnd_joints['end_joint'],
                                                                rn.ControlType('ik'),
                                                                self.num_upperTwist_joints,
                                                                self.num_lowerTwist_joints)

        # Add a matrix attribute to represent each bnd joint on the output node
        for joint_name in self.bnd_joints.keys():
            mc.addAttr(self.output, longName=f'{joint_name}_matrix', attributeType='matrix')

    def build(self):
        #FK
        self.fk_arm_controls = list()
        for joint in self.fk_skeleton:
            # TODO: USE THE RigName class to name this!
            fk_control = mc.createNode('transform', n=f'{joint}'+'_fk_ctrl_transform')
            mt.snap_offset_parent_matrix(fk_control, joint)
            mt.matrix_parent_constraint(fk_control, joint)

            mc.xform(joint, ro = [0, 0, 0], os=True)
            mc.setAttr(joint+'.jointOrient', 0,0,0)
            self.fk_arm_controls.append(fk_control)

        for index in range(len(self.fk_arm_controls)):
            if index != 0:
                mc.parent(self.fk_arm_controls[index], self.fk_arm_controls[index-1])
                mt.matrix_parent_constraint(self.fk_arm_controls[index-1], self.fk_arm_controls[index])

        #IK

        root = self.ik_skeleton[0]
        mid =  self.ik_skeleton[1]
        end =  self.ik_skeleton[2]

        #IK handle
        # TODO: Use rigname script to name handle and controls
        arm_ik_handle = mc.ikHandle(sj = root, ee = end, sol = 'ikRPsolver')
        self.ik_control = mc.createNode('transform')
        mt.snap_offset_parent_matrix(self.ik_control, arm_ik_handle[0])
        mc.parent(arm_ik_handle[0], self.ik_control)

        #pole vector
        # TODO: PV control naming
        pv_position = pv.calculate_pole_vector_position(root, mid, end)
        self.arm_pv_control = mc.createNode('transform')
        # TODO: place pole vector with offsetParentMatrix
        mc.move(pv_position.x, pv_position.y, pv_position.z, self.arm_pv_control)
        mc.makeIdentity(self.arm_pv_control, apply=True, t=True, r=True, s=True)
        mc.poleVectorConstraint(self.arm_pv_control, arm_ik_handle[0])

        # Create blended output
        # FKIK_switch = mc.createNode('transform', rn.RigName(element='armSwitches', side=self.side, control_type='switch', rig_type='grp'))
        FKIK_switch = mc.createNode('transform')
        mc.addAttr(FKIK_switch, ln=('FKIK'), at='double', min=0, max=1, k=True)


        result_matricies = list()
        for fk, ik in zip(self.fk_skeleton, self.ik_skeleton):
            result_matricies.append(blend_skeleton(fk,
                                                    ik,
                                                    f'{FKIK_switch}.FKIK',
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
        mc.parent(self.fk_skeleton[0], self.controls_grp)
        mc.parent(self.ik_skeleton[0], self.controls_grp)






def blend_skeleton(fk_joint, ik_joint, switch_attribute, side=None):
    print ('fk_joint', fk_joint)

    blender = mc.createNode('blendColors', n= rn.RigName(element = f'ik_{fk_joint}',
                                            side=side,
                                            control_type='util',
                                            rig_type='blendColors'))
    mc.connectAttr((ik_joint + '.rotate'), (blender + '.color1'), f=True)
    mc.connectAttr((fk_joint + '.rotate'), (blender + '.color2'), f=True)
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
