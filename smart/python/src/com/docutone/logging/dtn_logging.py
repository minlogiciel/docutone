# -*- coding: UTF-8 -*-
from __future__ import unicode_literals


import sys
import logging

sys.path.append("../")

from docutone.utils import variables

class DTNLogging(object):
    
    def __init__(self):
        """
        """


def init_logger() :
    
    loggerhander = logging.FileHandler(variables.HOME_DIR +'/logs/dtn_python.log', encoding = "UTF-8")
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    loggerhander.setFormatter(formatter)
    loggerhander.setLevel(logging.DEBUG)
    

    streamhander = logging.StreamHandler()
    streamhander.setLevel(logging.ERROR)
    streamhander.setFormatter(formatter)
    

    return loggerhander, streamhander

loggerhander, streamhander = init_logger()


def get_logger(name):
    if name :
        logger = logging.getLogger(name)
    else :
        logger = logging.getLogger('dtn_python')
    
    logger.setLevel(logging.WARNING)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(loggerhander) 
    logger.addHandler(streamhander)

    return logger

    
def logger_info(name, info):
    logger = get_logger(name)
    logger.info(info)
    
def logger_debug(name, info):
    logger = get_logger(name)
    logger.debug(info)

def logger_error(name, info):
    logger = get_logger(name)
    logger.error(info)

