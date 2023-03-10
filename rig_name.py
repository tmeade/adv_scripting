import maya.cmds as mc
import logging
logger = logging.getLogger(__name__)
# Naming convention
# lt_front_arm_ik_ctrl_curve_position

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


# Jodi
class Position(NameBase):
    pass


# Dayz
class Region(NameBase):
    pass


# Giryang
class Element(NameBase):
    pass


# Jessica
class ControlType(NameBase):
    pass


# Hari
class RigType(NameBase):
    pass


# Thomas
class MayaType(NameBase):
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

    def validate(self):
        # First check if full_name is specified and if so, break it up into individual segments.
        # Potentially allow 'none' as a type if not applicable
        #
        # Check type of each variable.  If NameBase then continue, otherwise instantiate the name
        pass

    def output(self):
        # Construct the string for entire object name.
        #
        # Allow side, region, position
        pass
