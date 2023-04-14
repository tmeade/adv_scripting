import maya.cmds as cmds

def create_fk_control(joint):
    fk_control = cmds.createNode('transform', n=f'{joint}'+'_fk_ctrl_transform')
    mt.snap_offset_parent_matrix(fk_control, joint)
    mt.matrix_parent_constraint(fk_control, joint)

    cmds.xform(joint, ro = [0, 0, 0], os=True)
    cmds.setAttr(joint+'.jointOrient', 0,0,0)


def create_control_joints_from_skeleton(start_joint,
                                        end_joint,
                                        control_type,
                                        num_upperTwist_joints,
                                        num_lowerTwist_joints):

    # Duplicate the skeleton and parent it to the world
    duplicate_skeleton = cmds.duplicate(start_joint)
    cmds.parent(duplicate_skeleton[0], w=True)

    # Rename the skeleton by replaceing 'bnd' with the control_type.
    for joint in cmds.listRelatives(duplicate_skeleton[0], ad=True, fullPath=True):
        cmds.rename(joint,
                  joint.split('|')[-1].replace('_bnd_', (f'_{control_type}_')))
    start_joint = cmds.rename(duplicate_skeleton[0],
                            duplicate_skeleton[0].split('|')[-1].replace('_bnd_', (f'_{control_type}_')))

    # Delete all of the joints in the hierarchy below the end joint
    cmds.delete(cmds.listRelatives(end_joint.replace('_bnd_', (f'_{control_type}_'))))

    # Use the number of twist joints to extract the control joints
    skeleton = cmds.listRelatives(start_joint, ad=True)
    skeleton.reverse()
    if num_upperTwist_joints > 0:
        middle_joint = skeleton[num_upperTwist_joints]
    else:
        middle_joint = skeleton[0]

    end_joint = skeleton[-1]

    # Create control hierarchy
    cmds.parent(end_joint, middle_joint)
    cmds.parent(middle_joint, start_joint)

    # Remove twist joints
    cmds.delete(cmds.listRelatives(start_joint)[0])
    cmds.delete(cmds.listRelatives(middle_joint)[0])

    control_skeleton = cmds.listRelatives(start_joint, ad=True)
    control_skeleton.append(start_joint)
    control_skeleton.reverse()

    return control_skeleton
