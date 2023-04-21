import unittest
import maya.standalone
maya.standalone.initialize()

import rig_name as rig_name


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
        pass

    def test_create_fk_control(self):
        pass


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
