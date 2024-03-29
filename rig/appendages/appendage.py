from abc import ABC, abstractmethod
import logging
import maya.cmds as cmds
import adv_scripting.rig_name as rig_name

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
        self.bnd_joints = dict()
        self.controls = {'fk': {}, 'ik': {}, 'switches': {}}
        '''
        Example:
        {
        'fk': {'lt_up_arm': 'lt_uparm_ctrl_tranform',
                'lt_elbow': lt_elbow_ctrl_transform},
        'ik': {'lt_wrist': 'lt_wrist_ctrl_transform',
                lt_arm_pv': 'lt_arm_pv_ctrl_transform'},
        'switches': {'lt_arm_space_switch': 'lt_arm_space_switch_grp'}
        }
        '''
        self.skeleton = cmds.listRelatives(self.start_joint, ad=True)

        # Run methods
        self.create_appendage_container()
        self.setup()
        self.create_output_attributes()
        self.build()
        self.connect_inputs()
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
        self.appendage_grp = cmds.createNode('transform', name=rig_name.RigName(
                                                        element=self.appendage_name,
                                                        rig_type='grp').output())
        self.controls_grp = cmds.createNode('transform', name=rig_name.RigName(
                                                        element='controls',
                                                        rig_type='grp').output())
        self._input = cmds.ls(cmds.createNode('transform', name=rig_name.RigName(
                                                        element='input',
                                                        rig_type='grp').output()),
                                                        uuid=True)[0]
        cmds.addAttr(self.input, longName='input_matrix', attributeType='matrix')

        self._output = cmds.ls(cmds.createNode('transform', name=rig_name.RigName(
                                                        element='output',
                                                        rig_type='grp').output()),
                                                        uuid=True)[0]
        if self.input_matrix:
            cmds.connectAttr(self.input_matrix, f'{self.input}.input_matrix')

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

    def create_output_attributes(self):
        '''
        Create matrix attributes on the appendage's output node for each of the joints in the
        source skeleton.  Also add an attribute for the leaf-most world matrix of the appendage to
        connect to other appendages.
        '''
        # Add a matrix attribute that holds the end/leaf most world space matrix of the appendage.
        # This will be what other child appendages can connect to.
        cmds.addAttr(self.output, longName='output_leaf_world_matrix', attributeType='matrix')
        # Add a matrix attribute to represent each bnd joint on the output node
        for joint_name in self.bnd_joints.keys():
            cmds.addAttr(self.output, longName=f'{joint_name}_matrix', attributeType='matrix')

            logger.debug(f'Added {joint_name}_matrix attribute to {self.output}')


    @abstractmethod
    def build(self):
        '''
        Create and connect nodes for rigging
        '''
        return

    @abstractmethod
    def connect_inputs(self):
        '''
        Connect the input matricies from the input node to the root control of the appendage.
        '''
        return

    @abstractmethod
    def connect_outputs(self):
        '''
        Connect the ouput matricies to their corresponding joints in the source skeleton.  Disabling
        this method will allow the rig to be built without a connection to the skelton.
        '''
        return

    @abstractmethod
    def cleanup(self):
        '''
        Rename, parent, delete extra nodes, etc..
        '''
        return

    def finish(self):
        cmds.parent(self.controls_grp, self.appendage_grp)
        self.controls_grp = cmds.listRelatives(self.appendage_grp, f=True)[-1]
        cmds.parent(self.input, self.appendage_grp)
        cmds.parent(self.output, self.appendage_grp)

    @property
    def input(self):
        return cmds.ls(self._input, uuid=True, l=True)[0]
        logger.info(f'input: {self.input}')

    @property
    def output(self):
        return cmds.ls(self._output, uuid=True, l=True)[0]
        logger.info(f'output: {self.output}')

    @property
    def result_matrix(self):
        return f'{self.output}.output_leaf_world_matrix'
