import maya.cmds as cmds
import logging
logging.getLogger(__name__)
def create_aiStandardSurface_for_particleShape(
                                                particle_node=cmds.ls(selection=True),
                                                delete_original_shader=True):
    '''
    Description:
        A function to replace current particle shader with Arnold shading network.  This
        includes a particle sampler info to support per particle color, opacity, and emission.
    Arguments:
        particle_node (list): The particle node to process.
        delete_original_shader (bool): When True, delete original shading network.
    Returns:
        shading_group (str): The new Arnold shading group

    '''

    # Validate selection
    if len(particle_node) == 0:
        logging.error('Nothing is selected')
        return

    # Validade particle type
    shapes = cmds.listRelatives(particle_node, shapes=True)
    particle_shape_node = str()
    if shapes:
        particle_shape_node = shapes[0]

    logging.debug('Particle shape node: {}'.format(particle_shape_node))

    # Create 3 nodes:

    arnold_shader = cmds.createNode('aiStandardSurface', name='particleAiShader')
    shading_group = cmds.createNode('shadingEngine', name='particleAiSG')
    particle_sampler_info = cmds.createNode('particleSamplerInfo', name='particleAiSamplerInfo')

    # Connect nodes together
    cmds.connectAttr(f'{particle_sampler_info}.outColor', f'{arnold_shader}.baseColor')
    cmds.connectAttr(f'{particle_sampler_info}.outIncandescence', f'{arnold_shader}.emissionColor')
    cmds.connectAttr(f'{particle_sampler_info}.outTransparency', f'{arnold_shader}.opacity')
    cmds.connectAttr(f'{arnold_shader}.outColor', f'{shading_group}.surfaceShader')

    # Set opacity attribute on particle shape
    cmds.setAttr(f'{particle_shape_node}.aiOpaque', 0)

    # Connect the shading group to particle
    if delete_original_shader:
        shading_network = list()
        for node in cmds.listConnections(particle_shape_node):
            if cmds.objectType(node) == 'shadingEngine':
                shading_network.extend(cmds.listConnections('nParticlePointsSE', source=True, destination=False))
                cmds.delete(node)

        for node in shading_network:
            if cmds.objectType(node) != 'transform':
                cmds.delete(node)
    # Connect the shading group to particle
    cmds.connectAttr('nParticleShape1.instObjGroups[0]', 'particleAiSG.dagSetMembers[0]', f=True)

    return shading_group
