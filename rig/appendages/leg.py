import maya.cmds as cmds
import adv_scripting.rig_name as rig_name
import adv_scripting.matrix_tools as mt
import adv_scripting.rig.appendages.appendage as appendage
import adv_scripting.pole_vector as pv
import adv_scripting.utilities as utils
import adv_scripting.rig.appendages.two_bone_fkik as two_bone_fkik
import logging
logger = logging.getLogger(__name__)

class Leg(two_bone_fkik.TwoBoneFKIK):
	def __init__(	self,
					appendage_name,
					start_joint,
					num_upleg_joints,
					num_lowleg_joints,
					side,
					input_matrix=None):

		two_bone_fkik.TwoBoneFKIK.__init__( self,
											appendage_name,
											start_joint,
											num_upleg_joints,
											num_lowleg_joints,
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
        self.upleg_joint = self.bnd_joints['start_joint']
		self.ankle_joint = self.bnd_joints['end_joint']
		self.ball_joint = cmds.listRelatives(self.ankle_joint)
		self.toeEnd_joint = cmds.listRelatives(self.ball_joint)
		mc.addAttr(self.output, longName='foot_matrix', attributeType='matrix')


	    # Extract a control skeleton for the fk
		self.fk_skeleton = utils.create_control_joints_from_skeleton(self.ankle_joint,
		                                                    self.toeEnd_joint,
		                                                    rig_name.ControlType('fk'),
		                                                    self.num_upperTwist_joints,
															self.num_lowerTwist_joints)

	def build(self):
        # TODO: name should be more accessable.  The renaming utility is basing the rename on
        # the joint name and this does not work well in this case.  rigname should be:
        #            rn.RigName(
        #                    element='root',
        #                    rig_type='ctrl',
        #                    maya_type='transform'))
        self.foot_ctrl = utils.create_fk_control(self.start_joint,
                                                 connect_output=f'{self.output}.foot_matrix')

    def connect_outputs(self):
        # Connect the start matrix on the output node to the skeleton
        cmds.connectAttr(f'{self.output}.foot_matrix', f'{self.start_joint}.offsetParentMatrix')
    

		# Extract a control skeleton for the ik
		# self.ik_skeleton = utils.create_control_joints_from_skeleton(self.bnd_joints['start_joint'],
		#                                                         self.bnd_joints['end_joint'],
		#                                                         rig_name.ControlType('ik'),
		#                                                         self.num_upleg_joints)
		#
		# # Extract a control skeleton for the revfoot
		# self.rev_skeleton = utils.create_control_joints_from_skeleton(self.ankle_joint['start_joint'],
		#                                                         self.rev_joints['end_joint'],
		#                                                         rig_name.ControlType('rev'),
		#                                                         self.num_ankle_joints)
		#
		# utils.rename_skeleton_rev(self.rev_skeleton)
