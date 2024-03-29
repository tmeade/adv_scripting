import maya.cmds as cmds
import logging
import adv_scripting.rig_name as rig_name
import adv_scripting.rig.appendages.root as root
import adv_scripting.rig.appendages.spine as spine
import adv_scripting.rig.appendages.head as head
import adv_scripting.rig.appendages.leg as leg
import adv_scripting.rig.appendages.arm as arm
import adv_scripting.rig.appendages.hand_rev2 as hand
import adv_scripting.rig.settings as rig_settings
import adv_scripting.utilities as utils
import adv_scripting.matrix_tools as matrix_tools
import importlib as il
il.reload(root)
il.reload(head)
il.reload(spine)
il.reload(leg)
il.reload(arm)
il.reload(hand)
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
        # self.connect_control_shapes()

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
                                                        element='skeleton',
                                                        rig_type='grp'))
        cmds.parent(self.settings.root_start_joint, self.skeleton_grp)
        cmds.parent(self.skeleton_grp, self.rig_grp)

        self.controls_grp = cmds.createNode('transform', name=rig_name.RigName(
                                                        element='controls',
                                                        rig_type='grp'))
        cmds.parent(self.controls_grp, self.rig_grp)

        # TODO: global control should inherit from appendage.
        self.global_control = cmds.createNode('transform', name=rig_name.RigName(
                                                        element='main',
                                                        rig_type='ctrl'))
        cmds.parent(self.global_control, self.controls_grp)

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
        self.build_hands()

    def connect_control_shapes(self):
        # List all appendages
        appendages = [self.root, self.spine, self.head,
            self.arms[self.sides[0]], self.arms[self.sides[1]],
            self.legs[self.sides[0]], self.legs[self.sides[1]],
            self.hands[self.sides[0]], self.hands[self.sides[1]]]

        # List of all controls
        controls = list()

        for appendage in appendages:
            logger.debug(appendage.appendage_name)
            fk_controls = list()
            ik_controls = list()
            switch_controls = list()
            if 'fk' in appendage.controls:
                fk_controls = appendage.controls['fk'].items()
            if 'ik' in appendage.controls:
                ik_controls = appendage.controls['ik'].items()
            if 'switch' in appendage.controls:
                switch_controls = appendage.controls['switch'].items()

            for label, ctrl in fk_controls: # FK Controls
                controls.append(ctrl)
                ctrlname = rig_name.RigName(ctrl).remove(maya_type=True).output()
                ctrlfk = utils.create_control(ctrl, parent=self.global_control, size=1, name=ctrlname)
                utils.display_color(ctrlfk, 15) # Blue display color
            for label, ctrl in ik_controls: # IK Controls
                controls.append(ctrl)
                ctrlname = rig_name.RigName(ctrl).remove(maya_type=True).output()
                if 'pv' in label: # PV Control
                    ctrlik = utils.create_control_pv(ctrl, ctrlname, parent=self.global_control, size=1)
                else:
                    ctrlik = utils.create_control(ctrl, parent=self.global_control, size=1, name=ctrlname)
                utils.display_color(ctrlik, 10) # Peach display color
            for label, ctrl in switch_controls:
                controls.append(ctrl)
                ctrlname = rig_name.RigName(ctrl).remove(maya_type=True).output()
                ctrlswitch = utils.create_control(ctrl, parent=self.global_control, size=1, name=ctrlname)
                utils.display_color(ctrlswitch, 22) # Yellow display color

        # Connect controls as message to top node rig_grp
        for control in controls:
            cmds.addAttr(self.rig_grp, ln=control, at='message')
            cmds.connectAttr(f'{control}.message', f'{self.rig_grp}.{control}')

        # self.shape_grp = rig_name.RigName(side=None,
        #                             element="shape",
        #                             control_type=None,
        #                             rig_type='grp',
        #                             maya_type='transform').output()
        # self.shape_grp = cmds.createNode('transform', n="shape_grp")
        #
        # for
        #     utilities.create_control(node, parent=None, size=1, name=None):
        #
        #self_ctrl_list = cmds.ls(type='transform')
        #self_ctrl_list = [ctrl for ctrl in self_ctrl_list if '_ctrl_transform' in ctrl]
        # for i in range(len(self_ctrl_list)):
        #     self.controller_shape = cmds.circle(normal=(0, 1, 0), sweep=360, radius=20, degree=3,
        #                                       useTolerance=False,
        #                                       tolerance=0, constructionHistory=False, name=self_ctrl_list[i] + "_shape")[0]
        #     matrix_tools.snap_offset_parent_matrix(self.controller_shape, self_ctrl_list[i])
        #     # Temporary_parent
        #     cmds.parent(self.controller_shape,self.shape_grp)

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
                                 input_matrix= self.root.result_matrix)
        cmds.parent(self.spine.appendage_grp, self.rig_grp)

    def build_head(self):
        logger.debug('build_head')
        self.head = head.Head(self.settings.head_appendage_name,
                                         rig_name.RigName(full_name=self.settings.head_start_joint).output(),
                                         self.settings.head_num_twist_joints,
                                         input_matrix= self.spine.controls['ik']['spine_fk_5'] + ".worldMatrix[0]")
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
                                    side,
                                    self.settings.arm_num_upperTwist_joints,
                                    self.settings.arm_num_lowerTwist_joints,
                                    input_matrix= self.spine.controls['ik']['spine_fk_5'] + ".worldMatrix[0]")
            cmds.parent(self.arms[side].appendage_grp, self.rig_grp)

    def build_legs(self):
        logger.debug('build_legs')

        self.legs = dict()
        for side in self.sides:
            self.legs[side] = leg.Leg(rig_name.RigName(
                                        full_name=self.settings.leg_appendage_name).rename(
                                        side=side).output(),
                                    rig_name.RigName(
                                        full_name=self.settings.leg_start_joint).rename(
                                        side=side).output(),
                                    side,
                                    self.settings.leg_num_upperTwist_joints,
                                    self.settings.leg_num_lowerTwist_joints,
                                    input_matrix = self.root.result_matrix)

            cmds.parent(self.legs[side].appendage_grp, self.rig_grp)

    def build_hands(self):
        logger.debug('build_hand')
        self.hands = dict()
        for side in self.sides:
            self.hands[side] = hand.Hand(self.settings.hand_appendage_name,
                                        rig_name.RigName(
                                            full_name=self.settings.hand_start_joint).rename(
                                            side=side).output(),
                                        side,
                                        input_matrix = self.arms[side].result_matrix)
            cmds.parent(self.hands[side].appendage_grp, self.rig_grp)

def build_biped(rig_settings):
    logging.info(f'Building {rig_settings.asset_name} rig......')

    rig = Biped(rig_settings.asset_name)
    logging.info(f'Finished building rig: {rig}')
