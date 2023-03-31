import maya.cmds as cmds

def matrix_parent_constraint():
    """
     Description:
         parent joint to control
     Args:
         joint : joint1
         control : nurbsCircle1
    """
    # connect control's World matrix and joint's offset matrix
    joint = 'joint1'
    control = 'nurbsCircle1'
    cmds.connectAttr(control + '.worldMatrix', joint + '.offsetParentMatrix')
    # make all channel value of joint
    # Set the translate values to zero
    cmds.setAttr(joint + '.translateX', 0)
    cmds.setAttr(joint + '.translateY', 0)
    cmds.setAttr(joint + '.translateZ', 0)
    
    # Set the rotate values to zero
    cmds.setAttr(joint + '.rotateX', 0)
    cmds.setAttr(joint + '.rotateY', 0)
    cmds.setAttr(joint + '.rotateZ', 0)
    
    # Set the joint orient values to zero
    cmds.setAttr(joint + '.jointOrientX', 0)
    cmds.setAttr(joint + '.jointOrientY', 0)
    cmds.setAttr(joint + '.jointOrientZ', 0)
    
    #this is only for single joint and single control
    
matrix_parent_constraint()
    