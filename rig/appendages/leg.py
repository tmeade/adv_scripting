import maya.cmds as cmds
import adv_scripting.rig_name as rig_name
import adv_scripting.matrix_tools as mt
import adv_scripting.rig.appendages.appendage as appendage
import adv_scripting.pole_vector as pv
import adv_scripting.utilities as utils
import adv_scripting.rig.appendages.two_bone_fkik as two_bone_fkik
import logging
logger = logging.getLogger(__name__)


import importlib as il
il.reload(appendage)
il.reload(mt)
il.reload(rig_name)
il.reload(utils)

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
		# self.build_leg()
		# self.connect_leg_output()
		# self.cleanup_leg()

	def setup_leg(self):
		logger.debug('setup_leg')

	    # Get foot bnd_joints
        # ball_joint
        # toe_end_joint
        # TODO: Validate/test that there is a parent joint here.
		self.upleg_joint = self.bnd_joints['start_joint']
		self.ankle_joint = self.bnd_joints['end_joint']
		try:
			self.ball_joint = cmds.listRelatives(self.ankle_joint)[0]
		except:
			logging.error('Ankel joint has not children')
			return

		self.toeEnd_joint = cmds.listRelatives(self.ball_joint)[0]
		cmds.addAttr(self.output, longName='ball_matrix', attributeType='matrix')


		print('self.ankle_joint: ', self.ankle_joint)
		print('self.toeEnd_joint: ', self.toeEnd_joint)
	    # Extract a control skeleton for the fk
		self.fk_skeleton = utils.create_control_joints_from_skeleton('lt_ankle_bnd_jnt',
		                                                    'lt_toe_end_jnt',
		                                                    rig_name.ControlType('fk'),
		                                                    0,
															0)

	def build_leg(self):
		logger.debug('build_leg')
        # TODO: name should be more accessable.  The renaming utility is basing the rename on
        # the joint name and this does not work well in this case.  rigname should be:
        #            rn.RigName(
        #                    element='root',
        #                    rig_type='ctrl',
        #                    maya_type='transform'))
		self.foot_ctrl = utils.create_fk_control(self.ball_joint,
                                                 connect_output=f'{self.output}.ball_matrix')

	def connect_leg_output(self):
		logger.debug('connect_leg_output')
    	# Connect the start matrix on the output node to the skeleton
		cmds.connectAttr(f'{self.output}.ball_matrix', f'{self.ball_joint}.offsetParentMatrix')
    

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

	def cleanup_leg(self):
		pass