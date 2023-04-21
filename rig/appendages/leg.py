import maya.cmds as cmds
import adv_scripting.rig_name as rn
import adv_scripting.matrix_tools as mt
import adv_scripting.rig.appendages.appendage as rap
import pole_vector as pv
import adv_scripting.rig.appendages.two_bone_fkik as two_bone_fkik
import logging
logger = logging.getLogger(__name__)

class Leg(two_bone_fkik.TwoBoneFKIK):
	def __init__(	self,
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
        self.setup_leg()
        self.build_leg()
        self.connect_leg_output()
        self.cleanup_leg()

	def setup_leg(self):
	        # Get foot bnd_joints
	        # ball_joint
	        # toe_end_joint
	        # TODO: Validate/test that there is a parent joint here.
	        self.upleg_joint = mc.listRelatives(self.bnd_joints['start_joint'])[0]
	        self.ball_joint = mc.listRelatives(self.bnd_joints['end_joint'])[0]
	        mc.addAttr(self.output, longName='ball_matrix', attributeType='matrix')
	        self.bnd_joins['ball_matrix'] = self.ball_joint
	        self.ankle_joint = mc.listRelatives(self.bndjoints['start_joint'])[0]

    def build_leg(self):
        # Build foot rig ///reverse foot
        self.ball_control = mc.createNode('transform', n=rig_name.RigName(side=self.side,
                                                                                element='clavicle',
                                                                                control_type='fk',
                                                                                rig_type=rig_name.RigType('ctrl'),
                                                                                maya_type='transform'))
        matrix_tools.snap_offset_parent_matrix(self.ball_control, self.ball_joint)
        matrix_tools.matrix_parent_constraint(  self.ball_control,
                                                self.ball_joint,
                                                connect_output=f'{self.output}.ball_matrix')




'''
        cmds.duplicate(bnd_lt_ankle_bnd_jnt, rc = True)
		# Unparent the duplicated joint
   	 	cmds.parent('lt_ankle_bnd_jnt1', world=True)
'''

   	 	# I tried to build reverse foot manually but the end joint is not avaiable to rotate
	
	#duplicate ankle/ unparent / add "_rev"suffix / duplicate toe joint and renmae it heel / move back heel jnt
	#parent heel joint to toe / select heel joint to reroot / 




    def connect_leg_output(self):
        mc.connectAttr(f'{self.output}.ball_matrix', f'{self.ball_joint}.offsetParentMatrix')

    def cleanup_leg(self):
        mc.parent(self.ball_control, self.controls_grp)
        mc.parent(self.fk_arm_controls[0], self.ball_control)


