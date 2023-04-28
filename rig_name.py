'''
rig_name.py
anm355 Advanced Scripting

Naming convention:
side_region_element_controltype_rigtype_mayatype_position
e.g. lt_front_arm_ik_ctrl_nurbscurve_01
'''
import maya.cmds as mc
import logging
import re

logger = logging.getLogger()

# Constants
VALID_SIDE_TYPES = ['lt', 'rt', 'ctr']
VALID_REGION_TYPES = ['front', 'rear', 'middle', 'upper', 'lower', 'start', 'end']
VALID_CONTROL_TYPES = ['ik', 'fk', 'bnd', 'dyn', 'mocap', 'driver', 'switch']
VALID_RIG_TYPES = ['ctrl', 'offset', 'sdk', 'handle', 'pv', 'loc', 'jnt', 'geo', 'constraint', 'grp', 'util']
VALID_MAYA_TYPES = [x.lower() for x in mc.ls(nodeTypes=True)]

# Parse name possibilities
PARSE_SIDE_TYPES = {
    'lt': ['lt', 'lf', 'lft', 'left', 'l'],
    'rt': ['rt', 'rgt', 'right', 'r'],
    'ctr': ['ctr', 'cen', 'cntr', 'center', 'c', 'mid', 'midl', 'middle', 'm']
    }
PARSE_REGION_TYPES = {
    'front': ['front', 'f', 'fr', 'ft', 'for', 'fore', 'head', 'hd'],
    'rear': ['rear', 'r', 're', 'rr', 'b', 'bak', 'back', 'behind', 'tail', 'tl'],
    'middle': ['middle', 'm', 'mid', 'mdl', 'ctr', 'cen', 'cntr', 'center', 'c'],
    'upper': ['upper', 'u', 'up', 'upp', 'upr', 't', 'tp', 'top'],
    'lower': ['lower', 'l', 'lo', 'low', 'lwr', 'b', 'bt', 'bot', 'bottom'],
    'start': ['start', 'starting', 'st', 'str', 'sta', 'begin', 'beg', 'bg'],
    'end': ['end', 'ending', 'ee', 'final', 'fin', 'fn']
    }
PARSE_CONTROL_TYPES = {
    'ik': ['ik'],
    'fk': ['fk'],
    'bnd': ['bnd', 'bind', 'bn'],
    'dyn': ['dyn', 'dn', 'dynamic'],
    'mocap': ['mocap', 'mo', 'moc'],
    'driver': ['driver', 'd', 'dr', 'drv', 'driv'],
    'switch': ['switch', 's', 'sw', 'swi', 'swt', 'sch', 'swch']
    }
PARSE_RIG_TYPES = {
    'ctrl': ['ctrl', 'ctl', 'ctr', 'ctlr', 'control'],
    'offset': ['offset', 'offest', 'ofs', 'off', 'ofst'],
    'sdk': ['sdk', 'setdrivenkey', 'set', 'driven'],
    'handle': ['handle', 'handl', 'ikhandle', 'han', 'hdl'],
    'pv': ['pv', 'polevector', 'pole', 'vec', 'pvec', 'pov'],
    'loc': ['loc', 'locator'],
    'jnt': ['jnt', 'jn', 'joi', 'joint'],
    'geo': ['geo', 'geometry'],
    'constraint': ['constraint', 'constr', 'cn', 'con', 'cst', 'cnsr'],
    'grp': ['grp', 'gr', 'gro', 'group'],
    'util': ['util', 'utl', 'uti', 'utility']
}
NUM_TYPES = 7


