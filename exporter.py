'''
exporter.py
author: Dayz Lee

AnimExporter
1. Animation Bake. Copy bnd skeleton to proxy skeleton. Bake animation from bnd to proxy.
    Get transforms on each joint at every frame.
2. Animation Export. Get keys and corresponding transform values, animation curves for each key.
    Also get camera data and camera keys.

AnimImporter
1. Animation Import. Import data file for given shot. Get keys and
    corresponding transform values, animation curves for each key.
2. Animation Bake. Import data file and bake to proxy.

In Maya Script Editor, run:
import adv_scripting.exporter as exporter
import importlib as il
il.reload(exporter)
exporter.run()

Before calling exporter.run(), make sure to change paths as necessary:
path_to_maya_scene, path_to_baked_anim, path_to_anim_curves

'''
import maya.cmds as cmds
import os
import json
import adv_scripting.utilities as utils
import adv_scripting.rig_name as rig_name
import adv_scripting.masterfile as masterfile
import adv_scripting.publish_animation.publish_data as publish_data
import logging

logger = logging.getLogger()

# Filename used for data import/export
ANIM_BAKE_FILENAME = 'anim_bake.json'
ANIM_CURVE_FILENAME = 'anim_curve.json'


# ANIMATION SETUP BASE CLASS ===========================================

class AnimSetup():
    def __init__(self, top_node, publish_data, anim_file):
        '''
        Arguments:
        top_node (str): Asset top node
        publish_data (dict) (str->value): Data dict holding animation publish data
            asset_name (str): Name of asset
            start_frame (int): Start of animation
            end_frame (int): End of animation
            rig_version (int): Version of rig generating the animation
            publish (bool): Flag indicating the asset should be published
            cache (bool): Flag indicating the asset should be cached
        anim_file (dict) (masterfile.AnimFile): AnimFile object used to track animation versions
            project (str): Project name, e.g. 'avengers',
            context (str): Context name, e.g. 'shots'
            scene (str): Scene number, e.g. '001'
            shot (str): Shot number, e.g. '010'
            maya_scene (str): Path to maya scene
            baked_anim (str): Path to baked anim
            anim_curves (str): Path to anim curves
            asset_name (str): Name of asset

        If publish_data['publish'] is enabled, export file is written to anim_file.baked_anim and anim_file.
        If publish_data['cache'] is enabled, cleanup methods are disabled.
        '''
        self.publish_data = publish_data
        self.anim_file = anim_file
        self.controls = self.get_controls(top_node)

        self.bnd_jnt = list() # Bind joint list
        self.proxy_jnt = list() # Proxy joint list
        self.anim_bake_data = dict() # Animation bake data. Transforms for each frame
        self.anim_curve_data = dict() # Animation curve data. Keys and tangents

        self.setup(top_node)


    def setup(self, top_node):
        # Get root jnt from top_node
        root_jnt = self.get_root_joint(top_node)
        # Store bnd joints
        bnd_dict = utils.read_hierarchy(root_jnt) # Bnd jnt name->RigName
        self.bnd_jnt = list(bnd_dict.keys())
        # Unlock all joint transforms
        for jnt in self.bnd_jnt:
            utils.unlock_all(jnt)

        # Duplicate skeleton
        skeleton = utils.duplicate_skeleton(root_jnt, tag='BAKE')
        # Rename skeleton to proxy
        proxy_dict = utils.replace_hierarchy(skeleton, control_type='proxy', rig_type='jnt', tag='BAKE')
        # Store proxy joints
        self.proxy_jnt = list(proxy_dict.keys())


    def get_root_joint(self, top_node):
        '''
        Return root joint / starting bind joint of skeleton
        '''
        # Possible names for skeleton grp
        skeleton_grp_names = [
            rig_name.RigName(element='skeleton').output(),
            rig_name.RigName(element='skeleton', rig_type='grp').output(),
            rig_name.RigName(element='skeleton', control_type='bnd', rig_type='grp').output(),
            rig_name.RigName(element='skeleton', control_type='bnd', rig_type='grp', maya_type='transform').output()
        ]
        # Get children of top_node
        top_node_children = cmds.listRelatives(top_node, typ='transform') or []
        skeleton_grp = None
        skeleton_jnt = None
        for skeleton_grp_name in skeleton_grp_names: # Check skeleton grp is under top_node
            if skeleton_grp_name in top_node_children:
                skeleton_grp = skeleton_grp_name
                skeleton_jnt = cmds.listRelatives(skeleton_grp, typ='joint')
        if not skeleton_grp: # Check if skeleton jnt is directly under top_node
            skeleton_jnt = cmds.listRelatives(top_node, typ='joint')
        if skeleton_jnt: # Skeleton jnt found
            root_jnt = skeleton_jnt[0]
            return root_jnt
        else:
            logger.error("Failed to find root jnt for asset {self.publish_data['asset_name']}")


    def get_controls(self, top_node):
        '''
        Get list of all controls. Controls are message connections to top_node
        '''
        controls = cmds.listConnections(top_node, s=True, d=False)
        if not controls:
            logger.error(f"Controls not found on top node '{top_node}'")
        return controls


