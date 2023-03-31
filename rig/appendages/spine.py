import maya.cmds as mc
import adv_scripting.rig.name as rn
import adv_scripting.martix_tools as mt
import adv_scripting.rig.appendages.appendage as rap
import logging
import pymel.core as pm
logger = logging.getLogger(__name__)


import importlib as il
il.reload(rap)
il.reload(mt)

class Root(rap.Appendage):
    def __init__(self, appendage_name, start_joint, input_matrix):
        rap.Appendage.__init__(self, appendage_name, start_joint, input_matrix)
    def setup(self):
        ### Select root first ###

        def main():
            dv_copied()
            Delete_non_spine()
            Unparent_and_clean_driver_joint()
            ribbon_setup()


        # for adding prefix from original joints, it makes unique name for children.
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

        def dv_copied():

            # Get the selected joint
            selectionCheck = mc.ls(sl=1, type="joint")
            if not selectionCheck:
                mc.warning("Please select a root joint.")
            else:
                selected_joint = mc.ls(sl=True)[0]
                child_joint = mc.listRelatives(selected_joint, ad=True, type="joint")

                dv_prefix = "driver_"

                # Copy and rename the joint hierarchy
                dv_root_joint = copy_rename_joint_hierarchy(selected_joint, dv_prefix)

                # make list for ik, fk joints children
                dvchild_list = mc.listRelatives(dv_root_joint, ad=True, type="joint")

                children = mc.listRelatives(selected_joint, c=True, type="joint")

        def Delete_non_spine():

            # Get the selected joints
            selected_joints = mc.ls(selection=True, type='joint')

            # Get the hierarchy of the selected joints
            joint_hierarchy = mc.listRelatives(selected_joints, allDescendents=True, type='joint')

            # Select only the joints with "spine" in their name
            spine_joints = [joint for joint in joint_hierarchy if 'spine' in joint]

            # Delete non-spine joints
            for joint in joint_hierarchy:
                if joint not in spine_joints:
                    mc.delete(joint)
            copy_rename_joint_hierarchy("driver_root", "for_ik_")
            mc.parent("for_ik_driver_spine_1", world=True)
            mc.delete("for_ik_driver_root")

        def Unparent_and_clean_driver_joint():
            # Unparent the joint hierarchy group
            root_joint = mc.ls("driver_root", dag=True)

            # Unparent each joint in the hierarchy
            while mc.listRelatives(root_joint, children=True, type='joint') is not None:
                children = mc.listRelatives(root_joint, children=True, type='joint')
                mc.parent(children, world=True)
            mc.delete("driver_root")
            mc.delete("driver_spine_2")  # for other rig can delete  if list[x]%2 == true delete (list[1],list[3])
            mc.delete("driver_spine_4")

        def ribbon_setup():
            # Get the selected joint group
            sel_joints = mc.ls("for_ik_driver_spine_1", type="joint")
            # Get the hierarchy of the selected joints
            joint_hierarchy = mc.listRelatives(sel_joints, allDescendents=True, type='joint')[::-1]

            # Get the first and last joints
            start_joint = sel_joints[0]
            end_joint = joint_hierarchy[-1]

            # Create an IK handle for the spine
            ik_handle = mc.ikHandle(startJoint=start_joint, endEffector=end_joint, ccv=True, scv=False,
                                    solver="ikSplineSolver")
            mc.delete("ikHandle1")

            # Get the original curve
            orig_curve = "curve1"

            # Duplicate the original curve
            copy_curve = mc.duplicate(orig_curve)[0]

            # Translate the copy curve +3 on X-axis
            mc.move(3, 0, 0, orig_curve, relative=True)

            # Translate the copy curve -3 on X-axis
            mc.move(-3, 0, 0, copy_curve, relative=True)

            # Make loft curve 1,2
            mc.loft('curve2', 'curve1', ch=True, rn=True, ar=True)

            # save on valuable Joint Heierarchy
            root_joint = mc.ls("for_ik_driver_spine_1", dag=True)

            # Unparent each joint in the hierarchy
            while mc.listRelatives(root_joint, children=True, type='joint') is not None:
                children = mc.listRelatives(root_joint, children=True, type='joint')
                mc.parent(children, world=True)

            # Clean curves, history
            mc.delete("curve1")
            mc.delete("curve2")

            mc.delete("loftedSurface1", constructionHistory=True)

            """# Make uvPin node, connect surface with joints.
            mc.createNode("uvPin", n='hybridSpine_uvPin')
            for joint, in zip(root_joint, 5):
                mc.connectAttr"""
            # uvpin's Output Matrix stop on the [0] cannot increase [1]..[2].. so, I just choose nhair-ribbon process

            # pymel for createHair command
            mc.select("loftedSurface1", r=True)
            pm.language.Mel.eval("createHair 1 5 10 0 0 1 0 5 0 1 1 1;")
            created_hairsystem = pm.PyNode("hairSystem1")

            # Get the hierarchy of the selected group
            hairSys_hierarchy = mc.listRelatives("hairSystem1Follicles", allDescendents=True, type='transform')

            # Select only the groups with "curve" in their name
            groups_del = [group for group in hairSys_hierarchy if 'curve' in group]

            # Delete "curve" groups and clean
            for group in groups_del:
                mc.delete(group)
            mc.delete("pfxHair1")
            mc.delete("nucleus1")
            mc.delete("hairSystem1")

            hairSys_hierarchy = mc.listRelatives("hairSystem1Follicles", allDescendents=True,
                                                 type='transform')  # override

            follicle_ls = [follicle for follicle in hairSys_hierarchy if 'Shape' not in follicle]
            ikJoint_ls = ["for_ik_driver_spine_1", "for_ik_driver_spine_2", "for_ik_driver_spine_3",
                          "for_ik_driver_spine_4", "for_ik_driver_spine_5"]

            for follicle, ikJ in zip(follicle_ls, ikJoint_ls):
                mc.parent(ikJ, follicle)
                mc.rename(follicle, "spine_follicle_1")

            mc.select(cl=True)

            mc.select("driver_spine_1", "driver_spine_3", "driver_spine_5", "loftedSurface1")
            mc.skinCluster(n="ik_skinC")
            mc.skinCluster("ik_skinC", e=True, mi=3)

            mc.rename("loftedSurface1", "spineSetupSurface")
            mc.setAttr("spineSetupSurface.visibility", False)

        main()
        # No additional setup needed for setup()
        return

    def build(self):
        # Create a root control, place its offsetParentMatrix to the root joint and connect the
        # resulting matrix constraint to the start_matrix attribute on the output node.
        self.root_ctrl = mc.createNode('transform', name=rn.RigName(
                                                            element='root',
                                                            rig_type='ctrl',
                                                            maya_type='transform'))
        mt.snap_offset_parent_matrix(self.root_ctrl, self.start_joint)
        mt.martix_parent_constraint(self.root_ctrl,
                                    self.start_joint,
                                    connect_output=f'{self.output}.start_matrix')

        def makeControls():

            controlJointlist = ["for_ik_driver_spine_1", "for_ik_driver_spine_2", "for_ik_driver_spine_3",
                                "for_ik_driver_spine_4", "for_ik_driver_spine_5"]
            for selectedJoint in controlJointlist:
                # Create nurbs circle control
                createControl = mc.circle(center=(0, 0, 0), normal=(0, 1, 0), sweep=360, radius=20, degree=3,
                                          useTolerance=False,
                                          tolerance=0, constructionHistory=False, name=selectedJoint + "_ctrl")
                controlPOS = mc.group(createControl[0], name=createControl[0] + "_offset")
                mc.delete(createControl, constructionHistory=True)
                mt.snap_offset_parent_matrix(controlPOS, controlJointlist)
                mt.martix_parent_constraint(controlPOS, controlJointlist, connect_output=f'{self.output}.start_matrix')

            controlDvJointlist = ["driver_spine_1", "driver_spine_3", "driver_spine_5"]

            for selectedDvJoint in controlDvJointlist:
                # Create nurbs circle control
                createControl = mc.circle(center=(0, 0, 0), normal=(0, 1, 0), sweep=360, radius=30, degree=3,
                                          useTolerance=False,
                                          tolerance=0, constructionHistory=False, name=selectedDvJoint + "_ctrl")
                controlPOS = mc.group(createControl[0], name=createControl[0] + "_offset")
                mc.delete(createControl, constructionHistory=True)
                mt.snap_offset_parent_matrix(controlPOS, controlDvJointlist)
                mt.martix_parent_constraint(controlPOS, controlDvJointlist, connect_output=f'{self.output}.start_matrix')

    def connect_outputs(self):
        # Connect the start matrix on the output node to the skeleton
        mc.connectAttr(f'{self.output}.start_matrix', f'{self.start_joint}.offsetParentMatrix')

    def cleanup(self):
        # Parent the controls to the control group.
        mc.parent(self.root_ctrl, self.control_grp)

