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
        logger.info('Passed test create_fk_control_type')

    def test_create_fk_control_position(self):
        self.assertEqual(self.position, [5, 5, 10])
        logger.info('Passed test create_fk_control_position')

class TestRootAppendage(unittest.TestCase):
    def setUp(self):
        self.joint = cmds.joint(p=(50, 50, 10))
        self.root = root.Root('test_root', self.joint)

    def test_root_placement_position(self):
        position = cmds.xform(self.root.controls['fk']['root'], query=True, ws=True, t=True)
        self.assertEqual(position, [50, 50, 10])
        logger.info('Passed test root_placement_position')

    def test_root_translation(self):
        cmds.xform(self.root.controls['fk']['root'], ws=True, t=(20, 20, 20))
        position = cmds.xform(self.joint, query=True, ws=True, t=True)
        logger.info(position)
        self.assertEqual(position, [20.0, 20.0, 20.0])
        logger.info('Passed test root_translation')

    def test_root_rotation(self):
        cmds.xform(self.root.controls['fk']['root'], ws=True, ro=(5, 5, 5))
        rotation = cmds.xform(self.joint, query=True, ws=True, ro=True)
        self.assertAlmostEqual(rotation[0], 5, 1)
        self.assertAlmostEqual(rotation[1], 5, 1)
        self.assertAlmostEqual(rotation[2], 5, 1)
        logger.info('Passed test test_root_rotation')

class TestHandAppendage(unittest.TestCase):
    def __init__(self):
        self.sides = [rig_name.Side('lt'), rig_name.Side('rt')]
        self.hands = dict()
        self.settings: {
            'Hand': {
                'appendage_name': rig_name.Element('test_hand'),
                'start_joint': rig_name.RigName(full_name='wrist_bnd_jnt'),
                'num_upperTwist_joint': None,
                'num_lowerTwist_joint': None,
                'input_matrix': rig_name.RigName(full_name='lower_arm_bnd_jnt_02')
            }
        }
        self.transforms = dict()
        self.controls = dict()
        '''
        hands.controls = {
            'fk': {
                'wrist_bnd':,
                'hand_bnd':,
                'thumb_fk_01':,
                'thumb_fk_02':,
                'thumb_fk_03':,
                'index_fk_01':,
                'index_fk_02':,
                'index_fk_03':,
                'ring_fk_01':,
                'ring_fk_02':,
                'ring_fk_03':,
                'pinky_fk_01':,
                'pinky_fk_02':,
                'pinky_fk_03':,
                },
            'ik': {
                'thumb_ik':,
                'index_ik':,
                'middle_ik':,
                'ring_ik':,
                'pinky_ik':,
                'thumb_pv':,
                'index_pv':,
                'middle_pv':,
                'ring_pv':,
                'pinky_pv':,
            },
            'switches' = {
                'hand_fkik_switch':
            }
        }
        '''

    def sum_xyz(self, xyz1, xyz2):
        # Sum each coordinate (x,y,z) in two tuples
        return tuple(map(lambda a,b: a+b, xyz1, xyz2))

    def setup(self):
        for side in self.sides:
            # Read initial transforms on joints
            self.transforms[side] = utils.read_joint_transforms(
                self.settings['Hand']['start_joint'].rename(side=side).output())
            logger.debug(f'Transforms {side.output()}: {self.transforms[side]}')
            # Rig Hand
            self.hands[side] = hand.Hand(self.settings['Hand']['appendage_name'],
                                        self.settings['Hand']['start_joint'].rename(side=side).output(),
                                        self.settings['Hand']['num_upperTwist_joint'],
                                        self.settings['Hand']['num_lowerTwist_joint'],
                                        self.settings['Hand']['input_matrix'].rename(side=side).output() + '.worldMatrix[0]')
            self.controls[side] = {**hand.fk_ctrl, **hand.ik_ctrl, **hand.pv_ctrl}

    def test_hand_position(self):
        for side in self.sides:
            for jnt, ctrl in self.controls[side].items():
                position_ctrl = utils.read_position(ctrl)
                position_jnt = utils.read_position(jnt)
                self.assertEqual(position_ctrl, self.transforms['position'][jnt])
                self.assertEqual(position_jnt, self.transforms['position'][jnt])
        logger.debug('Passed test position check')

    def test_hand_translate(self):
        move = (10,10,10)
        for side in self.sides:
            for jnt, ctrl in self.controls[side].items():
                cmds.xform(ctrl, t=move, r=1)
                translate_ctrl = utils.read_translate(ctrl)
                translate_jnt = utils.read_translate(jnt)
                translate_calc = self.sum_xyz(self.transforms['translate'][jnt], move)
                self.assertEqual(translate_ctrl, translate_calc)
                self.assertEqual(translate_jnt, translate_calc)
        logger.debug('Passed test translation check')

        for side in self.sides: # Reset
            for ctrl in self.controls[side].values():
                utils.reset_translate(ctrl)

    def test_hand_rotate(self):
        move = (10,50,10)
        for side in self.sides:
            for jnt, ctrl in self.controls[side].items():
                cmds.xform(ctrl, ro=move, r=1)
                rotate_ctrl = utils.read_rotate(ctrl)
                rotate_jnt = utils.read_rotate(jnt)
                rotate_calc = self.sum_xyz(self.transforms['rotate'][jnt], move)
                self.assertEqual(rotate_ctrl, rotate_calc)
                self.assertEqual(rotate_jnt, rotate_calc)
        logger.debug('Passed test rotate check')

        for side in self.sides: # Reset
            for ctrl in self.controls[side].values():
                utils.reset_rotate(ctrl)

    def test_hand_scale(self):
        move = (2,2,2)
        for hand in self.hands:
            for jnt, ctrl in self.controls.items():
                cmds.xform(ctrl, s=move, r=1)
                scale_ctrl = utils.read_scale(ctrl)
                scale_jnt = utils.read_scale(jnt)
                scale_calc = self.sum_xyz(self.transforms['scale'][jnt], move)
                self.assertEqual(scale_ctrl, scale_calc)
                self.assertEqual(scale_jnt, scale_calc)
        logger.debug('Passed test scale check')

        for side in self.sides: # Reset
            for ctrl in self.controls[side].values():
                utils.reset_scale(ctrl)

if __name__ == '__main__':
    unittest.main()
