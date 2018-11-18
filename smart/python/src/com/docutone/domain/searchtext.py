# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

import sys, os

from gensim import corpora, models, similarities
from gensim.models import word2vec
from six import iteritems, itervalues, string_types

from docutone.core.datasets import Datasets
from docutone.core.document import LawDocument
from docutone.core.text4sentences import Text4Sentences
from docutone.utils import variables


sys.path.append("../")




class TextSearch(object) :

    def __init__(self, stop_words_file = None):
       
        #self.law_document = LawDocument()
        self.text_sentence = Text4Sentences()
        self.datasets = Datasets()
        pass


    def get_text_bow(self, dictionary, text) :
        #find these words in dictionary 
        self.text_sentence = Text4Sentences()
        if isinstance(text, string_types):
            doc = [text]
        else :
            doc = text
        self.text_sentence.create_segment_sentences(doc)
        
        tab = []
        for words in self.text_sentence.words_no_filter :
            vec_bow = dictionary.doc2bow(words)     
            tab.append(vec_bow)
        return tab[0]
   

 
    def get_document_type(self, dictname) :
        
        textfname = "../dictionary/text/" + dictname  + ".txt"
        law_document = LawDocument()
        law_document.analyze(filename=textfname)
        
        text = law_document.document_type;
        
        return text
 
    def get_document(self, dictname) :
        
        textfname = "../dictionary/text/" + dictname  + ".txt"
        law_document = LawDocument()
        law_document.analyze(filename=textfname)
        
        text = "\n".join(law_document.document_title);
        
        return text
        
    def get_document_chapiter(self, sims, dictname) :
        
        textfname = "../dictionary/text/" + dictname  + ".txt"
        law_document = LawDocument()
        law_document.analyze(filename=textfname)
        text = "";
        n_line = 1
        for sim in sims :
            doc_no, simil = sim[0], sim [1]
            if (simil > 0.4) :
                text +=  "******** " + str(n_line) + "  ********\n"
                text += law_document.get_document_chapiter(doc_no) + "\n"
                n_line += 1
                if n_line > 2:
                    break;
            else :
                break
        return text



    def get_similarity_value(self, sims) :
        total = 0.0
        n_line = 1
        for sim in sims :
            doc_no, simil = sim[0], sim [1]
            if simil > 0.4 and n_line < 2:
                total += simil
            else :
                break
            n_line += 1
        
        return total

    def text_search_lsi(self, sentence) :
        
        dictfname = self.datasets.get_dict_file_name()
        mm_fname = self.datasets.get_mm_file_name()
        lsifname = self.datasets.get_model_list_name()
        
        dictionary = corpora.Dictionary.load(dictfname)
        corpus = corpora.MmCorpus(mm_fname)
         
        tfidf = models.TfidfModel(corpus, normalize=True)
        
        corpus_tfidf = tfidf[corpus]
        # load lsi model 
        lsi = models.LsiModel.load(lsifname)
        # create lsi model 
        #lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=300)
        index = similarities.MatrixSimilarity(lsi[corpus_tfidf],  num_features=corpus.num_terms)
        #find these words in dictionary 
        vec_bow = self.get_text_bow(dictionary, sentence)
            
        
        vec_lsi = lsi[vec_bow] # convert the query to LSI space
        
        # perform a similarity query against the corpus
        #sims = index[vec_lsi] 
        #sims = sorted(enumerate(sims), key=lambda item: -item[1])
 
        index.num_best = 3
        sims = index[vec_lsi] 

        return sims
            
 

    def text_search_bow(self, textpath, text) :
        
        dictfname = self.datasets.get_dict_file_name(textpath)
        mm_fname = self.datasets.get_mm_file_name(textpath)
        lsifname = self.datasets.get_model_list_name(textpath)
         
        dictionary = corpora.Dictionary.load(dictfname)
        corpus = corpora.MmCorpus(mm_fname)
        #tfidf = models.TfidfModel(corpus, normalize=True)
        tfidf = models.TfidfModel(corpus)
        
 
        index = similarities.SparseMatrixSimilarity(tfidf[corpus], num_features=corpus.num_terms)
       
        #find these words in dictionary 
        vec_bow = self.get_text_bow(dictionary, text)
        sims = index[vec_bow]
        sims = sorted(enumerate(sims), key=lambda item: -item[1])
        
        #####self.get_documents(dictionary, corpus, sims, dictname)
        
 
    def search_document(self, textpath, filename) :
        ld = LawDocument()
        ld.analyze(filename=filename)
        
        
        doc_tab = []
        names = os.listdir("../dictionary/dict")
        n_file = 1
        for filename in os.listdir("../dictionary/dict") :
            if filename.endswith(".dict") :
                dictname = filename.replace('.dict', '')
                total = 0.0
                sentences = []
                for sentence in ld.table_contents :
                    if len(sentence) > 1 :
                        
                        sims = self.text_search_lsi(textpath, sentence[1])
                        total += self.get_similarity_value(sims)
                
                doc_tab.append([dictname, total])
        doc_tab = sorted(doc_tab, key=lambda total: total[1], reverse=True)

        return self.get_document_type(doc_tab[0][0])
 

    def searching(self, text) :
        
        sims = self.text_search_lsi(text)
    
        print(self.get_document_chapiter(sims))
    
    def test_words_to_vector(self) :
        
        filename = self.datasets.get_word_model_name()
        
        self.model = word2vec.Word2Vec.load_word2vec_format(filename, binary=False)
        print (self.model.similarity('投资人', '营业执照'))
        print (self.model.similarity('董事', '法律' ))
        #print (self.model.similarity('旅行社', '酒店'))


        
if __name__ == "__main__":
    

    fpath = fclassify = variables.CORPUS_DIR + "\\TEXT"

    file_nb = 8
    test_files = [
        "zhangcheng.txt",
        "hezihetong.txt",
        "hetong.txt",
        "BEIJING-1-28150-v7A-SLEB - Shareholders Agreement - Chinese（091118）markup.txt",
        "BEIJING-1-28243-v9A-SLEB - Subscription Agreement - Chinese（091116）.txt",
        "Changchun Lease Agreement Chinese Feb-25-2001.txt",
        "Delta LTAA CH 10 Dec 2004 bln.txt",
        "Delta MSA CH 10 Dec 2004 bln.txt",
        ]



    search = TextSearch()
    search.test_words_to_vector()
    
    search.searching("人民网股份有限公司")
    """
    for n in range(0, file_nb) :
        fname = test_files[n]
        type = search.search_document(path+fname)
        print ("**** %s ====> (%s) ..." %(fname, type))

    """




