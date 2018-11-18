# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import sys,os

from gensim import corpora, models, similarities
from gensim.models import doc2vec
from gensim.models.doc2vec import TaggedDocument


#from PIL.WmfImagePlugin import word

sys.path.append("../")

from docutone.core.document import LawDocument
from docutone.core.segmentation import Segmentation

from docutone.utils import variables, docutonejson, dtn_sentence
from docutone.utils import docutonelocate, synonyms

from docutone.utils.extract_data import ExtractData
from docutone.domain.crf_extract import CRFExtract
from docutone import config
from docutone.document import dtn_document

'''
不是法律文件信息提取
'''
class Extraction(object):
    
    SIMU_SEUIL = 0.6
    
    def __init__(self, crf_mode=True):

        self.filename = None
        self.fullname = None
        self.categorie = None;
        self.document = LawDocument()
        self.segment = Segmentation()
        self.result = {}
        self.crf_mode = crf_mode
        if crf_mode :
            self.crf_extract = CRFExtract ()
        else :
            self.crf_extract = None
            
    
    
    def _init_extraction(self, doctype) :
        
        if ";" in doctype :
            parent, cat = doctype.split(";", 1)
            self.categorie = cat.strip()
            self.ftype = parent.strip()
        else :
            self.categorie = doctype.strip()
            self.ftype = None

        self.result = {} 
        self.keywords = dtn_sentence.get_document_categorie(self.categorie)
        if self.keywords :
            for key in self.keywords :
                if len(key) > 0 :
                    self.result[key] = ExtractData(key, self.categorie)

    
    def _add_section_sentences(self, key, n_section):
        
        n = n_section
        section = self.document.sections[n]
        if len(section.sentences) > 0 :
            for s in section.sentences :
                self.result[key].add_value(s, 1)
        
        n += 1
        if n < len(self.document.sections) :
            next_section = self.document.sections[n]
            while next_section.level > section.level :
                if len(next_section.sentences) > 0 :
                    for s in next_section.sentences :
                        self.result[key].add_value(s, 1)
                n += 1
                next_section = self.document.sections[n]
        return n

    
    
    def analyze_document_sections(self, sections) :

        sentences = []
        nb = len(sections)
        i = 0
        while i < nb :
            section = self.document.sections[i]
            if section.title :
                key = dtn_sentence.get_keywords_by_name(section.title, self.keywords)
                if key :
                    i = self._add_section_sentences(key, i)
                    continue
                
            if len(section.sentences) > 0:
                paragrph = [dtn_sentence.get_sentence(p) for p in section.sentences]
                sentences.append(paragrph)
            i += 1
            
        return sentences
    
    
    def analyze_text_document(self, text_sentences) :
        sentences = []
        i = 0
        nb = len(text_sentences)
        while (i < nb) :
            s = dtn_sentence.get_sentence(text_sentences[i])
            i += 1
           
            ''' if search keyword in the sentence, add it to result '''
            key = dtn_sentence.get_keyword_from_sentence(s, self.keywords)
            if key :
                self.result[key].add_value(s, 1)
                
                ''' if sentence end with ':'  add following sentence '''
                if dtn_sentence.is_keyword_title_sentence(s) :                        
                    sentence_tag = None
                    section_num = 0
                    firstline = True
                    while (i < nb) :

                        s = dtn_sentence.get_sentence(text_sentences[i])
                        
                        ''' find next keyword, stop while '''  
                        if dtn_sentence.get_keyword_from_sentence(s, self.keywords) :
                            break
                            
                        s_type = self.document.parser_sentence(s)
                        i += 1
                        if firstline :
                            self.result[key].add_value(s, 1)
                            firstline = False
                            if s_type :
                                sentence_tag = s_type[0]
                                section_num = s_type[1]
                            else :
                                ''' if this is not section type, stop while '''
                                break
                        else :
                            if s_type :
                                if s_type[1] <= section_num  or s_type[0] != sentence_tag :
                                    i -= 1
                                    break
                                else :
                                    section_num = s_type[1]
                                    self.result[key].add_value(s, 1)
                                       
                            else :
                                self.result[key].add_value(s, 1)

                   
            else :
                ''' keyword is not found in sentence '''
                sentences.append([s])   

        return sentences




    def load_document(self, filename, filetype) :
 
        self.fullname = filename
        self.filename = os.path.basename(filename).split('.')[0]
        if (filename.endswith(".txt")) :
            ofile = filename
        else :
            ofile = docutonelocate.convert_file(filename)
        
        self.document.read_document(ofile, filetype)
        nb = len(self.document.sections)
        if nb > 0 :
            ss = self.analyze_document_sections(self.document.sections)
        else :
            ss = self.analyze_text_document(self.document.document_header)
            
        
        docdocs = []
        sentences = []
        
        if len(ss) > 0 :
            doc_str = self.segment.segment(ss)[0]
            index = 0
            for s in doc_str :       
                if len(s) > 0 :
                    sentences.append(s)
                    doc = TaggedDocument(s, tags = [index])         
                    docdocs.append(doc)
                    index += 1

        return sentences, docdocs

       
    def create_keywords_bow(self, dictionary, sentences) :
        #find these words in dictionary 
        words = self.segment.segment(sentences, wlen=1)[0]
        
        tab = []
        for word in words :
            vec_bow = dictionary.doc2bow(word)
            if  vec_bow: 
                tab.append(vec_bow)
        return tab


    def create_model(self, sentences, docs, min_count=2, sg=0, workers=1, size=256, window=5) :

        dictionary = corpora.Dictionary(sentences)
        corpus = [dictionary.doc2bow(text) for text in sentences]
        
        mm_fname = os.path.join(variables.TMODEL_DIR, "model_tmp.mm")
        corpora.MmCorpus.serialize(mm_fname, corpus) 
        '''
        # save dictionary
        dictfname = os.path.join(variables.TMODEL_DIR, "model_tmp.dict")
        dictionary.save(dictfname)
        
        
        dictfname = os.path.join(variables.TMODEL_DIR, "model_tmp.lst")  
        # initialize a model
        tfidf = models.TfidfModel(corpus, normalize=True)
            
        # use the model to transform vectors        
        corpus_tfidf = tfidf[corpus]
            
        # initialize an LSI transformation, LSI 2-D space
        lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=300) 
        lsi.save(dictfname) # same for tfidf, lda, ...
        '''
       
        # training create doc2vec model
        model = doc2vec.Doc2Vec(docs, min_count=min_count, size=size, window=window, alpha=0.025, min_alpha=0.025)
        model.train(docs, total_examples=len(docs), total_words=None, epochs=5, start_alpha=0.05, end_alpha=0.01)
        
        # load document corpus 
        corpus = corpora.MmCorpus(mm_fname)
        
        
        # create tfidf
        tfidf = models.TfidfModel(corpus, normalize=True)
        
        corpus_tfidf = tfidf[corpus]
        
        # create lsi model
        lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=300) 
        
        # get similarity index
        index = similarities.MatrixSimilarity(lsi[corpus_tfidf],  num_features=corpus.num_terms)
        # set 3 best simularities
        index.num_best = 3
        
        return dictionary, lsi, index
                            


    def extraction_keyword(self, filename, doctype, encoding="utf-8"):
    
        ''' init result '''
        self._init_extraction(doctype)
        ''' load document '''
        sentences, docs = self.load_document(filename, self.categorie)
        ''' create lsi '''
        dictionary, lsi, index = self.create_model(sentences, docs)
        
        # create keywords bow
        key_lists = []
        for s in self.keywords :
            key = s.strip()
            if len(key) > 0 :
                # add 文件名称
                if key == '文件名称' or key == '合同名称' :
                    if self.document.document_name  :
                        self.result[key].add_value(self.document.document_name, 1)
                # add 合同日期 
                elif key == '签约日期' or key == '签发日期' or key == '合同日期' :
                    if self.document.document_date :
                        self.result[key].add_value(self.document.document_date, 1)
                        continue
                else :
                    key_lists.append(key)
                    # add synonyms words 
                    synonym_words = synonyms.get_synonyms(key)
                    if (synonym_words) :
                        for s_key in synonym_words :
                            key_lists.append(s_key)
                

        vec_bows = self.create_keywords_bow(dictionary, key_lists)
       
        i = 0
        for vec_bow in vec_bows :
            #find keyword vector in lsi        
            vec_lsi = lsi[vec_bow] # convert the query to LSI space
            # perform a similarity query against the corpus
            #sims = index[vec_lsi] 
            #sims = sorted(enumerate(sims), key=lambda item: -item[1])

            sims = index[vec_lsi] 
            name = key_lists[i]
            key = dtn_sentence.get_keywords_by_name(name, self.keywords)
            if key :
                xdata = self.result[key]
            
                for sim in sims:   
                    if sim[1] > self.SIMU_SEUIL :
                        nl = sim[0]
                        ss = sentences[nl];
                        s = ''.join(ss)
                        xdata.add_value(s, sim[1])
                    else :
                        break
            i += 1
    
        return self.result
    
    def extraction(self, filename, doctype):

        if self.crf_mode :
            self.result = self.crf_extract.extraction(filename, doctype)
            self.filename = self.crf_extract.filename
            self.fullname = self.crf_extract.fullname
            self.categorie = self.crf_extract.categorie

        else :
            self.extraction_keyword(filename, doctype)
        return self.result
    
    def full_create_model(self, sentences, docs, keywords, min_count=2, sg=0, workers=1, size=256, window=5) :
        
        needed = 0
        
        dictionary = corpora.Dictionary(sentences)
        corpus = [dictionary.doc2bow(text) for text in sentences]
        
        mm_fname = os.path.join(variables.TMODEL_DIR, "model_tmp.mm")
        corpora.MmCorpus.serialize(mm_fname, corpus) 
        # save dictionary
        if needed :
            dictfname = os.path.join(variables.TMODEL_DIR, "model_tmp.dict")
            dictionary.save(dictfname)

        
            # initialize a model
            tfidf = models.TfidfModel(corpus, normalize=True)
            
            # use the model to transform vectors        
            corpus_tfidf = tfidf[corpus]
            
            # initialize an LSI transformation, LSI 2-D space
            lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=300) 
            lsifname = os.path.join(variables.TMODEL_DIR, "model_tmp.lsi")   
            lsi.save(lsifname) 
        
            
        model = doc2vec.Doc2Vec(docs, size=size, window=window, alpha=0.025, min_alpha=0.025)
        model.train(docs)
        
        if needed :
            # save doc vector
            vectfname = os.path.join(variables.TMODEL_DIR, "model_tmp.d2v")
            model.save(vectfname)

        
        vec_bows = self.create_keywords_bow(dictionary, keywords)
        
        
        
        
        #dictionary = corpora.Dictionary.load(dictfname)
        corpus = corpora.MmCorpus(mm_fname)
         
        tfidf = models.TfidfModel(corpus, normalize=True)
        
        corpus_tfidf = tfidf[corpus]
        # load lsi model 
        if needed :
            lsi = models.LsiModel.load(lsifname)
        else :
            lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=300) 
            
        

        index = similarities.MatrixSimilarity(lsi[corpus_tfidf],  num_features=corpus.num_terms)
        index.num_best = 3
        
        i = 0
        for vec_bow in vec_bows :
        
            #find these words in dictionary        
            vec_lsi = lsi[vec_bow] # convert the query to LSI space
        
            # perform a similarity query against the corpus
            #sims = index[vec_lsi] 
            #sims = sorted(enumerate(sims), key=lambda item: -item[1])

            sims = index[vec_lsi] 
            print("**** " + keywords[i][0]+ " *****")
            for sim in sims:
                if sim[1] > 0.5 :
                    print(''.join(sentences[sim[0]]))

            i += 1
        return sims
    
    def _to_list(self, extractdata) :
        lists = [] 
        for name, data in extractdata.items() :
            val = []
            simu = 0
            if len(data.term_value) > 0 :
                for v, s_simu in data.term_value :
                    if s_simu == 1: # is term name and find term string
                        simu = s_simu
                        val.append(dtn_sentence.get_sentence(v))
                       
                    elif simu < s_simu : # get term value for max simu value
                        simu = s_simu
                        val.append(dtn_sentence.get_sentence(v))
                        
                
                lists.append([name, val,  simu])
            else :
                lists.append([name, val,  0])
        return lists
   
    def _to_html_text(self, extractdata) :
        
        lists = []
        for name, data in extractdata.items() :
            text = ""
            if len(data.term_value) > 0 :
                for v, s_simu in data.term_value :
                    if s_simu > 0: # is term name and find term string
                        s = dtn_sentence.get_sentence(v)
                        ss = dtn_document.law_document.parser_sentence(s)
                        text +=  '<p>'
                        if ss :
                            text +=  '<b>' + ss[1] + ' ' + ss[2] + '</b></p>'
                            text += '<p> ' # empty line
                        else :
                            text +=  s
                        text +=  '</p>'
         
                lists.append([name, text])
            else :
                lists.append([name, text])
        
        return lists

    def to_json(self, lists) :
        result = {}
        result["filename"] = [self.filename, self.fullname, self.categorie]
            
        result["result"] = self._to_list(lists)
        #result["result"] = self._to_html_text(lists)
            
        docutonejson.print_json(result)

    def example(self):
        fname = config.TEST_PATH + "/营业执照/二连浩通年检后营业执照副本.JPG.txt"
        ftype = "政府批准证书-批文;营业执照"
        term_list = self.extraction(fname, ftype)
        print("TEST FILE : %s (%s)" %(fname, ftype))
        self.to_json(term_list)
        
    def example0(self):
        
        fname = config.TEST_PATH + "/章程/A股国投新集能源股份有限公司章程.txt"
        fname = config.TEST_PATH + "/章程/创业环保公司章程.txt"
        ftype = "A股公司章程"
        term_list = self.extraction(fname, ftype)
        print("TEST FILE : %s (%s)" %(fname, ftype))
        self.to_json(term_list)

if __name__ == '__main__':
          


    extr = Extraction(True)
    extr.example0()

    

    






