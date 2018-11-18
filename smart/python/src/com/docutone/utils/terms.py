#-*- encoding:utf-8 -*-
from __future__ import (unicode_literals)

import os, codecs, sys

sys.path.append("../")

from docutone.utils import variables, docutonejson
from docutone import working, config

'''
python 读取条款
'''


TERM_ITEM_TYPE = "TERM"
TERM_GROUP_TYPE = "GROUP"
CONTENTS_NAME = "contents"
ATTR_NAME = "name"
ATTR_TYPE = "type"


class ElementItem(object) :
    
    
    def __init__(self, name, type="string", level=1, selected=True, indice=1):
        
        self.name = name
        self.type = type
        self.level = level
        self.level = selected
        self.indice = indice
        


class TermItem(object) :
    
    def __init__(self, name):
        if '=' in name :
            self.name, self.categorie = name.split('=')
        else :
            self.name = name
            self.categorie = name
        self.name = self.name.strip()
        self.categorie = self.categorie.strip()
        
        self.children = [];
    
    
    
    def addItem(self, elem) :
        self.children.append(elem)
        
        
        
        
class TermGroup(object) :
    
    def __init__(self, name):
        if '=' in name :
            self.name, self.categorie = name.split('=')
        else :
            self.name = name
            self.categorie = name

        self.children = [];
    
    def addItem(self, elem) :
        self.children.append(elem)

def get_filename(fname) :
    path = os.path.join(variables.BASE_DIR, 'data')
    if not os.path.exists(path) :
        os.mkdir(path)
    filename = os.path.join(path, fname);
    if os.path.exists(filename) :
        return filename
        
    path = os.path.join(working.PYTHON_SRC, 'data');
    filename = os.path.join(path, fname);
    return filename



