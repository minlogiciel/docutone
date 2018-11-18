#-*- encoding:utf-8 -*-
from __future__ import (unicode_literals)


import sys, os
import codecs
from gensim.models import word2vec
import jieba
import jieba.posseg as pseg
import numpy

from gensim.models import KeyedVectors

sys.path.append("../")

from docutone.core.segmentation import Segmentation
from docutone.utils import util, docutonejson, variables
from docutone import config
from docutone.logging import dtn_logging as logging

class Text4Words(object):
    
 
    def __init__(self, stopwords_file = None):
 
        """
        Arguments:
        
        stop_words_file : stop words file name 
        
        """
        self.VECTOR_LENGTH = 100
        self.pagerank_config = {'alpha': 0.85,}
        self.text = ''
        self.keywords = None
       
        self.list_words = []
        self.sentences = []
    
        self.seg = Segmentation(stopwords_file = stopwords_file)
        
        self.seg.load_suggest_words()
        self._model = None
        
    def segment(self, sentences, window = 2, vertex_source = None, edge_source = None):
        """
        Arguments:
        
        sentences : sentence of docuent。
        
        window      窗口大小，int，用来构造单词之间的边。默认值为2。
        """

        words, words_no_stop, words_filter = self.seg.segment(sentences)
        
        return util.sort_words(words, words_no_stop, window=window)


    def get_keywords(self, filename, num=0, min_word_len=1, encoding='utf-8'):
        ''' Argument :      
        filename : input file name
        num : keywords number (0 = all words)
                
        Return list of keywords 
        '''
        
        f = codecs.open(filename, 'r', encoding, 'ignore')
        sentences = [s for s in f if len(s.strip()) > 0]
        f.close()
    
        keywords = self.segment(sentences)
        
        result = []
        count = 0
        for item in keywords:
            if num > 0 and count >= num:
                break

            if len(item.word) > min_word_len:
                result.append(item)
                count += 1

        return result
 
  
    def to_json(self, num=20) :        
        result = []
        count = 0
        for item in self.keywords :
            if count < num :
                result.append(item)
            else :
                break
            count += 1
        keywords = {}
        keywords["KEYWORDS"] = result;
        
        docutonejson.print_json(keywords)
  



    def write_dictionary_line(self, w, dict_file=None,  withFlag=True):
        """
        write to dictionary file 
        
        w : word
        dict_file : dictionary file
        
        """
        
        n = jieba.get_FREQ(w.word)
        if n:
            if dict_file != None :
                if withFlag == True :
                    dict_file.write(w.word + " " + str(n) +" " + w.flag + "\n")
                else :
                    dict_file.write(w.word + "/ ")
            else :
                print (w.word + " " + str(n) +" " + w.flag + "\n")
                



    def add_file_to_dictionary(self, filename, dict_file, encoding="utf-8"):
        """
        filename: docfile name
        add file to dictionary
        """
       
        f = codecs.open(filename, 'r', encoding, "ignore")
        sentences = [s for s in f if len(s.strip()) > 0 ]
        f.close()       
        s = ''.join(sentences)
        jieba_result = pseg.cut(s, HMM=False)
        jieba_result = [w for w in jieba_result if w.flag!='x' and w.flag!='eng']
        words = [w for w in jieba_result if len(w.word)>0]


        for w in words :
            if w.word not in self.list_words :
                self.write_dictionary_line(w, dict_file=dict_file)
                self.list_words.append(w.word)


    def add_files_to_dictionary(self, fpath, dict_file):
        """
        fpath : input file or directory
        dict_file : dictionary file
        """

        for name in os.listdir(fpath):
            path = os.path.join(fpath, name)
            if os.path.isdir(path):
                self.add_files_to_dictionary(path, dict_file)
            else :
                if name.endswith(".txt") :
                    self.add_file_to_dictionary(path, dict_file)


    def load_vocablary(self, dictname):
        """       
        dictname : dictionary file name
            
        """
        
        dict_file = codecs.open(dictname, "r", "utf-8")
        sentences = dict_file.readlines()
        self.list_words = [s.split()[0] for s in sentences if (len(s.strip()) > 0) ]
        dict_file.close()
                 
                 
                 
    def _create_dictionary(self, infile, dict_file):
        """
        infile : input file or folder
        
        """
        if os.path.isdir(infile):
            self.add_files_to_dictionary(infile, dict_file)
        else :
            self.add_file_to_dictionary(infile, dict_file)
        
        
    def create_dictionary(self, dictname="docutone.dict"):
        """
        infile : input file or folder
        
        dictname : dictionary file name
        
        """
        
        dictname = util.get_default_vocabulary_file(dictname)
        
        if os.path.exists(dictname) :
            self.load_vocablary(dictname)
            dict_file = codecs.open(dictname, "a", "utf-8")
        else :
            dict_file = codecs.open(dictname, "w", "utf-8")
        
        self._create_dictionary(variables.CORPUS_DIR + "/TEXT", dict_file)
        self._create_dictionary(config.TEMPLATE_DIR + "/TEXT", dict_file)

        dict_file.close()



    def load_file(self, filename, encoding="utf-8"):
       
        if filename.endswith(".txt") :
            f = codecs.open(filename, 'r', encoding, "ignore")
            sentences = [s for s in f if len(s.strip()) > 0 ]
            f.close()       
            
            words = self.seg.segment(sentences)[2]
            
            self.sentences += words
    
    
    def load_directory(self, path):
       
        for name in os.listdir(path):
            fpath = os.path.join(path, name)
            if os.path.isdir(fpath):
                if variables.noloaddir(name) :
                    continue
                else :
                    self.load_directory(fpath)
            else :
                if name.endswith(".txt") :
                    #self.sentences.append(self.load_file(fpath))
                    self.load_file(fpath)
   
    
    def train_word_vector_embedding(self, min_count=2, sg=0, vectfname=None):
        # word to vector file name
        if vectfname == None :
            vectfname = util.get_default_wordvect_file()

        # word to vector 
        self._model = word2vec.Word2Vec(self.sentences, min_count=min_count, sg=sg, workers=4, size=self.VECTOR_LENGTH, window=5)
        
        # save wood to vector model 
        self._model.wv.save_word2vec_format(vectfname, binary=False)
 
        # summarize vocabulary size in model
        words = list(self._model.wv.vocab)

        logging.logger_info("Embedded", 'create vocabulary : %d (%s)' %(len(words), vectfname))

        
    def load_word_vector_embedding(self, vectfname=None):
        # word to vector file name
        if vectfname == None :
            vectfname = util.get_default_wordvect_file()
        
        self._model = KeyedVectors.load_word2vec_format(vectfname, binary=False)
        # summarize vocabulary size in model
        words = list(self._model.wv.vocab)
        
        logging.logger_info("Embedded", 'load vocabulary : %d (%s)' %(len(words), vectfname))

                 
       
    def create_embedding(self) :
        self.sentences = []
        
        self.load_directory(variables.CORPUS_DIR + "/TEXT")
        self.load_directory(config.TEMPLATE_DIR + "/TEXT")
        
        self.train_word_vector_embedding()
         
       
        
 
    def similar_words(self, positive=None, negative=None, word1=None, word2=None) :
        
        # word to vector file name
        if self._model == None :
            vectfname = util.get_default_wordvect_file()
            self._model = word2vec.KeyedVectors.load_word2vec_format(vectfname, binary=False)
        
        try:
            if positive and negative :
                return self._model.wv.most_similar(positive=positive, negative=negative)
            elif positive :
                return self._model.wv.most_similar(positive=positive)
            elif negative :
                return self._model.wv.most_similar(negative=negative)
            elif word1 and word2 :
                return self._model.wv.similarity(word1, word2)
            elif word1 :
                return self._model.wv.similar_by_word(word1)
            elif word2 :
                return self._model.wv.similar_by_word(word2)
            else :
                return ""
        except KeyError :
            return "Error : word not found!"
            
        
        
    def test_word_vector_model(self) :
        
        #print ("Test word2vec most similar for 公司合伙人 : ")
        #print (model.wv.most_similar(positive=['公司', '合伙人']))
        print ("Test word2vec most similar for 公司的住所为")
        #print (self.similar_words(positive=['公司', '中文', '名称']))
        print (self.similar_words(positive=['公司', '住所']))
        
        #print (self.similar_words(word1='公司住所', word2='公司的住所为'))
        
        #print (self.similar_words(word1='公司中文名称'))
        
        '''
        print (self.similar_words(positive=['股东'], negative=['大会']))
        print (self.similar_words(positive=['支付', '工资'], negative=['董事']))
        
        #print (model.wv.similarity('合伙人', '董事'))
        print (self.similar_words(word1='董事会', word2='股东大会'))
        print (self.similar_words(word1='董事会'))
        print (self.similar_words(word1='董事'))
        print (self.similar_words(word1='违法'))
        '''
        
    
    def load_embedding_vector(self):
    # load embedding into memory, skip first line
        filename = util.get_default_wordvect_file()
        file = codecs.open(filename, 'r', "utf-8")
        lines = file.readlines()[1:]
        file.close()
        # create a map of words to vectors
        embedding = dict()
        for line in lines:
            parts = line.split()
            # key is string word, value is numpy array for vector
            embedding[parts[0]] = numpy.asarray(parts[1:], dtype='float32')
            
        return embedding

    # create a weight matrix for the Embedding layer from a loaded embedding
    def get_weight_matrix(self, embedding, vocab):
        # total vocabulary size plus 0 for unknown words
        vocab_size = len(vocab) + 1
        # define weight matrix dimensions with all 0
        weight_matrix = numpy.zeros(vocab_size, self.VECTOR_LENGTH)
        # step vocab, store vectors using the Tokenizer's integer mapping
        for word, i in vocab.items():
            weight_matrix[i] = embedding.get(word)
    
        return weight_matrix
        
    def creater_embedding_layer(self):
        # load embedding from file
        raw_embedding = self.load_embedding_vector()
        # get vectors in the right order
        vocab = None # tokenizer.word_index
        max_length = 1
        embedding_vectors = self.get_weight_matrix(raw_embedding, vocab)
        # create the embedding layer
        #embedding_layer = Embedding(len(vocab) + 1, self.VECTOR_LENGTH, weights=[embedding_vectors], input_length=max_length, trainable=False)        
        
    

        
        
        
        
if __name__ == '__main__':
    
    tw = Text4Words()
    #tw.create_embedding()  
    tw.create_dictionary()
    
    #tw.load_embedding()
    #tw.test_word_vector_model()
    
    print("="*20 + " end " + "="*20)
    
    
    
    
    