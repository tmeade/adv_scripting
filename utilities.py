'''
utilities.py

Make sure skeleton is named correctly using
util.rename_hierarchy('root')
util.rename_skeleton_bnd('root')

Test control skeleton setup / duplicating joints using
util.create_control_joints_from_skeleton('lt_shoulder_bnd_jnt', 'lt_hand_bnd_jnt', 'fk', 1, 1)
'''
import maya.api.OpenMaya as om
import adv_scripting.rig_name as rig_name
import adv_scripting.matrix_tools as matrix_tools
import maya.cmds as cmds
import logging

logger = logging.getLogger()

import importlib as il
il.reload(matrix_tools)


def create_fk_control(joint, connect_output=None, parent_control=None, rotate_order='xyz'):
    # TODO: Set rotate order on control
    fk_control = cmds.createNode('transform', n=f'{joint}'+'_fk_ctrl_transform')
    if parent_control:
        cmds.parent(fk_control, parent_control)

    matrix_tools.snap_offset_parent_matrix(fk_control, joint)
    matrix_tools.matrix_parent_constraint(fk_control, joint, connect_output=connect_output)

    if not connect_output:
        cmds.xform(joint, ro = [0, 0, 0], os=True)
        cmds.setAttr(joint+'.jointOrient', 0,0,0)

    return fk_control


# RENAME / REPLACE SKELETON OR HIERARCHY ===============================

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
    if parent:
        cmds.parent(joint, w=True) # Move joint to world to avoid prefix
    jnt = rig_name.RigName(joint) # Create RigName for joint
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
        if jnt.element:
            jnt.rename(element=f'{jnt.element.output()}_{tag}')
        else:
            jnt.rename(element=tag)

    # Rename in maya
    cmds.rename(joint, jnt.output())
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


# DUPLICATE SKELETON ===================================================

def duplicate_skeleton(joint, end_joint=None, tag='COPY'):
    copy = cmds.duplicate(joint, po=True, n=joint+f'_{tag}')[0]
    if joint != end_joint:
        children = cmds.listRelatives(joint, typ='joint') or []
        for child in children:
            child_copy = duplicate_skeleton(child, end_joint, tag)
            cmds.parent(child_copy, copy)
    return copy


# TWOBONE IK ===========================================================

def get_joint_twobone(jnt_list, num_upperTwist_joint=None, num_lowerTwist_joint=None):
    '''
    Get start, middle, end joints for two-bone ik.
    If upperTwist is None, start defaults to first element of jnt_list.
    If lowerTwist is None, end defaults to last element of jnt_list.

    Arguments:
    jnt_list (str list) - List of all joints in a linear joint hierarchy
    num_upperTwist_joint (int/None) - Number of upperTwist joints
    num_lowerTwist_joint (int/None) - Number of lowerTwist joints

    Returns list [start, middle, end] joints.
    '''
    jnt_len = len(jnt_list)
    # jnt_list must have at least 3 joints, start middle end
    if jnt_len < 3:
        logger.error('Need at least 3 joints. start, middle, end. '\
            f'Currently only {jnt_len} joints.\n{jnt_list}')

    if num_upperTwist_joint is None: # Count joint position from lower
        if num_lowerTwist_joint is None: # Automatically detect joint position
            # upperTwist=None, lowerTwist=None
            return get_joint_twobone_default(jnt_list)
        else: # Count using only lower
            # upperTwist=None, lowerTwist=n
            if num_lowerTwist_joint > jnt_len - 3:
                logger.warning(f'num_lowerTwist_joint invalid. {jnt_list}\n'\
                    f'\tAutomatically positioning start, middle, end joints.\t'\
                    f'upperTwist:{num_upperTwist_joint}\tlowerTwist:{num_lowerTwist_joint}')
                return get_joint_twobone_default(jnt_list)
            else:
                start = jnt_list[0]
                middle = jnt_list[jnt_len - num_lowerTwist_joint - 2]
                end = jnt_list[-1]
    elif num_lowerTwist_joint is None: # Count joint position from upper
        if num_upperTwist_joint > jnt_len - 3:
            logger.warning(f'num_upperTwist_joint invalid. {jnt_list}\n'\
                f'\tAutomatically positioning start, middle, end joints.\t'\
                f'upperTwist:{num_upperTwist_joint}\tlowerTwist:{num_lowerTwist_joint}')
            return get_joint_twobone_default(jnt_list)
        else: # upperTwist=n, lowerTwist=None
            start = jnt_list[0]
            middle = jnt_list[num_upperTwist_joint + 1]
            end = jnt_list[-1]
    else: # Count using both upper and lower
        # Check if number of twist joints is applicable
        if jnt_len < num_upperTwist_joint + num_lowerTwist_joint + 3:
            logger.warning(f'Number of twist joints invalid. {jnt_list}\n'\
                f'\tAutomatically positioning start, middle, end joints.\t'\
                f'upperTwist:{num_upperTwist_joint}\tlowerTwist:{num_lowerTwist_joint}')
            return get_joint_twobone_default(jnt_list)
        else: # upperTwist=n, lowerTwist=n
            start = jnt_list[0]
            middle = jnt_list[num_upperTwist_joint + 1]
            end = jnt_list[num_upperTwist_joint + num_lowerTwist_joint + 2]
    return [start, middle, end]

