import maya.cmds as mc

def create_aiStandardSurface_for_particleShape(
                                                particle_node=mc.ls(selection=True),
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
        print('Nothing Selected')


    # Validate particle type
    shape = mc.listRelatives(particle_node, shapes=True)
    particle_shape_node = str()
    if shapes:
        particle_shape_node = shapes[0]

 

    # Create 3 nodes:

    # Particle Sampler Info
    # Arnold Standard Surface
    # Shading group


    arnold_shader = mc.createNode('aiStandardSurface', name='particleAiShader')

    particle_sampler_info = mc.createNode('particleSamplerInfo', name='particleAiSamplerInfo')

    shading_group = mc.createNode('shadingEngine', name='particleAiSG')


    # Connect nodes together


    mc.connectAttr(f'{particle_sampler_info}.outColor', f'{arnold_shader}.baseColor')
    mc.connectAttr(f'{particle_sampler_info}.outIncandescence', f'{arnold_shader}.emissionColor')
    mc.connectAttr(f'{particle_sampler_info}.outTransparency', f'{arnold_shader}.opacity')
    mc.connectAttr(f'{arnold_shader}.outColor', f'{shading_group}.surfaceShader')
    


    # Set opacity attribute on particle shape


    mc.setAttr(f'{particle_shape_node}.aiOpaque', 0)


    # Delte old shading network


    if delete_original_shader:
        shading_network = list()
        for node in mc.listRelatives(particle_shape_node):
            if mc.objecType(node) == 'shadingEngine':
                shading_network.extend(mc.listConnection('nParticlePointsSE', issource=True))
                mc.delete(node)

        for node in shading_network:
            if mc. objecType(node) != 'transform':
                mc.delte(node)        



    # Connect the shading group to particle


    mc.connectAttr('nParticleShape1.instObjGroups[0]', 'particleAiSG.dagSetMembers[0]', f=True)

    return shading_group
