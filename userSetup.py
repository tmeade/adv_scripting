import maya
import logging

TM_ROOT_LOGGER = logging


def init_log(standalone=False):

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    handlers = root_logger.handlers

    # Create a file handler
    file_handler = logging.FileHandler('/Users/tmeade/Desktop/myLog.log')
    root_logger.addHandler(file_handler)

    # Add formatter to handlers
    file_log_formatter = logging.Formatter(
                        '%(asctime)s | %(levelname)s | %(module)s | %(funcName)s | %(message)s')
    maya_formatter = logging.Formatter(
                        '%(levelname)s | %(module)s | %(funcName)s | %(message)s')

    handlers[1].setFormatter(maya_formatter)
    handlers[2].setFormatter(file_log_formatter)

    root_logger.propagate = 0

    root_logger.info('LOGGER INITIATED')

    global TM_ROOT_LOGGER
    TM_ROOT_LOGGER = root_logger

    return root_logger

maya.utils.executeDeferred(init_log, standalone=True)