def get_joint_twobone_default(jnt_list):
    '''
    Default method of getting start, middle, end joints for two-bone ik.
    Calculate middle joint position based on length of jnt_list.

    Arguments:
    jnt_list (str list) - List of all joints in a linear joint hierarchy

    Returns list [start, middle, end] joints.
    '''
    start = jnt_list[0]
    middle = jnt_list[(len(jnt_list)-1)//2]
    end = jnt_list[-1]
    return [start, middle, end]

def create_control_joints_from_skeleton(start_joint,
                                        end_joint,
                                        control_type,
                                        num_upperTwist_joint,
                                        num_lowerTwist_joint,
                                        deleteTwist=True):
    '''
    Create control skeleton of control_type and
    Create 3 control joints [start, middle, end] for two-bone ik.

    Arguments
    start_joint (str): name of start joint
    end_joint (str): name of end joint
    control_type (str): control type such as 'bnd', 'fk', 'ik'
    num_upperTwist_joint (int/None): number of upperTwist joints
    num_lowerTwist_joint (int/None): number of lowerTwist joints
    deleteTwist (bool): delete twist joints / all non-control joints

    Returns list [start, middle, end] joints.
    Each item is a tuple of (<str name>, <rig_name.RigName object>)
    '''
    # Duplicate the skeleton and parent it to the world
    skeleton = duplicate_skeleton(start_joint, end_joint, tag='COPY')
    cmds.parent(skeleton, w=True)

    # Rename the skeleton by replacing 'bnd' with the control_type.
    joint_map = replace_hierarchy(skeleton, control_type=control_type, rig_type='jnt', tag='COPY')
    joint_map = list(joint_map.items())
    #logger.debug(joint_map)

    start, middle, end = get_joint_twobone(joint_map, num_upperTwist_joint, num_lowerTwist_joint)

    # Create control hierarchy
    middle_children = cmds.listRelatives(middle[0], c=True)
    if end[0] not in middle_children:
        cmds.parent(end[0], middle[0])
    start_children = cmds.listRelatives(start[0], c=True)
    if middle[0] not in start_children:
        cmds.parent(middle[0], start[0])
    control_jnt = [start, middle, end]

    if deleteTwist: # Remove twist joints for now
        for joint in joint_map:
            if joint not in control_jnt and cmds.objExists(joint[0]):
                cmds.delete(joint[0])

    logger.debug('Control Joints:')
    for ctrl_jnt in control_jnt:
        logger.debug(f'\t{ctrl_jnt}')
    return control_jnt


# CREATE CONTROLS & GROUP ==============================================

def create_control(node, parent=None, size=1, name=None):
    '''
    Build a nurbs circle control at position of node.
    Size determines circle's radius. Move control under parent if provided.

    Arguments:
    node (str): node to match transforms and position of control
    parent (str): parent of control, if any
    size (str): control radius

    Returns name of created control.
    '''
    #logger.debug(f"node:'{node}', parent:'{parent}', size:'{size}', name:'{name}'")
    if name:
        ctrl = cmds.circle(nr=(1,0,0), c=(0,0,0), r=size, n=name)[0]
    else:
        ctrl_rn = rig_name.RigName(node).rename(rig_type='ctrl')
        ctrl = cmds.circle(nr=(1,0,0), c=(0,0,0), r=size, n=ctrl_rn.output())[0]
    logger.debug(ctrl)
    if parent:
        cmds.parent(ctrl, parent, a=True)
        # modify ctrl's transform to match parent
        cmds.matchTransform(ctrl, parent, pos=1, rot=1, scl=1, piv=1)
        # freeze transformations
        cmds.makeIdentity(ctrl, apply=True, t=1, r=1, s=1, n=0)
    # match ctrl's transform to node
    matrix_tools.snap_offset_parent_matrix(ctrl, node)
    return ctrl

def create_control_pv(pv_pos, pv_name, ik_handle, parent=None, size=1):
    '''
    Build a nurbs circle control at position of node.
    Size determines circle's radius. Move control under parent if provided.

    Arguments:
    pos (float tuple): (x,y,z) position of pole vector
    parent (str): parent of control, if any
    size (str): control radius

    Returns name of created control.
    '''
    # Create pyramid nurbs ctrl
    pts_pyramid = [\
        [0,-0.5,-1], [1,-0.5,0], [0,-0.5,1], [-1,-0.5,0], [0,-0.5,-1],
        [0,0.5,0], [0,-0.5,1], [1,-0.5,0], [0,0.5,0], [-1,-0.5,0]]
    pv_ctrl = cmds.curve(d=1, p=pts_pyramid, n=pv_name)
    cmds.xform(pv_ctrl, s=(size,size,size))
    cmds.makeIdentity(pv_ctrl, apply=True, t=1, r=1, s=1, n=0)

    # Parent pv under parent if provided
    if parent:
        cmds.parent(pv_ctrl, parent, a=True)
        # modify ctrl's transform to match parent
        cmds.matchTransform(pv_ctrl, parent, pos=1, rot=1, scl=1, piv=1)
        # freeze transformations
        cmds.makeIdentity(pv_ctrl, apply=True, t=1, r=1, s=1, n=0)
    # move pv_ctrl to absolute position
    cmds.move(pv_pos.x, pv_pos.y, pv_pos.z, pv_ctrl, a=True)
    # transfer values to offsetParentMatrix
    transform_mat = om.MMatrix(cmds.xform(pv_ctrl, q=True, m=True, ws=False))
    cmds.setAttr(f'{pv_ctrl}.offsetParentMatrix', transform_mat, typ='matrix')
    make_identity(pv_ctrl)
    cmds.poleVectorConstraint(pv_ctrl, ik_handle)
    return pv_ctrl

def create_control_copy(control, node, parent=None, size=1):
    '''
    Duplicate control object and match transforms to node.
    Scale control object by size. Move control under parent if provided.

    Arguments:
    control (str): control object to duplicate
    node (str): node to match transforms and position of control
    parent (str): parent of control, if any
    size (str): control scale

    Returns name of created control.
    '''
    ctrl_rn = rig_name.RigName(node)
    ctrl_rn.rename(rig_type='ctrl')
    ctrl = cmds.duplicate(control, po=True, n=ctrl_rn.output())[0]
    if size != 1:
        cmds.xform(ctrl, r=True, s=(size, size, size))
    #logger.debug(f'Created control: {ctrl}')
    if parent:
        cmds.parent(ctrl, parent)
        # modify ctrl's transform to match parent
        cmds.matchTransform(ctrl, parent, pos=1, rot=1, scl=1, piv=1)
        # freeze transformations
        cmds.makeIdentity(ctrl, apply=True, t=1, r=1, s=1, n=0)
    # match ctrl's transform to node
    matrix_tools.snap_offset_parent_matrix(ctrl, node)
    return ctrl

def create_group(node, parent=None, name=None):
    '''
    Build an empty group / transform at position of node.
    Move group under parent if provided.
    '''
    if name:
        grp = cmds.createNode('transform', n=name)
    else:
        grp_rn = rig_name.RigName(node).rename(rig_type='grp', maya_type='transform')
        grp = cmds.createNode('transform', n=grp_rn.output())
    #logger.debug(f'Created group: {grp}')
    if parent:
        cmds.parent(grp, parent)
        # modify grp's transform to match parent
        cmds.matchTransform(grp, parent, pos=1, rot=1, scl=1, piv=1)
        # freeze transformations
        cmds.makeIdentity(grp, apply=True, t=1, r=1, s=1, n=0)
    # match grp's transform to node
    matrix_tools.snap_offset_parent_matrix(grp, node)
    return grp


# BLEND SKELETON =======================================================

def blend_skeleton(fk_joint, ik_joint, blend_switch, blend_attribute):
    '''
    Creates blendMatrix and multMatrix to switch between joints for FK/IK control.

    Arguments
    fk_joint (str): name of FK joint
    ik_joint (str): name of IK joint
    blend_switch (str): node to connect switch attribute / envelope
    blend_attribute (str): name of switch attribute

    Returns name of resulting multMatrix
    '''
    # Create blendMatrix node
    blend_mat = cmds.createNode('blendMatrix', n=f'{blend_attribute}_blendMatrix')
    cmds.connectAttr(f'{fk_joint}.worldMatrix', f'{blend_mat}.inputMatrix', f=True)
    cmds.connectAttr(f'{ik_joint}.worldMatrix', f'{blend_mat}.target[0].targetMatrix', f=True)
    cmds.connectAttr(f'{blend_switch}.{blend_attribute}', f'{blend_mat}.envelope', f=True)

    # Create multMatrix node
    mult_mat = cmds.createNode('multMatrix', n=f'{blend_attribute}_multMatrix')
    cmds.connectAttr(f'{blend_mat}.outputMatrix', f'{mult_mat}.matrixIn[0]', f=True)
    return mult_mat

def blend_skeleton(fk_joint, ik_joint, blend_switch, blend_output, blend_attribute):
    '''
    Creates blendMatrix and multMatrix to switch between joints for FK/IK control.

    Arguments
    fk_joint (str): name of FK joint
    ik_joint (str): name of IK joint
    blend_switch (str): node to connect switch attribute / envelope
    blend_output (str): node to connect output of multMatrix
    blend_attribute (str): name of switch attribute

    Returns name of resulting multMatrix
    '''
    # Create blendMatrix node
    blend_mat = cmds.createNode('blendMatrix', n=f'{blend_attribute}_blendMatrix')
    cmds.connectAttr(f'{fk_joint}.worldMatrix', f'{blend_mat}.inputMatrix', f=True)
    cmds.connectAttr(f'{ik_joint}.worldMatrix', f'{blend_mat}.target[0].targetMatrix', f=True)
    cmds.connectAttr(f'{blend_switch}.{blend_attribute}', f'{blend_mat}.envelope', f=True)

    # Create multMatrix node
    mult_mat = cmds.createNode('multMatrix', n=f'{blend_attribute}_multMatrix')
    cmds.connectAttr(f'{blend_mat}.outputMatrix', f'{mult_mat}.matrixIn[0]', f=True)
    cmds.connectAttr(f'{mult_mat}.matrixSum', f'{blend_output}.{blend_attribute}')
    return mult_mat


# LOCK / UNLOCK ATTRIBUTES =============================================

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

# SET DISPLAY COLOR ====================================================

def display_color(node, color_index):
    '''
    Change display color using Maya's Index color.
    To change color manually, see Display > Wireframe Color

    Color Index is as follows [1,31]:
    1-black
    2-grey
    3-light grey
    4-magenta
    5-navy blue
    6-primary blue
    7-green
    8-purple
    9-pink
    10-peach
    11-brown
    12-orange
    13-primary red
    14-primary green
    15-blue
    16-white
    17-yellow
    18-pastel blue
    19-pastel green
    20-pastel pink
    21-pastel peach
    22-pastel yellow
    23-light green
    24-light brown
    25-light yellow
    26-light yellow-green
    27-light green
    28-light cyan
    29-light blue
    30-light purple
    31-light pink
    '''
    rgb = cmds.colorIndex(color_index, q=True)
    if rgb: # Color rgb values
        cmds.color(node, rgb=rgb)


# READ JOINT TRANSFORMS ================================================
# (Used in tests.py)

def read_transforms_hierarchy(node, end_node=None):
    '''
    Read transforms of all nodes in hierarchy from node to end_node.

    Arguments
    node (str): object name
    end_node (str): end object name

    Returns
    transforms (dict): mapping of transforms including
        position, translate, rotate, scale, and jointOrient for each node
    '''
    transforms = {
        node: {
            'position': None,
            'translate': None,
            'rotate': None,
            'scale': None,
            'jointOrient': None
        }
    }
    transforms[node]['position'] = read_translate(node, os=0) # world space
    transforms[node]['translate'] = read_translate(node, os=1) # local space
    transforms[node]['rotate'] = read_rotate(node) # world space
    transforms[node]['scale'] = read_scale(node) # world space
    transforms[node]['jointOrient'] = read_joint_orient(node)

    if node != end_node:
        children = cmds.listRelatives(node) or []
        for child in children:
            child_transforms = read_transforms_hierarchy(child, end_node)
            transforms.update(child_transforms)
    return transforms

def read_transforms_list(nodes):
    '''
    Read transforms of all nodes in given list.

    Arguments
    nodes (str list): list of objects

    Returns
    transforms (dict): mapping of transforms including
        position, translate, rotate, scale for each node
    '''
    transforms = dict()

    for node in nodes:
        transforms[node] = {
            'position': None,
            'translate': None,
            'rotate': None,
            'scale': None,
        }
        transforms[node]['position'] = read_translate(node, os=0)
        transforms[node]['translate'] = read_translate(node, os=1)
        transforms[node]['rotate'] = read_rotate(node)
        transforms[node]['scale'] = read_scale(node)
        transforms[node]['jointOrient'] = read_joint_orient(node)
    return transforms

def read_translate(node, os=0):
    if os:
        return cmds.xform(node, q=1, t=1, os=1) # object space
    else:
        return cmds.xform(node, q=1, t=1, ws=1) # world space

def read_rotate(node, os=0):
    if os:
        return cmds.xform(node, q=1, ro=1, os=1) # object space
    else:
        return cmds.xform(node, q=1, ro=1, ws=1) # world space

def read_scale(node, os=0):
    if os:
        return cmds.xform(node, q=1, s=1, os=1) # object space
    else:
        return cmds.xform(node, q=1, s=1, ws=1) # world space

def read_joint_orient(node):
    if cmds.objectType(node, isType='joint'):
        return cmds.joint(node, q=1, o=1)
    return None


# RESET TRANSFORMS =====================================================

def make_identity(node):
    '''
    Make identity on current node. Ignore locked attributes.
    Reset transforms including translate, rotate, scale, and joint orient.
    '''
    for attribute in ['translate', 'rotate', 'scale', 'jointOrient']:
        value = 1 if attribute == 'scale' else 0
        for axis in 'XYZ':
            if cmds.attributeQuery(attribute + axis, node=node, exists=True):
                attribute_name = '{}.{}{}'.format(node, attribute, axis)
                if not cmds.getAttr(attribute_name, lock=True):
                    cmds.setAttr(attribute_name, value)

def reset_transform(node, transform):
    '''
    Set transforms of node to given transform.

    Arguments:
    node (str): node to reset
    transform (dict): transform attributes, e.g.
        {'position': <value>,
         'translate': <value>,
         'rotate': <value>,
         'scale': <value>,
         'jointOrient': <value>
        }
    '''
    cmds.xform(node, t=transform['position'], ws=1)
    cmds.xform(node, ro=transform['rotate'], ws=1)
    cmds.xform(node, s=transform['scale'], ws=1)
    if cmds.objectType(node, isType='joint'):
        cmds.joint(node, o=transform['jointOrient'])

def reset_translate(node):
    for axis in 'XYZ':
        if cmds.attributeQuery(f'translate{axis}', node=node, exists=True):
            attribute_name = f'{node}.translate{axis}'
            if not cmds.getAttr(attribute_name, lock=True):
                cmds.setAttr(attribute_name, 0)

def reset_rotate(node):
    for axis in 'XYZ':
        if cmds.attributeQuery(f'rotate{axis}', node=node, exists=True):
            attribute_name = f'{node}.rotate{axis}'
            if not cmds.getAttr(attribute_name, lock=True):
                cmds.setAttr(attribute_name, 0)

def reset_scale(node):
    for axis in 'XYZ':
        if cmds.attributeQuery(f'scale{axis}', node=node, exists=True):
            attribute_name = f'{node}.scale{axis}'
            if not cmds.getAttr(attribute_name, lock=True):
                cmds.setAttr(attribute_name, 1)

def reset_joint_orient(node):
    if not cmds.objectType(node, isType='joint'):
        logger.error("{node} is not 'joint' type. Unable to reset jointOrient")
    for axis in 'XYZ':
        if cmds.attributeQuery(f'jointOrient{axis}', node=node, exists=True):
            attribute_name = f'{node}.jointOrient{axis}'
            if not cmds.getAttr(attribute_name, lock=True):
                cmds.setAttr(attribute_name, 0)


# GIRYANG'S JOINT UTILITIES ============================================

def copy_rename_joint_hierarchy(joint, prefix):
    # Copy the joint
    new_joint = cmds.duplicate(joint, rc=True, n=prefix + joint)[0]

    children = cmds.listRelatives(joint, c=True, type="joint")
    if children:
        # Get all children of the copied joint
        child_list = cmds.listRelatives(joint, ad=True, type="joint")[::-1]

        copied_child_list = cmds.listRelatives(new_joint, ad=True, type="joint")[::-1]

        # Rename each child *for make Unique name for each joints*
        for child, copied in zip(child_list, copied_child_list):
            new_name = prefix + child
            cmds.rename(copied, new_name)

    return new_joint

def delete_useless_joint(root, keyword):
    # Get the hierarchy of the selected joints
    joint_hierarchy = cmds.listRelatives(root, allDescendents=True, type='joint')

    # Select only the joints with "keyword" in their name
    element_joints = [joint for joint in joint_hierarchy if keyword in joint]

    # Delete non-spine joints
    for joint in joint_hierarchy:
        if joint not in element_joints:
            cmds.delete(joint)
    return

def getSurfaceCoordinate(surface, joint):
    # Get the position of the joint
    joint_position = cmds.xform(joint, query=True, translation=True, worldSpace=True)

    # Determine the closest point on the surface to the joint
    closest_point_info = cmds.skinPercent(surface, closestPoint=True, query=True, position=joint_position)

    # Convert the closest point to UV coordinates
    cmds.polyListComponentConversion(toUV=True)
    uv_values = cmds.polyEditUV(query=True, u=True, v=True)

    # Print the UV-coordinate values
    print("UV Coordinates: U={}, V={}".format(uv_values[0], uv_values[1]))

    return
