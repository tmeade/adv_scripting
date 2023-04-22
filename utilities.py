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


def rename_hierarchy(joint, end_joint=None, unlock=True):
    '''
    Rename hierarchy from joint to end_joint.
    Ensures names follow naming convention in RigName.

    Arguments
    joint (str): joint name
    end_joint (str): end joint name
    unlock (bool): unlock all attributes

    Returns
    joint_map (dict) (str->RigName): mapping of joint name to RigName
    '''
    joint_map = dict()
    parent = cmds.listRelatives(joint, p=True)
<<<<<<< HEAD
    if parent:
        cmds.parent(joint, w=True) # Move joint to world to avoid prefix
    jnt = rig_name.RigName(joint) # Create RigName for joint
=======
    if parent: # Move joint to world to avoid prefix
        cmds.parent(joint, w=True)
    jnt = rn.RigName(joint) # Create RigName for joint
>>>>>>> 5bf65ffb7ac0340ac236a5cd1c74dda95e34ba84
    cmds.rename(joint, jnt.name)
    joint_map[jnt.name] = jnt
    if unlock: # Unlock attributes
        unlock_all(jnt.name)
    if parent: # Move joint back under parent
        cmds.parent(jnt.name, parent)

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
    middle_jnt = None
    end_jnt = joint_map[-1]
    if num_upperTwist_joints == 0:
        if num_lowerTwist_joint==0:
            middle_jnt = joint_map[(len(joint_map)-1)//2]
        elif num_lowerTwist_joints > 0 and num_lowerTwist_joints < len(joint_map):
            middle_jnt = joint_map[len(joint_map)-num_lowerTwist_joints-2]
        else:
            logger.error('num_lowerTwist_joints {num_lowerTwist_joints} not valid')
    elif num_upperTwist_joints > 0 and num_upperTwist_joints < len(joint_map):
        middle_jnt = joint_map[num_upperTwist_joints+1]
    else:
        logger.error('num_upperTwist_joints {num_upperTwist_joints} not valid')

    # Create control hierarchy
    cmds.parent(end_jnt, middle_jnt)
    cmds.parent(middle_jnt, start_jnt)

    # Remove twist joints for now
    cmds.delete(cmds.listRelatives(start_jnt)[0])
    cmds.delete(cmds.listRelatives(middle_jnt)[0])

    control_jnt = [start_jnt, middle_jnt, end_jnt]
    logger.debug(f'control joints: {control_jnt}')
    return control_jnt


def unlock_all(node):
    '''
    Unlock translate, rotation, scale
    '''
    for axis in 'XYZ':
        # Unlock keyable attributes
        for attribute in ['translate', 'rotate', 'scale', 'jointOrient']:
            if cmds.attributeQuery(attribute+axis, node=node, exists=True):
                attribute_name=f'{node}.{attribute}{axis}'
                cmds.setAttr(attribute_name, k=True, lock=False)
        # Unlock hidden attributes
        for attribute in ['jointOrient', 'preferredAngle', 'stiffness']:
            if cmds.attributeQuery(attribute+axis, node=node, exists=True):
                attribute_name=f'{node}.{attribute}{axis}'
                cmds.setAttr(attribute_name, k=False, lock=False)
    # Remove transform limits
    cmds.transformLimits(node, rm=True)
    # Unlock visibility. Set visibility nonkeyable displayed
    cmds.setAttr(f'{node}.visibility', k=False, cb=True, lock=False)

def unlock_translate(node):
    '''
    Unlock translate
    '''
    for axis in 'XYZ':
        if cmds.attributeQuery(f'translate{axis}', node=node, exists=True):
            cmds.setAttr(f'{node}.translate{axis}', k=True, lock=False)
    cmds.transformLimits(node, etx=(False,False), ety=(False,False), etz=(False,False))

def unlock_rotate(node):
    '''
    Unlock rotation
    '''
    for axis in 'XYZ':
        if cmds.attributeQuery(f'rotate{axis}', node=node, exists=True):
            cmds.setAttr(f'{node}.rotate{axis}', k=True, lock=False)
    cmds.transformLimits(node, erx=(False,False), ery=(False,False), erz=(False,False))

def unlock_scale(node):
    '''
    Unlock scale
    '''
    for axis in 'XYZ':
        if cmds.attributeQuery(f'scale{axis}', node=node, exists=True):
            cmds.setAttr(f'{node}.scale{axis}', k=True, lock=False)
    cmds.transformLimits(node, esx=(False,False), esy=(False,False), esz=(False,False))

def lock_rotate(node, raxis='Z', limits=False):
    '''
    Lock rotation except on specified rotation axis, raxis.
    If limits is True, set transform limits.
    '''
    if raxis not in 'XYZ':
        logger.error('Specified axis must be X,Y,Z')
    for axis in 'XYZ':
        if axis == raxis: # Unlock raxis
            if cmds.attributeQuery(f'rotate{axis}', node=node, exists=True):
                cmds.setAttr(f'{node}.rotate{axis}', k=True, lock=False)
            if limits: # Set transform limits
                if axis == 'X':
                    cmds.transformLimits(node,
                        rx=(-180,180), ry=(0,0), rz=(0,0),
                        erx=(True,True), ery=(True,True), erz=(True,True))
                elif axis == 'Y':
                    cmds.transformLimits(node,
                        rx=(0,0), ry=(-180,180), rz=(0,0),
                        erx=(True,True), ery=(True,True), erz=(True,True))
                elif axis == 'Z':
                    cmds.transformLimits(node,
                        rx=(0,0), ry=(0,0), rz=(-180,180),
                        erx=(True,True), ery=(True,True), erz=(True,True))
        else: # Lock other axis
            if cmds.attributeQuery(f'rotate{axis}', node=node, exists=True):
                cmds.setAttr(f'{node}.rotate{axis}', k=True, lock=True)


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
