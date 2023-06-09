import maya.cmds as cmds
import adv_scripting.rig_name as rig_name
import adv_scripting.matrix_tools as matrix_tools
import adv_scripting.rig.appendages.appendage as appendage
import adv_scripting.rig.appendages.finger as finger
import logging
import importlib as il
il.reload(finger)
il.reload(appendage)


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
                 side,
                 input_matrix=None):
        '''
        Arguments:
            appendage_name (str): Name of the appendage (e.g. hand, arm, leg, spine, tail)
            start_joint (str): Name of starting joint of appendage
            input_matrix (str): If specified, will connect/contrain to the parent appendage.
        '''

        start_rn = rig_name.RigName(start_joint)
        self.side = start_rn.side.output()
        self.start_joint = start_joint
        self.appendage_name = f'{self.side}_{appendage_name}'

        # initialize Appendage class
        appendage.Appendage.__init__(self, self.appendage_name, start_joint, input_matrix)

    def setup(self):
        '''
        Method to prepare nodes for rigging. e.g.
            Create organizational groups
            Assign variables to joint names
            Measure offsets
            Create additional input matrix attributes
        '''
        # Bnd joint dict
        self.bnd_joints['hand_joint'] = self.start_joint
        self.finger_roots = cmds.listRelatives(self.start_joint, ad=False)

        logger.debug(f'self.finger_roots: {self.finger_roots}')

    def build(self):
        self.hand_control = cmds.createNode('transform',
                                            n=rig_name.RigName( side=self.side,
                                                                element='hand',
                                                                control_type='switch',
                                                                rig_type=rig_name.RigType('ctrl'),
                                                                maya_type='transform'))
        logger.debug(f'self.hand_control: {self.hand_control}')
        matrix_tools.snap_offset_parent_matrix(self.hand_control, self.start_joint)

        # Create a finger instance for each of the finger_roots and connect them to the hand control.
        for index, root in enumerate(self.finger_roots):
            finger_appendage = finger.Finger(f'finger_0{index+1}',
                                            root,
                                            self.side,
                                            input_matrix=f'{self.hand_control}.worldMatrix[0]')

            # Add bnd joints and controls from each finger to the hand's bnd_jnt and controls data.
            self.bnd_joints[f'finger_0{index+1}'] = finger_appendage.bnd_joints
            self.controls[f'finger_0{index+1}'] = finger_appendage.controls

            # Create switch attributes on the hand control for each finger and route them though the
            # input node.
            switch_node = cmds.ls(finger_appendage.FKIK_switch, uuid=True, l=True)[0]
            cmds.addAttr(self.hand_control, longName=f'finger_0{index+1}_FKIK', at='double', max=1, min=0)
            cmds.addAttr(finger_appendage.input, longName=f'finger_0{index+1}_FKIK', at='double', max=1, min=0)

            cmds.connectAttr(f'{self.hand_control}.finger_0{index+1}_FKIK',
                            f'{finger_appendage.input}.finger_0{index+1}_FKIK')
            cmds.connectAttr(f'{finger_appendage.input}.finger_0{index+1}_FKIK',
                            f'{switch_node}.FKIK')

            # Parent the finger appendage group to the hand's appendage group to keep the scene
            # organized.
            cmds.parent(finger_appendage.appendage_grp, self.appendage_grp)

        logger.debug(f'hand.bnd_joints: {self.bnd_joints}')

    def connect_inputs(self):
        '''
        Connect the input_matrix to the hand control to drive the hand appendage from parent.
        '''
        if self.input_matrix:
            matrix_tools.matrix_parent_constraint(f'{self.input}.input_matrix', self.hand_control)

    def connect_outputs(self):
        '''
        The hand control is not used to directly transform any nodes and does not have any direct
        connections from the output.  All joints are being controled from the finger outputs.
        '''
        pass

    def cleanup(self):
        '''
        Rename, parent, delete extra nodes, etc..
        '''
        return


def test():
    '''
    In Maya Script Editor (python), run:
    import adv_scripting.rig.appendages.hand as hand
    il.reload(hand)
    hand.test()
    '''
    hand_lt = Hand('hand', 'lt_hand_bnd_jnt', 'lt')
    hand_rt = Hand('hand', 'rt_hand_bnd_jnt', 'rt')
    return hand_lt, hand_rt
