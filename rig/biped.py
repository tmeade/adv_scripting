import maya.cmds as cmds
import logging
import adv_scripting.rig_name as rig_name
import adv_scripting.rig.appendages.root as root
import adv_scripting.rig.appendages.spine as spine
import adv_scripting.rig.appendages.head as head
import adv_scripting.rig.appendages.leg as leg
import adv_scripting.rig.appendages.arm as arm
import adv_scripting.rig.appendages.hand as hand
import adv_scripting.rig.settings as rig_settings
import adv_scripting.utilities as utils
import importlib as il
il.reload(root)
il.reload(spine)
il.reload(leg)
il.reload(arm)
il.reload(rig_settings)

logger = logging.getLogger(__name__)


CONTROL_SHAPES = {'Root': 'circle', 'wrist_ik_ctrl': 'cross'}

def tag_rig_node(rig_grp, name):
    cmds.addAttr(rig_grp, longName='AssetName', dt='string')
    cmds.addAttr(rig_grp, longName='RigVersion', dt='string')


class Rig():

    def __init__(self, name, settings):
        self.name = name
        self.settings = settings

        self.setup()
        self.build()
        self.connect_control_shapes()

    def setup(self):
        logger.debug('build')
        '''
        Sets up basic global transform control and groups for rig.
        '''
        self.rig_grp = cmds.createNode('transform', name=rig_name.RigName(
                                                        element=self.name,
                                                        rig_type='grp'))
        tag_rig_node(self.rig_grp, self.name)

        self.skeleton_grp = cmds.createNode('transform', name=rig_name.RigName(
                                                        control_type = 'bnd',
                                                        rig_type='grp'))
        cmds.parent(self.settings.root_start_joint, self.skeleton_grp)

        self.global_control = cmds.createNode('transform', name=rig_name.RigName(
                                                        element='main',
                                                        rig_type='ctrl'))
        cmds.parent(self.global_control, self.rig_grp)

    def build(self):
        logger.debug('build')

    def connect_control_shapes(self):
        logger.debug('connect_control_shapes')


class Biped(Rig):

    def __init__(self, name, settings=rig_settings.BipedSettings()):
        self.sides = [rig_name.Side('lt'), rig_name.Side('rt')]
        Rig.__init__(self, name, settings)

    def build(self):
        logger.debug('build')
        self.build_root()
        self.build_spine()
        self.build_head()
        self.build_arms()
        self.build_legs()

    def connect_control_shapes(self):
        # Add controls as message connections to rig_grp
        controls = self.get_controls()
        for control in controls:
            cmds.addAttr(self.rig_grp, ln=control, at='message')
            cmds.connectAttr(f'{control}.message', f'{self.rig_grp}.{control}')

    def get_controls(self):
        # Get controls from all appendages
        appendages = [self.root, self.spine, self.head,
            self.arms[self.sides[0]], self.arms[self.sides[1]],
            self.legs[self.sides[0]], self.legs[self.sides[1]],
            self.hands[self.sides[0]], self.hands[self.sides[1]]]

        controls = list()
        for appendage in appendages:
            control_dict = appendage.controls
            controls.expand(control_dict['fk'].values())
            controls.expand(control_dict['ik'].values())
            controls.expand(control_dict['switches'].values())
        return controls

    def build_root(self):
        logger.debug('build_root')
        self.root = root.Root(self.settings.root_appendage_name,
                              rig_name.RigName(full_name=self.settings.root_start_joint).output(),
                              input_matrix=f'{self.global_control}.worldMatrix[0]')
        cmds.parent(self.root.appendage_grp, self.rig_grp)
        utils.rename_hierarchy(rig_name.RigName(full_name=self.settings.root_start_joint).output(),
                                end_joint=None,
                                unlock=True)

    def build_spine(self):
        logger.debug('build_spine')
        self.spine = spine.Spine(self.settings.spine_appendage_name,
                                 rig_name.RigName(full_name=self.settings.spine_start_joint).output(),
                                 input_matrix= self.root.controls['fk']['root'] + ".worldMatrix[0]")
        cmds.parent(self.spine.appendage_grp, self.rig_grp)

    def build_head(self):
        logger.debug('build_head')
        self.head = head.Head(self.settings.head_appendage_name,
                                         rig_name.RigName(full_name=self.settings.head_start_joint).output(),
                                         self.settings.head_num_twist_joints,
                                         input_matrix=f'{self.global_control}.worldMatrix[0]')
        cmds.parent(self.head.appendage_grp, self.rig_grp)

    def build_arms(self):
        logger.debug('build_arms')
        self.arms  = dict()
        for side in self.sides:
            self.arms[side] = arm.Arm(rig_name.RigName(
                                      full_name=self.settings.arm_appendage_name).rename(
                                      side=side).output(),
                                    rig_name.RigName(
                                      full_name=self.settings.arm_start_joint).rename(
                                      side=side).output(),
                                    self.settings.arm_num_upperTwist_joints,
                                    self.settings.arm_num_lowerTwist_joints,
                                    side)
            cmds.parent(self.arms[side].appendage_grp, self.rig_grp)

    def build_legs(self):
        logger.debug('build_legs')
        print('IM******', f"{self.root.controls}['fk']['root'].worldMatrix[0]")

        self.legs = dict()
        for side in self.sides:
            self.legs[side] = leg.Leg(rig_name.RigName(
                                        full_name=self.settings.leg_appendage_name).rename(
                                        side=side).output(),
                                    rig_name.RigName(
                                        full_name=self.settings.leg_start_joint).rename(
                                        side=side).output(),
                                    self.settings.leg_num_upperTwist_joints,
                                    self.settings.leg_num_lowerTwist_joints,
                                    side,
                                    input_matrix = self.root.controls['fk']['root'] + '.worldMatrix[0]')

            cmds.parent(self.legs[side].appendage_grp, self.rig_grp)

    def build_hands(self):
        logger.debug('build_hand')
        self.hands = dict()
        for side in self.sides:
            self.hands[side] = hand.Hand(self.settings.hand_appendage_name,
                                        rig_name.RigName(
                                            full_name=self.settings.hand_start_joint).rename(
                                            side=side).output(),
                                        self.settings.hand_num_upperTwist_joint,
                                        self.settings.hand_num_lowerTwist_joint,
                                        rig_name.RigName(full_name='lt_lower_arm_bnd_jnt_02').rename(side=side).output() + '.worldMatrix[0]')
            cmds.parent(self.hands[side].appendage_grp, self.rig_grp)
