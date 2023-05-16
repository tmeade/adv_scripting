import logging
import maya.api.OpenMaya as om
import maya.cmds as mc
import adv_scripting.rig_name as rn
import rig_name

logger = logging.getLogger(__name__)

def snap_offset_parent_matrix(source, target):
    '''
    Description:
        Matches the parent offset matrix of one transform to a target transform.
    Arguments:
        source (str): Object to move
        target (str): Object to move to
    Returns:
        offsetParentMatrix (list)
    '''
    # Set the source's offestParentMatrix to target's world space matrix to acount
    # for source's parent offset.
    parent = mc.listRelatives(source, parent=True, f=True)
    if parent:
        # TODO: This is a useful funciton on it's own.  Create a new function to return the offset
        offset_matrix = (om.MMatrix(mc.xform(target, q=True, m=True, ws=True)) *
                         om.MMatrix(mc.xform(parent, q=True, m=True, ws=True)).inverse())
    else:
        offset_matrix = mc.xform(target, q=True, m=True, ws=True)

    # Set the source object's offsetParentMatrix to the offset
    mc.setAttr(f'{source}.offsetParentMatrix', offset_matrix, type='matrix')

    # Zero out the object space transforms
    make_identity(source)

    return offset_matrix

def matrix_parent_constraint(driver, driven, connect_output=None):
    '''
    Description:
        A function to connect "control" to a driven object using offset parent matrix
    Arguments:
        driver (str): name of the object that will control the matrix of the other.  This will
                      accept node names ('input_grp') and plugs ('input_grp.input_matrix').  The
                      names will get converted to plugs with the worldMatrix output.
        derven (str): Name of the object whose parentOffset matrix will be determined by the offset
                    and transform of the driver.
    Returns:
        offset_matriix (MMatrix): offset beteween driver and driven.
    '''

    # Allow driver to be a node name or plug name
    # TODO: Add some additional checks on driver type
    driver_plug = driver
    if '.' not in driver_plug:
        driver_plug = f'{driver}.worldMatrix[0]'

    # Get offset between driver and driven
    offset_matrix = (om.MMatrix(mc.getAttr(f'{driven}.worldMatrix[0]')) *
                    om.MMatrix(mc.getAttr(driver_plug)).inverse())

    # Create a mult matrix node.  It will have three inpusts:
    #       in[0]: offset matrix from driver.
    #       in[1]: The world matrix of the driver.
    #       in[2]: The worldInverseMatrix of the driven objects parent.
    name_mult = rig_name.RigName(driven).remove(rig_type=1, maya_type=1).output()
    mult_matrix_node = mc.createNode('multMatrix', n=f'{name_mult}_parentConstraint_multMatrix')
    mc.setAttr(f'{mult_matrix_node}.matrixIn[0]', offset_matrix, type='matrix')
    mc.connectAttr(driver_plug, f'{mult_matrix_node}.matrixIn[1]')

    driven_parent = mc.listRelatives(driven, parent=True, f=True)
    if driven_parent:
        mc.connectAttr(f'{driven_parent[0]}.worldInverseMatrix[0]',
                       f'{mult_matrix_node}.matrixIn[2]')

    # Connect resulting matrix to specified output or to the driven's offsetParentMatrix
    if connect_output:
        mc.connectAttr(f'{mult_matrix_node}.matrixSum', f'{connect_output}')
    else:
        mc.connectAttr(f'{mult_matrix_node}.matrixSum', f'{driven}.offsetParentMatrix')
        make_identity(driven)

    return offset_matrix

def make_identity(transform):
    '''
    Description:
        Set matrix on specified transform to identity.
    Args:
        transform (str): Name of transform node to set.
    Return (list): Matrix of control
    '''
    identity_mtx = om.MMatrix()
    mc.xform(transform, m=identity_mtx.setToIdentity(), os=True)
    #logger.info(f'Set identity on {transform}')
