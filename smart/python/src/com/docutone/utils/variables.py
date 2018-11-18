# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

import os

from docutone import working, config


WORKING_DIR = working.WORKING_DIR


MODEL_MM = "model.mm"
MODEL_DICT = "model.dict"
MODEL_LSI = "model.lsi"
SVC_MODEL = "model.svc"
DOC_MODEL = "model.d2v"
WORD_MODEL = "model.w2v"
FILE_LABEL = "label_file.txt"
DOC_LABEL = "label_doc.txt"
VECT_LABEL = "label_vect.txt"
WORD_DICT = "docutone.dict"
CLASSIFY_LABEL = "label_classify.txt"

TERM_MODEL_MM = "term.mm"
TERM_MODEL_DICT = "term.dict"
TERM_MODEL_LSI = "term.lsi"
TERM_DOC_MODEL = "term.d2v"
TERM_WORD_MODEL = "term.w2v"
TERM_LIST = "term_list.txt"
TERM_LABEL = "term_label.txt"
TERM_VECT = "term_vect.txt"


OUTPUT_DIR = 'TEXT'
TEMP_DIR = 'TEMP'
DATA_DIR = "data"
MODEL_DATA_DIR = "data"
MODELS = "models"
TRAINING_DATA = "training_data"

PYTHON_SRC = working.PYTHON_SRC
PROG_SRC = working.PROG_SRC

HOME_DIR = WORKING_DIR + '/home'
BASE_DIR = HOME_DIR
BIN_DIR = WORKING_DIR +'/bin'
TMODEL_DIR = HOME_DIR + '/model'
PROJECT_ROOT = HOME_DIR + '/import'

CORPUS_DIR = config.CORPUS_DIR

def load_properties() :
    props = {}  
   
    fname = os.path.join(HOME_DIR, 'config/DocutoneConfig.properties')

    with open(fname, 'r') as f:
        for line in f:
            line = line.rstrip() #removes trailing whitespace and '\n' chars

            if '=' not in line: 
                continue #skips blanks and comments 
            
            if line.startswith("#"): 
                continue #skips comments which contain =

            k, v = line.split("=", 1)
            props[k] = v
    return props
    

#CONFIG_PROPERTIES = load_properties()
OUTPUT_RESULT = "output_result.log"


def get_data_file_name(dataname, categorie=MODELS) :
    path = os.path.join(BASE_DIR, DATA_DIR)
    if not os.path.exists(path) :
        os.mkdir(path)
    path = os.path.join(path, categorie)
    if not os.path.exists(path) :
        os.mkdir(path)
    if dataname :
        path = os.path.join(path, dataname)
    return path

def get_template_path(tpath="Template") :
    return get_data_file_name(tpath, categorie="terms")
    

def get_temp_path() :
    path = os.path.join(BASE_DIR, "temp")
    if not os.path.exists(path) :
        os.mkdir(path)
    
    return path


def noloaddir(name):
    if name[0] == '.' or name[0] == '~' or name == "DATA" :
        return True
    elif name == OUTPUT_DIR or name == TEMP_DIR or name == DATA_DIR or name == TRAINING_DATA :
        return True
    else :
        return False
    
def locate_file(filename, tp="TEXT"):

    root = PROJECT_ROOT.replace("\\", "/")
    
    path = filename.replace("\\", "/")
    if (root in path) :
        fpath = path[(len(root)+1):]
        index = fpath.index('/')
        fname = fpath[(index+1):]               # file name
        pname = fpath[0:index]                  # project name
        ppath = root + "/" + pname + "/" + tp   # root/project path/TEXT
        if not os.path.exists(ppath) :
            os.mkdir(ppath)
        
        fname = os.path.join(ppath, fname)
    else :
        name = os.path.basename(filename)
        fname = get_temp_path() + "/" + name
        
    if not fname.endswith(".txt") :
        fname += ".txt"
    
    return fname



