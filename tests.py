'''
tests.py

Run in command line:
mayapy -m tests -v
mayapy -m tests -v -f<filename> -fp<filepath -p<projectname>

Use options -f --filename, -fp --filepath, -p --projectname to test on Maya file
e.g.
mayapy.exe -m tests -v -fp 'C:/Users/dayz/Documents/maya/projects/adv_scripting/scenes/rigging_skeleton_v04.ma'
mayapy.exe -m tests -v -f 'rigging_skeleton_v04.ma' -p 'adv_scripting'

To add additional tests, add them to the TestSuite in __main__
e.g. suite.addTest(TestHandAppendage(test, args.filepath))

Note:
TestHandAppendage takes filename / filepath as commandline arguments,
since building the hand rig needs a skeleton to test it on.
Ideally unit tests should be stand alone and not rely on outside information,
but I didn't have time to write a skeleton build script.
'''
import unittest
import os, sys
import argparse
import maya.standalone
maya.standalone.initialize()
import maya.cmds as cmds


import adv_scripting.rig_name as rig_name
import adv_scripting.utilities as utils
import adv_scripting.rig.appendages.appendage as appendage
import adv_scripting.rig.appendages.root as root
import adv_scripting.rig.appendages.spine as spine
import adv_scripting.rig.appendages.head as head
import adv_scripting.rig.appendages.leg as leg
import adv_scripting.rig.appendages.arm as arm
import adv_scripting.rig.appendages.hand as hand
import pdb # Debugger. Set breakpoint() to break into the debugger.
import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

import importlib as il
il.reload(rig_name)
il.reload(utils)
il.reload(hand)


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
        fullname = rig_name.RigName(full_name = 'lt_front_arm_ik_ctrl_nurbscurve_20')
        self.assertEqual(fullname.output(), 'lt_front_arm_ik_ctrl_nurbscurve_20')


