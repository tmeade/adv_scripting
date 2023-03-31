import maya.cmds as cmds
import maya.api.OpenMaya as om

def snap_offset_parent_matrix():
    """
     Description:
         Set target's matrix to source's matrix (snapping without changing values)
     Args:
         sourceObj : joint1
         targetObj : nurbsCircle1
    """
    sourceObj = 'joint1'
    targetObj = 'nurbsCircle1'
    # joint1 can be sourceObj
    joint_world_mtx = cmds.xform(sourceObj, query=True, worldSpace=True, matrix=True)
    joint_math_mtx = om.MMatrix(joint_world_mtx)
    # nurbsCircle1 can be targetObj or offset group for snapping
    target_world_mtx = cmds.xform(targetObj, query=True, worldSpace=True, matrix=True)
    target_math_mtx = om.MMatrix(target_world_mtx)    
    
    #offset_matrix = target_math_mtx * joint_math_mtx.inverse()
    
    # Set target's matrix to source's matrix
    cmds.setAttr(targetObj + '.offsetParentMatrix',joint_math_mtx, type='matrix')
    
snap_offset_parent_matrix()