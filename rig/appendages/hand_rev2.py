import maya.cmds as cmds
import adv_scripting.rig_name as rig_name
import adv_scripting.utilities as utils
import adv_scripting.matrix_tools as matrix_tools
import adv_scripting.rig.appendages.appendage as appendage
import adv_scripting.rig.appendages.finger as finger
import logging
import copy
import importlib as il
il.reload(utils)
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
        for index, root in enumerate(self.finger_roots):
            finger_appendage = finger.Finger(f'finger_0{index+1}', root, self.side)
            self.bnd_joints[f'finger_0{index+1}'] = finger_appendage.bnd_joints
            cmds.parent(finger_appendage.appendage_grp, self.appendage_grp)

        logger.debug(f'self.bnd_joints: {self.bnd_joints}')

    def connect_inputs(self):
        '''
        Connect the input matricies from the input node to the root control of the appendage.
        '''
        return

    def connect_outputs(self):
        '''
        Connect the ouput matricies to their corresponding joints in the source skeleton
        '''
        return

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
