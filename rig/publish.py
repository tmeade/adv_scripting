import os
import pathlib
import adv_scripting.masterfile as mf
import maya.cmds as cmds

import logging
logger = logging.getLogger(__name__)

import importlib as il
il.reload(rap)
il.reload(matrix_tools)
il.reload(utils)


#Module of publishing rig
class RigPublish():
    def __init__(self, asset_name, path_dir):
        self.asset_name = asset_name
        #self.path_dir = path_dir

        self.root_direcotry = os.path.join(str(pathlib.Path(__file__).parent), 'projects')
        self.project = project
        self.context = assets
        self.type = rig
        self.base = base

    #GET ASSET NAME FROM THE TOP NODE OF THE RIG
    def find_asset_name():
        import adv_scripting.publish_animation.main as main
        publishable_assests = main.get_publishable_assests()
        for asset in publishable_assests:
            self.asset_name = cmds.getAttr('{}.asset_name'.format(asset))
            #return?


    def file_path(self):
        return os.path.join(self.root_direcotry, self.project, self.context, self.type, self.asset_name, self.base)


    def save_file():
        #self.path_dir = ("projects/assets/rig/" + asset_name + "/base")
        if os.path.exists(self.file_path()):
            logger.info(f'Valid path found\n{self.file_path()}')
            cmds.file(rename=self.asset_name)
            cmds.file(self.file_path(), s=True, f=True, type='mayaBinary')
        else:
            logger.info(f'Created new directory: \n{self.file_path()}')
            pathlib.Path(self.file_path()).mkdir(parents=True, exist_ok=True)
            cmds.file(rename=self.asset_name)
            cmds.file(self.file_path(), s=True, f=True, type='mayaBinary')
        #Did not what name should the file be, so I have used the asset_name

    def masterfile_update():
        rf = mf.RigFile(self.project, self.context, self.asset_name, self.base, self.file_path())
        rf.read()
        rf.create_version()
        rf.write()
