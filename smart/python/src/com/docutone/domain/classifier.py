# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import sys,os, logging, io

logger = logging.getLogger(__name__)


from gensim.models import doc2vec

sys.path.append("../")

from docutone.core.datasets import Datasets
from docutone.utils.base import File
from docutone.utils import variables, docutonejson
from docutone.utils.convert import Convert

'''
文件分类
'''
class Classifier(object):   
     
    def __init__(self, filename=None, ouputfile=None):
        
        self.datasets = Datasets()
        self._ftypes = {}
        self._categorie = {}
        self._debug = 1
        self._outputpath = None
        if filename != None :
            self.classification(filename, ouputfile);
        pass

    def get_file_types(self) :
        return self._ftypes
    
    def get_file_categories(self) :
        return self._categorie
    
    
    def classify_doc(self, model, target_names, labelSet, filelabel, classifylabel, filename)  :
        doctype = 'Unknown'
        f_simu = 0.0
        
        f = File(filename, self._outputpath, verbose=0)
        if f.get_file_type() in self._ftypes.keys() :
            self._ftypes[f.get_file_type()] += 1
        else :
            self._ftypes[f.get_file_type()] = 1
            
        doc_fname = f.get_file_name()
        
        docs = f.get_document_words()
        
        if docs :
            docvec = model.infer_vector(doc_words=docs)
            sims = model.docvecs.most_similar(positive=[docvec], topn=5)
            #sims = model.docvecs.most_similar(doc_id, topn=model.docvecs.count) 
            if f.categorie : 
                self._categorie[doc_fname] = [f.categorie, 1]
            else :
                res = None
                for i in range(5) :
                    n_doc = int(sims[i][0])
                    f_simu = sims[i][1]
                    #fname = filelabel[n_doc]
                    doctype = classifylabel[n_doc]
                    if (doctype == "转让协议") or True :
                        res = doctype
                        break
                    elif res == None :
                        res = doctype
               
                #doctype = target_names[labelSet[n_doc]-1]
                    
                self._categorie[doc_fname] = [res, f_simu]

        
    def set_output_dir(self, path) :
        path = os.path.dirname(path)
        self._outputpath = os.path.join(path, variables.OUTPUT_DIR)
        if not os.path.exists(self._outputpath) :
            os.mkdir(self._outputpath)
        return self._outputpath

     
    def classify_folder(self, model, target_names, labelSet, filelabel, classifylabel, path) :
            
        for fname in sorted(os.listdir(path)):
            if fname == variables.TEMP_DIR or fname == variables.OUTPUT_DIR :
                continue
            fpath = os.path.join(path, fname)
            if os.path.isdir(fpath):
                self.classify_folder(model, target_names, labelSet, filelabel, classifylabel, fpath)
            else :
                self.classify_doc(model, target_names, labelSet, filelabel, classifylabel, fpath)   
                
    
    def convert_classification_files(self,  textpath) :
        
        if (self._outputpath == None) :
            if os.path.isdir(textpath):
                o_file = os.path.join(textpath, variables.OUTPUT_DIR)
            else :
                path = self.set_output_dir(textpath)
                fname = os.path.basename(textpath)
                o_file = os.path.join(path, fname)
                if not o_file.lower().endswith(".txt") :
                    o_file += ".txt"
                
                
        else :
            o_file = self._outputpath
            
            # dir base name for output 
            pathbase = os.path.dirname(o_file)
            pathbase = pathbase.replace('\\', '/')
            textpathname = textpath.replace('\\', '/')
            while textpathname :
                if (textpathname == pathbase) :
                    path = textpath[(len(textpathname)+1):]
                    o_file = os.path.join(self._outputpath, path)
                    if (not os.path.isdir(textpath)) :
                        if not textpath.lower().endswith(".txt") :
                            o_file += ".txt"
                    break
                textpathname = os.path.dirname(textpathname)
       
        conv = Convert()
        conv.open_output(textpath, self._outputpath)
        if os.path.isdir(textpath):
            conv.files_to_text(textpath, o_file)
        else :
            conv.file_to_text(textpath, o_file)
        conv.close_output()               
       
        return o_file
             
       
    def classification(self, textpath, outputpath) :
        
        self._ftypes = {}
        self._categorie = {}
        #lists, alldocs = self.datasets.load_documents() 
        target_names = self.datasets.load_doclabel()
        labelSet = self.datasets.load_labelset()
        filelabel = self.datasets.load_filelabel()
        classifylabel = self.datasets.load_classifierlabel()
        
        fname = self.datasets.get_model_file_name()
        model = doc2vec.Doc2Vec.load(fname)
        
        
        if (outputpath != None) :
            self._outputpath = os.path.join(outputpath, variables.OUTPUT_DIR)
        elif os.path.isdir(textpath) :
            self._outputpath = os.path.join(textpath, variables.OUTPUT_DIR)
        elif not textpath.lower().endswith(".txt") :
            root = os.path.dirname(textpath)
            self._outputpath = os.path.join(root, variables.OUTPUT_DIR)
        
        if self._outputpath and not os.path.exists(self._outputpath) :
            os.mkdir(self._outputpath)
        
        
        if os.path.isdir(textpath) :
            self.classify_folder(model, target_names, labelSet, filelabel, classifylabel, textpath) 
        else :
            self.classify_doc(model, target_names, labelSet, filelabel, classifylabel, textpath)
        

    
    
    def debug(self) :        
        
        print('**** classification ***** ') 
        for key, val in self._ftypes.items() :
            print('%s : \t\t %d' % (key, val)) 
        print("\n\n")
        for doc_fname, cat in self._categorie.items() :
            print('%s  \t\t==>  %s (sim = %f)' % (doc_fname, cat[0], cat[1])) 
        
       
    def write_json(self) :        

        docutonejson.save_json_format(self._categorie, self._outputpath+"/classification_files.json")
        
        
    def _to_list(self, cls) :
        lists = [] 
        for name, val in cls.items():
            lists.append([name, val])
        return lists
     
    def to_json(self) :
        result = {}   
        tt = []
        for key, val in self._ftypes.items() :
            tt.append(key)
            tt.append(val)
        '''result["FTYPE"] = tt
        result["result"] = self._to_list(self._categorie)
        docutonejson.print_json(result)'''
       
        self._categorie["FTYPE"] = tt
        docutonejson.print_json(self._categorie)
        
        
    

                
      
         
if __name__ == "__main__":
    
    fpath = "D:/DTNSoftware/dtn-smart/python/src/data/Corpus/TEXT/合同、协议/转让协议"
    fpath = "D:/DTNSoftware/dtn-smart/python/src/data/Corpus/TEXT/合同、协议/劳动合同"
    files = ["1. 刘岩宏劳动合同-中文版.txt", "2. 董伟劳动合同模板-2.txt", "3. 劳动合同模板-3 20180319.txt","4. 劳动合同法模板20180319.txt","5. 劳动合同模板-5 20180319.txt"]
    opath = None #"D:/DocutoneSoftware/SmartDoc/home/import/59b9b3129a1d3f5825c5306a"
    classifying = Classifier()
    classifying.classification(fpath, opath)
    classifying.to_json()
    
    '''for fname in files :
        filename = fpath  +"/" + fname
        classifying.classification(filename, opath)
        #classifying.write_json()
        classifying.to_json() '''
    

     
    
    