class BipedSettings():
    def __init__(self,
        asset_name = 'Biped',
        root_appendage_name = 'root',
        root_start_joint = 'root_bnd_jnt',
        spine_appendage_name = 'spine',
        spine_start_joint = 'spine_bnd_jnt_01',
        spine_num_spine_joints = 5,
        head_appendage_name = 'head',
        head_start_joint = 'neck_bnd_jnt',
        head_num_twist_joints = 0,
        arm_appendage_name = 'lt_arm_appendage',
        arm_start_joint = 'lt_upArm_bnd_jnt_01',
        arm_num_upperTwist_joints = 1,
        arm_num_lowerTwist_joints = 1,
        leg_appendage_name = 'lt_leg_appendage',
        leg_start_joint = 'lt_upLeg_bnd_jnt_01',
        leg_num_upperTwist_joints = 1,
        leg_num_lowerTwist_joints = 1,
        hand_appendage_name = 'hand',
        hand_start_joint = 'lt_hand_bnd_jnt',
        hand_num_upperTwist_joint = 0,
        hand_num_lowerTwist_joint = 0
        ):

        self.asset_name = asset_name
        self.root_appendage_name = root_appendage_name
        self.root_start_joint = root_start_joint
        self.spine_appendage_name = spine_appendage_name
        self.spine_start_joint = spine_start_joint
        self.spine_num_spine_joints = spine_num_spine_joints
        self.head_appendage_name = head_appendage_name
        self.head_start_joint = head_start_joint
        self.head_num_twist_joints = head_num_twist_joints
        self.arm_appendage_name = arm_appendage_name
        self.arm_start_joint = arm_start_joint
        self.arm_num_upperTwist_joints = arm_num_upperTwist_joints
        self.arm_num_lowerTwist_joints = arm_num_lowerTwist_joints
        self.leg_appendage_name = leg_appendage_name
        self.leg_start_joint = leg_start_joint
        self.leg_num_upperTwist_joints = leg_num_upperTwist_joints
        self.leg_num_lowerTwist_joints = leg_num_lowerTwist_joints
        self.hand_appendage_name = hand_appendage_name
        self.hand_start_joint = hand_start_joint
        self.hand_num_upperTwist_joint = hand_num_upperTwist_joint
        self.hand_num_lowerTwist_joint = hand_num_lowerTwist_joint
