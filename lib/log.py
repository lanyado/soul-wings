import sys
import logging

logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

def getLog(name):
    """
    Get logger with name as log prefix

    format: 2019-11-06 22:39:38,498 - INFO - Test - log this
    """

    logger = logging.getLogger(name)
    return logger
