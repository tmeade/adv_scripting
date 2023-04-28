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
il.reload(appendage)
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
                 side=None,
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
        self.side = side
        if not side:
            start_rn = rig_name.RigName(start_joint)
            self.side = start_rn.side.output()
            logger.debug(f"Detected side '{self.side}' from joint '{start_joint}'")
        elif side not in rig_name.VALID_SIDE_TYPES:
            logger.error(f"Side '{side}' must match valid side type: {rig_name.VALID_SIDE_TYPES}")

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
        self.hand_jnt = None
        self.hand_fk = None
        self.hand_ik = None
        self.start_fk = None
        self.start_ik = None

        self.fk_ctrl = None # List of fk controls
        self.ik_ctrl = None # List of ik controls, one for each branch/finger
        self.skeleton_fk = None # IK joints
        self.skeleton_ik = None # FK joints
        # bnd_jnt is a 2D list of all control bind joints
        # Contains each branch's start,middle,end joints. Discards any twist/bendy joints.
        # e.g.
        #      [['lt_thumb_bnd_jnt_01', 'lt_thumb_bnd_jnt_02', 'lt_thumb_bnd_jnt_03'],
        #       ['lt_index_bnd_jnt_01', 'lt_index_bnd_jnt_02', 'lt_index_bnd_jnt_03'],
        #       ['lt_middle_bnd_jnt_01', 'lt_middle_bnd_jnt_02', 'lt_middle_bnd_jnt_03'],
        #       ['lt_ring_bnd_jnt_01', 'lt_ring_bnd_jnt_02', 'lt_ring_bnd_jnt_03'],
        #       ['lt_pinky_bnd_jnt_01', 'lt_pinky_bnd_jnt_02', 'lt_pinky_bnd_jnt_03']]
        self.bnd_jnt = list() # Bind joints
        # uppertwist_jnt is a 2D list containing each branch's upperTwist joints
        self.uppertwist_jnt = list()
        # lowertwist_jnt is a 2D list containing each branch's lowerTwist joints
        self.lowertwist_jnt = list()

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
        self.freeze_joint(self.start_joint)
        self.orient_joint(self.start_joint)

        # Read current hand skeleton starting from wrist joint
        skeleton_hand = self.read_skeleton(self.start_joint)
        if not skeleton_hand:
            logger.error('Failed to read skeleton from joint {self.start_joint}')
        #logger.debug('Hand Skeleton (skeleton_hand):')
        #for branch in skeleton_hand:
        #    logger.debug(f'\t{branch}')

        # Determine start middle end joints of each branch.
        for branch in skeleton_hand:
            bnd_jnt_twobone = utils.get_joint_twobone(branch,
                self.num_upperTwist_joint, self.num_lowerTwist_joint)
            self.bnd_jnt.append(bnd_jnt_twobone)
        logger.debug(f'upperTwist:{self.num_upperTwist_joint}\tlowerTwist:{self.num_lowerTwist_joint}')

        logger.debug(self.start_joint)

        # Extract FK control skeleton
        self.start_fk, self.hand_fk, self.skeleton_fk = self.create_control_joints_from_skeleton(
                                self.start_joint,
                                self.bnd_jnt,
                                'fk',
                                self.num_upperTwist_joint,
                                self.num_lowerTwist_joint)

        # Extract IK control skeleton
        self.start_ik, self.hand_ik, self.skeleton_ik = self.create_control_joints_from_skeleton(
                                self.start_joint,
                                self.bnd_jnt,
                                'ik',
                                self.num_upperTwist_joint,
                                self.num_lowerTwist_joint)

        logger.debug('Bind Joint (self.bnd_jnt):')
        for branch in self.bnd_jnt:
            logger.debug(f'\t{branch}')

        logger.debug('FK Joint (self.skeleton_fk):')
        for branch in self.skeleton_fk:
            logger.debug(f'\t{branch}')

        logger.debug('IK Joint (self.bnd_jnt):')
        for branch in self.skeleton_ik:
            logger.debug(f'\t{branch}')

        # If Hand has Parent,
        # Add Parent matrix to Output attributes
        self.parent = cmds.listRelatives(self.start_joint, p=True)
        if self.parent:
            cmds.addAttr(self.output, longName='limb_matrix', attributeType='matrix')

        # Add Bnd joint matrix to Output attributes
        for branch in self.bnd_jnt:
            for jnt in branch:
                cmds.addAttr(self.output, longName=f'{jnt}_matrix', attributeType='matrix')


    def create_control_joints_from_skeleton(self,
                                            start_joint,
                                            bnd_jnt,
                                            control_type,
                                            num_upperTwist_joint,
                                            num_lowerTwist_joint):
        '''
        Create control skeleton of control_type and
        Create 3 control joints [start, middle, end] for two-bone ik.

        Arguments
        start_joint (str): name of start joint
        end_joint (str): name of end joint
        control_type (str): control type such as 'bnd', 'fk', 'ik'
        num_upperTwist_joint (int/None): number of upperTwist joints
        num_lowerTwist_joint (int/None): number of lowerTwist joints
        deleteTwist (bool): delete twist joints / all non-control joints

        Returns list [start, middle, end] joints.
        Each item is a tuple of (<str name>, <rig_name.RigName object>)
        '''
        # Duplicate the skeleton and parent it to the world
        skeleton = utils.duplicate_skeleton(start_joint, tag='COPY')
        cmds.parent(skeleton, w=True)

        # Rename joint skeleton by replacing 'bnd' with the control_type
        joint_map = utils.replace_hierarchy(skeleton, control_type=control_type, rig_type='jnt', tag='COPY')
        #joint_map = list(joint_map.items())
        #logger.debug(joint_map)

        # Rename wrist joint to control_type
        wrist_rn = rig_name.RigName(self.start_joint)
        wrist_rn.rename(control_type=control_type)
        wrist_copy = wrist_rn.output()
        # Rename hand joint to control_type
        hand_rn = rig_name.RigName(self.hand_jnt)
        hand_rn.rename(control_type=control_type)
        hand_copy = hand_rn.output()

        skeleton_copy = copy.deepcopy(bnd_jnt)
        # Duplicate skeleton_hand and rename to control_type
        for branch in skeleton_copy:
            for idx in range(len(branch)):
                jnt_rn = rig_name.RigName(branch[idx])
                jnt_rn.rename(control_type=control_type)
                branch[idx] = jnt_rn.output()

        return wrist_copy, hand_copy, skeleton_copy


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
            # TODO check if this part works
            split_branch0 = self.has_split_skeleton_branch(children[0])
            split_branch1 = self.has_split_skeleton_branch(children[1])
            # Check if thumb branch splits before hand joint
            if split_branch0: # branch1 is thumb
                skeleton_hand = self.read_skeleton(children[0])
                skeleton_hand.append(self.read_skeleton_branch(children[1]))
            elif split_branch1: # branch0 is thumb
                skeleton_hand = self.read_skeleton(children[1])
                skeleton_hand.append(self.read_skeleton_branch(children[0]))
            else: # Hand only consists of two branches
                skeleton_hand.append(self.read_skeleton_branch(children[0]))
                skeleton_hand.append(self.read_skeleton_branch(children[1]))
        elif len(children) > 2: # Hand joint
            self.hand_jnt = joint
            logger.debug(f'{self.hand_jnt} - hand joint')
            for child in children:
                skeleton_hand.append(self.read_skeleton_branch(child))

        return skeleton_hand


    def read_skeleton_v2(self, joint):
        '''
        Read current hand skeleton.
        Build list called skeleton_hand consisting of each finger joint chain.

        Arguments
        joint: starting joint to read skeleton
        skeleton_hand: list of finger joint chains, branches

        Returns 2D list with each finger branch as its own list.
        Includes wrist/hand joint. e.g.
        ['rt_wrist_bnd_jnt', 'rt_hand_bnd_jnt',
        ['rt_pinky_bnd_jnt_01', 'rt_pinky_bnd_jnt_02', 'rt_pinky_bnd_jnt_03'],
        ['rt_ring_bnd_jnt_01', 'rt_ring_bnd_jnt_02', 'rt_ring_bnd_jnt_03'],
        ['rt_middle_bnd_jnt_01', 'rt_middle_bnd_jnt_02', 'rt_middle_bnd_jnt_03'],
        ['rt_index_bnd_jnt_01', 'rt_index_bnd_jnt_02', 'rt_index_bnd_jnt_03'],
        ['rt_thumb_bnd_jnt_01', 'rt_thumb_bnd_jnt_02', 'rt_thumb_bnd_jnt_03']]
        '''
        skeleton_hand = list()
        children = [joint]
        # Walk down joint chain until finding hand joint or end joint
        while len(children) == 1:
            skeleton_hand.append(children[0])
            children = cmds.listRelatives(children[0], typ='joint') or []

        if len(children) == 0: # End joint discarded
            end = skeleton_hand.pop()
            #logger.debug(f'{end} - end joint, has no children.')
        elif len(children) > 1: # Hand joint
            self.hand_jnt = children[0]
            #logger.debug(f'{self.hand_jnt} - hand joint')
            for child in children:
                skeleton_hand.append(self.read_skeleton_v2(child))

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
        if len(children) > 1:
            return True
        else:
            return self.has_split_skeleton_branch(children[0])


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
        ctrl_rn = rig_name.RigName(node)
        ctrl_rn.rename(rig_type='ctrl')
        ctrl = cmds.circle(nr=(1,0,0), c=(0,0,0), r=size, n=ctrl_rn.output())[0]
        logger.debug(f'Created control: {ctrl}')
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
        hand_ctrl_sz = 1.5
        branch_ctrl_sz = 1

        # Build FK controls
        fk_ctrl_grp_rn = rig_name.RigName(side=self.side,
                                          element=self.appendage_name,
                                          control_type='fk',
                                          rig_type='ctrl',
                                          maya_type='transform')
        self.fk_ctrl_grp = cmds.createNode('transform', n=fk_ctrl_grp_rn.output())

        self.fk_ctrl = dict()
        # Build start/wrist control
        start_ctrl = self.build_control(self.start_joint, self.fk_ctrl_grp, hand_ctrl_sz)
        self.fk_ctrl[self.start_joint] = start_ctrl
        # Build hand control
        if self.start_joint != self.hand_jnt:
            hand_ctrl = self.build_control(self.hand_jnt, start_ctrl, hand_ctrl_sz)
            self.fk_ctrl[self.hand_jnt] = hand_ctrl
        else:
            hand_ctrl = start_ctrl

        # Build finger controls
        for branch in self.skeleton_fk:
            ctrlfk0 = self.build_control(branch[0], hand_ctrl, branch_ctrl_sz)
            ctrlfk1 = self.build_control(branch[1], ctrlfk0, branch_ctrl_sz)
            ctrlfk2 = self.build_control(branch[2], ctrlfk1, branch_ctrl_sz)
            self.fk_ctrl[branch[0]] = ctrlfk0
            self.fk_ctrl[branch[1]] = ctrlfk1
            self.fk_ctrl[branch[2]] = ctrlfk2

        # Build IK controls
        ik_ctrl_grp_rn = rig_name.RigName(side=self.side,
                                          element=self.appendage_name,
                                          control_type='ik',
                                          rig_type='ctrl',
                                          maya_type='transform')
        self.ik_ctrl_grp = cmds.createNode('transform', n=ik_ctrl_grp_rn.output())

        self.ik_ctrl = dict()
        # Build finger controls
        for branch in self.skeleton_ik:
            ctrlik = self.build_control(branch[2], self.ik_ctrl_grp, size=branch_ctrl_sz)
            self.ik_ctrl[branch[2]] = ctrlik

        self.build_ik()


    def build_ik(self):
        # TODO: Use Two-Bone IK class to build IK controls
        # for branch in self.skeleton_ik:
        #     finger = two_bone_fkik.TwoBoneFKIK('finger', branch[0],
        #         self.num_upperTwist_joint, self.num_lowerTwist_joint, self.side)
        pass


    def connect_outputs(self):
        '''
        Connect the output matrices to their corresponding joints in the source skeleton
        '''
        # Connect FK
        for branch in self.skeleton_fk:
            for jnt in branch:
                ctrl = self.fk_ctrl[jnt]
                matrix_tools.matrix_parent_constraint(ctrl, jnt)

        # Connect IK
        # TODO


    def cleanup(self):
        '''
        Rename, parent, delete extra nodes, etc..
        '''
        # Group skeletons under appendage grp
        cmds.parent(self.start_fk, self.appendage_grp)
        cmds.parent(self.start_ik, self.appendage_grp)
        # Group controls under controls grp
        cmds.parent(self.fk_ctrl_grp, self.controls_grp)
        cmds.parent(self.ik_ctrl_grp, self.controls_grp)


def test():
    '''
    In Maya Script Editor (python), run:
    import adv_scripting.rig.appendages.hand as hand
    il.reload(hand)
    hand.test()
    '''
    lhand1 = Hand('hand', 'lt_wrist_bnd_jnt', 'lt')
    #lhand1 = Hand('hand', 'lt_wrist_bnd_jnt', num_upperTwist_joint=1, num_lowerTwist_joint=1)
    #lhand2 = Hand('hand', 'lt_wrist_bnd_jnt', num_upperTwist_joint=1, num_lowerTwist_joint=None)
    #lhand3 = Hand('hand', 'lt_wrist_bnd_jnt', num_upperTwist_joint=None, num_lowerTwist_joint=1)
    #lhand4 = Hand('hand', 'lt_wrist_bnd_jnt', num_upperTwist_joint=None, num_lowerTwist_joint=None)
    #rhand1 = Hand('hand', 'rt_wrist_bnd_jnt', 'rt')

    #TODO
    # test scenario where thumb is on separate branch than rest of fingers
