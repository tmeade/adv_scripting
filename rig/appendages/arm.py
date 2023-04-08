import maya.cmds as mc
import maya.api.OpenMaya as om
import adv_scripting.rig_name as rn
import adv_scripting.matrix_tools as mt
import adv_scripting.rig.appendages.appendage as rap
import adv_scripting.pole_vector as pv

import logging
logger = logging.getLogger(__name__)

import importlib as il
il.reload(rap)
il.reload(mt)

class Leg(TwoBoneFKIK):
    def __init__(   self,
                    appendage_name,
                    start_joint,
                    num_upperTwist_joint,
                    num_lowerTwist_joint,
                    input_matrix=None):
        rap.Appendage.__init__(self, appendage_name, start_joint, input_matrix)
        foot_setup()

    def setup(self):
        pass



class TwoBoneFKIK(rap.Appendage):
    def __init__(   self,
                    appendage_name,
                    start_joint,
                    num_upperTwist_joint,
                    num_lowerTwist_joint,
                    input_matrix=None):
        self.num_upperTwist_joints = num_upperTwist_joint
        self.num_lowerTwist_joints = num_lowerTwist_joint
        rap.Appendage.__init__(self, appendage_name, start_joint, input_matrix)

    def setup(self):
        # {'start_joint': lt_upArm_bnd_10, 'upTwist_01':lt_upArm_bnd_jnt_04, 'midle_joint': 'lt_loArm'}
        skeleton = mc.listRelatives(self.start_joint, ad=True)
        skeleton.reverse()
        print('skeleton: ', skeleton)

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
        self.fk_skeleton = create_control_joints_from_skeleton( self.bnd_joints['start_joint'],
                                                                self.bnd_joints['end_joint'],
                                                                rn.ControlType('fk'),
                                                                self.num_upperTwist_joints,
                                                                self.num_lowerTwist_joints)

        # Extract a control skeleton for the ik
        self.ik_skeleton = create_control_joints_from_skeleton( self.bnd_joints['start_joint'],
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
            fk_control = mc.createNode('transform', n=f'{joint}'+'_fk_control')
            mt.snap_offset_parent_matrix(fk_control, joint)
            mt.matrix_parent_constraint(fk_control, joint)

            mc.xform(joint, ro = [0, 0, 0], os=True)
            mc.setAttr(joint+'.jointOrient', 0,0,0)
            self.fk_arm_controls.append(fk_control)

        for index in range(len(self.fk_arm_controls)):
            if index != 0:
                mc.parent(self.fk_arm_controls[index], self.fk_arm_controls[index-1])
                mt.matrix_parent_constraint(self.fk_arm_controls[index-1], self.fk_arm_controls[index])


    def connect_outputs(self):
        # Connect the start matrix on the output node to the skeleton
        for key, joint_name in self.bnd_joints.items():
            mc.connectAttr(f'{self.output}.{key}_matrix', f'{joint_name}.offsetParentMatrix')

    def cleanup(self):
        # Parent the controls to the control group.
        mc.parent(self.fk_arm_controls[0], self.controls_grp)
        mc.parent(self.fk_skeleton[0], self.controls_grp)
        mc.parent(self.ik_skeleton[0], self.controls_grp)




def create_control_joints_from_skeleton(start_joint,
                                        end_joint,
                                        control_type,
                                        num_upperTwist_joints,
                                        num_lowerTwist_joints):

    # Duplicate the skeleton and parent it to the world
    duplicate_skeleton = mc.duplicate(start_joint)
    mc.parent(duplicate_skeleton[0], w=True)

    # Rename the skeleton by replaceing 'bnd' with the control_type.
    for joint in mc.listRelatives(duplicate_skeleton[0], ad=True, fullPath=True):
        mc.rename(joint,
                  joint.split('|')[-1].replace('_bnd_', (f'_{control_type}_')))
    start_joint = mc.rename(duplicate_skeleton[0],
                            duplicate_skeleton[0].split('|')[-1].replace('_bnd_', (f'_{control_type}_')))

    # Delete all of the joints in the hierarchy below the end joint
    mc.delete(mc.listRelatives(end_joint.replace('_bnd_', (f'_{control_type}_'))))

    # Use the number of twist joints to extract the control joints
    skeleton = mc.listRelatives(start_joint, ad=True)
    skeleton.reverse()
    if num_upperTwist_joints > 0:
        middle_joint = skeleton[num_upperTwist_joints]
    else:
        middle_joint = skeleton[0]

    end_joint = skeleton[-1]

    # Create control hierarchy
    mc.parent(end_joint, middle_joint)
    mc.parent(middle_joint, start_joint)

    # Remove twist joints
    mc.delete(mc.listRelatives(start_joint)[0])
    mc.delete(mc.listRelatives(middle_joint)[0])

    control_skeleton = mc.listRelatives(start_joint, ad=True)
    control_skeleton.append(start_joint)
    control_skeleton.reverse()

    return control_skeleton

'''
#import arm as arm
#arm.fk_arm_setup('LeftShoulder','fk', 1, 1)
#arm.ik_arm_setup('LeftShoulder','ik', 1, 1)

def shoulder_rig():
    shoulder_joint = mc.ls(sl=True)[0]
    #need to name control with tool's naming convention
    shoulder_control = mc.circle()[0]
    mt.snap_offset_parent_matrix(shoulder_control,shoulder_joint)
    mt.matrix_parent_constraint(shoulder_control,shoulder_joint)

    #joint rotation and joint oriernt was not zero out after matrix script
    mc.xform(shoulder_joint, ro = [0,0,0], os=True)
    mc.setAttr(shoulder_joint +'.jointOrient', 0,0,0)

    return source

#arm part

#duplicate arm chain
#FK
def fk_arm_setup(start_joint,chain_type, num_upperTwist_joint, num_lowerTwist_joint):
    #FK arm
    fk_arm_joints = arm_chain_duplicate(start_joint,chain_type, num_upperTwist_joint, num_lowerTwist_joint)
    valid_joints = [fk_arm_joints[0],fk_arm_joints[int((len(fk_arm_joints)-1)/2)],fk_arm_joints[-1]]
    fk_arm_controls = list()

    for joint in valid_joints:
        fk_control = mc.circle(n=f'{joint}'+'_fk_control')[0]
        mt.snap_offset_parent_matrix(fk_control,joint)
        mt.matrix_parent_constraint(fk_control,joint)

        mc.xform(joint, ro = [0,0,0], os=True)
        mc.setAttr(joint+'.jointOrient', 0,0,0)
        fk_arm_controls.append(fk_control)

    for index in range(len(fk_arm_controls)):

        if index != 0:
            mc.parent(fk_arm_controls[index],fk_arm_controls[index-1])
            mt.matrix_parent_constraint(fk_arm_controls[index-1],fk_arm_controls[index])

    return fk_arm_controls


#IK
def ik_arm_setup(start_joint,chain_type, num_upperTwist_joint, num_lowerTwist_joint):

    ik_arm_joints = arm_chain_duplicate(start_joint,chain_type, num_upperTwist_joint, num_lowerTwist_joint)
    valid_joints = [ik_arm_joints[0],ik_arm_joints[int((len(ik_arm_joints)-1)/2)],ik_arm_joints[-1]]

    root = valid_joints[0]
    mid =  valid_joints[1]
    end =  valid_joints[2]

    #IK handle
    arm_ik_handle = mc.ikHandle(sj = root, ee = end, sol = 'ikRPsolver')
    ik_control = mc.circle()
    mt.snap_offset_parent_matrix(ik_control[0],arm_ik_handle[0])
    mc.parent(arm_ik_handle[0],ik_control[0])

    #pole vector
    pv_position = pv.calculate_pole_vector_position(root, mid, end)
    arm_pv_control = mc.circle()
    mc.move(pv_position.x, pv_position.y, pv_position.z, arm_pv_control)
    mc.makeIdentity(arm_pv_control,apply=True, t=True, r=True, s=True)
    mc.poleVectorConstraint(arm_pv_control,arm_ik_handle[0])
'''