import unittest
import maya.standalone
maya.standalone.initialize()
import maya.cmds as cmds

import rig_name
import utilities


class TestRigName(unittest.TestCase):
    def setUp(self):
        self.object = rig_name.RigName(side='lt',
                                        region='front',
                                        element='arm',
                                        control_type='ik',
                                        rig_type='ctrl',
                                        maya_type='curve',
                                        position=20)

    def test_str(self):
        self.assertEqual(self.object.output(), 'lt_front_arm_ik_ctrl_20')

    def test_repr(self):
        self.assertTrue(isinstance(self.object, rig_name.RigName))

    def test_fullname(self):
        fullname = rig_name.RigName(full_name = 'lt_front_arm_ik_ctrl_curve_20')
        self.assertEqual(fullname.output, 'lt_front_arm_ik_ctrl_curve_20')


class TestUtilities(unittest.TestCase):
    def setUp(self):
        self.joint = cmds.joint(p=(5, 5, 10))
        self.control = utilities.create_fk_control(self.joint, connect_output=None)
        self.position = cmds.xform(self.control, query=True, ws=True, t=True)
        self.rotation = cmds.xform(self.control, query=True, ws=True, ro=True)

    def test_create_fk_control_type(self):
        self.assertTrue(cmds.nodeType(self.control), 'transform')

    def test_create_fk_control_position(self):
        self.assertEqual(self.position, [5, 5, 10])



if __name__ == '__main__':
    unittest.main()

'''
    test1 = RigName(side=side_type, region='front', element='arm', control_type='ik', rig_type=RigType('ctrl'), maya_type='curve', position=20)
    logger.debug('--- test1 ---')
    logger.debug(f'Full name: {test1.full_name}')
    logger.debug(f'Name: {test1.name}')
    logger.debug(f'{test1}')

    test2 = RigName(full_name = 'lt_front_arm_ik_ctrl_curve_20')
    logger.debug('--- test2 ---')
    logger.debug(f'Full name: {test2.full_name}')
    logger.debug(f'Name: {test2.name}')
    logger.debug(f'{test2}')

    test3 = RigName(full_name = 'LeftHandIndex1')
    logger.debug('--- test3 ---')
    logger.debug(f'Full name: {test3.full_name}')
    logger.debug(f'Name: {test3.name}')
    logger.debug(f'{test3}')
'''
