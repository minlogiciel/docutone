# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import sys,os,codecs


sys.path.append("../")

from docutone.utils import variables, util
from docutone.utils.terms import Terms
from docutone.core.document import LawDocument

'''
读文件夹
'''
class Folder(object):   
     
    FOLDER_STRUCTURE_NAME = "training_file_structure.dat"
    CORPUS_FILE_NAME = "training_document"
    
    DOCUMEN_START_TAG = "<![["
    DOCUMEN_END_TAG = "]]>"
    DOCUMEN_SEP = "||"
    FILE_SIZE = 10000000
    
    
    def __init__(self):
        
        self.law_doc =  LawDocument()


        self.file_index = 1
        self.folder_structure = {}
        self.folder_order = []
        
        self.corpus_document = []
        
        instance = Terms()
        self.categories = instance.get_all_term_items() 
        
        pass
    
        
                        

    # write file folder structure
    def write(self, fpath, fname=FOLDER_STRUCTURE_NAME):       
 
        fpath = os.path.join(fpath, self.TRAININ_DATA)
        if not os.path.exists(fpath) :
            os.mkdir(fpath)
        
        fname = os.path.join(fpath, fname)
        if not os.path.exists(fname) :        
            ofile = codecs.open(fname, 'w', 'utf-8')

            for name in self.folder_order :
                v = self.folder_structure.get(name)
                if v[1] > 0 :
                    if v[0] != None :
                        ofile.write("%s=%d=%s\n" % (name, v[1], v[0]))
                    else :
                        ofile.write("%s=%d\n" % (name, v[1]))
                else :
                    ofile.write("%s\n" % (name))
                
            ofile.close()

        else :
            '''
            for name in self.folder_order :
                v = self.folder_structure.get(name)
                if v[1] > 0:
                    if v[0] != None :
                        print("%s=%d=%s" % (name, v[1], v[0]))
                    else :
                        print("%s=%d" % (name, v[1]))
                    if len(v) > 2 :
                        for nn in v[2] :
                            print("\t\t%s" % (nn))
                else :
                    print(name)
            '''
            pass

    # load training file folder structure  
    def load_folder_structure(self, path, fname=FOLDER_STRUCTURE_NAME) :
        
        self.folder_structure = {}
        self.folder_order = []
        
        
        filename = os.path.join(path, fname)
        if not os.path.exists(filename) :  
            print(filename)
            path = os.path.join(path, self.TRAININ_DATA)
            filename = os.path.join(path, fname)
        
        if os.path.exists(filename) :  
            
            file = codecs.open(filename, 'r', 'utf-8')
            lists = file.read().split("\n")
            file.close()
         
            for line in lists :
                line = line.strip()
                if len(line) > 0 :
                    if '=' in line :
                        tab = line.split('=')
                        fname = tab[0].strip()
                        level = int(tab[1].strip())
                        if len(tab) > 2 :
                            label = tab[2].strip()
                        else :
                            label = None
                         
                    else :
                        fname = line
                        level = 0
                        label = None
                    
                    self.folder_order.append(fname)
                    self.folder_structure[fname] = [label,  level]
        return self.folder_structure;
    
    def get_categorie_label(self, name, level) : 
        if level < 3 :
            for key in self.categories :
                if key in name :
                    return name
            
            if level == 1:
                return None
            else :
                return name
        return None
        
    # write file folder structure
    def add_folder_structure(self, fpath, offset, parent):
        listf = []
        for name in os.listdir(fpath):
            if variables.noloaddir(name) :
                continue
            path = os.path.join(fpath, name)
            if os.path.isdir(path):
                
                label = self.get_categorie_label(name, offset)
                if parent != None and label !=None:
                    label = parent + ";" + name
                
                                                 
                self.folder_structure[name] = [label, offset]
                self.folder_order.append(name)

                ll = self.add_folder_structure(path, (offset+1), label)
                if len(ll) > 0 :
                    self.folder_structure[name].append(ll)
                    
            elif name.endswith('.txt') :
                listf.append([name, self.file_index])
                self.file_index += 1
        
        
        return listf
            
                
                
            
                 
    
    # create a file folder for training      
    def create_folder_structure(self, fpath) :    
        
        self.folder_structure = {}
        self.folder_order = []
        self.file_index = 1
        
        self.add_folder_structure(fpath, 1, None)

        return  self.folder_order, self.folder_structure 
         
     
    def write_restore_corpus_file(self, sentences):

        path = sentences[0][4]
        pp = path.find('doc')
        fpath = path[pp:]
        path = os.path.join(variables.HOME_DIR, "init/restore")
        if not os.path.exists(path) :  
            os.mkdir(path) 
        path = os.path.join(path, fpath)
        if not os.path.exists(path) :  
            os.makedirs(path) 
       
                            
        filename = os.path.join(path, sentences[0][0])
        
        ofile = codecs.open(filename, 'w', 'utf-8')
        ss = ''
        for s in sentences[1:] :
            ss += s;
            # ss += s.replace('\n', '').replace('\r', '');
        ofile.write(ss)
        ofile.close()
   

    # load training file folder structure  
    def restore_corpus_file(self, filename) :
                
        sentences = None
        file = codecs.open(filename, 'r', 'utf-8')
        for s in file :
            if s.startswith(self.DOCUMEN_START_TAG) :
                            
                if sentences != None and len(sentences) > 0 :
                    self.write_restore_corpus_file(sentences)
                                
                                
                sentences = []
                start_p = len(self.DOCUMEN_START_TAG)
                end_p = -len(self.DOCUMEN_END_TAG)-1
                ss = s[start_p:end_p]
                           
                            
                tab = ss.split(self.DOCUMEN_SEP)
                sentences.append(tab)
                            
            elif sentences != None :
                if (len(s.strip()) > 0) :
                    sentences.append(s)
        
        # last document        
        if sentences != None and len(sentences) > 0 :
            self.write_restore_corpus_file(sentences)
     
        file.close()
            
    
    # load training file folder structure  
    def load_corpus_file(self, filename) :
                
        docs = []
        sentences = None
        file = codecs.open(filename, 'r', 'utf-8')
        for s in file :
            s_norm = util.normalize_sentence(s)
            if len(s_norm) > 0 : 
                if s_norm.startswith(self.DOCUMEN_START_TAG) :
                            
                    if sentences != None and len(sentences) > 0 :
                        docs.append(sentences)
                                
                    sentences = []
                    start_p = len(self.DOCUMEN_START_TAG)
                    end_p = -len(self.DOCUMEN_END_TAG)-1
                    ss = s[start_p:end_p]
                           
                            
                    tab = ss.split(self.DOCUMEN_SEP)
                    sentences.append(tab)
                            
                elif sentences != None :
                    sentences.append(s_norm)
        
        # last document        
        if sentences != None and len(sentences) > 0 :
            docs.append(sentences)
     
        file.close()
            
        return docs


    # load training file folder structure  
    def load_corpus_document(self, path, fname=CORPUS_FILE_NAME, restore = False) :
        
        docs = []
        path = os.path.join(path, variables.TRAINING_DATA)
        for fname in sorted(os.listdir(path)):
            if (self.CORPUS_FILE_NAME in fname) :
                filename = os.path.join(path, fname)
                if restore :
                    self.restore_corpus_file(filename)
                else :
                    doc = self.load_corpus_file(filename)
                    docs.append(doc)
            
        return docs


 
 
    def write_corpus(self, fpath, fname=CORPUS_FILE_NAME, created=True):
                                    
        fpath = os.path.join(fpath, self.TRAININ_DATA)
        if not os.path.exists(fpath) :
            os.mkdir(fpath)
            
        filename = os.path.join(fpath, fname+".dat")
        
        n = 1
        if created or not os.path.exists(filename) :
            docsize = 0
            ofile = codecs.open(filename, 'w', 'utf-8')
            for doc in self.corpus_document :
                docsize +=len(doc)
                ofile.write("%s\n" % (doc))
                if docsize > self.FILE_SIZE :
                    ofile.close()
                    
                    ff = fname+str(n)+".dat"
                    
                    # create new file
                    filename = os.path.join(fpath, ff)
                    ofile = codecs.open(filename, 'w', 'utf-8')
                    n += 1
                    docsize = 0

            ofile.close()
        else :
            pass
                
        
    def load_corpus_text_file(self, path, fname, name, level, encoding='utf-8') :
        
        if fname.endswith(".txt") :
            
            if name in self.folder_structure.items() :
                categorie = self.folder_structure[name]
            else :
                categorie = [name, level]

            
            fpath = os.path.join(path, fname)   
            f = codecs.open(fpath, 'r', encoding, 'ignore')
            sentences = [s for s in f if len(s.strip()) > 0]
            #norm_sentences = [util.normalize_sentence(s) for s in sentences]
            f.close()
                
            text = self.DOCUMEN_START_TAG + fname+self.DOCUMEN_SEP+name + self.DOCUMEN_SEP
            text += categorie[0] + self.DOCUMEN_SEP 
            text += str(categorie[1]) + self.DOCUMEN_SEP 
            text += path + self.DOCUMEN_END_TAG+"\n" 
                
            for s in sentences :
                text += s + "\n"
                    
            self.corpus_document.append(text + "\n")
        else :
            print(fname)
        
    def load_corpus_directories(self, path, name, level, encoding='utf-8') :
    
        for fname in sorted(os.listdir(path)):
            fpath = os.path.join(path, fname)
            if os.path.isdir(fpath):
                if variables.noloaddir(fname) :
                    pass
                else :
                    self.load_corpus_directories(fpath, fname, (level+1))
            
            else :
                self.load_corpus_text_file(path, fname, name, level)
    
     
   
    
    
    def create_corpus_documents(self, text_path) :
            
        self.folder_structure = self.load_folder_structure(text_path);
        
        for name in sorted(os.listdir(text_path)):
            path = os.path.join(text_path, name)
            if os.path.isdir(path) :
                if variables.noloaddir(name):
                    pass
                else :
                    self.load_corpus_directories(path, name, 1) 
            else :
                self.load_corpus_text_file(text_path, name, name, 1)
                       
    
    def update_corpus_text_file(self, ifile, ofile, name):
                                    
        if name.endswith(".txt") :
            infile = codecs.open(ifile, 'r', 'utf-8', 'ignore')
            sentences = [s for s in infile if len(s.strip()) > 0]
            infile.close()
            
            
            outfile = codecs.open(ofile, 'w', 'utf-8')
            for s in sentences :
                s = s.replace('\n', '').replace('\r', '' )
                outfile.write("%s" % (s))
            
            outfile.close()
        
                
   
    def update_corpus_folder(self, path, outfile, name) :
        
        if not variables.noloaddir(path) : 
            if not os.path.exists(outfile) :
                os.mkdir(outfile)
            for fname in sorted(os.listdir(path)):
                ipath = os.path.join(path, fname)
                ofile = os.path.join(outfile, fname);
                if os.path.isdir(ipath):
                    self.update_corpus_folder(ipath, ofile, fname)
                else :
                    self.update_corpus_text_file(ipath, ofile, fname)
     
                     
    def update_corpus(self, inpath, outpath) :
    
        for fname in sorted(os.listdir(inpath)):
            ipath = os.path.join(inpath, fname)
            ofile = os.path.join(outpath, fname);
            
            if os.path.isdir(fpath):
                self.update_corpus_folder(ipath, ofile, fname)
            
            else :
                self.update_corpus_text_file(ipath, ofile, fname)
     
                     
           

if __name__ == "__main__":
    
    test_n = 5
    fpath = variables.CORPUS_DIR
    fpath = variables.HOME_DIR + "/Junhe"
    fpath = "/doc/文本库"
    
    fpath = variables.CORPUS_DIR + "/TEXT/合同、协议"

    folder = Folder()   
    
    if test_n == 1 :
        folder.create_folder_structure(fpath)
        folder.write(fpath);
    
    if test_n == 2 :
        folder.create_corpus_documents(fpath);
        folder.write_corpus(fpath)
    
    if test_n == 3  :
        folder.load_folder_structure(fpath);
    if test_n == 4  :
        folder.load_corpus_document(fpath, restore = True)
    
    if test_n == 5 :
        
        opath = "D:\\WORK\\docutone\\working\\init/TEXT"
        folder.update_corpus(fpath, opath);
   
    print("===== end ==== ")
    
    
