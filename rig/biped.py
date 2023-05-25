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
import importlib as il
il.reload(root)
il.reload(spine)
il.reload(leg)
il.reload(arm)

logger = logging.getLogger(__name__)

SETTINGS = {'Root': {
                'appendage_name': 'root',
                'start_joint': rig_name.RigName(full_name='root_bnd_jnt')},
            'Spine': {
                'appendage_name': 'spine',
                'start_joint': rig_name.RigName(full_name='spine_bnd_jnt_01')},
            'Head': {
                'appendage_name': 'head',
                'start_joint': rig_name.RigName(full_name='neck_bnd_jnt'),
                'num_neck_joints': 0},
            'Leg': {'appendage_name': rig_name.RigName(full_name='lt_leg_appendage'),
                'start_joint': rig_name.RigName(full_name='lt_upLeg_bnd_jnt_01'),
                'num_upperTwist_joint': 1,
                'num_lowerTwist_joint': 1},
            'Hand': {
                'appendage_name': rig_name.Element('hand'),
                'start_joint': rig_name.RigName(full_name='lt_wrist_bnd_jnt'),
                'num_upperTwist_joint': None,
                'num_lowerTwist_joint': None,
                'input_matrix': rig_name.RigName(full_name='lt_lower_arm_bnd_jnt_02')},
            'Arm': {
                'appendage_name': rig_name.RigName(full_name='lt_arm_appendage'),
                'start_joint': rig_name.RigName(full_name='lt_upArm_bnd_jnt_01'),
                'num_upperTwist_joint': 1,
                'num_lowerTwist_joint': 1},
            }

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

        # TODO: add skelton grp
        self.skeleton_grp = cmds.createNode('transform', name=rig_name.RigName(
                                                        control_type = 'bnd',
                                                        rig_type='grp'))

        cmds.parent(self.settings['Root']['start_joint'],self.skeleton_grp)

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
                                 self.settings['Spine']['start_joint'].output(),
                                 input_matrix= self.root.controls['fk']['root'] + ".worldMatrix[0]")

    def build_head(self):
        logger.debug('build_head')
        self.head = appendages.head.Head(self.settings['Head']['appendage_name'],
                                         self.settings['Head']['start_joint'].output(),
                                         self.settings['Head']['num_neck_joints'],
                                         input_matrix=f'{self.global_control}.worldMatrix[0]')
        cmds.parent(self.head.appendage_grp, self.rig_grp)

    def build_arms(self):
        logger.debug('build_arms')
        self.arms  = dict()
        for side in self.sides:
            self.arms[side] = arm.Arm(self.settings['Arm']['appendage_name'].rename(side=side).output(),
                                    self.settings['Arm']['start_joint'].rename(side=side).output(),
                                    self.settings['Arm']['num_upperTwist_joint'],
                                    self.settings['Arm']['num_lowerTwist_joint'],
                                    side)
            cmds.parent(self.arms[side].appendage_grp, self.rig_grp)

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
        self.hands = dict()
        for side in self.sides:
            self.hands[side] = hand.Hand(self.settings['Hand']['appendage_name'],
                                        self.settings['Hand']['start_joint'].rename(side=side).output(),
                                        self.settings['Hand']['num_upperTwist_joint'],
                                        self.settings['Hand']['num_lowerTwist_joint'],
                                        self.settings['Hand']['input_matrix'].rename(side=side).output() + '.worldMatrix[0]')
            cmds.parent(self.hands[side].appendage_grp, self.rig_grp)
