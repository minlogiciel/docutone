# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import sys,os
import codecs
import re

from six import string_types
from gensim import corpora, models
from gensim.models import word2vec
from gensim.models.doc2vec import TaggedDocument

sys.path.append("../")

from docutone.core.segmentation import Segmentation
from docutone.core.datasets import Datasets
from docutone.core.document import LawDocument
from docutone.core.clause import Clause
from docutone.core.crf import CRF
from docutone.utils import variables
from docutone.utils.convert import Convert
from docutone import config
'''
读取标注合同文件，生成训练向量模板
'''
class Contract(object):
    
    '''
    create legal terms classifier
    
    input model : data/terms/template
    
    output model : data/models
    '''
       
    def __init__(self, debug=0, crf_model=True):
        
        self.texts = []         # list of legal terms tests
        self.terms_index = {}  #  mapping legal term name to numeric id
        self.terms_name = {}   #  legal term name 
        self.terms_label = []  #  mapping legal term name to label
        self.labels = []        # list of legal term label ids
        self._debug = debug
        self.seg = Segmentation()
        self.seg.load_suggest_words()
        self.lawdocument = LawDocument()
        self.clause = Clause()
        self.doc_type = None
        self.doc_path = None
        self.labor_model = True
        self.crf_model = crf_model
    
    def get_data_file_name(self, dataname, categorie='models') :
        path = variables.get_data_file_name(self.doc_path, categorie=categorie)
        if not os.path.exists(path) :
            os.mkdir(path)
        return os.path.join(path, dataname)
 
    def get_term_model_name(self) :
        return self.get_data_file_name(variables.TERM_DOC_MODEL)
        

    # term vector [0, 0, 1, 1, ...]  
    def load_term_set(self) :
        fname = self.get_data_file_name(variables.TERM_VECT)
        f = codecs.open(fname, 'r', 'utf-8')
        
        termSet = [int(line) for line in f if len(line.strip()) > 0]
        f.close()
    
        return termSet

    def save_term_set(self) :
        fname = self.get_data_file_name(variables.TERM_VECT)
        f = codecs.open(fname, 'w', 'utf-8')

        for v in self.labels :
            f.write("%s\n" % (v))
        f.close()
         
    
    
    # term name [termname=termid]
    def load_term_label(self) :
        fname = self.get_data_file_name(variables.TERM_LABEL)
        f = codecs.open(fname, 'r', 'utf-8')
        
        labelSet = [line.split('=')[0] for line in f if len(line.strip()) > 0]
        f.close()
    
        return labelSet


    def save_term_label(self) :
        fname = self.get_data_file_name(variables.TERM_LABEL)
        f = codecs.open(fname, 'w', 'utf-8')
        
        for v, k in self.terms_name.items():
            f.write("%s=%d\n" % (k, v))
        f.close()
          
    
    # term list 
    def load_term_list(self) :
        fname = self.get_data_file_name(variables.TERM_LIST)
        f = codecs.open(fname, 'r', 'utf-8')
        
        termList = [line.split('=')[0] for line in f if len(line.strip()) > 0]
        f.close()
    
        return termList
 

    def save_term_list(self) :
        fname = self.get_data_file_name(variables.TERM_LIST)
        f = codecs.open(fname, 'w', 'utf-8')
        for index in range(len (self.terms_label)):
            k = self.terms_label[index]
            v = self.labels[index]
            f.write("%s=%d\n" % (k, v))
        f.close()
 
    def _convert(self, text_path, convert=False) :   
        
        path = text_path;
        if text_path.endswith("doc") :
            doc_path = text_path
            path = text_path[0:-3] + "TEXT"
        
        if (convert and os.path.exists(doc_path)) :
            conv = Convert(verbose=0)
            o_file = conv.open_output(doc_path, path)
            conv.files_to_text(doc_path, o_file)    
            conv.close_output()
        return path

    
    def get_term_words(self, text) :
        
        if isinstance(text, string_types) :
            sentences = [text]
        else :
            sentences = text

        words_all_filter = self.seg.segment(sentences)[2]

        words = []
        for sentences in words_all_filter :
            for w in sentences :
                if len(w.strip()) > 0 :
                    words.append(w.strip()) 
        return words
 


    
    
    def segment_terms(self, term_sentences):
        """
        Arguments :
        
        term_sentences : test term sentences
    
        return segmentation words
        
        """
        words_all_filter = self.seg.segment(term_sentences)[2]
            
        return words_all_filter
       

    
    def get_terms(self, filename, encoding="utf-8"):
                        
        terms = [] 
         
        self.lawdocument.create_document(filename, encoding)
        
        if len(self.lawdocument.sections) > 0 :         
            for p in self.lawdocument.sections :
                
                term_sentences = []
                term_sentences.append(p.title)
                for s in p.sentences :
                    term_sentences.append(s[0]) # document sentence [s, num, type]
                terms.append(term_sentences)
        # if doc is not law document
        else :
            for p in self.lawdocument.document_header :
                terms.append([p])
            pass
        return terms
             
    
    def load_file(self, filename, encoding="utf-8"):
        
        # directory name is document type 
        ftype = os.path.basename(os.path.dirname(filename))
        
        self.clause.create_clauses(filename, encoding=encoding)

        for p in self.clause.sections :
            name = p.title
            term_sentences = []
            term_sentences.append(name)
            for s in p.sentences :
                term_sentences.append(s)
            
            # add term vector 
            self.texts.append(self.segment_terms(term_sentences))
                     
            if name in self.terms_index :
                label_id = self.terms_index[name]
            else :
                label_id = len(self.terms_index)+1
                self.terms_index[name] = label_id
                self.terms_name[label_id] = name
                        
            self.labels.append(label_id)
            
            self.terms_label.append(name+":"+ftype)
  


    def load_directory(self, path) :

        for fname in sorted(os.listdir(path)):
            fpath = os.path.join(path, fname)
            if os.path.isdir(fpath):
                if variables.noloaddir(fname) :
                    continue
                self.load_directory(fpath)
    
            elif fname.endswith(".txt"):
                self.load_file(fpath)
            else :
                #is not text file
                pass
    
    
    def load_terms(self, text_path) :
 
        self.load_directory(text_path) 

        termdocs = []   # term doc2vec
        allterms = []   # term contents

        for index in range(len(self.texts)) :
            term = self.texts[index]
            if len(term) > 0 :
                s = []
                for sentences in term :                 
                    for word in sentences :
                        s.append(word)
                    
                #string = 'doc_' + str(index+1)
                docs = TaggedDocument(s, tags = [index])         
                termdocs.append(docs)
                allterms.append(s)
        return allterms, termdocs
                 

        
    def _create_terms(self, text_path, doctype=None, min_count=2, sg=0, workers=1, size=256, window=5) :   
        """
        min_count : ignore all words with total frequency lower than this.
        sg : sg = O CBOW, sg=1 skip-gram 
        workers: thread
        size : dimension feature vectors.
        window : maximum distance between the current and predicted word within a sentence.
    
        """
        
        self.texts = []         # list of legal terms tests
        self.terms_index = {}  #  mapping legal term name to numeric id
        self.terms_name = {}   #  legal term name 
        self.terms_label = []  #  mapping legal term name to label
        self.labels = []        # list of legal term label ids
        self.doc_type = doctype
        self.doc_path = doctype
        
        path = text_path
            
    
        allterms, termdocs = self.load_terms(path)
        
        # if there is no more clauses, do nothing
        if  len(allterms) < 10 :       
            return
                
        dictionary = corpora.Dictionary(allterms)
        corpus = [dictionary.doc2bow(text) for text in allterms]
        
        # save corpus
        corpusfname = self.get_data_file_name(variables.TERM_MODEL_MM)
        corpora.MmCorpus.serialize(corpusfname, corpus) 
    
        
        # save dictionary
        dictfname = self.get_data_file_name(variables.TERM_MODEL_DICT)
        dictionary.save(dictfname)
        
    
    
        dictfname = self.get_data_file_name(variables.TERM_MODEL_LSI)        
        # initialize a model
        tfidf = models.TfidfModel(corpus, normalize=True)
            
        # use the model to transform vectors        
        corpus_tfidf = tfidf[corpus]
            
        # initialize an LSI transformation, LSI 2-D space
        lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=300) 
        lsi.save(dictfname) # same for tfidf, lda, ...
    
    
        #trainig doc2vec
        datasets = Datasets()
        model = datasets.TrainingDoc2Vec(termdocs, size, window, 16) 
        # save doc vector
        vectfname = self.get_term_model_name()
        model.save(vectfname)

        '''
        # word to vector 
        model = word2vec.Word2Vec(allterms, min_count=min_count, sg=sg, workers=workers, size=size, window=window)
        # save words vector
        vectfname = self.get_data_file_name(variables.TERM_WORD_MODEL)
        model.wv.save_word2vec_format(vectfname, binary=False)
        '''
        # save term list 
        self.save_term_list()
        
        # save term vector  
        self.save_term_set()
    
        # save term name 
        self.save_term_label()


    def create_crf(self, path) :   

        crf = CRF()
        if self.labor_model :
            fpath = path + "/劳动合同" 
            ftype = "劳动合同"
            crf.create_categorie_tagging(fpath, ftype)
        else :
            crf.create_crf_model()
            
    def create_terms(self, text_path, convert=False) :   
        
        path = self._convert(text_path, convert)
        
        if self.crf_model :
            self.create_crf(path)
        else :
            self._create_terms(path, doctype=None)
            for doctype in sorted(os.listdir(path)):
                fpath = os.path.join(path, doctype)
                if os.path.isdir(fpath):
                    self._create_terms(fpath, doctype=doctype)
    
    
    
       

if __name__ == '__main__':
 
    path = config.TEMPLATE_DIR + "/TEXT"
    
    cont = Contract(debug=1)
    cont.create_terms(path)
    

    print('=== end ===')
        
       

    
    

    

    
    

    
