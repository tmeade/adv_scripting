import maya.cmds as cmds
import logging
import adv_scripting.rig_name as rig_name
import adv_scripting.rig.appendages.root as root
import adv_scripting.rig.appendages.spine as spine
import adv_scripting.rig.appendages.head as head
import adv_scripting.rig.appendages.leg as leg
import adv_scripting.rig.appendages.arm as arm
import adv_scripting.rig.appendages.hand as hand
import adv_scripting.utilities as utils





logger = logging.getLogger(__name__)

import importlib as il
il.reload(root)
il.reload(spine)
il.reload(leg)

SETTINGS = {'Root': {
                'appendage_name': 'root',
                'start_joint': rig_name.RigName(full_name='root_bnd_jnt')},
            'Spine': {
                'appendage_name': 'spine',
                'start_joint': rig_name.RigName('spine_bnd_jnt_01')},
            'Head': {
                'appendage_name': 'head',
                'start_joint': 'neck_bnd_jnt',
                'num_neck_joints': 0},
            'Leg': {
                'appendage_name': rig_name.RigName(full_name='lt_leg_appendage'),
                'start_joint': rig_name.RigName(full_name='lt_upLeg_bnd_jnt_01'),
                'num_upperTwist_joint': 1,
                'num_lowerTwist_joint': 1,
                'side': rig_name.Side('lt')},
            'Hand_Left': {
                'appendage_name': 'hand',
                'start_joint': 'lt_wrist_bnd_jnt',
                'num_upperTwist_joint': None,
                'num_lowerTwist_joint': None,
                'input_matrix': 'lt_lower_arm_bnd_jnt_02.worldMatrix[0]' },
            'Hand_Right': {
                'appendage_name': 'hand',
                'start_joint': 'rt_wrist_bnd_jnt',
                'num_upperTwist_joint': None,
                'num_lowerTwist_joint': None,
                'input_matrix': 'rt_lower_arm_bnd_jnt_02.worldMatrix[0]' }
            }


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
        self.global_control = cmds.createNode('transform', name=rig_name.RigName(
                                                        element='main',
                                                        rig_type='ctrl'))
        cmds.parent(self.global_control, self.rig_grp)

    def build(self):
        logger.debug('build')

    def connect_control_shapes(self):
        logger.debug('connect_control_shapes')


class Biped(Rig):
    def __init__(self, name, settings):
        self.sides = [rig_name.Side('lt'), rig_name.Side('rt')]
        Rig.__init__(self, name, settings)

    def build(self):
        logger.debug('build')
        self.build_root()
        self.build_spine()
        self.build_head()
        self.build_arms()
        self.build_legs()

    def build_root(self):
        logger.debug('build_root')
        self.root = root.Root(self.settings['Root']['appendage_name'],
                                    self.settings['Root']['start_joint'].output(),
                                    input_matrix=f'{self.global_control}.worldMatrix[0]')
        cmds.parent(self.root.appendage_grp, self.rig_grp)
        utils.rename_hierarchy(self.settings['Root']['start_joint'].output(), end_joint=None, unlock=True)

    def build_spine(self):
        logger.debug('build_root')
        self.spine = spine.Spine(self.settings['Spine']['appendage_name'],
                                self.settings['Spine']['start_joint'],
                                input_matrix= f"{self.root.controls['fk']['root']}.worldMatrix[0]")

    def build_head(self):
        logger.debug('build_head')
        self.head = head.Head(SETTINGS['Head']['appendage_name'],
                                    SETTINGS['Head']['start_joint'],
                                    SETTINGS['Head']['num_neck_joints'],
                                    input_matrix='driver_spine_bnd_jnt_05_fk_ctrl_transform.worldMatrix[0]')
        cmds.parent(self.head.appendage_grp, self.rig_grp)

    def build_arms(self):
        logger.debug('build_arms')


    def build_legs(self):
        logger.debug('build_legs')
        self.legs = dict()
        for side in self.sides:
            self.legs[side] = leg.Leg(self.settings['Leg']['appendage_name'].rename(side=side).output(),
                                    self.settings['Leg']['start_joint'].rename(side=side).output(),
                                    self.settings['Leg']['num_upperTwist_joint'],
                                    self.settings['Leg']['num_lowerTwist_joint'],
                                    side,
                                    input_matrix = f"{self.root.controls}['fk']['root'].worldMatrix[0]")
            cmds.parent(self.legs[side].appendage_grp, self.rig_grp)



    def build_hands(self):
        logger.debug('build_hand')
        # self.hands = dict()
        # for side in self.sides:
        #     self.hands[side] = appendages.hand.Hand()
        self.hand_lt = hand.Hand(SETTINGS['Hand_Left']['appendage_name'],
                                            SETTINGS['Hand_Left']['start_joint'],
                                            SETTINGS['Hand_Left']['num_upperTwist_joint'],
                                            SETTINGS['Hand_Left']['num_lowerTwist_joint'],
                                            SETTINGS['Hand_Left']['input_matrix'])
        self.hand_rt = hand.Hand(SETTINGS['Hand_Right']['appendage_name'],
                                            SETTINGS['Hand_Right']['start_joint'],
                                            SETTINGS['Hand_Right']['num_upperTwist_joint'],
                                            SETTINGS['Hand_Right']['num_lowerTwist_joint'],
                                            SETTINGS['Hand_Right']['input_matrix'])
        cmds.parent(self.hand_lt.appendage_grp, self.rig_grp)
        cmds.parent(self.hand_rt.appendage_grp, self.rig_grp)
