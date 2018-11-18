#-*- encoding:utf-8 -*-
from __future__ import (unicode_literals)

import os, codecs, sys

sys.path.append("../")

from docutone.utils import docutonejson, docutonelocate



TERM_ITEM_TYPE = "TERM"
TERM_GROUP_TYPE = "GROUP"
CONTENTS_NAME = "contents"
ATTR_NAME = "name"
ATTR_TYPE = "type"
ATTR_RELATED = "related"
ATTR_TAGGING = "tagging"
ATTR_LEVEL = "level"


class FocusElement(object) :
    
    
    def __init__(self, name, tagging=None, related=None, level=1, ftype="string"):
        
        self.name = name
        self.tagging = tagging
        self.ftype = ftype
        self.level = level
        self.related = related
    
    def get_name(self):
        return self.name
    
    def set_name(self, name):
        self.name= name

    def get_tagging(self):
        if self.tagging :
            return '-' + self.tagging
        else :
            return ''

    def set_tagging(self, tagging):
        self.tagging = tagging
        
    def get_related(self):
        return self.related
    
    def set_related(self, related):
        self.related = related
    
    def get_type(self):
        return self.ftype
    
    def set_type(self, ftype):
        self.ftype= ftype
        
    def get_level(self):
        return self.level
    
    def set_level(self, level):
        self.level= level


class FocusItem(object) :
    
    def __init__(self, name):
        if '=' in name :
            self.name, self.categorie = name.split('=')
        else :
            self.name = name
            self.categorie = name
        self.name = self.name.strip()
        self.categorie = self.categorie.strip()
        
        self.children = [];
    
    
    
    def getItem(self, name) :
        for elem in self.children :
            if elem.name == name :
                return elem
        return None
    
    def getItemTagging(self, name) :
        for elem in self.children :
            if elem.name == name :
                return elem.get_tagging()
        return ''
    
    def getItemTaggingName(self, tagging) :
        for elem in self.children :
            if elem.tagging and elem.tagging == tagging :
                return elem.name
        return ''

    def addItem(self, elem) :
        self.children.append(elem)
        
    def delItem(self, elem) :
        self.children.remove(elem)
    
    def get_type(self):
        return TERM_ITEM_TYPE
    
    def get_item_names(self):
        names = []
        for elem in self.children :
            names.append(elem.name)
        return names
            
        
        
        
class FocusGroup(object) :
    
    def __init__(self, name):
        if '=' in name :
            self.name, self.categorie = name.split('=')
        else :
            self.name = name
            self.categorie = name

        self.children = [];
    
    def addItem(self, item) :
        self.children.append(item)
        
    def delItem(self, item) :
        self.children.remove(item)

    def get_type(self):
        return TERM_GROUP_TYPE
    
    
