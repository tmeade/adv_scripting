import maya.cmds as cmds
import adv_scripting.rig_name as rig_name
import adv_scripting.matrix_tools as matrix_tools
import adv_scripting.rig.appendages.appendage as appendage
import adv_scripting.utilities as utils
import logging
import pymel.core as pm

import importlib as il

il.reload(utils)

logger = logging.getLogger(__name__)


class Spine(appendage.Appendage):
    def __init__(self, appendage_name, start_joint, input_matrix=None):
        self.side = None
        self.element = None
        self.spine_joint_num = 0
        appendage.Appendage.__init__(self, appendage_name, start_joint, input_matrix)


    def setup(self):


        self.bnd_joints = dict()
        self.bnd_joints['start_joint'] = self.start_joint
        #print(self.bnd_joints)

        # Get the selected joint
        selected_joint = self.start_joint
        child_joint = cmds.listRelatives(selected_joint, ad=True, type="joint")

        dv_prefix = 'driver_'
        fk_prefix = 'fk_follow_'

        """dv_prefix = rig_name.RigName(element=self.element, side=self.side,
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


        ik_spine_joints = utils.copy_rename_joint_hierarchy(dv_root_joint, fk_prefix)

        cmds.parent(ik_spine_joints, world=True)
        ik_spine_joints_list = cmds.ls(type='joint')
        ik_spine_joints_list = [joint for joint in ik_spine_joints_list if fk_prefix in joint]



        # list for Unparent
        spine_joints_list = cmds.listRelatives(dv_root_joint, ad=True, type='joint')
        spine_joints_list.append(dv_root_joint)

        bnd_joints_list = cmds.ls(type='joint')
        bnd_joints_list = [joint for joint in bnd_joints_list if 'spine_' in joint]
        bnd_joints_list = [joint for joint in bnd_joints_list if not fk_prefix or not dv_prefix in joint]

        self.spine_joint_num = len(ik_spine_joints_list)
        if self.spine_joint_num > 0:
            for index in range(self.spine_joint_num):
                self.bnd_joints[f'spine_{index+1}'] = bnd_joints_list[index]

        print(self.bnd_joints)
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
        childs_joint = cmds.listRelatives(root_joint, ad=True, type="joint")

        # Clean curves, history
        cmds.delete(curve_loft, constructionHistory=True)

        cmds.delete(orig_curve)
        cmds.delete(copy_curve)

        cmds.parent(root_joint[0], self.appendage_grp)
        for joint in childs_joint:
            cmds.parent(joint, self.appendage_grp)

        """
        cmds.select(curve_loft[0])
        cmds.select(root_joint, add=True)
        cmds.UVPin()
        """

        # Tried to make as node without select but not moving
        tempBS = cmds.blendShape(curve_loft[0], n='tempBS')
        sPin = cmds.createNode('uvPin', n='spineUvPin')
        cmds.setAttr("spineUvPin.tangentAxis", 1)
        cmds.connectAttr('spineSetupSurfaceShape.worldSpace', f'{sPin}.deformedGeometry')
        cmds.connectAttr('spineSetupSurfaceShapeOrig.local', f'{sPin}.originalGeometry')

        cmds.delete(tempBS)

        for i, joint in enumerate(root_joint):
            cmds.setAttr(f'{joint}.inheritsTransform', 0)
            cmds.connectAttr(f'spineUvPin.outputMatrix[{i}]', f'{joint}.offsetParentMatrix')
            cmds.setAttr(f'{sPin}.coordinate[{i}].coordinateU', 0.5)
            cmds.setAttr(f'{joint}.translateX', 0)
            cmds.setAttr(f'{joint}.translateY', 0)
            cmds.setAttr(f'{joint}.translateZ', 0)
            cmds.setAttr(f'{joint}.jointOrientX', 0)
            cmds.setAttr(f'{joint}.jointOrientY', 0)
            cmds.setAttr(f'{joint}.jointOrientZ', 0)
        cmds.setAttr(f'{sPin}.coordinate[1].coordinateV', 0.182)
        cmds.setAttr(f'{sPin}.coordinate[2].coordinateV', 0.470)
        cmds.setAttr(f'{sPin}.coordinate[3].coordinateV', 0.751)
        cmds.setAttr(f'{sPin}.coordinate[4].coordinateV', 1)

        dv_spine_joints_list = cmds.ls(type='joint')
        dv_spine_joints_list = [joint for joint in dv_spine_joints_list if not fk_prefix in joint]
        dv_spine_joints_list = [joint for joint in dv_spine_joints_list if dv_prefix in joint]

        cmds.skinCluster(dv_spine_joints_list[0], dv_spine_joints_list[1], dv_spine_joints_list[2], curve_loft[0],
                         n="ik_skinC")
        cmds.skinCluster("ik_skinC", e=True, mi=3)

        cmds.setAttr("spineSetupSurface.visibility", False)
        cmds.parent(curve_loft[0], self.appendage_grp)
        for joint in dv_spine_joints_list:
            cmds.parent(joint, self.appendage_grp)

        # No additional setup needed for setup()
        return

    def build(self):

        dv_prefix = 'driver_'
        fk_prefix = 'fk_follow_'
        self.fk_ctrl = dict()
        self.dv_ctrl = dict()

        # Implement build method here
        spine_joints_list = cmds.ls(type='joint')
        spine_joints_list = [joint for joint in spine_joints_list if 'spine_' in joint]
        spine_joints_list = [joint for joint in spine_joints_list if not fk_prefix or not dv_prefix in joint]

        follow_spine_joints_list = cmds.ls(type='joint')
        follow_spine_joints_list = [joint for joint in follow_spine_joints_list if fk_prefix in joint]

        dv_spine_joints_list = cmds.ls(type='joint')
        dv_spine_joints_list = [joint for joint in dv_spine_joints_list if not fk_prefix in joint]
        dv_spine_joints_list = [joint for joint in dv_spine_joints_list if dv_prefix in joint]

        self.spine_dv_ls = []
        self.spine_fk_ls = []

        fk_ctrls = rig_name.RigName(side=None,
                                    element=self.appendage_name,
                                    control_type='fk',
                                    rig_type='grp',
                                    maya_type='transform').output()
        self.fk_ctrls = cmds.createNode('transform', n=fk_ctrls)
        matrix_tools.snap_offset_parent_matrix(self.fk_ctrls, follow_spine_joints_list[0])

        dv_ctrls = rig_name.RigName(side=None,
                                    element=self.appendage_name,
                                    control_type='driver',
                                    rig_type='grp',
                                    maya_type='transform').output()
        self.dv_ctrls = cmds.createNode('transform', n=dv_ctrls)
        matrix_tools.snap_offset_parent_matrix(self.dv_ctrls, dv_spine_joints_list[0])

        for i, joint in enumerate(dv_spine_joints_list):
            self.dv_spine_transform = utils.create_fk_control(dv_spine_joints_list[i], parent_control=self.dv_ctrls)
            self.spine_dv_ls.append(self.dv_spine_transform)

        for i, joint in enumerate(spine_joints_list):
            self.fk_spine_transform = utils.create_fk_control(spine_joints_list[i], parent_control=self.fk_ctrls)
            self.spine_fk_ls.append(self.fk_spine_transform)
            self.fk_ctrl[f'spine_fk_{i+1}'] = self.spine_fk_ls[i]

        for btrans, ijoint in zip(self.spine_fk_ls, follow_spine_joints_list):
            matrix_tools.matrix_parent_constraint(ijoint, btrans)

        for i in range(len(self.spine_dv_ls)):
            self.dv_ctrl[f'spine_dv_{i+1}'] = self.spine_dv_ls[i]

            if i + 1 < len(self.spine_dv_ls):
                cmds.parent(self.spine_dv_ls[i + 1], self.spine_dv_ls[i])

        print(self.fk_ctrl)
        print(self.dv_ctrl)

    def cleanup(self):
        cmds.parent(self.dv_ctrls, self.fk_ctrls, self.controls_grp)
        self.controls['ik'] = self.fk_ctrl
        self.controls['fk'] = self.dv_ctrl

    def connect_inputs(self):
        # Implement connect_inputs method here

        if self.input_matrix:
            matrix_tools.matrix_parent_constraint(f'{self.input}.input_matrix',
                                                  self.dv_ctrls)

    def connect_outputs(self):
        # Implement connect_outputs method here
        # Connect the start matrix on the output node to the skeleton
        pass

# Maya Test
#spine = Spine("spine", "spine_bnd_jnt_01")
