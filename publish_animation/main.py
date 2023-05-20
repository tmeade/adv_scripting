from PySide2 import QtCore
import logging
logger = logging.getLogger(__name__)

# if __name__ == "__main__" and __package__ is None:
#     __package__ = "tools.publish_animation"
import adv_scripting.publish_animation.publish_animation_ui as pa
import adv_scripting.publish_animation.publish_data as pd

def get_publishable_assests():
    import maya.cmds as mc
    publishable_assests = list()
    for item in mc.ls(type='locator'):
        if mc.attributeQuery('asset_name', node=item, exists=True):
            publishable_assests.append(item)

    logging.info('publishable_items: {}'.format(publishable_assests))

    return publishable_assests


def build_publish_data(publishable_assests):
    import maya.cmds as mc
    publish_data = list()
    for asset in publishable_assests:
        asset_name = mc.getAttr('{}.asset_name'.format(asset))
        rig_version = mc.getAttr('{}.rig_version'.format(asset))
        publish_data.append(pd.PublishData(asset_name=asset_name, rig_version=rig_version))

    logging.info('publishable_data: {}'.format(publish_data))

    return publish_data


def show_publish_window(publish_data):
    try:
        win.close()
    except Exception as e:
        logging.debug('{}.  Window has not previously initialized.'.format(e))
    logging.info('Launching window....')

    window = pa.PublishAnimationUI(publish_data=publish_data)
    window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    window.show()

    return window


def build_publish():
    publish_data = None
    try:
        publish_data = build_publish_data(get_publishable_assests())
        print('publish_data: ', publish_data)
    except:
        logging.info('Cannot import maya.cmds')

    show_publish_window(publish_data)


if __name__ == '__main__':
    build_publish()


# import maya.cmds as mc
# import random
#
# ASSETS = ['bilbo', 'frodo', 'gandalf', 'warg', 'aragorn']
# for asset in ASSETS:
#     loc = mc.createNode('locator', name=asset)
#     mc.addAttr(asset, dataType='string', longName='asset_name')
#     mc.setAttr('{}.asset_name'.format(asset), asset, type='string')
#     mc.addAttr(asset, dataType='string', longName='rig_version')
#     mc.setAttr('{}.rig_version'.format(asset), random.randint(1,50), type='string')
