from abc import ABC, abstractmethod
import logging
import maya.cmds as mc
import adv_scripting.rig_name as rn
import adv_scripting.matrix_tools as mt

logger = logging.getLogger()

class Appendage(ABC):
    def __init__(self, appendage_name, start_joint, input_matrix=None):
        '''
        Description:
            A base class for rigging appendages.
        Arguemnts:
            appendage_name (str): name of the appendage (ex: arm, leg, spine, tail).
            start_joint (str): Name of the root most joint in the appendage.
            input_matrix (str): If specified, will connect/contrain to the parent appendage.
        '''
        logger.info(f'appendage_name: {appendage_name}')
        logger.info(f'start_joint: {start_joint}')
        logger.info(f'input_matrix: {input_matrix}')

        self.appendage_name = appendage_name
        self.start_joint = start_joint
        self.input_matrix = input_matrix
        # TODO: Maybe use a dict with fk/ik keys?
        self.controls = list()

        # Run methods
        self.create_appendage_container()
        self.setup()
        self.build()
        self.connect_outputs()
        self.cleanup()
        self.finish()

    def __str__(self):
        return self.controls

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.start_joint}', appendage_name={self.appendage_name}')"

    def create_appendage_container(self):
        '''
        Sets up basic groups for appendage (parent/appendage group, controls, input and output groups)
        '''
        self.appendage_grp = mc.createNode('transform', name=rn.RigName(
                                                        element=self.appendage_name,
                                                        rig_type='grp'))
        self.controls_grp = mc.createNode('transform', name=rn.RigName(
                                                        element='controls',
                                                        rig_type='grp'))
        self.input = mc.createNode('transform', name=rn.RigName(
                                                        element='input',
                                                        rig_type='grp'))
        mc.addAttr(self.input, longName='input_matrix', attributeType='matrix')

        self.output = mc.createNode('transform', name=rn.RigName(
                                                        element='output',
                                                        rig_type='grp'))
        # mc.addAttr(self.output, longName='start_joint_matrix', attributeType='matrix')

    @abstractmethod
    def setup(self):
        '''
        Method to prepare nodes for rigging.  Example:
            Create organizational groups
            Assign variables to joint names
            Measure offsets
            Create additional input matrix attributes
        '''
        return

    @abstractmethod
    def build(self):
        '''
        Create and connect nodes for rigging
        '''
        return

    @abstractmethod
    def connect_outputs(self):
        '''
        Connect the ouput matracies to their corresponding joints in the source skeleton
        '''
        return

    @abstractmethod
    def cleanup(self):
        '''
        Rename, parent, delete extra nodes, etc..
        '''
        return

    def finish(self):
        self.controls = mc.listRelatives(self.controls_grp)
        mc.parent(self.controls_grp, self.appendage_grp)
        mc.parent(self.input, self.appendage_grp)
        mc.parent(self.output, self.appendage_grp)
