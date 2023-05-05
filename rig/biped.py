import maya.cmds as cmds
import logging
import adv_scripting.rig_name as rig_name
import adv_scripting.rig.appendages.root as root
logger = logging.getLogger(__name__)

import importlib as il
il.reload(root)

SETTINGS = {'Root': {
                'name': 'root',
                'start_joint': 'root_bnd_jnt'},
            'Spine': {
                'appendage_name': 'spine',
                'start_joint': 'spine_bnd_jnt_01'},
            'Head': {
                'name': 'head',
                'start_joint': 'neck_bnd_jnt',
                'num_neck_joints': 0}
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

    def build(self):
        logger.debug('build')

    def connect_control_shapes(self):
        logger.debug('connect_control_shapes')

class Biped(Rig):
    def __init__(self, name, settings):
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
        self.root = appendages.root.Root(appendage_name='root',
                                    start_joint='root_bnd_jnt',
                                    input_matrix=f'{self.global_control}.worldMatrix[0]')

    def build_spine(self):
        logger.debug('build_root')

    def build_head(self):
        logger.debug('build_head')

    def build_arms(self):
        logger.debug('build_arms')

    def build_legs(self):
        logger.debug('build_legs')

    def build_hands(self):
        logger.debug('build_hands')
