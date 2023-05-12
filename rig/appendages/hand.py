'''
hand.py
author: Dayz Lee

Module to rig Hand Appendage.

Naming convention: (lowercase separated by underscores)
side_region_element_controltype_rigtype_mayatype_position
e.g. lt_hand_index_bnd_jnt_01

RUN/ In Maya Script Editor (python):
import adv_scripting.rig.appendages.hand as hand
il.reload(hand)
hand.test()
'''
import maya.cmds as cmds
import adv_scripting.rig_name as rig_name
import adv_scripting.utilities as utils
import adv_scripting.matrix_tools as matrix_tools
import adv_scripting.rig.appendages.appendage as appendage
import adv_scripting.rig.appendages.two_bone_fkik as two_bone_fkik
import adv_scripting.pole_vector as pole_vector
import logging
import copy
import importlib as il
il.reload(utils)

logger = logging.getLogger()


class Hand(appendage.Appendage):
    '''
    Hand Appendage class.

    Hand can have a variable number of branches / fingers.
    However, assumes that each finger consists of 3 joints
    to allow two-bone ik implementation,
    and any extra joints are twist / bendy joints (to be ignored for now).
    '''

    def __init__(self,
                 appendage_name,
                 start_joint,
                 num_upperTwist_joint=None,
                 num_lowerTwist_joint=None,
                 input_matrix=None):
        '''
        Arguments:
            appendage_name (str): Name of the appendage (e.g. hand, arm, leg, spine, tail)
            start_joint (str): Name of starting joint of appendage
            num_upperTwist_joint: Number of joints between start and middle joint.
                If None, automatically counts the number of upperTwist joints
                assuming that the middle joint is at halfway point.
            num_lowerTwist_joint: Number of joints between middle and end joint.
                If None, automatically counts the number of lowerTwist joints.
            input_matrix (str): If specified, will connect/contrain to the parent appendage.
        '''
        start_rn = rig_name.RigName(start_joint)
        self.side = start_rn.side.output()
        if self.side not in rig_name.VALID_SIDE_TYPES:
            logger.debug(f"Detected side '{self.side}' from joint '{start_joint}'")
            logger.error(f"Side '{self.side}' must match valid side type: {rig_name.VALID_SIDE_TYPES}")
        if not appendage_name:
            appendage_name = start_rn.element.output()

        if num_upperTwist_joint:
            if not isinstance(num_upperTwist_joint, int):
                logger.error(f"num_upperTwist_joint '{num_upperTwist_joint}' must be int or None.")
            if num_upperTwist_joint < 0:
                logger.error(f"num_upperTwist_joint '{num_upperTwist_joint}' cannot be negative.")
        if num_lowerTwist_joint:
            if not isinstance(num_lowerTwist_joint, int):
                logger.error(f"num_lowerTwist_joint '{num_lowerTwist_joint}' must be int or None.")
            if num_lowerTwist_joint < 0:
                logger.error(f"num_lowerTwist_joint '{num_lowerTwist_joint}' cannot be negative.")
        self.num_upperTwist_joint = num_upperTwist_joint
        self.num_lowerTwist_joint = num_lowerTwist_joint


        # hand_jnt is parent joint of all branches except possibly thumb
        # hand_jnt == start_joint if there is no separate wrist
        # e.g. 'lt_hand_bnd_jnt'
        self.wrist_bnd = start_joint
        self.hand_bnd = None
        self.thumb_bnd = None

        self.fk_ctrl = dict() # List of fk controls
        self.ik_ctrl = dict() # List of ik controls, one for each branch/finger
        self.pv_ctrl = dict() # List of pole vectors
        self.fk_jnt_grp = None
        self.ik_jnt_grp = None
        self.fk_ctrl_grp = None
        self.ik_ctrl_grp = None
        self.pv_ctrl_grp = None
        self.blend_switch = None # Blend control for switching FK/IK
        self.blend_matrix = list() # Blend matrices multMatrix
        self.blend_attribute = list() # Blend attribute names
        self.skeleton_fk = None # IK joints
        self.skeleton_ik = None # FK joints
        self.bnd_jnt = list() # bnd joints
        # uppertwist_jnt is a 2D list containing each branch's upperTwist joints
        # self.uppertwist_jnt = list()
        # lowertwist_jnt is a 2D list containing each branch's lowerTwist joints
        # self.lowertwist_jnt = list()

        # initialize Appendage class
        appendage.Appendage.__init__(self, appendage_name, start_joint, input_matrix)


    def setup(self):
        '''
        Method to prepare nodes for rigging. e.g.
            Create organizational groups
            Assign variables to joint names
            Measure offsets
            Create additional input matrix attributes
        '''
        # Read current hand skeleton starting from wrist joint
        skeleton_hand = self.read_skeleton(self.wrist_bnd)
        if not skeleton_hand:
            logger.error('Failed to read skeleton from joint {self.wrist_bnd}')
        #logger.debug('Hand Skeleton (skeleton_hand):')
        #for branch in skeleton_hand:
        #    logger.debug(f'\t{branch}')

        # Freeze and orient joints
        self.freeze_joint(self.wrist_bnd)
        children = cmds.listRelatives(self.hand_bnd, typ='joint') or []
        for child in children:
            self.orient_joint(child)

        # self.bnd_jnt is a 2D list of all control bind joints
        # Contains each branch's start, middle, end joints. Discard any twist/bendy joints.
        # e.g.
        #      [['lt_thumb_bnd_jnt_01', 'lt_thumb_bnd_jnt_02', 'lt_thumb_bnd_jnt_03'],
        #       ['lt_index_bnd_jnt_01', 'lt_index_bnd_jnt_02', 'lt_index_bnd_jnt_03'],
        #       ['lt_middle_bnd_jnt_01', 'lt_middle_bnd_jnt_02', 'lt_middle_bnd_jnt_03'],
        #       ['lt_ring_bnd_jnt_01', 'lt_ring_bnd_jnt_02', 'lt_ring_bnd_jnt_03'],
        #       ['lt_pinky_bnd_jnt_01', 'lt_pinky_bnd_jnt_02', 'lt_pinky_bnd_jnt_03']]
        for branch in skeleton_hand:
            # Determine start middle end joints in each branch
            bnd_jnt_twobone = utils.get_joint_twobone(branch,
                self.num_upperTwist_joint, self.num_lowerTwist_joint)
            self.bnd_jnt.append(bnd_jnt_twobone)

        # Extract FK control skeleton
        wrist_fk, self.skeleton_fk = self.create_control_joints_from_skeleton(
                                self.wrist_bnd,
                                self.bnd_jnt,
                                'fk',
                                self.num_upperTwist_joint,
                                self.num_lowerTwist_joint)

        # Extract IK control skeleton
        wrist_ik, self.skeleton_ik = self.create_control_joints_from_skeleton(
                                self.wrist_bnd,
                                self.bnd_jnt,
                                'ik',
                                self.num_upperTwist_joint,
                                self.num_lowerTwist_joint)

        # --- Setup Debug Statements ---
        #logger.debug(f'upperTwist:{self.num_upperTwist_joint}\tlowerTwist:{self.num_lowerTwist_joint}')
        #logger.debug(self.wrist_bnd)

        logger.debug('Bind Joint (self.bnd_jnt):')
        for branch in self.bnd_jnt:
            logger.debug(f'\t{branch}')

        logger.debug('FK Joint (self.skeleton_fk):')
        for branch in self.skeleton_fk:
            logger.debug(f'\t{branch}')

        logger.debug('IK Joint (self.bnd_jnt):')
        for branch in self.skeleton_ik:
            logger.debug(f'\t{branch}')

        # Change display color for fk,ik skeleton
        utils.display_color(wrist_fk, 6) # Blue IK skeleton
        utils.display_color(wrist_ik, 8) # Burple IK skeleton

        # Create FK joint group
        fk_jnt_grp = rig_name.RigName(side=self.side,
                                          element=self.appendage_name,
                                          control_type='fk',
                                          rig_type='jnt',
                                          maya_type='transform').output()
        self.fk_jnt_grp = cmds.createNode('transform', n=fk_jnt_grp)
        matrix_tools.snap_offset_parent_matrix(fk_jnt_grp, self.hand_bnd)

        # Create IK joint group
        ik_jnt_grp = rig_name.RigName(side=self.side,
                                          element=self.appendage_name,
                                          control_type='ik',
                                          rig_type='jnt',
                                          maya_type='transform').output()
        self.ik_jnt_grp = cmds.createNode('transform', n=ik_jnt_grp)
        matrix_tools.snap_offset_parent_matrix(ik_jnt_grp, self.hand_bnd)

        # Parent all branches under fk,ik jnt grp
        for branch in self.skeleton_fk:
            cmds.parent(branch[0], fk_jnt_grp)
        for branch in self.skeleton_ik:
            cmds.parent(branch[0], ik_jnt_grp)
        # Remove wrist and hand joints from fk,ik skeleton
        cmds.delete(wrist_fk)
        cmds.delete(wrist_ik)


    def create_control_joints_from_skeleton(self,
                                            start_joint,
                                            bnd_jnt,
                                            control_type,
                                            num_upperTwist_joint,
                                            num_lowerTwist_joint):
        '''
        Copy bnd skeleton to create control skeleton of control_type.
        Get 3 control joints [start, middle, end] for two-bone ik.

        Arguments
        start_joint (str): name of start joint
        bnd_jnt (str): list of branches in bnd skeleton
        control_type (str): control type such as 'bnd', 'fk', 'ik'
        num_upperTwist_joint (int/None): number of upperTwist joints
        num_lowerTwist_joint (int/None): number of lowerTwist joints

        Returns list [start, middle, end] joints.
        '''
        # Duplicate the skeleton and parent it to the world
        skeleton = utils.duplicate_skeleton(start_joint, tag='COPY')
        cmds.parent(skeleton, w=True)

        # Rename joint skeleton by replacing 'bnd' with the control_type
        joint_map = utils.replace_hierarchy(skeleton, control_type=control_type, rig_type='jnt', tag='COPY')
        #joint_map = list(joint_map.items())

        # Rename wrist joint to control_type
        start_copy = rig_name.RigName(start_joint).rename(control_type=control_type).output()

        skeleton_copy = copy.deepcopy(bnd_jnt)
        # Duplicate skeleton_hand and rename to control_type
        for branch in skeleton_copy:
            for idx in range(len(branch)):
                jnt_rn = rig_name.RigName(branch[idx])
                jnt_rn.rename(control_type=control_type)
                branch[idx] = jnt_rn.output()

        return start_copy, skeleton_copy


    def read_skeleton(self, joint):
        '''
        Read current hand skeleton.
        Build list called skeleton_hand consisting of each finger joint chain.

        Arguments
        joint: starting joint to read skeleton
        skeleton_hand: list of finger joint chains, branches

        Returns 2D list with each finger branch as its own list.
        Excludes wrist/hand joint. e.g.
        [['rt_pinky_bnd_jnt_01', 'rt_pinky_bnd_jnt_02', 'rt_pinky_bnd_jnt_03'],
        ['rt_ring_bnd_jnt_01', 'rt_ring_bnd_jnt_02', 'rt_ring_bnd_jnt_03'],
        ['rt_middle_bnd_jnt_01', 'rt_middle_bnd_jnt_02', 'rt_middle_bnd_jnt_03'],
        ['rt_index_bnd_jnt_01', 'rt_index_bnd_jnt_02', 'rt_index_bnd_jnt_03'],
        ['rt_thumb_bnd_jnt_01', 'rt_thumb_bnd_jnt_02', 'rt_thumb_bnd_jnt_03']]
        '''
        skeleton_hand = list()
        children = cmds.listRelatives(joint, typ='joint') or []

        if len(children) == 0: # End joint
            return skeleton_hand
        elif len(children) == 1: # Walk down joint chain
            skeleton_hand = self.read_skeleton(children[0])
        elif len(children) == 2: # Branch split
            split_branch0 = self.has_split_skeleton_branch(children[0])
            split_branch1 = self.has_split_skeleton_branch(children[1])
            # Check if thumb branch splits before hand joint
            if split_branch0: # branch1 is thumb
                self.thumb_bnd = children[1]
                skeleton_hand = self.read_skeleton(children[0])
                skeleton_hand.append(self.read_skeleton_branch(children[1]))
            elif split_branch1: # branch0 is thumb
                self.thumb_bnd = children[0]
                skeleton_hand = self.read_skeleton(children[1])
                skeleton_hand.append(self.read_skeleton_branch(children[0]))
            else: # Hand only consists of two branches
                skeleton_hand.append(self.read_skeleton_branch(children[0]))
                skeleton_hand.append(self.read_skeleton_branch(children[1]))
        elif len(children) > 2: # Hand joint
            self.hand_bnd = joint
            for child in children:
                skeleton_hand.append(self.read_skeleton_branch(child))

        return skeleton_hand


    def read_skeleton_branch(self, joint):
        '''
        Read finger, or single branch, assumed to be a linear joint chain.
        '''
        skeleton_branch = [joint]
        children = cmds.listRelatives(joint, typ='joint')
        if not children: # End joint
            return []
        elif len(children) > 1:
            logger.warning(f'{joint} has multiple children. Expected linear joint chain.')

        skeleton_branch.extend(self.read_skeleton_branch(children[0]))
        return skeleton_branch


    def has_split_skeleton_branch(self, joint):
        if not joint: return False
        children = cmds.listRelatives(joint, typ='joint') or []
        if len(children) == 1:
            return self.has_split_skeleton_branch(children[0])
        elif len(children) > 1:
            return True


    def freeze_joint(self, jnt):
        '''
        Freeze rotation and scale for each joint in hierarchy.

        Argument
        jnt (str): name of joint
        '''
        cmds.makeIdentity(jnt, apply=True, t=0, r=1, s=1, n=0, pn=1)
        children = cmds.listRelatives(jnt, typ='joint') or []
        for child in children:
            self.freeze_joint(child)


    def orient_joint(self, jnt):
        '''
        Orient joint for each joint in hierarchy.
        Primary axis X, Secondary axis Y, SAO Z.

        Argument
        jnt (str): name of joint
        '''
        if not self.side or self.side=='lt':
            #cmds.joint(jnt, e=True, zso=True, oj='xyz', sao='yup') # Rotate on Z-axis
            cmds.joint(jnt, e=True, zso=True, oj='xyz', sao='zup') # Rotate on Y-axis
        elif self.side=='rt':
            #cmds.joint(jnt, e=True, zso=True, oj='xyz', sao='ydown') # Rotate on Z-axis
            cmds.joint(jnt, e=True, zso=True, oj='xyz', sao='zdown') # Rotate on Y-axis
        else:
            logger.error(f'Side {self.side} not recognized. {jnt}')
        children = cmds.listRelatives(jnt, typ='joint')
        if children:
            for child in children:
                self.orient_joint(child)
        else:
            cmds.joint(jnt, e=True, zso=True, oj='none')


    def build_control(self, node, parent=None, size=1):
        ctrl_rn = rig_name.RigName(node).rename(rig_type='ctrl')
        ctrl = cmds.circle(nr=(1,0,0), c=(0,0,0), r=size, n=ctrl_rn.output())[0]
        if parent:
            cmds.parent(ctrl, parent)
            # modify ctrl's transform to match parent
            cmds.matchTransform(ctrl, parent, pos=1, rot=1, scl=1, piv=1)
            # freeze transformations
            cmds.makeIdentity(ctrl, apply=True, t=1, r=1, s=1, n=0)
        # match ctrl's transform to node
        matrix_tools.snap_offset_parent_matrix(ctrl, node)
        return ctrl


    def build(self):
        '''
        Create and connect nodes for rigging.
        Create a root control, place its offsetParentMatrix to the root joint,
        '''
        branch_ctrl_sz = 1 # Control shape size

        # Build wrist bnd control
        wrist_ctrl = utils.create_group(self.wrist_bnd, self.controls_grp)
        self.fk_ctrl[self.wrist_bnd] = wrist_ctrl

        # Build hand bnd control
        if self.wrist_bnd != self.hand_bnd:
            hand_ctrl = utils.create_group(self.hand_bnd, wrist_ctrl)
            utils.display_color(hand_ctrl, 15) # Blue display color
            self.fk_ctrl[self.hand_bnd] = hand_ctrl
        else:
            hand_ctrl = wrist_ctrl

        # Build FK controls
        # Create group for FK skeleton and controls
        fk_ctrl_grp = rig_name.RigName(side=self.side,
                                          element=self.appendage_name,
                                          control_type='fk',
                                          rig_type='ctrl',
                                          maya_type='transform').output()
        self.fk_ctrl_grp = cmds.createNode('transform', n=fk_ctrl_grp)
        # Match transforms of fk_jnt_grp and fk_ctrl_grp to hand
        matrix_tools.snap_offset_parent_matrix(self.fk_ctrl_grp, hand_ctrl)
        if self.thumb_bnd: # Thumb is separate from hand jnt
            #matrix_tools.matrix_parent_constraint(wrist_ctrl, self.thumb__ctrl[0])
            cmds.parent(self.thumb_ctrl[0], wrist_ctrl)
            matrix_tools.matrix_parent_constraint(wrist_ctrl, self.thumb__bnd[0])
        else:
            matrix_tools.matrix_parent_constraint(hand_ctrl, self.fk_ctrl_grp)
            matrix_tools.matrix_parent_constraint(hand_ctrl, self.fk_jnt_grp)

        # Build FK finger controls
        for branch in self.skeleton_fk:
            if self.thumb_bnd:
                ctrlfk0 = utils.create_control(branch[0], wrist_ctrl, branch_ctrl_sz)
            else:
                ctrlfk0 = utils.create_control(branch[0], fk_ctrl_grp, branch_ctrl_sz)
            ctrlfk1 = utils.create_control(branch[1], ctrlfk0, branch_ctrl_sz)
            ctrlfk2 = utils.create_control(branch[2], ctrlfk1, branch_ctrl_sz)
            utils.display_color(ctrlfk0, 15) # Blue display color
            utils.display_color(ctrlfk1, 15)
            utils.display_color(ctrlfk2, 15)
            self.fk_ctrl[branch[0]] = ctrlfk0
            self.fk_ctrl[branch[1]] = ctrlfk1
            self.fk_ctrl[branch[2]] = ctrlfk2

        # Build IK controls
        # Create group for IK skeleton and controls
        ik_ctrl_grp = rig_name.RigName(side=self.side,
                                          element=self.appendage_name,
                                          control_type='ik',
                                          rig_type='ctrl',
                                          maya_type='transform').output()
        self.ik_ctrl_grp = cmds.createNode('transform', n=ik_ctrl_grp)
        # Match transforms of ik_jnt_grp and ik_ctrl_grp to hand
        matrix_tools.snap_offset_parent_matrix(self.ik_ctrl_grp, hand_ctrl)
        if self.thumb_bnd:
            matrix_tools.matrix_parent_constraint(wrist_ctrl, self.thumb_bnd[0])
        matrix_tools.matrix_parent_constraint(hand_ctrl, self.ik_jnt_grp)
        matrix_tools.matrix_parent_constraint(hand_ctrl, self.ik_ctrl_grp)

        # Build IK finger controls
        for branch in self.skeleton_ik:
            if self.thumb_bnd:
                ctrlik = utils.create_control(branch[2], wrist_ctrl, size=branch_ctrl_sz)
            else:
                ctrlik = utils.create_control(branch[2], ik_ctrl_grp, size=branch_ctrl_sz)
            utils.display_color(ctrlik, 10) # Peach display color
            self.ik_ctrl[branch[2]] = ctrlik
        self.build_ik()


    def build_ik(self):
        pv_ctrl_sz = 1

        # Create group for PV controls
        pv_ctrl_grp_rn = rig_name.RigName(side=self.side,
                                          element=self.appendage_name,
                                          control_type='ik',
                                          rig_type='pv',
                                          maya_type='transform')
        self.pv_ctrl_grp = cmds.createNode('transform', n=pv_ctrl_grp_rn.output())

        # Create group for IK handles
        ikhandle_grp_rn = rig_name.RigName(side=self.side,
                                          element=self.appendage_name,
                                          control_type='ik',
                                          rig_type='handle',
                                          maya_type='transform')
        self.ikhandle_grp = cmds.createNode('transform', n=ikhandle_grp_rn.output())

        # Blended output node, allowing for FK/IK switch
        name_blend = rig_name.RigName(side=self.side, element=f'{self.appendage_name}_FKIK',
            control_type='switch', rig_type='grp')
        self.blend_switch = name_blend.output()
        cmds.createNode('transform', n=self.blend_switch)
        cmds.addAttr(self.blend_switch, ln='switch_fkik', nn=f'Switch FKIK', at='double', min=0, max=1, k=1)

        # Build IK
        for branch_fk, branch_ik in zip(self.skeleton_fk, self.skeleton_ik):
            fk0, fk1, fk2 = branch_fk
            ik0, ik1, ik2 = branch_ik
            # Get IK control for current finger/branch
            ik_ctrl = self.ik_ctrl[ik2]
            name_ik_handle = rig_name.RigName(ik_ctrl).rename(rig_type='handle', maya_type='ikrpsolver')
            # IK handle
            ik_handle = cmds.ikHandle(sj=ik0, ee=ik2, sol='ikRPsolver', n=name_ik_handle.output())[0]
            cmds.parent(ik_handle, self.ikhandle_grp)
            matrix_tools.matrix_parent_constraint(ik_ctrl, ik_handle)
            # Pole vector
            pv_pos = pole_vector.calculate_pole_vector_position(ik0, ik1, ik2)
            name_pv = rig_name.RigName(ik_ctrl).rename(rig_type='pv', maya_type='controller')
            pv_ctrl = utils.create_control_pv(pv_pos, name_pv.output(), ik_handle, self.pv_ctrl_grp, pv_ctrl_sz)
            self.pv_ctrl[ik_ctrl] = pv_ctrl
            #cmds.parent(pv_ctrl, self.pv_ctrl_grp, a=True)

            # Name each blend node based on name of FK joint
            name_blend0 = rig_name.RigName(fk0).remove(control_type=1, rig_type=1, maya_type=1).output()
            name_blend1 = rig_name.RigName(fk1).remove(control_type=1, rig_type=1, maya_type=1).output()
            name_blend2 = rig_name.RigName(fk2).remove(control_type=1, rig_type=1, maya_type=1).output()
            attr_blend0 = f'{name_blend0}_fkik'
            attr_blend1 = f'{name_blend1}_fkik'
            attr_blend2 = f'{name_blend2}_fkik'
            # Create FKIK attribute on blend switch
            cmds.addAttr(self.blend_switch, ln=attr_blend0, nn=f'{name_blend0} FKIK', at='double', min=0, max=1, k=0, h=1)
            cmds.addAttr(self.blend_switch, ln=attr_blend1, nn=f'{name_blend1} FKIK', at='double', min=0, max=1, k=0, h=1)
            cmds.addAttr(self.blend_switch, ln=attr_blend2, nn=f'{name_blend2} FKIK', at='double', min=0, max=1, k=0, h=1)
            cmds.connectAttr(f'{self.blend_switch}.switch_fkik', f'{self.blend_switch}.{attr_blend0}')
            cmds.connectAttr(f'{self.blend_switch}.switch_fkik', f'{self.blend_switch}.{attr_blend1}')
            cmds.connectAttr(f'{self.blend_switch}.switch_fkik', f'{self.blend_switch}.{attr_blend2}')
            # Create FKIK attribute on output
            cmds.addAttr(self.output, ln=attr_blend0, nn=f'{name_blend0} FKIK', at='matrix', k=0)
            cmds.addAttr(self.output, ln=attr_blend1, nn=f'{name_blend1} FKIK', at='matrix', k=0)
            cmds.addAttr(self.output, ln=attr_blend2, nn=f'{name_blend2} FKIK', at='matrix', k=0)

            # blend_switch -> blendMatrix -> multMatrix -> output
            # Create blendMatrix and multMatrix nodes for switching FKIK
            mat_blend0 = utils.blend_skeleton(fk0, ik0, self.blend_switch, self.output, attr_blend0)
            mat_blend1 = utils.blend_skeleton(fk1, ik1, self.blend_switch, self.output, attr_blend1)
            mat_blend2 = utils.blend_skeleton(fk2, ik2, self.blend_switch, self.output, attr_blend2)
            self.blend_matrix.append([mat_blend0, mat_blend1, mat_blend2])
            self.blend_attribute.append([attr_blend0, attr_blend1, attr_blend2])


    def connect_inputs(self):
        '''
        Connect the input matricies from the input node to the root control of the appendage.
        '''
        wrist_ctrl = self.fk_ctrl[self.wrist_bnd]
        # Connect input to wrist ctrl
        if self.input_matrix:
            matrix_tools.matrix_parent_constraint(f'{self.input}.input_matrix', wrist_ctrl)

        # Connect wrist/hand ctrl to respective bnd joints
        matrix_tools.matrix_parent_constraint(wrist_ctrl, self.wrist_bnd)
        if self.wrist_bnd != self.hand_bnd:
            hand_ctrl = self.fk_ctrl[self.hand_bnd]
            matrix_tools.matrix_parent_constraint(hand_ctrl, self.hand_bnd)


    def connect_outputs(self):
        '''
        Connect the output matrices to their corresponding joints in the source skeleton
        '''
        # Connect visibility
        reverse = cmds.createNode('reverse', n=f'{self.appendage_name}_visibility_reverse')
        cmds.connectAttr(f'{self.blend_switch}.switch_fkik', f'{reverse}.inputX')
        cmds.connectAttr(f'{self.blend_switch}.switch_fkik', f'{self.ik_jnt_grp}.visibility')
        cmds.connectAttr(f'{self.blend_switch}.switch_fkik', f'{self.ik_ctrl_grp}.visibility')
        cmds.connectAttr(f'{self.blend_switch}.switch_fkik', f'{self.pv_ctrl_grp}.visibility')
        cmds.connectAttr(f'{reverse}.outputX', f'{self.fk_jnt_grp}.visibility')
        cmds.connectAttr(f'{reverse}.outputX', f'{self.fk_ctrl_grp}.visibility')

        # Connect FK
        for branch in self.skeleton_fk:
            for jnt in branch:
                fk_ctrl = self.fk_ctrl[jnt]
                matrix_tools.matrix_parent_constraint(fk_ctrl, jnt)

        # Connect IK
        for branch in self.skeleton_ik:
            ik_ctrl = self.ik_ctrl[branch[2]]
            # Connect rotations to behave as orient constraint
            cmds.connectAttr(f'{ik_ctrl}.rotateX', f'{branch[2]}.rotateX')
            cmds.connectAttr(f'{ik_ctrl}.rotateY', f'{branch[2]}.rotateY')
            cmds.connectAttr(f'{ik_ctrl}.rotateZ', f'{branch[2]}.rotateZ')

        # multMatrix -> output -> bnd jnt
        # Connect multMatrix to output, connect output to bnd jnt
        for idx in range(len(self.blend_matrix)):
            branch_mat = self.blend_matrix[idx] # Blend matrix
            branch_attr = self.blend_attribute[idx] # Blend attrbute
            branch_bnd = self.bnd_jnt[idx] # bnd joint
            mat_blend0, mat_blend1, mat_blend2 = branch_mat
            attr_blend0, attr_blend1, attr_blend2 = branch_attr
            bnd0, bnd1, bnd2 = branch_bnd
            # hand jnt is parent of all branches. Connect multMatrix output to Hand output.
            cmds.connectAttr(f'{self.hand_bnd}.worldInverseMatrix[0]', f'{mat_blend0}.matrixIn[1]')
            cmds.connectAttr(f'{self.output}.{attr_blend0}', f'{bnd0}.offsetParentMatrix')
            utils.make_identity(bnd0)
            # ik0 is parent of ik1. Connect multMatrix output to Hand output.
            cmds.connectAttr(f'{bnd0}.worldInverseMatrix[0]', f'{mat_blend1}.matrixIn[1]')
            cmds.connectAttr(f'{self.output}.{attr_blend1}', f'{bnd1}.offsetParentMatrix')
            utils.make_identity(bnd1)
            # ik1 is parent of ik2. Connect multMatrix output to Hand output.
            cmds.connectAttr(f'{bnd1}.worldInverseMatrix[0]', f'{mat_blend2}.matrixIn[1]')
            cmds.connectAttr(f'{self.output}.{attr_blend2}', f'{bnd2}.offsetParentMatrix')
            utils.make_identity(bnd2)


    def cleanup(self):
        '''
        Rename, parent, delete extra nodes, etc..
        Appendage class groups everything under Hand grp
        under method finish()
        '''
        # Group skeletons under appendage grp
        cmds.parent(self.fk_jnt_grp, self.appendage_grp)
        cmds.parent(self.ik_jnt_grp, self.appendage_grp)
        cmds.parent(self.ikhandle_grp, self.appendage_grp)
        # Group controls under controls grp
        cmds.parent(self.fk_ctrl_grp, self.controls_grp)
        cmds.parent(self.ik_ctrl_grp, self.controls_grp)
        cmds.parent(self.pv_ctrl_grp, self.controls_grp)
        # Group blend/fkik switch under appendage group
        cmds.parent(self.blend_switch, self.appendage_grp)


def test():
    '''
    In Maya Script Editor (python), run:
    import adv_scripting.rig.appendages.hand as hand
    il.reload(hand)
    hand.test()
    '''
    lhand1 = Hand('hand', 'lt_wrist_bnd_jnt')
    #lhand1 = Hand('hand', 'lt_wrist_bnd_jnt', num_upperTwist_joint=1, num_lowerTwist_joint=1)
    #lhand2 = Hand('hand', 'lt_wrist_bnd_jnt', num_upperTwist_joint=1, num_lowerTwist_joint=None)
    #lhand3 = Hand('hand', 'lt_wrist_bnd_jnt', num_upperTwist_joint=None, num_lowerTwist_joint=1)
    #lhand4 = Hand('hand', 'lt_wrist_bnd_jnt', num_upperTwist_joint=None, num_lowerTwist_joint=None)
    #rhand1 = Hand('hand', 'rt_wrist_bnd_jnt')

    #TODO
    # test scenario where thumb is on separate branch than rest of fingers
