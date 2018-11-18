# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import sys, os, codecs

sys.path.append("../")

from docutone import working, config
from docutone.utils import util


CRF_LEARN = config.CRF_BIN+"/crf_learn"
CRF_TEST = config.CRF_BIN+"/crf_test"

CRF_TAG_BEGIN = 'B'  # B代表开头，M代表中间，E代表结尾 , S(Single)。
CRF_TAG_MIDDLE = 'M'  
CRF_TAG_END = 'E'  
CRF_TAG_SINGLE = 'S' 
         
CRF_CHAR_D = 'D'  # digital
CRF_CHAR_L = 'L'  # letter
CRF_CHAR_S = 'S'  # simple
CRF_CHAR_P = 'P'  # double 
CRF_CHAR_W = 'W'  # 

CRF_MODEL_EXT ='.model'
CRF_FILE_TAG_EXT = '.tag'

NO_NAME = "NoName"

def get_default_crf_file():
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(path, 'text/crfname.txt')


def get_crf_root() :
    root = os.path.join(working.PYTHON_SRC, 'data/crf')
    if not os.path.exists(root) :
        os.mkdir(root)
    return root

def get_crf_template_file():
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(path, 'text/crf_template')


def get_crf_categorie_file():
    root_path = get_crf_root()
    return os.path.join(root_path, 'crf_categorie_name.txt')

def get_crf_training_directory(subdir = None):
    root_path = get_crf_root()
    path = os.path.join(root_path, 'training')
    if not os.path.exists(path) :
        os.mkdir(path)
    
    if subdir :
        path = os.path.join(path, subdir)
        if not os.path.exists(path) :
            os.mkdir(path)
    return path



def load_crf_model_directories():
    modelname = {}
    fname = get_crf_categorie_file()
    if os.path.exists(fname) :
        f = codecs.open(fname, 'r', 'utf-8')
        for line in f :
            line = line.strip() 
            if len(line) > 0:
                if '#' in line :
                    continue
                elif ':' in line :
                    name, ty = line.split(":")
                    modelname[name.strip()] = ty.strip() 
        f.close()
    return modelname

def add_crf_model_name(categorie):
    
    if categorie in CRF_MODEL_NAME.keys() :
        name = CRF_MODEL_NAME[categorie]
    else :
        n = len(CRF_MODEL_NAME) + 1
        name = "crf_training" +str(n)
        CRF_MODEL_NAME[categorie] = name

        fname = get_crf_categorie_file()
        if os.path.exists(fname) :
            f = codecs.open(fname, 'a', 'utf-8')
        else :
            f = codecs.open(fname, 'w', 'utf-8')
        f.write(categorie+":"+name+"\n")
        f.close()
    return name

def get_crf_model_name(categorie):
    
    if categorie in CRF_MODEL_NAME.keys() :
        return CRF_MODEL_NAME[categorie]
    else :
        return None

CRF_MODEL_NAME = load_crf_model_directories()


def load_crf_tagging_name():
    crftypes = {}
    fname = get_default_crf_file()
    f = codecs.open(fname, 'r', 'utf-8')
    for line in f :
        line = line.strip() 
        if len(line) > 0:
            if '#' in line :
                continue
            elif ':' in line :
                name, ty = line.split(":")
                crftypes[name.strip()] = ty.strip()
                      
    f.close()
    return crftypes
        
CRF_TAGGING = load_crf_tagging_name()
        
'''
W代表普通的词，D代表数字， L表示字母, S代表结束标点符号，P表示对称标点符号，
'''
def get_word_tagging(word, _focus):
    tagging = ''
    if _focus :
        tagging = _focus.getItemTagging(word)
    elif word in CRF_TAGGING.keys() :
        tagging = "-" + CRF_TAGGING[word]
    
    return tagging
 
def get_tagging_name(key, keywords, _focus):
    
    tagging_name = None
    if "-" in key :
        tagging = key[2:]
        if _focus :
            tagging_name = _focus.getItemTaggingName(tagging)
        else :
            for word in keywords :
                if word in CRF_TAGGING.keys() :
                    clause_type = CRF_TAGGING[word]
                    if (clause_type == tagging) :
                        tagging_name = word
                        break
    
    if not tagging_name :
        tagging_name = NO_NAME

    return tagging_name
        

def get_character_type(ch):
    if ch in util.digital_char :
        return CRF_CHAR_D
    elif ch in util.alpha_char or ch in util.alpha_char1 :
        return CRF_CHAR_L
    elif ch in util.double_p :
        return CRF_CHAR_P
    elif ch in util.simple_p :
        return CRF_CHAR_S
    else :
        return CRF_CHAR_W

       
def get_extract_data(name, results):
    for xname, xdata in results.items() :
        if xname == name:
            if xdata.full_term :
                return None
            else :
                return xdata
    return None
    
    
def add_clause_string(clause_name, sentence, results):

    if len(clause_name) > 0 and clause_name != NO_NAME and len(sentence) > 0 :
        xdata = get_extract_data(clause_name, results)
        if xdata :
            xdata.add_value(sentence, 1)

