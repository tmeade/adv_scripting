import logging
# HOST/root level code - i.e., this goes in Maya

# instantiate logger and set level
root_logger = logging.getLogger()
root_logger.setLevel(logging.ERROR)

# Set a formatter
formatter = logging.Formatter('%(levelname)s - %(module)s - %(funcName)s - %(message)s')

# Get the current handlers and set formatter to the MayaGuiStream
handlers = root_logger.handlers
handlers[1].setFormatter(formatter)

# Note that you can create new handlers.  EX:
# This would create another stream similar to the exisitng maya stream
#handler = logging.StreamHandler()

# This will create another stream that outputs to a file
#handler = logging.FileHandler('C:/temp/logtest.log')


def test():
    logger = logging.getLogger(__name__)
    logger.debug('Debug stuff')
    logger.info('This is info')
    logger.warning('This is a warning')
    logger.error('Error this!')
    logger.critical('CRITICAL')
