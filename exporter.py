'''
exporter.py
author: Dayz Lee

Asset & Shot Exporter
1. Animation Bake. Bake animation on bnd skeleton. Get transforms on each joint and write to file.
2. Camera Exporter. Get transform values at each frame and write to filewrite to file
'''
import maya.cmds as cmds
import json
import adv_scripting.utilities as utils
import logging

logger = logging.getLogger()


class AnimExporter():

    def __init__(self, root_jnt, controls):
        '''
        Arguments:
        root_jnt: root joint / starting bind joint of skeleton
        '''
        self.controls = controls
        self.bnd_jnt = list()
        self.proxy_jnt = list()
        self.transforms = dict()
        self.keyset = dict()

        self.setup(root_jnt)
        self.bake_animation()
        self.export_animation()
        #self.export_file()


    def setup(self, root_jnt):
        # Store bnd joints
        bnd_dict = utils.read_hierarchy(root_jnt) # Bnd jnt name->RigName
        self.bnd_jnt = list(bnd_dict.keys())
        # Duplicate skeleton
        skeleton = utils.duplicate_skeleton(root_jnt, tag='BAKE')
        # Rename skeleton to proxy
        proxy_dict = utils.replace_hierarchy(skeleton, control_type='proxy', rig_type='jnt', tag='BAKE')
        # Store proxy joints
        self.proxy_jnt = list(proxy_dict.keys())


    def bake_animation(self):
        # Constrain duplicate to original
        for bnd, prx in zip(self.bnd_jnt, self.proxy_jnt):
            cmds.parentConstraint(bnd, prx)

        # Get transform values on each joint
        self.transforms = utils.read_transforms_hierarchy(self.proxy_jnt[0], os=1)


    def export_animation(self):

        # Get scene frame range
        start_frame = int(cmds.playbackOptions(q=True, min=True))
        end_frame = int(cmds.playbackOptions(q=True, max=True))

        # Create keyset dict
        for frame in range(start_frame, end_frame+1):
            self.keyset[frame] = dict()
            for jnt in self.proxy_jnt:
                self.keyset[frame][jnt] = dict()
            for ctrl in self.controls:
                self.keyset[frame][ctrl] = dict()

        # Iterate through each object and get animation data
        for jnt in self.proxy_jnt:
            self.get_anim_data(jnt)
        for ctrl in self.controls:
            self.get_anim_data(ctrl)


    def get_anim_data(self, node):
        anim_attributes = cmds.listAnimatable(node)

        for attribute in anim_attributes:

            # Get keys for each attribute
            num_keys = cmds.keyframe(attribute, q=True, kc=True)
            if num_keys:
                times = cmds.keyframe(attribute, q=True, index=(0,num_keys), tc=True)
                # Get attribute value
                values = cmds.keyframe(attribute, q=True, index=(0,num_keys), vc=True)
                # Get tangents on each attribute
                tangents = cmds.keyframe(attribute, q=True, index=(0,num_keys), ev=True)

            for key in range(0, num_keys):
                logger.debug(f'{key} {times[key]} {values[key]} {tangents[key]}')
                frame = values[key][0]
                # Get transform values on each joint
                self.keyset[frame][node][attribute] = values[key]
                self.keyset[frame][node]['tangent'] = tangents[key]


    def import_file(self, filename):
        with open(filename, 'r') as import_file:
            data_json = json.load(import_file)
        return data_json


    def export_file(self):
        # Write to file
        data_transforms = json.dumps(self.transforms, indent=4)
        with open('export_transforms.json', 'w') as export_file:
            export_file.write(data_transforms)

        data_keyset = json.dumps(self.keyset, indent=4)
        with open('export_keys.json', 'w') as export_file:
            export_file.write(data_keyset)


def test():
    import adv_scripting.rig.appendages.hand as hand
    hand_lt, hand_rt = hand.test()
    controls = list()
    controls.extend(hand_lt.controls['fk'].values())
    controls.extend(hand_lt.controls['ik'].values())
    controls.extend(hand_rt.controls['switches'].values())
    controls.extend(hand_rt.controls['fk'].values())
    controls.extend(hand_rt.controls['ik'].values())
    controls.extend(hand_rt.controls['switches'].values())

    exporter = AnimExporter('root_bnd_jnt', controls)
    return exporter
