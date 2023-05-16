import logging
logger = logging.getLogger()
import unittest
import maya.standalone
maya.standalone.initialize()
import maya.cmds as cmds
import rig_name
import utilities
import adv_scripting.rig.appendages.root as root



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
        self.assertEqual(fullname.output(), 'lt_front_arm_ik_ctrl_curve_20')


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

class TestRootAppendage(unittest.TestCase):
    def setUp(self):
        self.joint = cmds.joint(p=(50, 50, 10))
        self.root = root.Root('test_root', self.joint)

    def test_root_placement_position(self):
        position = cmds.xform(self.root.controls['fk']['root'], query=True, ws=True, t=True)
        self.assertEqual(position, [50, 50, 10])

    def test_root_translation(self):
        cmds.xform(self.root.controls['fk']['root'], ws=True, t=(20, 20, 20))
        position = cmds.xform(self.joint, query=True, ws=True, t=True)
        logger.info(position)
        self.assertEqual(position, [20.0, 20.0, 20.0])

    def test_root_rotation(self):
        cmds.xform(self.root.controls['fk']['root'], ws=True, ro=(5, 5, 5))
        rotation = cmds.xform(self.joint, query=True, ws=True, ro=True)
        self.assertAlmostEqual(rotation[0], 5, 1)
        self.assertAlmostEqual(rotation[1], 5, 1)
        self.assertAlmostEqual(rotation[2], 5, 1)

if __name__ == '__main__':
    unittest.main()
