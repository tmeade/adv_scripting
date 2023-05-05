import maya.cmds as cmds
import maya.api.OpenMaya as om
import adv_scripting.rig_name as rig_name
import adv_scripting.matrix_tools as matrix_tools
import adv_scripting.rig.appendages.two_bone_fkik as two_bone_fkik

import logging
logger = logging.getLogger(__name__)

import importlib as il
il.reload(two_bone_fkik)

class Arm(two_bone_fkik.TwoBoneFKIK):
    def __init__(   self,
                    appendage_name,
                    start_joint,
                    num_upperTwist_joint,
                    num_lowerTwist_joint,
                    side,
                    element,
                    control_to_local_orient=False,
                    input_matrix=None):
        two_bone_fkik.TwoBoneFKIK.__init__( self,
                                            appendage_name,
                                            start_joint,
                                            num_upperTwist_joint,
                                            num_lowerTwist_joint,
                                            side,
                                            element,
                                            control_to_local_orient,
                                            input_matrix)
        self.side = side
        self.control_to_local_orient = control_to_local_orient
        self.setup_arm()
        self.build_arm()
        self.connect_arm_output()
        self.cleanup_arm()



    def setup_arm(self):
        # TODO: Validate/test that there is a parent joint here.
        self.clavicle_joint = cmds.listRelatives(self.start_joint, parent=True)[0]
        cmds.addAttr(self.output, longName='clavicle_matrix', attributeType='matrix')
        self.bnd_joints['clavicle_matrix'] = self.clavicle_joint

    def build_arm(self):
        self.clavicle_control = cmds.createNode('transform', n=rig_name.RigName(side=self.side,
                                                                                element='clavicle',
                                                                                control_type='fk',
                                                                                rig_type=rig_name.RigType('ctrl'),
                                                                                maya_type='transform'))
        matrix_tools.snap_offset_parent_matrix(self.clavicle_control, self.clavicle_joint)
        matrix_tools.matrix_parent_constraint(  self.clavicle_control,
                                                self.clavicle_joint,
                                                connect_output=f'{self.output}.clavicle_matrix')

        cmds.xform(self.clavicle_joint, ro = [0, 0, 0], os=True)
        cmds.setAttr(f'{self.clavicle_joint}.jointOrient', 0,0,0)
        self.fk_controls.append(self.clavicle_control)

    def connect_arm_output(self):
        cmds.connectAttr(f'{self.output}.clavicle_matrix', f'{self.clavicle_joint}.offsetParentMatrix')
        matrix_tools.make_identity(self.clavicle_joint)

    def cleanup_arm(self):
        cmds.parent(self.clavicle_control, self.controls_grp)
        cmds.parent(self.fk_controls[0], self.clavicle_control)
        matrix_tools.matrix_parent_constraint(self.clavicle_control, self.fk_controls[0])


'''
import adv_scripting.rig.appendages.arm as arm
il.reload(arm)
arm = arm.Arm('arm', 'lt_upArm_bnd_jnt_01', 1, 1, 'lt', 'arm')
'''
