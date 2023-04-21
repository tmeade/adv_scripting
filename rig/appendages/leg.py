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
	        self.ball_joint = mc.listRelatives(self.bnd_joints['end_joint'])[0]
	        mc.addAttr(self.output, longName='ball_matrix', attributeType='matrix')
	        self.bnd_joins['ball_matrix'] = self.ball_joint
	        self.ankle_joint = mc.listRelatives(self.bndjoints['start_joint'])[0]

    def build_leg(self):
        # Build foot rig ///reverse foot
        self.ball_control =
        cmds.duplicate(bnd_lt_ankle_bnd_jnt, rc = True)
		# Unparent the duplicated joint
   	 	cmds.parent('lt_ankle_bnd_jnt1', world=True)


   	 	# I tried to build reverse foot manually but the end joint is not avaiable to rotate


    def connect_leg_output(self):
        mc.connectAttr(f'{self.output}.ball_matrix', f'{self.ball_joint}.offsetParentMatrix')

    def cleanup_leg(self):
        mc.parent(self.clavicle_control, self.controls_grp)
        mc.parent(self.fk_arm_controls[0], self.clavicle_control)






'''
    for eachJoint in fkjoints:
        # Create a NURBS circle
        ctrlCircle = cmds.circle(name='ctrl_'+eachJoint, nr=(1,0,0), c=(0, 0, 0), r=1.5, n='Circle1_%s' % eachJoint)
        # Create a NURBS circle offset grp
        ctrloffset = mc.group(ctrlCircle[0], name=ctrlCircle[0] + "_offset")
        # Match the circle to the joint using the snap_offset_parent_matrix function
        mt.snap_offset_parent_matrix(ctrloffset, eachJoint)
        # Create a matrix parent constraint between the joint and the circle
        mt.matrix_parent_constraint(ctrloffset, eachJoint)
'''