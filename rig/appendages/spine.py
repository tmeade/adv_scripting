import maya.cmds as cmds
import adv_scripting.rig_name as rn
import adv_scripting.matrix_tools as mt
import adv_scripting.rig.appendages.appendage as rap
import adv_scripting.utilities as utils
import logging
import pymel.core as pm

import importlib as il
il.reload(utils)

logger = logging.getLogger(__name__)


class Spine(rap.Appendage):
    def __init__(self, appendage_name, start_joint, input_matrix=None):
        self.side = None
        self.element = None
        rap.Appendage.__init__(self, appendage_name, start_joint, input_matrix)

    def setup(self):
        
        # Get the selected joint
        selected_joint = self.start_joint
        child_joint = cmds.listRelatives(selected_joint, ad=True, type="joint")

        dv_prefix = 'driver_'
        
        """dv_prefix = rn.RigName(element=self.element, side=self.side,
            control_type='driver', rig_type='jnt', maya_type=None) TypeError: expected string or bytes-like object  """
        

        # Copy and rename the joint hierarchy 
        dv_root_joint = utils.copy_rename_joint_hierarchy(selected_joint, dv_prefix)
        
        
        # make list for ik, fk joints children
        dvchild_list = cmds.listRelatives(dv_root_joint, ad=True, type="joint")

        children = cmds.listRelatives(selected_joint, c=True, type="joint")
        
        utils.delete_useless_joint(dv_root_joint, 'spine')
        """
        (root, keyword)
        root : root joint for delete useless joints children
        keyword : Select keywords not to delete
        """
        
        ik_spine_joints = utils.copy_rename_joint_hierarchy(dv_root_joint, "for_ik_")
        
        cmds.parent(ik_spine_joints, world=True)
        ik_spine_joints_list = cmds.ls(type='joint')
        ik_spine_joints_list = [joint for joint in ik_spine_joints_list if 'for_ik_' in joint]
        
        # list for Unparent
        spine_joints_list = cmds.listRelatives(dv_root_joint, ad=True, type='joint')
        spine_joints_list.append(dv_root_joint)

        # Unparent each joint in the hierarchy
        cmds.parent(spine_joints_list, world=True)
        
        # Delete [odd] joint for binding driver joint 
        for i, joint in enumerate(spine_joints_list):
            if i % 2 != 0:
                cmds.delete(spine_joints_list[i])
        
        # Get the selected joint group
        sel_joints = cmds.ls(ik_spine_joints, type="joint")
        # Get the hierarchy of the selected joints
        joint_hierarchy = cmds.listRelatives(sel_joints, allDescendents=True, type='joint')[::-1]

        # Get the first and last joints
        start_joint = sel_joints[0]
        end_joint = joint_hierarchy[-1]

        # Create an IK handle for the spine
        ik_handle = cmds.ikHandle(startJoint=start_joint, endEffector=end_joint, ccv=True, scv=False,
                                solver="ikSplineSolver")

        nn_ikhandle = cmds.ls(ik_handle, type="ikHandle")
        cmds.delete(nn_ikhandle)

        # Get the original curve
        orig_curve = cmds.ls(ik_handle, type="transform")

        # Duplicate the original curve
        copy_curve = cmds.duplicate(orig_curve)

        # Translate the copy curve +3 on X-axis
        cmds.move(3, 0, 0, orig_curve, relative=True)

        # Translate the copy curve -3 on X-axis
        cmds.move(-3, 0, 0, copy_curve, relative=True)

        # Make loft curve 1,2
        curve_loft = cmds.loft(copy_curve, orig_curve, ch=True, rn=True, ar=True, n="spineSetupSurface")

        # save on valuable Joint Hierarchy
        root_joint = cmds.ls(ik_spine_joints, dag=True)
        
        # Clean curves, history
        cmds.delete(curve_loft, constructionHistory=True)

        cmds.delete(orig_curve)
        cmds.delete(copy_curve)
        
        cmds.select(curve_loft[0])
        cmds.select(root_joint, add=True)
        cmds.UVPin()
        
        # Tried to make as node without select but not moving
        """
        sPin = cmds.createNode('uvPin', n='spineUvPin')
        cmds.connectAttr('spineSetupSurfaceShape.worldSpace', f'{sPin}.deformedGeometry')
        cmds.connectAttr('spineSetupSurfaceShapeOrig.local', f'{sPin}.originalGeometry')
        
        
        for i, joint in enumerate(root_joint):
            cmds.connectAttr(f'spineUvPin.outputMatrix[{i}]', f'{joint}.offsetParentMatrix')
        """
        
        ############################# Old Hair, ik system ################################
        """
        # pymel for createHair command
        cmds.select(curve_loft[0], r=True)
        pm.language.Mel.eval("createHair 1 5 10 0 0 1 0 5 0 1 1 1;")
        created_hairsystem = pm.PyNode("hairSystem1")

        # Get the hierarchy of the selected group
        hairSys_hierarchy = cmds.listRelatives("hairSystem1Follicles", allDescendents=True, type='transform')

        # Select only the groups with "curve" in their name
        groups_del = [group for group in hairSys_hierarchy if 'curve' in group]

        # Delete "curve" groups and clean
        for group in groups_del:
            cmds.delete(group)
        cmds.delete("pfxHair1")
        cmds.delete("nucleus1")
        cmds.delete("hairSystem1")

        hairSys_hierarchy = cmds.listRelatives("hairSystem1Follicles", allDescendents=True,
                                             type='transform')  # override

        follicle_ls = [follicle for follicle in hairSys_hierarchy if 'Shape' not in follicle]

        for follicle, ikJ in zip(follicle_ls, ik_spine_joints_list):
            cmds.parent(ikJ, follicle)
            cmds.rename(follicle, "spine_follicle_1")

        cmds.select(cl=True)
        """
        #######################################################################################
        cmds.select("driver_spine_bnd_jnt_01", "driver_spine_bnd_jnt_03", "driver_spine_bnd_jnt_05", curve_loft[0])
        cmds.skinCluster(n="ik_skinC")
        cmds.skinCluster("ik_skinC", e=True, mi=3)

        cmds.setAttr("spineSetupSurface.visibility", False)
        
        
        # No additional setup needed for setup()
        return
        
    def build(self):
        # Implement build method here
        spine_joints_list = cmds.ls(type='joint')
        spine_joints_list = [joint for joint in spine_joints_list if 'spine_' in joint]
        spine_joints_list = [joint for joint in spine_joints_list if not 'for_ik_' or not 'driver_' in joint]
        
        ik_spine_joints_list = cmds.ls(type='joint')
        ik_spine_joints_list = [joint for joint in ik_spine_joints_list if 'for_ik_' in joint]
        
        for sjoint, ijoint in zip(spine_joints_list, ik_spine_joints_list):
            mt.matrix_parent_constraint(ijoint,sjoint)

    def cleanup(self):
        # Implement cleanup method here
        pass

    def connect_outputs(self):
        # Implement connect_outputs method here
        pass

 # Maya Test
spine = Spine("spine", "spine_bnd_jnt_01")