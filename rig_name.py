import maya.cmds as mc
import logging
import re
logger = logging.getLogger(__name__)

# Naming convention
# lt_front_arm_ik_ctrl_curve_01

# Constants
VALID_SIDE_NAMES = ['lt', 'rt', 'ctr']
VALID_REGION_NAMES = ['front', 'rear', 'middle', 'upper', 'lower']
VALID_CONTROL_TYPES = ['ik', 'fk', 'bnd', 'dyn', 'mocap', 'driver']
VALID_RIG_TYPES = ['ctrl', 'offest', 'sdk', 'handle', 'loc', 'jnt', 'geo', 'constraint', 'grp']
VALID_MAYA_TYPES = mc.ls(nodeTypes=True)


class NameBase():
    '''
    Description:
        Base class for returning a valid string object name.
    Args:
        name (string): name of the naming element
    Returns:
        String representation of the valid naming element
    '''

    def __init__(self, name=None):
        self.name = name
        logger.debug('self.name: {}'.format(self.name))

        self.validate()
        self.output()

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.name}')"

    def validate(self):
        return

    def output(self):
        self.name = self.name.lower()


class Side(NameBase):
    def __init__(self, name):
        NameBase.__init__(self, name)

    def validate(self):
        if self.name not in VALID_SIDE_NAMES:
            logger.error('Side name must match: {}'.format(VALID_SIDE_NAMES))
            return

    def output(self):
        return


class Position(NameBase):
    def __init__(self, name):
        NameBase.__init__(self, name)

    def validate(self):
        if not isinstance(self.name, int):
            logger.error(f"{self} should be a positive number")
            return

    def output(self):
        self.name = f'{int(self.name):02}'


# Dayz
class Region(NameBase):
    def __init__(self, name):
        NameBase.__init__(self, name)

    def validate(self):
        if self.name not in VALID_REGION_NAMES:
            logger.error('Region name must match: {}'.format(VALID_REGION_NAMES))

    def output(self):
        return


# Giryang
class Element(NameBase):

    def __init__(self, name):
        NameBase.__init__(self, name)

    def validate(self):
        if not isinstance(self.name, str):
            logger.error('Element name must be a string.')

        regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')
        if regex.search(self.name):
            logger.error('Element name contains special characters')

        return

    def output(self):
        return


# Jessica
class ControlType(NameBase):
    def __init__(self, name):
        NameBase.__init__(self, name)

    def validate(self):
        if self.name not in VALID_CONTROL_TYPES:
            logger.error('Control types must match: {}'.format(VALID_CONTROL_TYPES))
            return

    def output(self):
        return


# Hari
class RigType(NameBase):
    def __init__(self, name):
        NameBase.__init__(self, name)

    def validate(self):
        if self.name not in VALID_RIG_TYPES:
            logger.error('Rig types must match: {}'.format(VALID_RIG_TYPES))
            return

    def output(self):
        return


# Thomas
class MayaType(NameBase):
    '''
    Description:
        Checks specified name againt all maya node types (mc.ls(nodeTypes=True))
    Arguemnts:
        name (str): Name of maya node type.
    Return:
        Validated name of maya node type.
    '''
    def __init__(self, name):
        NameBase.__init__(self, name)

    def validate(self):
        if self.name not in VALID_MAYA_TYPES:
            logger.error('Name must be a maya type: {}'.format(VALID_MAYA_TYPES))
            return

    def output(self):
        return


class RigName(NameBase):
    def __init__(
                self,
                full_name=None,
                side=None,
                region=None,
                element=None,
                control_type=None,
                rig_type=None,
                maya_type=None,
                position=None
                ):

        self.full_name = full_name
        self.side = side
        self.region = region
        self.element = element
        self.control_type = control_type
        self.rig_type = rig_type
        self.maya_type = maya_type
        self.position = position

        NameBase.__init__(self, full_name)

        logger.debug('self.full_name: {}'.format(self.full_name))
        logger.debug('self.side: {}'.format(self.side))
        logger.debug('self.region: {}'.format(self.region))
        logger.debug('self.element: {}'.format(self.element))
        logger.debug('self.control_type: {}'.format(self.control_type))
        logger.debug('self.rig_type: {}'.format(self.rig_type))
        logger.debug('self.maya_type: {}'.format(self.maya_type))
        logger.debug('self.position: {}'.format(self.position))



    def validate(self):
        # First check if full_name is specified and if so, break it up into individual segments.
        # Potentially allow 'none' as a type if not applicable

        if self.full_name:
            name_segments = self.name.split('_')

            self.side = Side(name_segments[0])
            self.region = Region(name_segments[1])
            self.element = Element(name_segments[2])
            self.control_type = ControlType(name_segments[3])
            self.rig_type = RigType(name_segments[4])
            self.maya_type = MayaType(name_segments[5])
            self.position = Position(name_segments[6])

        # Check type of each variable.  If NameBase then continue, otherwise instantiate the name
        else:
            if self.side and not isinstance(self.side, Side):
                self.side = Side(self.side)
            if self.region and not isinstance(self.region, Region):
                self.region = Region(self.region)
            if not isinstance(self.element, Element):
                self.element = Element(self.element)
            if self.control_type and not isinstance(self.control_type, ControlType):
                self.control_type = ControlType(self.control_type)
            if not isinstance(self.rig_type, RigType):
                self.rig_type = RigType(self.rig_type)
            if self.maya_type and not isinstance(self.maya_type, MayaType):
                self.maya_type = MayaType(self.maya_type)
            if self.position and not isinstance(self.position, Position):
                self.position = Position(self.position)

    def output(self):
        # Construct the string for entire object name.
        #
        # Allow optional side, region, control_type, maya_type, position
        name = str()
        if self.side:
            name = f'{name}{self.side}_'
        if self.region:
            name = f'{name}{self.region}_'
        # Element is required
        name = f'{name}{self.element}_'
        if self.control_type:
            name = f'{name}{self.control_type}_'
        # Rig_type is required
        name = f'{name}{self.rig_type}_'
        if self.maya_type:
            name = f'{name}{self.maya_type}_'
        if self.position:
            name = f'{name}{self.position}_'

        self.name = name.strip('_')
        # self.name = f'{self.side}_' \
        #                     f'{self.region}_' \
        #                     f'{self.element}_' \
        #                     f'{self.control_type}_' \
        #                     f'{self.rig_type}_' \
        #                     f'{self.maya_type}_' \
        #                     f'{self.position}'

# for testing purposes
def test():
    logger.debug(f"{Side('lt')}")
    logger.debug(f"{Region('Front')}")
    logger.debug(f"{Element('arm')}")
    logger.debug(f"{ControlType('ik')}")
    logger.debug(f"{RigType('ctrl')}")
    logger.debug(f"{MayaType('joint')}")
    logger.debug(f"{Position(20)}")
    logger.debug(f"{RigName(full_name = 'lt_front_arm_ik_ctrl_curve_20')}")

    side_type = Side('lt')
    full_name = RigName(side=side_type, region='front', element='arm', control_type='ik', rig_type=RigType('ctrl'), maya_type='curve', position=20)
    logger.debug(full_name)