class Focus (object) :
    
    FOCUS_POINT_NAME = 'focus_points'
    
    def __init__(self):
        pass
        
    
    
    def _get_filename(self) : 
        fname = self.FOCUS_POINT_NAME + '.json'
        return docutonelocate.dtn_locate_file(fname)

    
    def parse_group_elements(self, lists, fitems):

        elems = lists[CONTENTS_NAME]
        for elem in elems :
            name = elem[ATTR_NAME]
            if ATTR_TAGGING in elem.keys() :
                tagging  = elem[ATTR_TAGGING]
            else :
                tagging = ''
            if ATTR_RELATED in elem.keys() :
                related  = elem[ATTR_RELATED]
            else :
                related = None
            if ATTR_LEVEL in elem.keys() :
                level  = int(elem[ATTR_LEVEL])
            else :
                level = 0
            ftype = elem[ATTR_TYPE]
            elem = FocusElement(name, tagging, related, level, ftype=ftype)
            fitems.addItem(elem)

    def parse_group(self, groups, fgroup):

        contents = groups[CONTENTS_NAME]
        for lists in contents :
            ftype = lists[ATTR_TYPE]
            fname = lists[ATTR_NAME]
            if ftype == TERM_GROUP_TYPE :
                fg = FocusGroup(fname)
                self.parse_group(lists, fg)
                fgroup.addItem(fg)
            else :
                fitems = FocusItem(fname)
                self.parse_group_elements(lists, fitems)
                fgroup.addItem(fitems)

    def load(self):
        self.focus_points = []
        v = docutonejson.load_json(self._get_filename())
        for groups in v :
            gname = groups[ATTR_NAME]
            fgroup = FocusGroup(gname)
            self.parse_group(groups, fgroup)
            
            self.focus_points.append(fgroup)
           
    
    def _addname(self, f, name, value=False):
        f.write("\"" + name + "\": ")
        if value :
            f.write("\"" + value + "\"")
    
    def _addint(self, f, name, value):
        if value :
            f.write("\"" + name + "\": " + value)
            
    def _addtab(self, f, n):
        i = 0
        while i < n :
            f.write("\t")
            i +=1
       
    def _write_focus_item(self, item, f, islast):
        
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
            if elem.tagging :
                self._addname(f, ATTR_TAGGING, str(elem.tagging))
                f.write(", ")
            if elem.related :
                self._addname(f, ATTR_RELATED, str(elem.related))
                f.write(", ")
            if elem.level :
                self._addint(f, ATTR_LEVEL, str(elem.level))
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


    def _write_focus_group(self, group, f, islast):
        
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
        for i, item in enumerate(group.children) :
            if type(item) is FocusItem :
                self._write_focus_item(item, f, (i == nb-1))
            else :
                self._write_focus_group(item, f, (i == nb-1))
        self.tab_level -= 1
        self._addtab(f, self.tab_level)
        f.write("]\n" )
        self.tab_level -= 1
        self._addtab(f, self.tab_level)
        if islast :
            f.write("}\n" )
        else :
            f.write("},\n" )


    def save(self):
        self.tab_level = 1
        fname = self._get_filename()
        f = codecs.open(fname, 'w', 'utf-8')

        f.write("[\n")
        nb = len(self.focus_points)
        for i, group in enumerate(self.focus_points) :
            self._write_focus_group(group, f, (i == nb-1))
            
        f.write("]\n" )     
        f.close()

 
    def get_template_group(self, gname) :
        for group in self.focus_points :
            if group.name == gname :
                return group
            for item in group.children :
                if item.get_type() == TERM_GROUP_TYPE :
                    g = self.get_tempalte_group(gname)
                    if g != None :
                        return g
        return None
    
    def get_template_group_item(self, group, name) :
        for item in group.children :
            if item.name == name :
                return item
            if item.get_type() == TERM_GROUP_TYPE :
                elem = self.get_template_group_item(item, name) 
                if elem :
                    return elem
        return None


    def get_template_item(self, name):
        for group in self.focus_points :
            item = self.get_template_group_item(group, name)
            if item :
                return item
        return None
    
    
    def get_template_item_element(self, item, name):
        for elem in item.children :
            if (elem.name == name) :
                return elem

        return None
                
            
        
    def add_item_element(self, itemname, elem) :
        item = self.get_template_item(itemname)
        if item :
            e = self.get_template_item_element(item, elem.name)
            if e :
                item.delItem(e)
            
            item.addItem(elem)
    
    
    
    def add_group_item(self, gname, item) :
        group = self.get_template_group(gname)
        if group :
            item = self.get_template_group_item(group, item.name)
            if item :
                group.delItem(item)

            group.addItem(item)
                

   
    def test(self):
        item = self.get_template_item('转让协议')
        if item :
            for elem in item.children :
                if  elem.related :
                    print (elem.name +"\t" + elem.tagging +"\t" + elem.related +"\t" + elem.ftype)
                else :
                    print (elem.name +"\t" + elem.tagging  +"\t" + elem.ftype)
    
    
if __name__ == "__main__":
    
    
    focus = Focus()
    focus.load()
    focus.test()

    focus.save()
    print("end")

    
    