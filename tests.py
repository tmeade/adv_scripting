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
        position = cmds.xform(self.root.controls['fk']['root_ctrl'], query=True, ws=True, t=True)
        self.assertEqual(position, [50, 50, 10])

    def test_root_translation(self):
        cmds.xform(self.root.controls['fk']['root_ctrl'], ws=True, t=(20, 20, 20))
        position = cmds.xform(self.joint, query=True, ws=True, t=True)
        logger.info(position)
        self.assertEqual(position, [20.0, 20.0, 20.0])

    def test_root_rotation(self):
        cmds.xform(self.root.controls['fk']['root_ctrl'], ws=True, ro=(10, 10, 10))
        rotation = cmds.xform(self.joint, query=True, ws=True, ro=True)
        self.assertEqual(rotation, [10.0, 10.0, 10.0])

    def test_display_color():
        test_grp = cmds.createNode('transform', n='test_display_color')
        for idx in range(1,32):
            color_jnt = cmds.createNode('joint', n=f'color_jnt_{idx}')
            cmds.parent(color_jnt, test_grp)
            cmds.xform(color_jnt, t=(0,-idx,0))
            utils.display_color(node, idx)

if __name__ == '__main__':
    unittest.main()
