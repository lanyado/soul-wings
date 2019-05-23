import sys
import logging
import datetime

logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

def getLog(name):
    logger = logging.getLogger(name)
    return logger