class NameBase(): # Abstract Base Class
    '''
    Description:
        Base class for returning a valid string object name.
    Args:
        name (string): name of the naming element
    Returns:
        String representation of the valid naming element
    '''

    def __init__(self, name=None, parse=False):
        if isinstance(name, type(self)):
            self.name = name.name
        else:
            self.name = name
        if parse and not self.validate():
            self.parse_name()

    def __str__(self):
        return self.output()

    def __repr__(self):
        return f'{self.__class__.__name__}("{self.output()}")'
        #return f'{type(self).__name}({super().__repr__()})'

    def validate(self):
        '''
        Returns boolean whether self.name is valid
        '''
        if not self.name: return False
        if not isinstance(self.name, str): return False
        return True

    def parse_name(self):
        '''
        Parse self.name. Change name to adhere to naming convention.
        '''
        try:
            self.name = str(self.name)
        except:
            self.name = None

    def output(self):
        '''
        Return correctly formatted name
        '''
        if self.name:
            return self.name
        else:
            return ''


class Side(NameBase):
    def __init__(self, name, parse=False):
        NameBase.__init__(self, name, parse)

    def validate(self):
        if not self.name: return False
        if self.name not in VALID_SIDE_TYPES:
            #logger.debug('Side name must match options: {}'.format(VALID_SIDE_TYPES))
            return False
        return True

    def parse_name(self):
        name = self.name.lower()
        for opt in VALID_SIDE_TYPES:
            if name in PARSE_SIDE_TYPES[opt]:
                self.name = opt
                return
        #logger.debug(f'Side failed to parse name {self.name}')
        self.name = None


# Jodi
class Position(NameBase):
    def __init__(self, name, parse=False):
        NameBase.__init__(self, name, parse)

    def validate(self):
        if not self.name: return False
        if not isinstance(self.name, int):
            #logger.debug(f'{self.name} should be a positive integer')
            return False
        return True

    def parse_name(self):
        if isinstance(self.name, str):
            if self.name.isdecimal():
                self.name = int(self.name)
            else:
                #logger.debug(f'Position failed to parse name {self.name}')
                self.name = None
        else:
            try:
                self.name = int(self.name)
            except:
                #logger.debug(f'Position failed to parse name {self.name}')
                self.name = None

    def output(self):
        if self.name:
            return f'{int(self.name):02}'
        else:
            return ''


# Dayz
class Region(NameBase):
    def __init__(self, name, parse=False):
        NameBase.__init__(self, name, parse)

    def validate(self):
        if not self.name: return False
        if self.name not in VALID_REGION_TYPES:
            #logger.debug('Region name must match options: {}'.format(VALID_REGION_TYPES))
            return False
        return True

    def parse_name(self):
        name = self.name.lower()
        for opt in VALID_REGION_TYPES:
            if name in PARSE_REGION_TYPES[opt]:
                self.name = opt
                return
        #logger.debug(f'Region failed to parse name {self.name}')
        self.name = None


# Giryang
class Element(NameBase):

    def __init__(self, name, parse=False):
        NameBase.__init__(self, name, parse)

    def validate(self):
        if not self.name: return False
        if not isinstance(self.name, str):
            #logger.debug('Element name must be a string.')
            return False

        regex = re.compile('[@ !#$%^&*()<>?/\|}{~:]')
        if regex.search(self.name):
            #logger.debug('Element name contains special characters')
            return False

        return True

    def parse_name(self):
        name = self.name.lower()
        self.name = re.sub(r'\W+', '_', name).strip('_')


# Jessica
class ControlType(NameBase):
    def __init__(self, name, parse=False):
        NameBase.__init__(self, name, parse)

    def validate(self):
        if not self.name: return False
        if self.name not in VALID_CONTROL_TYPES:
            #logger.debug('Control types must match options: {}'.format(VALID_CONTROL_TYPES))
            return False
        return True

    def parse_name(self):
        name = self.name.lower()
        for opt in VALID_CONTROL_TYPES:
            if name in PARSE_CONTROL_TYPES[opt]:
                self.name = opt
                return
        #logger.debug(f'ControlType failed to parse name {self.name}')
        self.name = None


