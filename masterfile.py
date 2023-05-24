import os
import pathlib
import json
import logging

logger = logging.getLogger(__name__)

class MasterFile():
    def __init__(self, asset_name, project=None, context=None, type=None, category=None):
        self.asset_name = asset_name
        self.project = project
        self.context = context
        self.type = type
        self.category = category

        self.version = 0
        self.root_direcotry = os.path.join(str(pathlib.Path(__file__).parent), 'projects')
        self.data = dict()

        self.validate_path()

    def read(self, version=None):
        logger.info('read')
        if os.path.isfile(os.path.join(self.file_path(), 'masterfile.json')):
            file_object = open(os.path.join(self.file_path(), 'masterfile.json'), 'r')
            self.data = json.load(file_object)
            file_object.close()

            self.version = max(self.data[self.asset_name].keys())
            print('version', self.version)
            print('asset_name', self.asset_name)
            # if version:
            #     for key in data:
            #         if key == version:
            #             self.data[self.asset_name][key] = data[key]
            # else:
            # self.data[self.asset_name] = {self.version: self.data[self.asset_name][self.version]}
                # self.data[self.asset_name][self.version] = {}


    def write(self):
        logger.info('write')
        file_object = open(os.path.join(self.file_path(),'masterfile.json'), 'w')
        json.dump(self.data, file_object, sort_keys=True, indent=0)
        file_object.close()

        logger.info(f'Wrote masterfile to: \n{self.file_path()}')

    def get_version(self):
        logger.info('get_version')

    def get_masterfile(self):
        logger.info('get_masterfile')

    def file_path(self):
        return os.path.join(self.root_direcotry, self.project, self.context, self.type, self.category)

    def validate_path(self):
        if os.path.exists(self.file_path()):
            logger.info(f'Valid path found\n{self.file_path()}')
            return
        else:
            logger.info(f'Created new directory: \n{self.file_path()}')
            pathlib.Path(self.file_path()).mkdir(parents=True, exist_ok=True)



class RigFile(MasterFile):
    def __init__(self,
                project='gen',
                context='assets',
                asset_name='gen_man',
                asset_variant='base',
                maya_scene=None):
            MasterFile.__init__(self,
                                asset_name,
                                project=project,
                                context=context,
                                type=asset_name,
                                category=asset_variant)
            self.maya_scene = maya_scene
            self.asset_name = asset_name

    def create_version(self):
        logger.info('create_version')
        if self.version:
            print('version', self.version)
            self.data[self.asset_name][str(int(self.version)+1)] = {'rig_scene': self.maya_scene}
            logger.debug(f'Appended new version to data {self.data[self.asset_name][str(int(self.version)+1)]}')
        else:
            print ('data', self.data)
            self.data = {self.asset_name : {'1': {'rig_scene': self.maya_scene}}}
            logger.debug(f'Created initial data entry: {self.data}')

class AnimFile(MasterFile):
    def __init__(self,
                project='gen',
                context='shots',
                scene= '001',
                shot= '010',
                maya_scene=None,
                baked_anim=None,
                anim_curves=None,
                asset_name = 'gen_man'):
            MasterFile.__init__(self,
                                asset_name,
                                project=project,
                                context=context,
                                type=asset_name,
                                category=asset_variant)
            self.maya_scene = maya_scene
            self.baked_anim = baked_anim
            self.anim_curves = anim_curves

    def create_version(self):
        logger.info('create_version')
        if self.version:
            self.data[self.asset_name] = {str(int(self.version)+1): {
                                                    'anim_scene': self.maya_scene,
                                                    'baked_anim': self.baked_anim,
                                                    'anim_curves': self.anim_curves}}
            logger.debug(f'Appended new version to data {data[str(int(self.version)+1)]}')
        else:
            self.data = {self.asset_name: {'1': {'anim_scene': self.maya_scene,
                                'baked_anim': self.baked_anim,
                                'anim_curves': self.anim_curves}}}
            logger.debug(f'Created initial data entry: {self.data}')
