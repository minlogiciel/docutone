# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import json
import sys, io

from docutone.utils import variables
from docutone.utils import docufile

'''
转json
'''

# convert variable to json string
def to_json_string(var, indent=0):
    if indent > 1:
        return json.dumps(var, indent=4, separators=(',', ': '), ensure_ascii=False)
    else :
        return json.dumps(var, ensure_ascii=False)

# load json from file
def load_json(filename):
    f = docufile.openfile(filename)
    s = docufile.readfile(f)
    v = json.loads(s)
    return v

# save json string to file
def save_json_format(var, filename, indent=4):

    s = to_json_string(var, indent=indent)
    f = docufile.openfile(filename, mode='w')
    docufile.writefile(f, s)
    docufile.closefile(f)
    

def print_json(result) :
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding = 'utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding = 'utf-8')
    print("<JSON> "+to_json_string(result, indent=4)+" </JSON>")


# example    
def test_get_json():

    fname = variables.get_data_file_name("keywords.json", "json")
    v = load_json(fname)
    s = to_json_string(v)
    return s

   
    