# Hari
class RigType(NameBase):
    def __init__(self, name, parse=False):
        NameBase.__init__(self, name, parse)

    def validate(self):
        if not self.name: return False
        if self.name not in VALID_RIG_TYPES:
            #logger.debug('Rig types must match options: {}'.format(VALID_RIG_TYPES))
            return False
        return True

    def parse_name(self):
        name = self.name.lower()
        for opt in VALID_RIG_TYPES:
            if name in PARSE_RIG_TYPES[opt]:
                self.name = opt
                return
        #logger.debug(f'RigType failed to parse name {self.name}')
        self.name = None


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
    def __init__(self, name, parse=False):
        NameBase.__init__(self, name, parse)

    def validate(self):
        if not self.name: return False
        if self.name not in VALID_MAYA_TYPES:
            #logger.debug('Maya types must match options: {}'.format(VALID_MAYA_TYPES))
            return False
        return True

    def parse_name(self):
        name = self.name.lower()
        if name not in VALID_MAYA_TYPES:
            #logger.debug(f'MayaType failed to parse name {self.name}')
            self.name = None


class RigName(NameBase):
    def __init__(self,
                full_name=None,
                side=None,
                region=None,
                element=None,
                control_type=None,
                rig_type=None,
                maya_type=None,
                position=None):

        NameBase.__init__(self, full_name)

        self.prefix = None
        self.full_name = full_name
        if full_name and '|' in full_name:
            longname = full_name.rsplit('|', 1)
            self.prefix = longname[0]
            self.full_name = longname[1]
        if side:
            if isinstance(side, Side): self.side = side
            else: self.side = Side(side)
        else: self.side = None
        if region:
            if isinstance(region, Region): self.region = region
            else: self.region = Region(region)
        else: self.region = None
        if element:
            if isinstance(element, Element): self.element = element
            else: self.element = Element(element)
        else: self.element = None
        if control_type:
            if isinstance(control_type, ControlType): self.control_type = control_type
            else: self.control_type = ControlType(control_type)
        else: self.control_type = None
        if rig_type:
            if isinstance(rig_type, RigType): self.rig_type = rig_type
            else: self.rig_type = RigType(rig_type)
        else: self.rig_type = None
        if maya_type:
            if isinstance(maya_type, MayaType): self.maya_type = maya_type
            else: self.maya_type = MayaType(maya_type)
        else: self.maya_type = None
        if position:
            if isinstance(position, Position): self.position = position
            else: self.position = Position(position)
        else: self.position = None

        # logger.debug('self.full_name: {}'.format(self.full_name))
        # logger.debug('self.prefix: {}'.format(self.prefix))
        # logger.debug('self.side: {}'.format(self.side))
        # logger.debug('self.region: {}'.format(self.region))
        # logger.debug('self.element: {}'.format(self.element))
        # logger.debug('self.control_type: {}'.format(self.control_type))
        # logger.debug('self.rig_type: {}'.format(self.rig_type))
        # logger.debug('self.maya_type: {}'.format(self.maya_type))
        # logger.debug('self.position: {}'.format(self.position))

        if not self.validate():
            self.parse_name()
        #logger.debug(f'RigName output(): {self.name}')

    def rename(self,
                full_name=None,
                side=None,
                region=None,
                element=None,
                control_type=None,
                rig_type=None,
                maya_type=None,
                position=None):
        logger.debug('========== RENAME ==========')
        if full_name:
            if '|' in full_name:
                longname = full_name.rsplit('|', 1)
                self.prefix = longname[0]
                self.full_name = longname[1]
            else:
                self.full_name = full_name
        else:
            self.full_name = None
        if side:
            if isinstance(side, Side): self.side = side
            else: self.side = Side(side, parse=True)
        if region:
            if isinstance(region, Region): self.region = region
            else: self.region = Region(region, parse=True)
        if element:
            if isinstance(element, Element): self.element = element
            else: self.element = Element(element, parse=True)
        if control_type:
            if isinstance(control_type, ControlType): self.control_type = control_type
            else: self.control_type = ControlType(control_type, parse=True)
        if rig_type:
            if isinstance(rig_type, RigType): self.rig_type = rig_type
            else: self.rig_type = RigType(rig_type, parse=True)
        if maya_type:
            if isinstance(maya_type, MayaType): self.maya_type = maya_type
            else: self.maya_type = MayaType(maya_type, parse=True)
        if position:
            if isinstance(position, Position): self.position = position
            else: self.position = Position(position, parse=True)
        if not self.validate():
            self.parse_name()

        logger.debug('self.full_name: {}'.format(self.full_name))
        logger.debug('self.prefix: {}'.format(self.prefix))
        logger.debug('self.side: {}'.format(self.side))
        logger.debug('self.region: {}'.format(self.region))
        logger.debug('self.element: {}'.format(self.element))
        logger.debug('self.control_type: {}'.format(self.control_type))
        logger.debug('self.rig_type: {}'.format(self.rig_type))
        logger.debug('self.maya_type: {}'.format(self.maya_type))
        logger.debug('self.position: {}'.format(self.position))
        logger.debug('Rename output: {}'.format(self.output()))

    def components(self):
        '''
        Return class variables in list form, except name and full_name.
        '''
        return [self.side, self.region, self.element, self.control_type,
            self.rig_type, self.maya_type, self.position]

    def validate(self):
        '''
        Check that input is valid and adheres to naming convention.
        Check that all name components adhere to naming convention.

        Returns boolean.
        '''
        #logger.debug('========== VALIDATE ==========')
        if self.full_name == self.output_fullname():
            return True

        # First check if full_name is specified and if so, break it up into individual segments.
        # Potentially allow 'none' as a type if not applicable
        if self.full_name: # If provided full name, separate name components

            # Check that full_name is underscore format
            if not self.is_underscore(self.full_name):
                #logger.debug(f'Name {self.full_name} needs to be in underscore format')
                return False

            name_segments = self.full_name.split('_')
            if len(name_segments) >= NUM_TYPES:
                # Put extra name segments in Element component
                sid, reg, *ele, con, rig, may, pos = name_segments
                # Assign parsed name segments to name components
                if sid: sid = Side(sid)
                if reg: reg = Region(rig)
                if ele:
                    ele = '_'.join(ele)
                    ele = Element(ele)
                if con: con = ControlType(con)
                if rig: rig = RigType(rig)
                if may: may = MayaType(may)
                if pos: pos = Position(pos)
            else:
                #logger.debug(f'Name {self.full_name} requires 7 components '\
                #    'following the name convention:\t'\
                #    'side_region_element_controltype_rigtype_mayatype_position')
                return False

            components = [sid, reg, ele, con, rig, may, pos]
            # Validate each component
            for component in components:
                if not component: continue # Allow component to be None
                if not component.validate():
                    #logger.debug(f'Component name {component.name} is not valid')
                    return False

            # Check if full_name matches component_name
            component_name = '_'.join(c.output() for c in components)
            if self.full_name == component_name: # Store name components
                self.side = sid
                self.region = reg
                self.element = ele
                self.control_type = con
                self.rig_type = rig
                self.maya_type = may
                self.position = pos
                self.full_name = self.output_fullname()
                self.name = self.output()
                return True

        # If provided components
        components = self.components()
        for component in components:
            if not component: continue # Allow component to be None
            name = component.name
            # For non-Position component check that name is string
            if not isinstance(component, Position):
                if not isinstance(name, str):
                    #logger.warning(f'{name} is not string')
                    return False
                # Check that each component has no special characters
                if isinstance(component, Element):
                    if self.has_special_character(name, underscore=False):
                        #logger.warning(f'{name} contains special character')
                        return False
                else:
                    if self.has_special_character(name, underscore=True):
                        #logger.warning(f'{name} contains special character')
                        return False
            # Validate each component
            if not component.validate():
                #logger.debug(f'Component name {component.name} is not valid')
                return False
        # Assign component_name to full_name
        self.full_name = self.output_fullname()
        self.name = self.output()
        return True

    def parse_name(self):
        '''
        Parse/format full_name and construct name components.
        Allow optional side, region, control_type, maya_type, position.

        If both full_name and other name components are provided, component names take priority.
        Name components (Side, Region, Element, ControlType, RigType, MayaType, Position)
        will be overwritten by components of full_name.

        Change name components to be valid.
        Convert camelcase to underscore.
        e.g. LeftHandIndex1 (convert camelcase) -> lt_hand_index_bnd_jnt_joint_01
            side: lt
            region: None
            element: hand_index
            control_type: bnd
            rig_type: jnt
            maya_type: joint
            position: 01
        '''
        #logger.debug('========== PARSE_NAME ===========')
        components = self.components()
        full_name = self.full_name

        if full_name: # If provided full name, try to parse full_name first
            if self.has_special_character(full_name):
                #logger.debug(f'Full name {full_name} contains special characters')
                full_name = re.sub(r' ', '_', full_name) # Replace spaces with underscore
                full_name = self.remove_special_character(full_name) # Remove special characters

            if self.is_camelcase(full_name): # Name is camelcase format
                full_name = self.camelcase_to_underscore(full_name)
            elif self.is_underscore(full_name): # Name is underscore format
                pass
            elif self.is_underscore(full_name.lower()):
                full_name = full_name.lower()
            else: # Name is unidentified format
                logger.error(f'Unknown joint naming convention. '\
                    'Name {full_name} needs to be in underscore format')

            # Split full name into segments to parse name types
            name_segments = full_name.split('_')

            if len(name_segments) == 0:
                logger.error(f'len0/ Name {self.full_name} requires 7 components '\
                    'following the name convention:\t'\
                    'side_region_element_controltype_rigtype_mayatype_position')

            elif len(name_segments) == 1:
                self.element = Element(name_segments[0], parse=True)
                if not self.element.validate():
                    self.element = None
                    logger.error('len1/ Failed to parse name.\t'\
                                f'Full name: {full_name}\t'\
                                f'Name segments: {name_segments}')

            elif len(name_segments) < NUM_TYPES:
                # Try brute force matching components from left to right
                seglist = list() # remaining segments not matching
                for seg in name_segments:
                    if not seg: continue # Allow segment to be None
                    # If name segment matches, store to variable
                    # Check if name components are valid
                    if not self.side:
                        sid = Side(seg, parse=True)
                        if sid.validate():
                            self.side = sid
                            continue
                    if not self.region:
                        reg = Region(seg, parse=True)
                        if reg.validate():
                            self.region = reg
                            continue
                    if not self.control_type:
                        con = ControlType(seg, parse=True)
                        if con.validate():
                            self.control_type = con
                            continue
                    if not self.rig_type:
                        rig = RigType(seg, parse=True)
                        if rig.validate():
                            self.rig_type = rig
                            continue
                    if not self.maya_type:
                        may = MayaType(seg, parse=True)
                        if may.validate():
                            self.maya_type = may
                            continue
                    if not self.position:
                        pos = Position(seg, parse=True)
                        if pos.validate():
                            self.position = pos
                            continue
                    seglist.append(seg)

                if seglist:
                    # Check if remaining name segments are valid element name
                    ele = Element('_'.join(seglist), parse=True)
                    if ele.validate(): # Check if element is valid
                        self.element = ele
                    else:
                        logger.debug(f'Element: {ele}')
                        logger.debug(f'Name segments: {name_segments}')
                        logger.error('len-/ Failed to parse name.\t'\
                                    f'Full name: {full_name}\t'\
                                    f'Name segments: {name_segments}')

            elif len(name_segments) >= NUM_TYPES:
                # Assume Naming convention:
                # side_region_element_controltype_rigtype_mayatype_position

                # Put extra name segments in Element component ele
                sid, reg, *ele, con, rig, may, pos = name_segments
                segfront = list()
                segback = list()
                # Create name component from parsed name segment
                if sid and not self.side:
                    name_sid = Side(sid, parse=True)
                    if name_sid.validate():
                        self.side = name_sid
                    else:
                        segfront.append(sid)
                if reg and not self.region:
                    segfront.append(reg)
                    newlist = list()
                    for seg in segfront:
                        name_reg = Region(seg, parse=True)
                        if name_reg.validate():
                            self.region = name_reg
                        else:
                            newlist.append(seg)
                    segfront = newlist
                if pos and not self.position:
                    name_pos = Position(pos, parse=True)
                    if name_pos.validate():
                        self.position = name_pos
                    else:
                        segback.append(pos)
                if may and not self.maya_type:
                    segback.append(may)
                    newlist = list()
                    for seg in segback:
                        name_may = MayaType(seg, parse=True)
                        if name_may.validate():
                            self.maya_type = name_may
                        else:
                            newlist.append(seg)
                    segback = newlist
                if rig:
                    segback.append(rig)
                    newlist = list()
                    for seg in segback:
                        name_rig = RigType(seg, parse=True)
                        if name_rig.validate():
                            self.rig_type = name_rig
                        else:
                            newlist.append(seg)
                    segback = newlist
                if con:
                    segback.append(con)
                    newlist = list()
                    for seg in segback:
                        name_con = ControlType(seg, parse=True)
                        if name_con.validate():
                            self.control_type = name_con
                        else:
                            newlist.append(seg)
                    segback = newlist

                # Check if remaining name segments are valid element name
                ele = '_'.join(segfront+ele+segback)
                ele = Element(ele, parse=True)
                if ele.validate(): # Check if element is valid
                    self.element = ele
                else:
                    logger.debug(f'Element: {ele}')
                    logger.debug(f'Components: {self.components()}')
                    logger.error('len+/ Failed to parse name.\t'\
                                f'Full name: {full_name}\t'\
                                f'Name segments: {name_segments}')

                self.full_name = self.output_fullname()
                self.name = self.output()
                #logger.debug('Done parsing name!\t'\
                #            f'Full name: {self.full_name}\t'\
                #            f'Name: {self.name}')

        # For provided name components
        # Check that each name component is string without special characters
        for component in components:
            if not component: continue # Allow None
            name = component.name
            # For non-Position component check that name is string
            if not isinstance(component, Position):
                if not isinstance(name, str):
                    name = str(name)
                # For each component remove special characters
                if isinstance(component, Element):
                    if self.has_special_character(name, underscore=False):
                        self.remove_special_character(name, underscore=False)
                else:
                    if self.has_special_character(name, underscore=True):
                        self.remove_special_character(name, underscore=True)
            # Check that each component is valid
            if not component.validate():
                component.parse_name()

        # Store new names
        self.full_name = self.output_fullname()
        self.name = self.output()
        # Try validating again
        if not self.validate():
            logger.error(f'Failed to parse name {self.full_name}.\t'\
                'Try renaming or inputting individual name components.')
        # logger.debug('Done parsing name!\t'\
        #             f'Full name: {self.full_name}\t'\
        #             f'Name: {self.name}')
        return True

    def output(self):
        '''
        Construct string for object name.
        Allow optional side, region, control_type, maya_type, position.
        Missing components are excluded from name.
        '''
        components = self.components()
        name = self.underscore_cleanup('_'.join(c.output() for c in components if c))
        return name

    def output_fullname(self):
        '''
        Construct string for full object name full_name.
        Allow optional side, region, control_type, maya_type, position.
        Missing components are left as empty spaces ''.
        '''
        components = self.components()
        name = self.underscore_cleanup('_'.join(c.output() for c in components if c))
        if self.prefix:
            return f'{self.prefix}|{name}'
        return name

    def replace_fullname(self, full_name):
        self.full_name = full_name
        if not self.validate():
            self.parse_name()
        return self.name

    def replace_component(self, component):
        logger.debug(f'Replace component: {component}')
        if isinstance(component, Side):
            self.side = component
        elif isinstance(component, Region):
            self.region = component
        elif isinstance(component, Element):
            self.element = component
        elif isinstance(component, ControlType):
            self.control_type = component
        elif isinstance(component, RigType):
            self.rig_type = component
        elif isinstance(component, MayaType):
            self.maya_type = component
        elif isinstance(component, Position):
            self.position = component
        else:
            logger.warning(f'Failed to replace component {component}. Current name: {self.name}')
            return self.name

        if not component.validate():
            component.parse_name()
        self.full_name = self.output_fullname()
        self.name = self.output()
        logger.debug(f'New name: {self.name}')
        return self.name

    @staticmethod
    def is_underscore(name):
        if name.islower() and '_' in name:
            return True
        return False

    @staticmethod
    def is_camelcase(name):
        if not name.islower() and not name.isupper():
            return True
        return False

    @staticmethod
    def camelcase_to_underscore(name):
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        name = re.sub('(.)([0-9]+)', r'\1_\2', name)
        name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
        return re.sub(r'(\d+)', lambda x : x.group(1).zfill(2), name)

    @staticmethod
    def underscore_to_camelcase(name):
        name = re.sub(r'0+(.*?)(_|\Z)', r'\1', name)
        return ''.join(x.title() for x in name.split('_'))

    @staticmethod
    def underscore_cleanup(name):
        regex = re.compile(r'_{2,}')
        return regex.sub('_', name)

    @staticmethod
    def has_special_character(name, underscore=False):
        if underscore:
            special_chara = re.compile('[@ !#$%^&*()<>?/\}{~:]_')
        else:
            special_chara = re.compile('[@ !#$%^&*()<>?/\}{~:]')
        return special_chara.search(name)

    @staticmethod
    def remove_special_character(name, underscore=False):
        if underscore:
            special_chara = re.compile('[@ !#$%^&*()<>?/\}{~:]_')
        else:
            special_chara = re.compile('[@ !#$%^&*()<>?/\}{~:]')
        return re.sub(special_chara, '', name).strip('_')