class Terms (object) :
    
    _LEGALTERM_TYPE_NAME = 'document_categorie'
    
    def __init__(self, is_json=True):
        self.is_json = is_json
        self.term_types = self.load()
        
    
    
    def _get_filename(self, is_json=False) : 
        if is_json :
            fname = self._LEGALTERM_TYPE_NAME + '.json'
        else :
            fname = self._LEGALTERM_TYPE_NAME + '.txt'
        return get_filename(fname);
    
    
    
    def _load_json_term(self, term):

        termitem = TermItem(term[ATTR_NAME])
        elems = term[CONTENTS_NAME]
        for elem in elems :
            elem = ElementItem(elem[ATTR_NAME], type=elem[ATTR_TYPE], indice=elem['indice'])
            termitem.addItem(elem)

        return  termitem

    def _load_json_group(self, tgroup):

        termgroup = TermGroup(tgroup[ATTR_NAME])
        
        term_lists = tgroup[CONTENTS_NAME]
        for term in term_lists :
            if term[ATTR_TYPE] == TERM_GROUP_TYPE :
                termitem = self._load_json_group(term)
            else :
                termitem = self._load_json_term (term)
            termgroup.addItem(termitem)
        return termgroup
    
    
    def _load_json(self):
        term_types = []
        v = docutonejson.load_json(self._get_filename(is_json=True))
        for term_groups in v :
            termgroups = self._load_json_group(term_groups)
            term_types.append(termgroups)
           
        return term_types
    
    
    
    def _load_text(self) :
   
        term_types = []
        termitems = None
        termgroups = None
        subgroup = None
        f = codecs.open(self._get_filename(is_json=False), 'r', 'utf-8')
        for line in f :
            line = line.strip() 
            if len(line) > 0:
                if line[0] == '#' :
                    continue
                
                elif line[0] == '<' :
                    name = line[1:-1].strip()
                    subgroup = TermGroup(name)
                    termgroups.addItem(subgroup)
                    
                elif line[0] == '>' :
                    subgroup = None
                        
                elif line[0] == '[' :
                    name = line[1:-1].strip()
                    termgroups = TermGroup(name)
                    term_types.append(termgroups)

                elif line[0].isdigit() :
                    if ' ' in line :
                        nid, name = line.split(' ', 1)
                        nid = int(nid)
                        name = name.strip()
                        if nid == 0 :
                            # term start 
                            termitems = TermItem(name)
                            if subgroup :
                                subgroup.addItem(termitems)
                            elif termgroups :
                                termgroups.addItem(termitems)
                        else :
                            elem = ElementItem(name, indice=nid)
                            termitems.addItem(elem)
                else :
                    nid = len(termitems.children) + 1
                    elem = ElementItem(line, indice=nid)
                    termitems.addItem(elem)         
        f.close()
        
        return term_types
    
    
    def load(self) :
        if self.is_json :
            return self._load_json()
        else :
            return self._load_text()
    
    def _addname(self, f, name, value=False):
        f.write("\"" + name + "\": ")
        if value :
            f.write("\"" + value + "\"")
            
    def _addtab(self, f, n):
        i = 0
        while i < n :
            f.write("\t")
            i +=1
       
    def _write_term_item(self, item, f, islast):
        
        nb = len(item.children)
        
        self._addtab(f, self.tab_level)
        f.write("{\n")
        self.tab_level += 1
        self._addtab(f, self.tab_level)
        self._addname(f, ATTR_NAME, item.name)
        f.write(",\n" )
        self._addtab(f, self.tab_level)
        self._addname(f, ATTR_TYPE, TERM_ITEM_TYPE)
        f.write(",\n" )
        self._addtab(f, self.tab_level)
        self._addname(f, CONTENTS_NAME)
        f.write("[\n" )
        self.tab_level += 1
        for i in range(nb) :
            elem = item.children[i]
            self._addtab(f, self.tab_level)
            f.write("{")
            self._addname(f, ATTR_NAME, elem.name)
            f.write(", ")
            if '日期' in elem.name :
                self._addname(f, ATTR_TYPE, "date")
            elif '地址' in elem.name :
                self._addname(f, ATTR_TYPE, "address")
            elif '代表人' in elem.name :
                self._addname(f, ATTR_TYPE, "named")
            elif '编号' in elem.name :
                self._addname(f, ATTR_TYPE, "number")
            else :
                self._addname(f, ATTR_TYPE, "string")
            f.write(", ")
            self._addname(f, "selected", "true")
            f.write(", ")
            self._addname(f, "level", "1")
            f.write(", ")       
            self._addname(f, "indice", str(elem.indice))
            f.write("}")
            if i < nb - 1 :
                f.write(",")
            f.write("\n")
        self.tab_level -= 1
        self._addtab(f, self.tab_level)
        f.write("]\n" )
        
        self.tab_level -= 1
        self._addtab(f, self.tab_level)
        f.write("}" )
        if islast == False:
            f.write("," )
        f.write("\n" )


    def _write_term_group(self, group, f, islast):
        
        nb = len(group.children)
        self._addtab(f, self.tab_level)
        self.tab_level += 1
        f.write("{\n" )
        self._addtab(f, self.tab_level)
        self._addname(f, ATTR_NAME, group.name)
        f.write(",\n" )
        self._addtab(f, self.tab_level)
        self._addname(f, ATTR_TYPE, TERM_GROUP_TYPE)
        f.write(",\n" )
        self._addtab(f, self.tab_level)
        self._addname(f, CONTENTS_NAME)
        f.write("[\n" )
        self.tab_level += 1
        for i in range(nb) :
            item = group.children[i]
            if type(item) is TermItem :
                self._write_term_item(item, f, (i == nb-1))
            else :
                self._write_term_group(item, f, (i == nb-1))
        self.tab_level -= 1
        self._addtab(f, self.tab_level)
        f.write("]\n" )
        self.tab_level -= 1
        self._addtab(f, self.tab_level)
        if islast :
            f.write("}\n" )
        else :
            f.write("},\n" )


    def _write_json(self):
        self.tab_level = 1
        fname = self._get_filename(is_json=True)
        f = codecs.open(fname, 'w', 'utf-8')

        f.write("[\n")
        nb = len(self.term_types)
        for i in range(nb) :
            group = self.term_types[i] 
            self._write_term_group(group, f, (i == nb-1))
            
        f.write("]\n" )     
        f.close()

    def write(self, is_json=True):
        
        if is_json :
            self._write_json()
 
 
    def get_term_group(self, name) :
        for group in self.term_type :
            if group.name == name or group.type == name :
                return group
        return None
    
    def get_term_group_item(self, group, name) :
        for item in group.children :
            if item.name == name or item.type == name :
                return item
        return None

    def add_group_term_items(self, group, inst) :

        inst.append(group.categorie)
        for item in group.children :
            if (type(item) is TermGroup) :
                self.add_group_term_items(item, inst)
            else :
                inst.append(item.categorie)
        return inst
    
    def get_all_term_items(self) :
        inst = []
        for group in self.term_types :
            self.add_group_term_items(group, inst)
            
        return inst
    
    
    
    def get_document_categorie_from_group(self, group, doctype) :
        cat = []
        for item in group.children :
            if (type(item) is TermGroup) :
                cat = self.get_document_categorie_from_group(item, doctype)
                if len(cat) > 0 :
                    return cat
            else :
                if item.name == doctype or item.categorie == doctype :
                    for elem in item.children :
                        cat.append(elem.name)
        return cat

    def get_document_categorie(self, doctype) :
        for group in self.term_types :
            cat = self.get_document_categorie_from_group(group, doctype)
            if len(cat) > 0 :
                return cat
        return []

               

    def debug(self):
        print ("{")
        for group in self.term_types :
            print ("\t\"" + group.name + "\" : {" )
            for item in group.children :
                print ("\t\t\"" + item.name + "\" : [" )
                for elem in item.children :
                    print ("\t\t\t\"" + elem.name +"\"")
                print ("\t\t]," )
            print ("\t}," )
        print ("}" )
    
     
    
if __name__ == "__main__":
    
    
    terms = Terms()
   
    terms.write()
    '''
    terms.load(True)
    terms.write()
    '''
    terms.debug()
    
    