# ANIMATION EXPORTER ===================================================

class AnimExporter(AnimSetup):

    def __init__(self, top_node, publish_data, anim_file):
        AnimSetup.__init__(self, top_node, publish_data, anim_file)

        self.animation_bake()
        self.animation_export()

        if self.publish_data['publish']:
            self.file_export()
        if not self.publish_data['cache']:
            self.cleanup()
        logger.debug('Animation Export Complete!')


    def animation_bake(self):
        logger.debug('Start Animation Bake..')

        # Constrain proxy to original bnd jnt
        for bnd, prx in zip(self.bnd_jnt, self.proxy_jnt):
            cmds.parentConstraint(bnd, prx)

        # Get frame range
        start_frame = self.publish_data['start_frame']
        end_frame = self.publish_data['end_frame']

        # Get transforms data
        # transforms = dict()
        # # Walk through frames in timeslider
        # for frame in range(start_frame, end_frame+1):
        #     cmds.currentTime(frame, e=True)
        #     transforms[frame] = dict()
        #     for prx in self.proxy_jnt: # Get transform values on each joint
        #         transforms[frame][prx] = utils.read_transforms_hierarchy(self.proxy_jnt[0], os=1)
        # self.anim_bake_data = transforms

        # Bake Animation in Maya
        cmds.bakeResults(self.proxy_jnt, t=(start_frame, end_frame), sm=True, sb=1)
        for frame in range(start_frame, end_frame+1):
            self.anim_bake_data[frame] = dict()
            for jnt in self.proxy_jnt:
                self.anim_bake_data[frame][jnt] = dict()
        # Get transforms data
        for jnt in self.proxy_jnt:
            self.get_anim_data(jnt, self.anim_bake_data, get_tangents=False)

        logger.debug('Done Animation Bake..')


    def animation_export(self):
        logger.debug('Start Animation Export..')
        anim_data = dict()

        # Iterate through each object and get animation data
        for jnt in self.bnd_jnt:
            self.get_anim_data(jnt, anim_data, get_tangents=True)
        if self.controls:
            for ctrl in self.controls:
                self.get_anim_data(ctrl, anim_data, get_tangents=True)

        # Camera export
        self.camera_export(anim_data)

        # Sort anim_data and store to self.anim_curve_data
        for frame in sorted(anim_data.keys()):
            self.anim_curve_data[frame] = dict()
            for node in sorted(anim_data[frame].keys()):
                self.anim_curve_data[frame][node] = anim_data[frame][node]

        logger.debug('Done Animation Export..')


    def get_anim_data(self, node, data, get_tangents=True):
        anim_attributes = cmds.listAnimatable(node)

        for attribute in anim_attributes:

            # Get keys for each attribute
            num_keys = cmds.keyframe(attribute, q=True, kc=True)
            if num_keys:
                times = cmds.keyframe(attribute, q=True, index=(0,num_keys), tc=True)
                # Get attribute value
                values = cmds.keyframe(attribute, q=True, index=(0,num_keys), vc=True)
                # Get tangents on each attribute
                time_start = times[0]
                time_end = times[-1]
                if get_tangents:
                    tangent_itt = cmds.keyTangent(node, at=attribute, q=True, t=(time_start, time_end), itt=True)
                    tangent_ott = cmds.keyTangent(node, at=attribute, q=True, t=(time_start, time_end), ott=True)
                    tangent_iw = cmds.keyTangent(node, at=attribute, q=True, t=(time_start, time_end), iw=True)
                    tangent_ow = cmds.keyTangent(node, at=attribute, q=True, t=(time_start, time_end), ow=True)
                    tangent_ia = cmds.keyTangent(node, at=attribute, q=True, t=(time_start, time_end), ia=True)
                    tangent_oa = cmds.keyTangent(node, at=attribute, q=True, t=(time_start, time_end), oa=True)

            for idx in range(0, num_keys):
                frame = times[idx]
                if frame not in data.keys():
                    data[frame] = dict()
                if node not in data[frame].keys():
                    data[frame][node] = dict()
                # Get transform values on each joint
                attr = attribute.split('.')[-1]
                if get_tangents:
                    data[frame][node][attr]['value'] = round(values[idx], 5)
                    tangent = {
                               'itt': tangent_itt[idx],
                               'ott': tangent_ott[idx],
                               'iw': tangent_iw[idx],
                               'ow': tangent_ow[idx],
                               'ia': tangent_ia[idx],
                               'oa': tangent_oa[idx]
                              }
                    data[frame][node][attr]['tangent'] = tangent
                else:
                    data[frame][node][attr] = round(values[idx], 5)

    def camera_export(self, data):
        logger.debug('Start Camera Export..')
        # Get all cameras in scene
        cameras = cmds.listCameras()

        # Get animation data on each camera
        for camera in cameras:
            self.get_anim_data(camera, data, get_tangents=True)

        logger.debug('Done Camera Export..')


    def file_export(self):
        logger.debug('Start File Export..')
        # Write to file
        anim_bake_data = json.dumps(self.anim_bake_data, indent=4)
        export_anim_bake = os.path.join(self.anim_file.baked_anim, ANIM_BAKE_FILENAME)
        with open(export_anim_bake, 'w+') as file_bake:
            file_bake.write(anim_bake_data)
        file_bake.close()

        anim_curve_data = json.dumps(self.anim_curve_data, indent=4)
        export_anim_curve = os.path.join(self.anim_file.anim_curves, ANIM_CURVE_FILENAME)
        with open(export_anim_curve, 'w+') as file_anim:
            file_anim.write(anim_curve_data)
        file_anim.close()

        self.anim_file.create_version()
        logger.debug('Done File Export..')


    def cleanup(self):
        logger.debug('Exporter Cleanup..')
        for jnt in self.proxy_jnt:
            # Delete all parentConstraints
            cmds.delete(f'{jnt}*Constraint*')
            # Delete all keys
            #cmds.cutkey(time=(self.publish_data['start_frame'], self.publish_data['end_frame']))