# for testing purposes
def test():
    logger.debug(f"{Side('lt')}")
    logger.debug(f"{Region('Front')}")
    logger.debug(f"{Element('arm')}")
    logger.debug(f"{ControlType('ik')}")
    logger.debug(f"{RigType('ctrl')}")
    logger.debug(f"{MayaType('joint')}")
    logger.debug(f"{Position(20)}")
    logger.debug(f"{RigName(full_name = 'lt_front_arm_ik_ctrl_nurbscurve_20')}")

    side_type = Side('lt')

    test1 = RigName(side=side_type, region='front', element='arm', control_type='ik', rig_type=RigType('ctrl'), maya_type='nurbscurve', position=20)
    logger.debug('--- test1 ---')
    logger.debug(f'Full name: {test1.full_name}')
    logger.debug(f'Name: {test1.name}')
    logger.debug(f'{test1}')

    test2 = RigName(full_name = 'lt_front_arm_ik_ctrl_nurbscurve_20')
    logger.debug('--- test2 ---')
    logger.debug(f'Full name: {test2.full_name}')
    logger.debug(f'Name: {test2.name}')
    logger.debug(f'{test2}')

    test3 = RigName(full_name = 'LeftHandIndex1')
    logger.debug('--- test3 ---')
    logger.debug(f'Full name: {test3.full_name}')
    logger.debug(f'Name: {test3.name}')
    logger.debug(f'{test3}')
