import maya.cmds as cmds
import maya.api.OpenMaya as om

def calculate_pole_vector_position(root, mid, end):

    root_position = cmds.xform(root, q=True, ws=True, t=True)
    mid_position = cmds.xform(mid, q=True, ws=True, t=True)
    end_position = cmds.xform(end, q=True, ws=True, t=True)

    root_vector = om.MVector(root_position[0], root_position[1], root_position[2])
    mid_vector = om.MVector(mid_position[0], mid_position[1], mid_position[2])
    end_vector = om.MVector(end_position[0], end_position[1], end_position[2])

    # Calculate vectors
    start_end = end_vector - root_vector
    start_mid = mid_vector - root_vector

    dot_product = start_mid * start_end

    proj = float(dot_product) / float(start_end.length())
    proj_vector = start_end.normal() * proj

    arrow_vector = start_mid - proj_vector

    # Add resulting vecotr to mid joint
    final_vector = arrow_vector + mid_vector


    return final_vector