# ANIMATION IMPORTER ===================================================

class AnimImporter(AnimSetup):

    def __init__(self, top_node, publish_data, anim_file):
        AnimSetup.__init__(self, top_node, publish_data, anim_file)

        # Import animation from data file
        self.animation_import()
        # Bake proxy from imported data file
        self.animation_bake()
        logger.debug('Animation Import Complete!')


    def file_import(self, filename):
        logger.debug('File Import..')
        with open(filename, 'r') as file_import:
            data_json = json.load(file_import)
        return data_json


    def animation_import(self):
        logger.debug('Start Animation Import..')
        file_anim_curve = os.path.join(self.anim_file.anim_curves, ANIM_CURVE_FILENAME)
        self.anim_curve_data = self.file_import(file_anim_curve)

        for frame in self.anim_curve_data.keys():
            for node, attribute in self.anim_curve_data[frame].items():
                value = self.anim_curve_data[frame][node][attribute]['value']
                tangent = self.anim_curve_data[frame][node][attribute]['tangent']
                cmds.setKeyframe(node, at=attribute, t=frame, v=value)
                cmds.keyTangent(node, e=True, at=attribute, a=True,
                    itt=tangent['itt'], ott=tangent['ott'],
                    iw=tangent['iw'], ow=tangent['ow'],
                    ia=tangent['ia'], oa=tangent['oa'])

        logger.debug('Done Animation Import..')


    def animation_bake(self):
        logger.debug('Start Animation Bake..')
        file_anim_bake = os.path.join(self.anim_file.baked_anim, ANIM_BAKE_FILENAME)
        self.anim_bake_data = self.file_import(file_anim_bake)

        # Get frame range
        for frame in self.anim_bake_data.keys():
            for node, attribute in self.anim_bake_data[frame].items():
                value = self.anim_curve_data[frame][node][attribute]
                cmds.setKeyframe(node, at=attribute, t=frame, v=value)

        logger.debug('Done Animation Bake..')



# RUN ANIMATION EXPORTER ===============================================

def run():
    # Build Biped Rig
    #import adv_scripting.rig.biped as biped
    #rig = biped.Biped()

    # Initialize Publish Data
    pdata = publish_data.PublishData(
        asset_name='spiderman',
        start_frame=0,
        end_frame=100,
        rig_version=0,
        publish=True,
        cache=False)

    # Publish Animation UI
    import adv_scripting.publish_animation.publish_animation_ui as publish_animation_ui
    pui = publish_animation_ui.PublishAnimationUI(publish_data=pdata)

    # Initialize masterfile AnimFile
    project = 'avengers'
    context = 'shots'
    scene = '020'
    shot = '100'
    path_to_maya_scene= 'C:/Users/dayz/Documents/maya/projects/adv_scripting/scenes/rigging_skeleton_test.ma'
    path_to_baked_anim = f'C:/Users/dayz/Documents/adv_scripting/projects/{project}/{context}/{scene}/{shot}/'
    path_to_anim_curves = f'C:/Users/dayz/Documents/adv_scripting/projects/{project}/{context}/{scene}/{shot}/'
    afile = masterfile.AnimFile(project, context, scene, shot,
        path_to_maya_scene, path_to_baked_anim, path_to_anim_curves,
        pdata.asset_name)

    # Initialize Exporter
    exporter = AnimExporter('Biped_grp', pdata.data, afile)
    return exporter
