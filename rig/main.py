import logging
from PySide2 import QtCore

import adv_scripting.rig.ui.rig_build_ui as rig_build_ui
import adv_scripting.rig.settings as settings

logger = logging.getLogger(__name__)

import importlib as il
il.reload(rig_build_ui)
il.reload(settings)


def show_rig_build_window(rig_data):
    try:
        window.close()
    except Exception as e:
        logging.debug('{}.  Window has not previously initialized.'.format(e))
    logging.info('Launching window....')

    window = rig_build_ui.RigBuildUI(rig_data=rig_data)
    window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    window.show()

    return window

def main():
    rig_data = None
    try:
        rig_data = settings.BipedSettings()
        print('publish_data: ', rig_data)
    except:
        logging.info('Cannot import maya.cmds')

    show_rig_build_window(rig_data)
