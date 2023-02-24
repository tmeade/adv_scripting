'''
dayz_particle_arnoldshader.py
author: Dayz Lee

Make nParticle renderable in Arnold.
To use, select nParticle in Maya.

e.g. in Maya Script Editor run:
import dayz_particle_arnoldshader as ps
il.reload(ps)
ps.particleshader('nParticle1')
'''
import maya.cmds as mc
import logging

logger = logging.getLogger(__name__)

def particleshader(shadername='particle', delete_flag=True):
    '''
    Description: A function to replace default particle shader with
    Arnold shading network. Includes particle sampler info to support
    particle color, opacity, and emission.

    Arguments:
        shadername (str) - desired shader network name
        delete_flag (bool) - delete original shader network

    '''
    # If delete_flag is set, only delete nodes of the type below
    delete_type = ['shadingEngine', 'aiStandardSurface', 'particleSamplerInfo', 'particleCloud', 'blinn', 'lambert']

    # Select nParticle system to apply shader to
    nParticle = mc.ls(sl=True, tr=1, tl=1)
    if nParticle:
        nParticle = nParticle[0]
        logger.debug(f'Selected nParticle system: {nParticle}')
    else:
        logger.error('Select the nParticle system.')
        return
    # Get nParticleShape part of nParticle system
    npShape = mc.listRelatives(nParticle, s=True)
    if npShape:
        npShape = npShape[0]
        logger.debug(f'Found particleShape: {npShape}')
    else:
        logger.error('nParticle Shape not found.')
        return

    # Find connection to shadingEngine
    nPSE = mc.listConnections(f'{npShape}.instObjGroups')
    if not nPSE:
        logger.warning(f'shadingEngine connection not found. {npShape}.instObjGroups has no outbound connections.')

    # --- Delete old shader network ---
    if delete_flag:
        logger.debug('Deleting old shading network.')
        connections = None
        if nPSE: # Found connection to original shadingEngine before
            connections = nPSE
        elif mc.objExists('nParticlePointsSE'): # assume default naming
            connections = ['nParticlePointsSE']
        elif mc.objExists(f'{shadername}_aiSG'): # assume previously created but disconnected
            connections = [f'{shadername}_aiSG']
        else:
            logger.warning('Original shadingEngine not found. No nodes deleted.')

        while connections:
            node = connections.pop()
            if mc.objExists(node) and mc.objectType(node) in delete_type:
                connections.extend(mc.listConnections(node,s=True,d=False) or [])
                mc.delete(node)

    # --- Create shader nodes---
    # Arnold Standard Surface (aiSS)
    # Arnold Shading Group (aiSG)
    # particleSamplerInfo (pSI)
    aiSS = mc.createNode('aiStandardSurface', name=f'{shadername}_aiStandardSurface')
    logger.debug(f'Creating new node {aiSS}.')
    aiSG = mc.createNode('shadingEngine', name=f'{shadername}_aiSG')
    logger.debug(f'Creating new node {aiSG}.')
    pSI = mc.createNode('particleSamplerInfo', name=f'{shadername}_particleSamplerInfo')
    logger.debug(f'Creating new node {pSI}.')

    # --- Connect particle to shading group ---
    # connect particleSamplerInfo -> particle_aiStandardSurface
    # outColor -> baseColor
    # outIncandescence -> emissionColor
    # outTransparency -> opacity
    mc.connectAttr(f'{pSI}.outColor', f'{aiSS}.baseColor')
    mc.connectAttr(f'{pSI}.outIncandescence', f'{aiSS}.emissionColor')
    mc.connectAttr(f'{pSI}.outTransparency', f'{aiSS}.opacity')
    logger.debug(f'Linked attributes {pSI} -> {aiSS}')

    # Connect aiStandardSurface to aiSG
    mc.connectAttr(f'{aiSS}.outColor', f'{aiSG}.surfaceShader')
    logger.debug(f'Linked attributes {aiSS} -> {aiSG}')

    # Connect instObjGroups to dagSetMembers
    idx = 0
    if not delete_flag and nPSE:
        dag = mc.listConnections(f'{npShape}.instObjGroups', p=True)
        if dag:
            mc.disconnectAttr(f'{npShape}.instObjGroups', dag[0])
        else:
            logger.warning(f'Connection from {npShape}.instObjGroups to dagSetMembers not found.')

    mc.connectAttr(f'{npShape}.instObjGroups', f'{aiSG}.dagSetMembers', na=True)
    logger.debug(f'Linked attributes {npShape} -> {aiSG}')

    # Turn off Arnold opaque setting
    mc.setAttr(f'{nParticle}.aiOpaque', 0)
    logger.debug(f'Set Arnold Opaque off for {nParticle}.')

    logger.debug('Done creating Arnold particle shader network.')
