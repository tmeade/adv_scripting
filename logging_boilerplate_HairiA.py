import logging


root_logger = logging.getLogger()
root_logger.setLevel(logging.ERROR)

formatter = logging.Formatter('%(levelname)s - %(module)s - %(funcName)s - %(message)s')

handlers = root_logger.handlers
handlers[1].setFormatter(formatter)


def test_logger();

    root_logger.debug('Debug stuff')
    root_logger.info('This is info')
    root_logger.warning('This is a warning')
    root_logger.error('Error this!')
    root_logger.critical('CRITICAL')
