# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

import sys, codecs

sys.path.append("../")



def openfile(filename, mode='r', encoding='utf-8'):
    return codecs.open(filename, mode, encoding)

def readfile(file):
    return file.read()

def writefile(file, string):
    file.write(string)
    
def closefile(file):
    file.close()


