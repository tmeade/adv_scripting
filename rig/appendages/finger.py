import maya.cmds as cmds
import adv_scripting.rig_name as rig_name
import adv_scripting.utilities as utils
import adv_scripting.matrix_tools as matrix_tools
import adv_scripting.rig.appendages.two_bone_fkik as two_bone_fkik
import logging
import importlib as il
il.reload(utils)
il.reload(two_bone_fkik)


logger = logging.getLogger()


class Finger(two_bone_fkik.TwoBoneFKIK):
    def __init__(   self,
                    appendage_name,
                    start_joint,
                    side,
                    input_matrix=None):
        two_bone_fkik.TwoBoneFKIK.__init__( self,
                                            appendage_name,
                                            start_joint,
                                            side,
                                            control_to_local_orient=True,
                                            input_matrix=input_matrix)

        self.cleanup_finger()


    def cleanup_finger(self):
        pass
