# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import sys

sys.path.append("../")

from docutone import working

CRF_PATH = working.PYTHON_PATH+"/CRF++-0.58"

if sys.platform == "darwin" :
    CRF_BIN = CRF_PATH + "/mac"
    CORPUS_DIR = "/doc"
elif sys.platform == "linux" :
    CRF_BIN = CRF_PATH
    CORPUS_DIR = "/doc"
else :
    CRF_BIN = CRF_PATH + "/bin/windows"
    CORPUS_DIR = working.WORKING_DIR + '/home/data/Corpus'

CORPUS_DIR = working.PYTHON_SRC + '/data/Corpus'

#TEMPLATE_DIR = working.WORKING_DIR + '/home/data/terms/Template'
TEMPLATE_DIR = working.PYTHON_SRC + '/data/Template'

TEST_PATH = working.PYTHON_PATH + '/src-test/TESTFile/TEXT'


NER_PATH = working.PROG_SRC + "/src/classifiers/"
JAR_PATH = working.PROG_SRC + "/WebRoot/WEB-INF/lib/smart/"

UTF8_ENCODING = "utf-8"
