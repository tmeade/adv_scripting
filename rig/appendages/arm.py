import maya.cmds as mc
import maya.api.OpenMaya as om
import adv_scripting.rig_name as rig_name
import adv_scripting.matrix_tools as matrix_tools
import adv_scripting.rig.appendages.two_bone_fkik as two_bone_fkik

import logging
logger = logging.getLogger(__name__)


class Arm(two_bone_fkik.TwoBoneFKIK):
    def __init__(   self,
                    appendage_name,
                    start_joint,
                    num_upperTwist_joint,
                    num_lowerTwist_joint,
                    side,
                    input_matrix=None):
        two_bone_fkik.TwoBoneFKIK.__init__( self,
                                            appendage_name,
                                            start_joint,
                                            num_upperTwist_joint,
                                            num_lowerTwist_joint,
                                            input_matrix)
        self.side = side
        self.setup_arm()
        self.build_arm()
        self.connect_arm_output()
        self.cleanup_arm()



    def setup_arm(self):
        # TODO: Validate/test that there is a parent joint here.
        self.clavicle_joint = mc.listRelatives(self.start_joint, parent=True)[0]
        mc.addAttr(self.output, longName='clavicle_matrix', attributeType='matrix')
        self.bnd_joints['clavicle_matrix'] = self.clavicle_joint

    def build_arm(self):
        self.clavicle_control = mc.createNode('transform', n=rig_name.RigName(side=self.side,
                                                                                element='clavicle',
                                                                                control_type='fk',
                                                                                rig_type=rig_name.RigType('ctrl'),
                                                                                maya_type='transform'))
        matrix_tools.snap_offset_parent_matrix(self.clavicle_control, self.clavicle_joint)
        matrix_tools.matrix_parent_constraint(  self.clavicle_control,
                                                self.clavicle_joint,
                                                connect_output=f'{self.output}.clavicle_matrix')

        mc.xform(self.clavicle_joint, ro = [0, 0, 0], os=True)
        mc.setAttr(f'{self.clavicle_joint}.jointOrient', 0,0,0)
        self.fk_arm_controls.append(self.clavicle_control)

    def connect_arm_output(self):
        mc.connectAttr(f'{self.output}.clavicle_matrix', f'{self.clavicle_joint}.offsetParentMatrix')

    def cleanup_arm(self):
        mc.parent(self.clavicle_control, self.controls_grp)
        mc.parent(self.fk_arm_controls[0], self.clavicle_control)