class TestUtilities(unittest.TestCase):
    def setUp(self):
        self.joint = cmds.joint(p=(5, 5, 10), n='test_utilities_joint_01')
        self.control = utils.create_fk_control(self.joint, connect_output=None)
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
        self.joint = cmds.joint(p=(50, 50, 10), n='test_root_joint_01')
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

    def __init__(self, testname, filepath):
        super(TestHandAppendage, self).__init__(testname)
        self.sides = [rig_name.Side('lt'), rig_name.Side('rt')]
        self.hands = dict()
        self.settings = {
            'Hand': {
                'appendage_name': rig_name.Element('test_hand'),
                'start_joint': rig_name.RigName(full_name='wrist_bnd_jnt'),
                'num_upperTwist_joint': None,
                'num_lowerTwist_joint': None,
                'input_matrix': rig_name.RigName(full_name='lower_arm_bnd_jnt_02')
            }
        }
        self.transforms_orig = dict()
        self.transforms_jnt = dict()
        self.transforms_ctrl = dict()
        self.bnd_jnt = dict()
        self.joint_map = dict()
        self.controls = dict()

        cmds.file(filepath, o=1, f=1) # Open Maya file
        logger.setLevel(logging.DEBUG)

        for side in self.sides:
            # Read initial transforms on joints
            self.transforms_orig[side] = utils.read_transforms_hierarchy(
                self.settings['Hand']['start_joint'].rename(side=side).output())
            # Rig Hand
            rig_hand = hand.Hand(self.settings['Hand']['appendage_name'],
                                 self.settings['Hand']['start_joint'].rename(side=side).output(),
                                 self.settings['Hand']['num_upperTwist_joint'],
                                 self.settings['Hand']['num_lowerTwist_joint'],
                                 self.settings['Hand']['input_matrix'].rename(side=side).output() + '.worldMatrix[0]')
            self.hands[side] = rig_hand
            # Get Joint Transforms
            self.bnd_jnt[side] = rig_hand.bnd_jnt
            jnt_bnd = [x for branch in rig_hand.skeleton_bnd for x in branch]
            jnt_fk = [x for branch in rig_hand.skeleton_fk for x in branch]
            jnt_ik = [x for branch in rig_hand.skeleton_ik for x in branch]
            transforms_bnd = utils.read_transforms_list(self.bnd_jnt[side])
            transforms_fk = utils.read_transforms_list(jnt_fk)
            transforms_ik = utils.read_transforms_list(jnt_ik)
            self.transforms_jnt[side] = {**transforms_bnd, **transforms_fk, **transforms_ik}
            # Map FK/IK joint to Bnd joint
            self.joint_map[side] = dict()
            for idx in range(len(jnt_bnd)):
                bnd = jnt_bnd[idx]
                fk = jnt_fk[idx]
                ik = jnt_ik[idx]
                self.joint_map[side][fk] = bnd
                self.joint_map[side][ik] = bnd
            # Get Control Transforms
            #self.controls[side] = {**rig_hand.fk_ctrl, **rig_hand.ik_ctrl, **rig_hand.pv_ctrl}
            self.controls[side] = {**rig_hand.fk_ctrl, **rig_hand.ik_ctrl} # Ignore pv controls for now
            self.transforms_ctrl[side] = utils.read_transforms_list(self.controls[side].values())

    def get_sum(self, tuple1, tuple2):
        # Sum each coordinate (x,y,z) in two tuples
        return tuple(map(lambda x,y: x+y, tuple1, tuple2))

    def get_diff(self, tuple1, tuple2):
        return tuple(map(lambda x,y: y-x, tuple1, tuple2))

    def mod_rotate(self, tuple_rotate):
        return tuple(map(lambda x: x%360, tuple_rotate))

    def assert_equal(self, tuple1, tuple2, msg=None):
        for num1, num2 in zip(tuple1, tuple2):
            self.assertAlmostEqual(num1, num2, places=3, msg=msg)

    def test_hand_position(self):
        for side in self.sides:
            for jnt, bnd in self.joint_map[side].items():
                # Check that FK/IK joints are in same position as Bnd joint
                position_jnt = utils.read_translate(jnt)
                position_bnd = utils.read_translate(bnd)
                self.assert_equal(position_bnd, position_jnt, msg=
                    f"\nPOSITION jnt '{jnt}' {position_jnt} != bnd '{bnd}' {position_bnd}")
            for jnt, ctrl in self.controls[side].items():
                # Check that ctrl and jnt are in same position
                if jnt not in self.bnd_jnt[side]: # Not bnd jnt
                    position_jnt = utils.read_translate(jnt)
                    position_ctrl = utils.read_translate(ctrl)
                    self.assert_equal(position_jnt, position_ctrl, msg=
                    f"\nPOSITION jnt '{jnt}' {position_jnt} != ctrl '{ctrl}' {position_ctrl}")
            for bnd in self.bnd_jnt[side]:
                # Check that bnd jnt is in same position as original
                position_jnt = utils.read_translate(jnt)
                position_bnd = utils.read_translate(bnd)
                position_orig = self.transforms_orig[side][bnd]['translate']
                self.assert_equal(position_bnd, position_orig, msg=
                    f"\nPOSITION bnd '{bnd}' {position_bnd} != original pos {position_orig}")
        logger.info('Passed test position check')

    def test_hand_translate(self):
        move_offset = (5,5,5) # Translate value
        for side in self.sides:
            hand = self.hands[side]
            # Test by moving controls
            for jnt, ctrl in self.controls[side].items():
                tr_orig = self.transforms_ctrl[side][ctrl]['translate']
                move = self.get_sum(tr_orig, move_offset)
                # Switch FKIK
                if ctrl in hand.fk_ctrl.values(): # FK
                    cmds.setAttr(f'{hand.blend_switch}.switch_fkik', 0)
                    cmds.xform(ctrl, t=move, ws=1) # Translate
                    # For FK, check that ctrl and jnt position are same
                    translate_ctrl = utils.read_translate(ctrl)
                    translate_jnt = utils.read_translate(jnt)
                    self.assert_equal(translate_jnt, translate_ctrl, msg=
                    f"\nTRANSLATE '{ctrl}' {translate_ctrl} != '{jnt}' {translate_jnt} expected")
                elif ctrl in hand.ik_ctrl.values(): # IK
                    cmds.setAttr(f'{hand.blend_switch}.switch_fkik', 1)
                    cmds.xform(ctrl, t=move, ws=1) # Translate
                # Check that jnt and bnd position are same
                if jnt not in self.bnd_jnt[side]: # Not bnd jnt
                    bnd = self.joint_map[side][jnt]
                    position_jnt = utils.read_translate(jnt)
                    position_bnd = utils.read_translate(bnd)
                    self.assert_equal(position_jnt, position_bnd, msg=
                        f"\nPOSITION jnt '{jnt}' {position_jnt} != bnd '{bnd}' {position_bnd}")
                # Reset
                utils.reset_transform(ctrl, self.transforms_ctrl[side][ctrl])
        logger.info('Passed test translation check')

    def test_hand_rotate(self):
        move = (10,30,10) # Rotate value
        for side in self.sides:
            hand = self.hands[side]
            # Test by moving controls
            for jnt, ctrl in self.controls[side].items():
                # Check ctrl and bnd rotate are same initially
                if jnt in self.bnd_jnt[side]: # Bnd jnt
                    bnd = jnt
                else: # FK/IK jnt
                    bnd = self.joint_map[side][jnt]
                rotate_ctrl = self.mod_rotate(utils.read_rotate(ctrl))
                rotate_jnt = self.mod_rotate(utils.read_rotate(jnt))
                rotate_bnd = self.mod_rotate(utils.read_rotate(bnd))
                self.assert_equal(rotate_ctrl, rotate_bnd, msg=
                    f"\nROTATE '{ctrl}' {rotate_ctrl} != '{bnd}' {rotate_bnd} != '{jnt}' {rotate_jnt} expected")
                # Switch FKIK
                if ctrl in hand.fk_ctrl.values(): # FK
                    cmds.setAttr(f'{hand.blend_switch}.switch_fkik', 0)
                    cmds.xform(ctrl, ro=move, ws=1) # Rotate
                    # For FK ctrl, check that ctrl and jnt position are same
                    position_jnt = utils.read_translate(jnt)
                    position_ctrl = utils.read_translate(ctrl)
                    self.assert_equal(position_jnt, position_ctrl, msg=
                        f"\nPOSITION jnt '{jnt}' {position_jnt} != ctrl '{ctrl}' {position_ctrl}")
                elif ctrl in hand.ik_ctrl.values(): # IK
                    cmds.setAttr(f'{hand.blend_switch}.switch_fkik', 1)
                    cmds.xform(ctrl, ro=move, ws=1) # Rotate
                # Check that jnt and bnd position are same
                if jnt in self.bnd_jnt[side]: # Bnd jnt
                    bnd = jnt
                else: # FK/IK jnt
                    bnd = self.joint_map[side][jnt]
                    position_jnt = utils.read_translate(jnt)
                    position_bnd = utils.read_translate(bnd)
                    self.assert_equal(position_jnt, position_bnd, msg=
                        f"\nPOSITION jnt '{jnt}' {position_jnt} != bnd '{bnd}' {position_bnd}")
                # Check ctrl and bnd rotate are same
                rotate_ctrl = self.mod_rotate(utils.read_rotate(ctrl))
                rotate_bnd = self.mod_rotate(utils.read_rotate(bnd))
                self.assert_equal(rotate_ctrl, rotate_bnd, msg=
                    f"\nROTATE '{ctrl}' {rotate_ctrl} != '{bnd}' {rotate_bnd} expected")
                # Reset
                utils.reset_transform(ctrl, self.transforms_ctrl[side][ctrl])
        logger.info('Passed test rotate check')

    def test_hand_scale(self):
        move = (2,2,2) # Scale value
        for side in self.sides:
            hand = self.hands[side]
            # Test by moving controls
            for jnt, ctrl in self.controls[side].items():
                # Switch FKIK
                if ctrl in hand.fk_ctrl.values(): # FK
                    cmds.setAttr(f'{hand.blend_switch}.switch_fkik', 0)
                elif ctrl in hand.ik_ctrl.values(): # IK
                    cmds.setAttr(f'{hand.blend_switch}.switch_fkik', 1)
                cmds.xform(ctrl, s=move, ws=1) # Scale
                # Check that ctrl and jnt are in same position
                position_jnt = utils.read_translate(jnt)
                position_ctrl = utils.read_translate(ctrl)
                self.assert_equal(position_jnt, position_ctrl, msg=
                    f"\nPOSITION jnt '{jnt}' {position_jnt} != ctrl '{ctrl}' {position_ctrl}")
                # Check that jnt and bnd position are same
                if jnt not in self.bnd_jnt[side]: # Not bnd jnt
                    bnd = self.joint_map[side][jnt]
                    position_bnd = utils.read_translate(bnd)
                    self.assert_equal(position_jnt, position_bnd, msg=
                        f"\nPOSITION '{jnt}' {position_jnt} != bnd '{bnd}' {position_bnd}")
                # Check that moved jnt matches calculated value
                scale_jnt = utils.read_scale(jnt)
                self.assert_equal(scale_jnt, move, msg=
                    f"\nSCALE '{jnt}' {scale_jnt}!={move} expected")
                # Reset
                utils.reset_transform(ctrl, self.transforms_ctrl[side][ctrl])
        logger.info('Passed test scale check')


