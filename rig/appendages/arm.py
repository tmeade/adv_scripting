import maya.cmds as mc
import maya.api.OpenMaya as om
import matrix_tools as mt
import pole_vector as pv

#import arm as arm
#arm.fk_arm_setup('LeftShoulder','fk', 1, 1)
#arm.ik_arm_setup('LeftShoulder','ik', 1, 1)

def shoulder_rig():
    shoulder_joint = mc.ls(sl=True)[0]
    #need to name control with tool's naming convention
    shoulder_control = mc.circle()[0]
    mt.snap_offset_parent_matrix(shoulder_control,shoulder_joint)
    mt.matrix_parent_constraint(shoulder_control,shoulder_joint)

    #joint rotation and joint oriernt was not zero out after matrix script
    mc.xform(shoulder_joint, ro = [0,0,0], os=True)
    mc.setAttr(shoulder_joint +'.jointOrient', 0,0,0)

    return source

#arm part

#duplicate arm chain
def arm_chain_duplicate(start_joint,chain_type, num_upperTwist_joint, num_lowerTwist_joint):

    arm_joint = mc.listRelatives(start_joint)
    duplicated_chain = mc.duplicate(arm_joint, rc=True)
    mc.parent(duplicated_chain[0],w=True)
    valid_arm_chain = list()

    for i in duplicated_chain:
        new_name= mc.rename(i,f'{chain_type}_{i[:-1]}')

        if duplicated_chain.index(i) < num_upperTwist_joint+num_lowerTwist_joint+3:
            valid_arm_chain.append(new_name)

    mc.select(valid_arm_chain[num_upperTwist_joint+num_lowerTwist_joint+2],hi=True)
    mc.select(valid_arm_chain[num_upperTwist_joint+num_lowerTwist_joint+2],d=True)
    mc.delete()

    return valid_arm_chain
#FK
def fk_arm_setup(start_joint,chain_type, num_upperTwist_joint, num_lowerTwist_joint):
    #FK arm
    fk_arm_joints = arm_chain_duplicate(start_joint,chain_type, num_upperTwist_joint, num_lowerTwist_joint)
    valid_joints = [fk_arm_joints[0],fk_arm_joints[int((len(fk_arm_joints)-1)/2)],fk_arm_joints[-1]]
    fk_arm_controls = list()

    for joint in valid_joints:
        fk_control = mc.circle(n=f'{joint}'+'_fk_control')[0]
        mt.snap_offset_parent_matrix(fk_control,joint)
        mt.matrix_parent_constraint(fk_control,joint)

        mc.xform(joint, ro = [0,0,0], os=True)
        mc.setAttr(joint+'.jointOrient', 0,0,0)
        fk_arm_controls.append(fk_control)

    for index in range(len(fk_arm_controls)):

        if index != 0:
            mc.parent(fk_arm_controls[index],fk_arm_controls[index-1])
            mt.matrix_parent_constraint(fk_arm_controls[index-1],fk_arm_controls[index])

    return fk_arm_controls


#IK
def ik_arm_setup(start_joint,chain_type, num_upperTwist_joint, num_lowerTwist_joint):

    ik_arm_joints = arm_chain_duplicate(start_joint,chain_type, num_upperTwist_joint, num_lowerTwist_joint)
    valid_joints = [ik_arm_joints[0],ik_arm_joints[int((len(ik_arm_joints)-1)/2)],ik_arm_joints[-1]]

    root = valid_joints[0]
    mid =  valid_joints[1]
    end =  valid_joints[2]

    #IK handle
    arm_ik_handle = mc.ikHandle(sj = root, ee = end, sol = 'ikRPsolver')
    ik_control = mc.circle()
    mt.snap_offset_parent_matrix(ik_control[0],arm_ik_handle[0])
    mc.parent(arm_ik_handle[0],ik_control[0])

    #pole vector
    pv_position = pv.calculate_pole_vector_position(root, mid, end)
    arm_pv_control = mc.circle()
    mc.move(pv_position.x, pv_position.y, pv_position.z, arm_pv_control)
    mc.makeIdentity(arm_pv_control,apply=True, t=True, r=True, s=True)
    mc.poleVectorConstraint(arm_pv_control,arm_ik_handle[0])
