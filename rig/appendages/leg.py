import maya.cmds as cmds
import adv_scripting.rig_name as rig_name
import adv_scripting.matrix_tools as matrix_tools
import adv_scripting.rig.appendages.appendage as appendage
import adv_scripting.pole_vector as pv
import adv_scripting.utilities as utils
import adv_scripting.rig.appendages.two_bone_fkik as two_bone_fkik
import logging
logger = logging.getLogger(__name__)


import importlib as il

il.reload(appendage)
il.reload(matrix_tools)
il.reload(rig_name)
il.reload(utils)
il.reload(two_bone_fkik)

class Leg(two_bone_fkik.TwoBoneFKIK):
	'''
	Description: The leg class uses the data from the two_bone_fkik output as the leg and attaches an
				fk and ik foot rig to the end.
	'''
	def __init__(	self,
					appendage_name,
					start_joint,
					side,
					num_upleg_joints,
					num_lowleg_joints,
					rotate_axis = 'rz',
					axis_orient = -1,
                    control_to_local_orient=False,
					input_matrix=None):

		two_bone_fkik.TwoBoneFKIK.__init__( self,
											appendage_name,
											start_joint,
											side,
											num_upleg_joints,
											num_lowleg_joints,
											rotate_axis,
											axis_orient,
                                            control_to_local_orient,
											input_matrix)

		self.side = side
		self.rotate_axis = rotate_axis
		self.control_to_local_orient = control_to_local_orient
		self.setup_foot()
		self.build_fk_foot()
		self.build_ik_foot()
		self.connect_leg_output()
		self.connect_foot_inputs()
		self.cleanup_leg()

	def setup_foot(self):
		logger.debug('setup_leg')

	    # Get foot bnd_joints (ball_joint, toe_end_joint)
		try:
			self.ball_joint = cmds.listRelatives(self.bnd_joints['end_joint'])[0]
			self.bnd_joints['ball_joint'] = self.ball_joint
		except IndexError:
			logging.error(f"{self.bnd_joints['end_joint']} has no children.")
			return

		try:
			self.toeEnd_joint = cmds.listRelatives(self.ball_joint)[0]
		except IndexError:
			logging.error(f'{self.ball_joint} joint has no children.')
			return

		cmds.addAttr(self.output, longName='ball_matrix', attributeType='matrix')

		# WARNING: Begin hack.  Running the code without creating the skeleton and deleting it
		# results in the ankle joint positioned at the knee.  I suspect that something is selected
		# when a joint gets created somewhere in the code?
		workaround_garbage = utils.create_control_joints_from_skeleton(self.bnd_joints['end_joint'],
		                                                    self.toeEnd_joint,
		                                                    rig_name.ControlType('switch'),
		                                                    0,
															0)
		cmds.delete(workaround_garbage[0])
		# WARNING: End hack.  (soooo annoying)

	    # Extract a control skeleton for the fk
		self.fk_foot_skeleton = utils.create_control_joints_from_skeleton(self.bnd_joints['end_joint'],
					                                                    self.toeEnd_joint,
					                                                    rig_name.ControlType('fk'),
					                                                    0,
																		0)
		# Extract a control skeleton for the ik
		self.ik_foot_skeleton = utils.create_control_joints_from_skeleton(self.bnd_joints['end_joint'],
					                                                    self.toeEnd_joint,
					                                                    rig_name.ControlType('ik'),
					                                                    0,
																		0)

	def build_fk_foot(self):
		logger.debug('build_fk_foot')

		# Create a control for the fk ball joint and parent that control to the leg's fk control
		# hierarchy.
		self.ball_ctrl = utils.create_fk_control(self.fk_foot_skeleton[1][1].output(),
                                                 parent_control=self.fk_controls['ctrl_2'])
	def build_ik_foot(self):
		logger.debug('build_ik_foot')

		name_ball_ik_handle = rig_name.RigName(element='ball',
											side=self.side,
        									control_type='ik',
        									rig_type='handle',
        									maya_type='ikrpsolver')
		name_ball_ik_control = rig_name.RigName(element='ball',
											side=self.side,
            								control_type='ik',
            								rig_type='ctrl',
            								maya_type='controller')

		self.ball_ik_handle = cmds.ikHandle(  sj=self.ik_foot_skeleton[0][1].output(),
										 ee=self.ik_foot_skeleton[1][1].output(),
										 sol='ikRPsolver',
										 n=str(name_ball_ik_handle))[0]
		self.ball_ik_control = cmds.createNode('transform', n=str(name_ball_ik_control))

		name_toe_ik_handle = rig_name.RigName(element='toe',
											side=self.side,
        									control_type='ik',
        									rig_type='handle',
        									maya_type='ikrpsolver')
		name_toe_ik_control = rig_name.RigName(element='toe',
											side=self.side,
            								control_type='ik',
            								rig_type='ctrl',
            								maya_type='controller')

		self.toe_ik_handle = cmds.ikHandle(  sj=self.ik_foot_skeleton[1][1].output(),
										 	 ee=self.ik_foot_skeleton[2][1].output(),
										 	 sol='ikRPsolver',
										 	 n=str(name_toe_ik_handle))[0]
		self.toe_ik_control = cmds.createNode('transform', n=str(name_toe_ik_control))

		# Create ik pivot HIERARCHY
		matrix_tools.snap_offset_parent_matrix(self.toe_ik_control, self.ik_foot_skeleton[2][1].output())
		matrix_tools.snap_offset_parent_matrix(self.ball_ik_control, self.ik_foot_skeleton[1][1].output())
		cmds.parent(self.ball_ik_control, self.toe_ik_control)
		cmds.parent(self.toe_ik_handle, self.toe_ik_control)
		cmds.parent(self.ball_ik_handle, self.toe_ik_control)
		print ('self.ik_controls[0]', self.ik_controls['end_ctrl'])
		#TODO: This does nto seem to be parenting
		cmds.parent(self.toe_ik_control, self.ik_controls['end_ctrl'])

		leg_ik_handle = cmds.listRelatives(self.ik_controls['end_ctrl'])
		cmds.parent(leg_ik_handle[0], self.ball_ik_control)

		cmds.pointConstraint(self.ik_skeleton[-1], self.ik_foot_skeleton[0])

	def create_blended_result(self):
		'''
		Take the output matricies fromt he ik and fk and combine them using a blendMatrix node.  The
		result gets output ot he output node's joint matrix attribute.
		'''
		logger.debug('create_blended_result')

	def connect_leg_output(self):
		logger.debug('connect_leg_output')
    	# Connect the start matrix on the output node to the skeleton
		cmds.connectAttr(f'{self.output}.ball_matrix', f'{self.ball_joint}.offsetParentMatrix')
		matrix_tools.make_identity(self.ball_joint)

	def connect_foot_inputs(self):
		logger.debug('connect_inputs')
		print ('self.input', self.input)
		# if self.input_matrix:
		# 	matrix_tools.matrix_parent_constraint(f'{self.input}.input_matrix', self.fk_controls['ctrl_0'])
		# 	matrix_tools.matrix_parent_constraint(f'{self.input}.input_matrix', self.ik_skeleton[0][0])

	def cleanup_leg(self):
		logger.debug('cleanup_leg')
		cmds.parent(self.toe_ik_control, self.controls_grp)
		cmds.parent(self.fk_foot_skeleton[0], self.controls_grp)
		cmds.parent(self.ik_foot_skeleton[0], self.toe_ik_control)
		#cmds.parent(self.fk_foot_skeleton, self.input_grp)
		#cmds.parent(self.ik_foot_skeleton, self.input_grp)

'''
import adv_scripting.rig.appendages.leg as leg
il.reload(leg)
leg = leg.Leg('leg', 'lt_upLeg_bnd_jnt_01', 1, 1, 'lt')
'''
