'''
utilities.py

Make sure skeleton is named correctly using
util.rename_hierarchy('root')
util.rename_skeleton_bnd('root')

Test control skeleton setup / duplicating joints using
util.create_control_joints_from_skeleton('lt_shoulder_bnd_jnt', 'lt_hand_bnd_jnt', 'fk', 1, 1)
'''
import adv_scripting.rig_name as rig_name
import adv_scripting.matrix_tools as matrix_tools
import maya.cmds as cmds
import logging

logger = logging.getLogger()

import importlib as il
il.reload(matrix_tools)

def create_fk_control(joint, connect_output=None):
    fk_control = cmds.createNode('transform', n=f'{joint}'+'_fk_ctrl_transform')
    matrix_tools.snap_offset_parent_matrix(fk_control, joint)
    matrix_tools.matrix_parent_constraint(fk_control, joint, connect_output=connect_output)

    cmds.xform(joint, ro = [0, 0, 0], os=True)
    cmds.setAttr(joint+'.jointOrient', 0,0,0)

    return fk_control


def rename_hierarchy(joint, end_joint=None):
    '''
    Rename hierarchy from joint to end_joint.
    Ensures names follow naming convention in RigName.

    Arguments
    joint (str): joint name
    end_joint (str): end joint name

    Returns
    joint_map (dict) (str->RigName): mapping of joint name to RigName
    '''
    joint_map = dict()
    parent = cmds.listRelatives(joint, p=True)
    if parent:
        cmds.parent(joint, w=True) # Move joint to world to avoid prefix
    jnt = rig_name.RigName(joint) # Create RigName for joint
    cmds.rename(joint, jnt.name)
    joint_map[jnt.name] = jnt
    if parent:
        cmds.parent(jnt.name, parent) # Move joint back under parent

    if joint != end_joint:
        children = cmds.listRelatives(jnt.name) or []
        for child in children:
            child_joint_map = rename_hierarchy(child, end_joint)
            joint_map.update(child_joint_map)
    return joint_map


def replace_hierarchy(joint, end_joint=None,
                    full_name=None,
                    side=None,
                    region=None,
                    element=None,
                    control_type=None,
                    rig_type=None,
                    maya_type=None,
                    position=None,
                    tag=None):
    '''
    Rename joint hierarchy and replace name of each joint. Remove tag from names.
    e.g. replace_hierarchy(start_joint, end_joint=end_joint, control_type='bnd', rig_type='jnt')

    Arguments
    joint (str): joint name
    end_joint (str): end joint name

    Returns
    joint_map (dict) (str->RigName): mapping of joint name to RigName

    Warning: Needs fix, fails operation if running multiple times on same input.
    '''
    joint_map = dict()
    #parent = cmds.listRelatives(joint, typ='joint', p=True)
    #if parent: cmds.parent(joint, w=True) # Move joint to world to avoid prefix

    if tag:
        jnt_name = joint.replace(f'_{tag}', '')
    else:
        jnt_name = joint

    # Create RigName object and rename
    jnt = rig_name.RigName(jnt_name)
    jnt.rename(full_name, side, region, element, control_type, rig_type, maya_type, position)

    # Check for duplicates
    dupe = cmds.ls(jnt.output())
    if dupe:
        jnt.rename(element=f'{jnt.element.output()}_{tag}')

    # Rename in maya
    cmds.rename(joint, jnt.name)
    joint_map[jnt.name] = jnt

    #if parent: cmds.parent(jnt.fullname, parent) # Move joint back under parent
    if joint != end_joint:
        children = cmds.listRelatives(jnt.name, typ='joint') or []
        for child in children:
            child_joint_map = replace_hierarchy(child, end_joint, full_name,
                side, region, element, control_type, rig_type, maya_type, position, tag)
            joint_map.update(child_joint_map)
    return joint_map


def rename_skeleton_bnd(start_joint, end_joint=None):
    replace_hierarchy(start_joint, end_joint=end_joint, control_type='bnd', rig_type='jnt')

def rename_skeleton_fk(start_joint, end_joint=None):
    replace_hierarchy(start_joint, end_joint=end_joint, control_type='fk', rig_type='jnt')

def rename_skeleton_ik(start_joint, end_joint=None):
    replace_hierarchy(start_joint, end_joint=end_joint, control_type='ik', rig_type='jnt')


def duplicate_skeleton(joint, end_joint=None, tag='COPY'):
    copy = cmds.duplicate(joint, po=True, n=joint+f'_{tag}')[0]
    if joint != end_joint:
        children = cmds.listRelatives(joint, typ='joint') or []
        for child in children:
            child_copy = duplicate_skeleton(child, end_joint, tag)
            cmds.parent(child_copy, copy)
    return copy


def create_control_joints_from_skeleton(start_joint,
                                        end_joint,
                                        control_type,
                                        num_upperTwist_joints,
                                        num_lowerTwist_joints):
    # Duplicate the skeleton and parent it to the world
    skeleton = duplicate_skeleton(start_joint, end_joint, tag='COPY')
    cmds.parent(skeleton, w=True)
    print(skeleton)

    # Rename the skeleton by replaceing 'bnd' with the control_type.
    joint_map = replace_hierarchy(skeleton, control_type=control_type, rig_type='jnt', tag='COPY')
    joint_map = list(joint_map.items())
    logger.debug(joint_map)

    start_jnt = joint_map[0]
    end_jnt = joint_map[-1]
    middle_jnt = joint_map[(len(joint_map)-1)//2]

    # Create control hierarchy
    cmds.parent(end_jnt, middle_jnt)
    cmds.parent(middle_jnt, start_jnt)

    # Remove twist joints for now
    cmds.delete(cmds.listRelatives(start_jnt)[0])
    cmds.delete(cmds.listRelatives(middle_jnt)[0])

    control_jnt = [start_jnt, middle_jnt, end_jnt]
    logger.debug(f'control joints: {control_jnt}')
    return control_jnt

#Giryang utility
def copy_rename_joint_hierarchy(joint, prefix):
    # Copy the joint
    new_joint = mc.duplicate(joint, rc=True, n=prefix + joint)[0]

    children = mc.listRelatives(joint, c=True, type="joint")
    if children:
        # Get all children of the copied joint
        child_list = mc.listRelatives(joint, ad=True, type="joint")[::-1]

        copied_child_list = mc.listRelatives(new_joint, ad=True, type="joint")[::-1]

        # Rename each child *for make Unique name for each joints*
        for child, copied in zip(child_list, copied_child_list):
            new_name = prefix + child
            mc.rename(copied, new_name)

    return new_joint
