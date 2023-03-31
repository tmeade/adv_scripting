import maya.cmds as cmds
import adv_scripting.rig_name as rn
import adv_scripting.matrix_tools as mt
import adv_scripting.rig.appendages.appendage as rap
import pole_vector as pv
import logging
logger = logging.getLogger(__name__)


######### BECAUSE OF NAMING connvention. CANNOT DEFINE "1" and delete it ######
    
    
    
    
def LeftUpLeg_Duplicate():
    # Get the joint to duplicate
    bnd_left_leg = 'LeftUpLeg'
    # Duplicate the joint and prefix its name with 'fk_'
    fk_leg_joint = cmds.duplicate(bnd_left_leg, rc = True)
    cmds.select(fk_leg_joint, hi=True)
    fksel = cmds.ls(sl=True)
    # Add "fk_" prefix to all children's names
    for child in fksel:
        fk_child_name = 'fk_' + child
        cmds.select(child)
        cmds.rename(child, fk_child_name)
    # Unparent the duplicated joint
    cmds.parent('fk_LeftUpLeg1', world=True)
    
    # Duplicate the joint and prefix its name with ik_'
    ik_leg_joint = cmds.duplicate(bnd_left_leg, rc = True)
    cmds.select(ik_leg_joint, hi=True)
    iksel = cmds.ls(sl=True)
    # Add "ik_" prefix to all children's names
    for child in iksel:
        ik_child_name = 'ik_' + child
        cmds.select(child)
        cmds.rename(child, ik_child_name)
    # Unparent the duplicated joint
    cmds.parent('ik_LeftUpLeg1', world=True)
    

def fksetup():

    #create ctrlsfor each fk joint ******NOTE(fk up leg is not in the fkjoints...)
    fkjoints = cmds.listRelatives('fk_LeftUpLeg1', allDescendents=True, type='joint')

    for eachJoint in fkjoints:
        # Create a NURBS circle
        ctrlCircle = cmds.circle(name='ctrl_'+eachJoint, nr=(1,0,0), c=(0, 0, 0), r=1.5, n='Circle1_%s' % eachJoint)
        # Create a NURBS circle offset grp
        ctrloffset = mc.group(ctrlCircle[0], name=ctrlCircle[0] + "_offset")
        # Match the circle to the joint using the snap_offset_parent_matrix function
        mt.snap_offset_parent_matrix(ctrloffset, eachJoint)
        # Create a matrix parent constraint between the joint and the circle
        mt.matrix_parent_constraint(ctrloffset, eachJoint)