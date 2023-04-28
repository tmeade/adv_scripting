import maya.cmds as cmds
import adv_scripting.rig_name as rn
import adv_scripting.matrix_tools as mt
import adv_scripting.rig.appendages.appendage as appendage
import pole_vector as pv
import adv_scripting.utilities as utils
import adv_scripting.rig.appendages.two_bone_fkik as two_bone_fkik
import logging
logger = logging.getLogger(__name__)

class Leg(two_bone_fkik.TwoBoneFKIK):
	def __init__(	self,
					appendage_name,
					start_joint,
					num_upleg_joint,
					num_ankle_joint,
					side,
					input_matrix=None):
		two_bone_fkik.TwoBoneFKIK.__init__( self,
											appendage_name,
											start_joint,
											num_upleg_joint,
											num_lowleg_joint,
											num_ankle_joint,
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

	    skeleton = cmds.listRelatives(self.start_joint, ad=True)
	    skeleton.reverse()



        self.bnd_joints = dict()


        self.bnd_joints['start_joint'] = self.start_joint
        if self.num_upleg_joint > 0:
            for index in range(self.num_upleg_joint):
                self.bnd_joints[f'up_twist_{index+1}'] = skeleton[index]
        self.bnd_joints['middle_joint'] = skeleton[self.num_upleg_joint]
        if self.num_lowleg_joint > 0:
            for index in range(self.num_lowleg_joint):
                self.bnd_joints[f'low_twist_{index+1}'] = skeleton[self.num_upleg_joint + index+1]
        self.bnd_joints['end_joint'] = skeleton[self.num_upleg_joint + self.num_lowleg_joint + 1]

		'''
		self.upleg_joint = cmds.listRelatives(self.bnd_joints['start_joint'])[0]
		self.bnd_joints['upleg_matrix'] = self.upleg_joint
		self.bnd_joints['ankle_joint'] = self.skeleton[self.num_upleg_joints + 4]
		'''
		self.rev_joints = dict()
	    self.ankle_joint = cmds.listRelatives(self.rev_joints['start_joint'])[0]
        self.rev_joints['toe_joint'] = self.skeleton[self.num_ankle_joints + 2]


	   # Extract a control skeleton for the fk
     	self.fk_skeleton = utils.create_control_joints_from_skeleton(self.bnd_joints['start_joint'],
                                                                self.bnd_joints['end_joint'],
                                                                rig_name.ControlType('fk'),
                                                                self.num_upleg_joints)
                                                               

        # Extract a control skeleton for the ik
        self.ik_skeleton = utils.create_control_joints_from_skeleton(self.bnd_joints['start_joint'],
                                                                self.bnd_joints['end_joint'],
                                                                rig_name.ControlType('ik'),
                                                                self.num_upleg_joints)

        # Extract a control skeleton for the revfoot
        self.rev_skeleton = utils.create_control_joints_from_skeleton(self.ankle_joint['start_joint'],
                                                                self.rev_joints['end_joint'],
                                                                rig_name.ControlType('rev'),
                                                                self.num_ankle_joints)

        utils.rename_skeleton_rev(self.rev_skeleton)

    def build_leg(self):
        # Build foot rig ///reverse foot

   
        self.fk_upleg_control = cmds.createNode('transform', n=rig_name.RigName(side=self.side,
                                                                                element='upleg',
                                                                                control_type='fk',
                                                                                rig_type=rig_name.RigType('ctrl'),
                                                                                maya_type='transform'))
        matrix_tools.snap_offset_parent_matrix(self.upleg_control, self.upleg_joint)
        matrix_tools.matrix_parent_constraint(self.upleg_control,
                                              self.upleg_joint,
                                              onnect_output=f'{self.output}.upleg_matrix')
        cmds.xform(self.leg_joint, ro = [0, 0, 0], os=True)
        cmds.setAttr(f'{self.leg_joint}.jointOrient', 0,0,0)
        self.fk_leg_controls.append(self.upleg_control)
       

        '''

		self.upleg_control = utils.create_fk_control(self.bnd_joints['start_joint'], f'{self.output}.start_joint_matrix')
        self.head_ctrl = utils.create_fk_control(self.bnd_joints['head_joint'], f'{self.output}.head_joint_matrix')
     	
     	'''

        #IK
        root, root_rn = self.ik_skeleton[0]
        mid, mid_rn =  self.ik_skeleton[1]
        end, end_rn =  self.ik_skeleton[2]
        self.side = str(root_rn.side)
        self.element = str(root_rn.element)
        upleg_ik_handle = rig_name.RigName(element=self.element, side=self.side,
            control_type='ik', rig_type='handle', maya_type='ikrpsolver')
        upleg_ik_control = rig_name.RigName(element=self.element, side=self.side,
            control_type='ik', rig_type='ctrl', maya_type='controller')

 		#IK handle
        leg_ik_handle = cmds.ikHandle(sj=root, ee=end, sol='ikRPsolver', n=str(name_ik_handle))[0]
        self.ik_control = cmds.createNode('transform', n=str(name_ik_control))
        matrix_tools.snap_offset_parent_matrix(self.ik_control, leg_ik_handle)
        cmds.parent(leg_ik_handle, self.ik_control)

        #pole vector
        leg_pv = rig_name.RigName(element=self.element, side=self.side,
            control_type='ik', rig_type='pv', maya_type='controller')
        pv_position = pole_vector.calculate_pole_vector_position(root, mid, end)
        self.arm_pv_control = cmds.createNode('transform', n=str(name_pv))


        cmds.move(pv_position.x, pv_position.y, pv_position.z, self.arm_pv_control)
        cmds.makeIdentity(self.arm_pv_control, apply=True, t=True, r=True, s=True)
        cmds.poleVectorConstraint(self.leg_pv_control, leg_ik_handle)

        #rev

        #duplicate ankle/ unparent / duplicate toe joint and renmae it heel / 
		#move back heel jnt (how to calculate the length? just type num in z? what if unit sizes are different)
		#parent heel joint to toe / select heel joint to reroot / 

	
        toe, toe_rn =  self.rev_skeleton[2]
        cmds.duplicate(self.rev_skeleton[2])
	
		# Unparent the duplicated joint
		cmds.parent(self.self.rev_skeleton)

   	 	
	
	




    def connect_leg_output(self):
        cmds.connectAttr(f'{self.output}.upleg_matrix', f'{self.upleg_joint}.offsetParentMatrix')

    def cleanup_leg(self):
        cmds.parent(self.upleg_control, self.controls_grp)
        cmds.parent(self.fk_arm_controls[0], self.upleg_control)


'''
'''