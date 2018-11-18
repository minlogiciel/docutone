# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import sys, os

sys.path.append("../")

WORKING_DIR = 'D:/DocutoneSoftware/SmartDoc'
#WORKING_DIR = '/home/dtnuser/project/smartDoc/smart Doc/DocutoneSoftware/SmartDoc'


PYTHON_SRC = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PYTHON_PATH = os.path.dirname(PYTHON_SRC)
PROG_SRC = os.path.dirname(PYTHON_PATH)
