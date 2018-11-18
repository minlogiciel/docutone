# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

import os

from docutone.utils import variables, docutonejson

from docutone import working

def locate_file(filename, tp="TEXT"):

    root = variables.PROJECT_ROOT.replace("\\", "/")
    
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
        root = os.path.dirname(filename)
        path = os.path.join(root, variables.OUTPUT_DIR);
        if not os.path.exists(path) :
            os.mkdir(path)
        fname = os.path.join(path, name)

    if not fname.endswith(".txt") :
        fname += ".txt"
    
    return fname


def convert_file(filename, tojson = False) :
    from docutone.utils.convert import Convert
    o_file = locate_file(filename)
    if not os.path.exists(o_file) :
        conv = Convert()
        conv.file_to_text(filename, o_file)
    if tojson :
        result = {}
        result["inputfile"] = filename
        result["outputfile"] = o_file
        docutonejson.print_json(result)
    return o_file



def dtn_locate_file(fname, ftype="data"):

    path = os.path.join(variables.BASE_DIR, ftype)
    if not os.path.exists(path) :
        os.mkdir(path)
    filename = os.path.join(path, fname);
    if os.path.exists(filename) :
        return filename
        
    path = os.path.join(working.PYTHON_SRC, ftype);
    if not os.path.exists(path) :
        os.mkdir(path)
    filename = os.path.join(path, fname);
    if os.path.exists(filename) :
        return filename;
    

    return None
