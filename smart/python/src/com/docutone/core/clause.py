# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

import sys, codecs, os, glob


sys.path.append("../")


from docutone.utils import util, variables, dtn_sentence

from docutone.core import document as dt
from docutone.core.document import Section
from docutone.logging import dtn_logging as dtn_logger
from docutone import working


class Clause(object):
    
    MAX_FILE_SIZE = 50000
   
    def __init__(self):
        
        self.sections = []



    
    ''' get clause file name for adding new clause 
        if file size > MAX_FILE_SIZE, create new file 
    '''
    def _get_clause_file_name(self, clausetype):
        root = variables.get_template_path();
        path = os.path.join(root, "TEXT")
        path = os.path.join(path, clausetype)
        filename = None
        basename = None
        if not os.path.exists(path) :
            os.mkdir(path)
        else :
            fpath = os.path.join(path, '*.txt')
            files = sorted(glob.iglob(fpath), key=os.path.getctime, reverse=True)
            if (len(files) > 0) :
                filename = files[0]
                basename = os.path.basename(filename)

        
        if basename :
            if basename[0].isdigit() :
                fsize = os.path.getsize(filename) 
                #fsize = os.stat(filename).st_size)
                if fsize > self.MAX_FILE_SIZE :
                    filename = None
            else :
                filename = None
        
        if filename == None :
            basename = util.get_uid() +".txt"
            filename = os.path.join(path, basename)
        

        return filename
        
    def _create_clauses(self, filename):
            
        norm_sentences = util.get_file_sentences(filename)

        i = 0
        num = 1
        total = len(norm_sentences)
        while i < total :
            s = norm_sentences[i]
            i += 1
            if dt.is_clause_start(s) :
                title = s[2:]
                section = Section("", num, title, 1)
                num += 1
                while i < total : 
                    s = norm_sentences[i]
                    if dt.is_clause_start(s) :
                        self.sections.append(section)
                        break
                    elif dt.is_clause_end(s) :
                        self.sections.append(section)
                        i += 1
                        break
                    
                    section.addSentence(s)
                    i += 1
                    if i == total :
                        self.sections.append(section)


    def create_clauses(self, filename):
            
        self.sections = []
        self._create_clauses(filename)
    
    
    def add_clause(self, clausetype, name, value):
        
        filename = self._get_clause_file_name(clausetype)
        if os.path.exists(filename) :
            f = codecs.open(filename, 'a+', 'utf-8')
        else :
            f = codecs.open(filename, 'w', 'utf-8')
       
        dtn_logger.logger_info("Clause", "add clause %s : %s" %(clausetype, name))
        
        f.write("[[" + name + "\n")
        f.write(value + "\n]]\n\n")

        f.close()
    
    
    def _create_folder_clauses(self, fpath):
        for name in os.listdir(fpath):
            path = os.path.join(fpath, name)           
            if os.path.isdir(path) :
                if variables.noloaddir(name) :
                    continue
                self._create_folder_clauses(path)
            elif name.endswith(".txt") :
                self._create_clauses(path)

    def loading_clauses(self, fpath):
        self.sections = []
        for name in os.listdir(fpath):
            path = os.path.join(fpath, name)           
            if os.path.isdir(path) :
                if variables.noloaddir(name) :
                    continue
                self._create_folder_clauses(path)
            elif name.endswith(".txt") :
                self._create_clauses(path)



    def test_clauses_direcotry(self, fpath, ftype):
        for name in os.listdir(fpath):
            path = os.path.join(fpath, name)           
            if os.path.isdir(path) and name != variables.DATA_DIR and name != variables.TEMP_DIR :
                self.test_clauses_direcotry(path)
            elif name.endswith(".txt") :
                print("========"+name +  "===========");
                self.create_clauses(path)
                self.debug(ftype)
                
                
                
    def debug(self, ftype):
        item = dtn_sentence.focus.get_template_item(ftype)
   
        titles = [section.title for section in self.sections]
        '''for elem in item.children :
            if (elem.name not in titles) :
                print(elem.name  + " MISSING ")'''
        
        names = item.get_item_names()
        for name in titles :
            if name not in names :
                print(name  + " ERROR ")
            #self.assertTrue(elem.name in titles)
                        
                    
                
if __name__ == '__main__':
    
        
    ''' see test_clause '''
    TEMPLATE_PATH = working.WORKING_DIR + "/home/data/terms/Template/TEXT/"
    ftype = '劳动合同'
    path = TEMPLATE_PATH + ftype
    clause = Clause()

    clause.test_clauses_direcotry(path, ftype)
    print('--- end ----')