def parse_args(sys_argv):
    # Handle arguments filename, filepath, projectname
    parser = argparse.ArgumentParser(description='Read input Maya filename')
    parser.add_argument('-f', '--filename', action='store', required=False)
    parser.add_argument('-fp', '--filepath', action='store', required=False)
    parser.add_argument('-p', '--projectname', action='store', required=False)
    #parser.add_argument('nargs', nargs=argparse.REMAINDER)
    options, args = parser.parse_known_args(sys_argv)

    if not options.filename: # Filename given
        options.filename = 'rigging_skeleton_v04.ma'
        if not options.filepath:
            logger.warning(f"Required argument Maya filename. Assuming default '{options.filename}'")

    if options.filepath: # Filepath given
        if os.path.isfile(options.filepath): # Check if filepath exists
            if cmds.file(options.filepath, q=True, ex=True):
                options.filename = os.path.basename(options.filepath)
            else:
                logger.error(f"File '{options.filepath}' does not exist")
                sys.exit(0)
        elif os.path.isdir(options.filepath):
            filepath = os.path.join(options.filepath, options.filename)
            if cmds.file(filepath, q=True, ex=True):
                options.filepath = filepath
            else:
                logger.error(f"Directory '{options.filepath}' does not contain file '{options.filename}'")
                sys.exit(0)
        else:
            logger.error(f"Unrecognized file path '{options.filepath}'")
            sys.exit(0)

    else: # No filepath given
        if options.projectname:
            logger.debug('Attempt to detect project directory..')
            # Check if project exists
            filepath = os.path.join(cmds.workspace(q=True, dir=True), options.projectname)
            if not os.path.exists(filepath): # Try default rootDirectory
                logger.warning(f"Project '{options.projectname}' could not be found. Path: {filepath}")
                filepath = cmds.workspace(q=True, rd=True)
            # Check if file exists in project directory
            filepath = os.path.join(filepath, 'scenes', options.filename)
            if cmds.file(filepath, q=True, ex=True):
                options.filepath = filepath
            else:
                logger.error(f"File '{options.filename}' not found in project '{options.projectname}'. Path: {filepath}")
                sys.exit(0)

        else: # No projectname given
            # Check if filename is filepath
            if cmds.file(options.filename, q=True, ex=True):
                options.filename = os.path.basename(options.filename)
                options.filepath = options.filename

            else: # Check current directory for file
                currentpath = os.path.dirname(os.path.realpath(__file__))
                filepath = os.path.join(currentpath, options.filename)
                if cmds.file(filepath, q=True, ex=True):
                    options.filepath = filepath
                else:
                    logger.error(f"File '{options.filename}' not found in current directory. Optionally provide filepath(-fp) or projectname(-p) as arguments.")
                    sys.exit(0)

    logger.info(f'FILENAME: {options.filename}')
    logger.info(f'FILEPATH: {options.filepath}')
    return options


if __name__ == '__main__':
    # Parse arguments
    args = parse_args(sys.argv)

    # Create Test Loader
    test_loader = unittest.TestLoader()
    # Create Test Suite
    suite = unittest.TestSuite()

    # Add Test Cases
    test_rigname = test_loader.getTestCaseNames(TestRigName)
    test_utils = test_loader.getTestCaseNames(TestUtilities)
    test_root = test_loader.getTestCaseNames(TestRootAppendage)
    test_hand = test_loader.getTestCaseNames(TestHandAppendage)

    for test in test_rigname:
        suite.addTest(TestRigName(test))
    for test in test_utils:
        suite.addTest(TestUtilities(test))
    for test in test_root:
        suite.addTest(TestRootAppendage(test))
    for test in test_hand:
        suite.addTest(TestHandAppendage(test, args.filepath))

    # Run Test
    unittest.TextTestRunner(verbosity=2).run(suite)
    #unittest.main(verbosity=2, argv=[sys_argv[0]])
