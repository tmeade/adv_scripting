import logging
import maya.api.OpenMaya as om
import maya.cmds as mc
import adv_scripting.rig_name as rn

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
    parent = mc.listRelatives(source, parent=True)
    if parent:
        # TODO: This is a useful funciton on it's own.  Create a new function to return the offset
        offset_matrix = (om.MMatrix(mc.xform(target, q=True, m=True, ws=True)) *
                         om.MMatrix(mc.xform(parent, q=True, m=True, ws=True)).inverse())
    else:
        offset_matrix = mc.xform(target, q=True, m=True, ws=True)

    # Set the source object's offsetParentMatrix to the offset
    mc.setAttr(f'{source}.offsetParentMatrix', offset_matrix, type='matrix')

    # TODO: break this out into it's own function.  YES, its short.. but we'll use it a lot.
    # zero out source object's object transform
    identity_mtx = om.MMatrix()
    mc.xform(source, m=identity_mtx, os=True)

    return offset_matrix

def matrix_parent_constraint(driver, driven, connect_output=None):
    '''
    Description:
        A function to connect "control" to a driven object using offset parent matrix
    Arguments:
        driver (str): name of the object that will control the matrix of the other.
        derven (str): Name of the object whose parentOffset matrix will be determined by the offset
                    and transform of the driver.
    Returns:
        offset_matriix (MMatrix): offset beteween driver and driven.
    '''

    # TODO: This is a useful funciton on it's own.  Create a new function to return the offset
    offset_matrix = (om.MMatrix(mc.getAttr(f'{driven}.worldMatrix[0]')) *
                    om.MMatrix(mc.getAttr(f'{driver}.worldInverseMatrix[0]')))

    # Create a mult matrix node.  It will have three inpusts:
    #       in[0]: offset matrix from driver.
    #       in[1]: The world marrix of the driver.
    #       in[2]: The inverse worldInverseMatrix of the driven objects parent.
    mult_matrix_node = mc.createNode('multMatrix')
    mc.setAttr(f'{mult_matrix_node}.matrixIn[0]', offset_matrix, type='matrix')
    mc.connectAttr(f'{driver}.worldMatrix[0]', f'{mult_matrix_node}.matrixIn[1]')

    driven_parent = mc.listRelatives(driven, parent=True)
    if driven_parent:
        mc.connectAttr(f'{driven_parent[0]}.worldInverseMatrix[0]',
                       f'{mult_matrix_node}.matrixIn[2]')

    # Connect resulting matrix to specified output or to the driven's offsetParentMatrix
    if connect_output:
        mc.connectAttr(f'{mult_matrix_node}.matrixSum', f'{connect_output}')
    else:
        mc.connectAttr(f'{mult_matrix_node}.matrixSum', f'{driven}.offsetParentMatrix')

    # TODO: break this out into it's own function.  YES, its short.. but we'll use it a lot.
    # zero out source object
    identity_mtx = om.MMatrix()
    mc.xform(driven, m=identity_mtx, os=True)

    return offset_matrix
