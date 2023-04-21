import maya.cmds as cmds
import adv_scripting.rig_name as rn
import adv_scripting.matrix_tools as mt
import adv_scripting.rig.appendages.appendage as rap
import adv_scripting.utilities as utils
import logging
import pymel.core as pm

logger = logging.getLogger(__name__)


class Spine(rap.Appendage):
    def __init__(self, appendage_name, start_joint, input_matrix=None):
        rap.Appendage.__init__(self, appendage_name, start_joint, input_matrix)

    def setup(self):
        # Get the selected joint
        # Get the selected joint
        selected_joint = self.start_joint
        child_joint = cmds.listRelatives(selected_joint, ad=True, type="joint")

        dv_prefix = "driver_"

        # Copy and rename the joint hierarchy
        dv_root_joint = utils.copy_rename_joint_hierarchy(selected_joint, dv_prefix)

        # make list for ik, fk joints children
        dvchild_list = cmds.listRelatives(dv_root_joint, ad=True, type="joint")

        children = cmds.listRelatives(selected_joint, c=True, type="joint")

        # Get the hierarchy of the selected joints
        joint_hierarchy = cmds.listRelatives(dv_root_joint, allDescendents=True, type='joint')

        # Select only the joints with "spine" in their name
        spine_joints = [joint for joint in joint_hierarchy if 'spine' in joint]

        # Delete non-spine joints
        for joint in joint_hierarchy:
            if joint not in spine_joints:
                cmds.delete(joint)
        ik_spine_joints = utils.copy_rename_joint_hierarchy(dv_root_joint, "for_ik_")
        cmds.parent(ik_spine_joints, world=True)
        ik_spine_joints_list = cmds.ls(type='joint')
        ik_spine_joints_list = [joint for joint in ik_spine_joints_list if 'for_ik_' in joint]

        # list for Unparent
        spine_joints_list = cmds.listRelatives(dv_root_joint, ad=True, type='joint')
        spine_joints_list.append(dv_root_joint)

        # Unparent each joint in the hierarchy
        cmds.parent(spine_joints_list, world=True)
        cmds.delete("driver_spine_bnd_jnt_02")  # for other rig can delete  if list[x]%2 == true delete (list[1],list[3])
        cmds.delete("driver_spine_bnd_jnt_04")

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
        curve_loft = cmds.loft(copy_curve, orig_curve, ch=True, rn=True, ar=True)

        # save on valuable Joint Hierarchy
        root_joint = cmds.ls(ik_spine_joints, dag=True)

        # Unparent each joint in the hierarchy
        while cmds.listRelatives(root_joint, children=True, type='joint') is not None:
            children = cmds.listRelatives(root_joint, children=True, type='joint')
            cmds.parent(children, world=True)

        # Clean curves, history
        cmds.delete(curve_loft, constructionHistory=True)

        cmds.delete(orig_curve)
        cmds.delete(copy_curve)

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

        cmds.select("driver_spine_bnd_jnt_01", "driver_spine_bnd_jnt_03", "driver_spine_bnd_jnt_05", curve_loft[0])
        cmds.skinCluster(n="ik_skinC")
        cmds.skinCluster("ik_skinC", e=True, mi=3)

        cmds.rename(curve_loft[0], "spineSetupSurface")
        cmds.setAttr("spineSetupSurface.visibility", False)

        # No additional setup needed for setup()
        return
    """
    def build(self):
        # Create a root control, place its offsetParentMatrix to the root joint and connect the
        # resulting matrix constraint to the start_matrix attribute on the output node.
        self.root_ctrl = cmds.createNode('transform', name=rn.RigName(
            element='root',
            rig_type='ctrl',
            maya_type='transform'))
        mt.snap_offset_parent_matrix(self.root_ctrl, self.start_joint)
        mt.martix_parent_constraint(self.root_ctrl,
                                    self.start_joint,
                                    connect_output=f'{self.output}.start_matrix')
        self.makeControls()

        def makeControls():

            controlJointlist = ["for_ik_driver_spine_1", "for_ik_driver_spine_2", "for_ik_driver_spine_3",
                                "for_ik_driver_spine_4", "for_ik_driver_spine_5"]
            for selectedJoint in controlJointlist:
                # Create nurbs circle control
                createControl = cmds.circle(center=(0, 0, 0), normal=(0, 1, 0), sweep=360, radius=20, degree=3,
                                          useTolerance=False,
                                          tolerance=0, constructionHistory=False, name=selectedJoint + "_ctrl")
                controlPOS = cmds.group(createControl[0], name=createControl[0] + "_offset")
                cmds.delete(createControl, constructionHistory=True)
                mt.snap_offset_parent_matrix(controlPOS, controlJointlist)
                mt.martix_parent_constraint(controlPOS, controlJointlist, connect_output=f'{self.output}.start_matrix')

            controlDvJointlist = ["driver_spine_1", "driver_spine_3", "driver_spine_5"]

            for selectedDvJoint in controlDvJointlist:
                # Create nurbs circle control
                createControl = cmds.circle(center=(0, 0, 0), normal=(0, 1, 0), sweep=360, radius=30, degree=3,
                                          useTolerance=False,
                                          tolerance=0, constructionHistory=False, name=selectedDvJoint + "_ctrl")
                controlPOS = cmds.group(createControl[0], name=createControl[0] + "_offset")
                cmds.delete(createControl, constructionHistory=True)
                mt.snap_offset_parent_matrix(controlPOS, controlDvJointlist)
                mt.martix_parent_constraint(controlPOS, controlDvJointlist,
                                            connect_output=f'{self.output}.start_matrix')

    def connect_outputs(self):
        # Connect the start matrix on the output node to the skeleton
        cmds.connectAttr(f'{self.output}.start_matrix', f'{self.start_joint}.offsetParentMatrix')

    def cleanup(self):
        # Parent the controls to the control group.
        cmds.parent(self.root_ctrl, self.control_grp)
        # for adding prefix from original joints, it makes unique name for children.
    """


"""    
import adv_scripting.rig.appendages.spine as spine
il.reload(spine)
spine.setup("spine_bnd_jnt_01")
"""