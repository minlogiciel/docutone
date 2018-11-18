#-*- encoding:utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

"""
@author:   docutone

"""
import sys
import jieba
import jieba.posseg as pseg
import codecs

from six import string_types

sys.path.append("../")

from docutone.utils import util

'''
分词
'''
class Segmentation(object):
    

    def __init__(self, stopwords_file=None, delimiters=None):

        """
        
        stopwords_file : stop words file name


        
        delimiters : delimiters the sentence
        
        """
        
        self.delimiters = delimiters
        
        self.load_stop_words(stopwords_file)
        
        

    def set_library(self, extdict=None, idfdict=None, stopdict=None):
        """
        arguments :
        
        extdict :
        
        idfdict :
        
        stopdict :
        
        """
    
        if type(extdict) is str:
            jieba.load_userdict(extdict)
        else :
            jieba.load_userdict("./data/dict/dict.txt.big")
        """  
        if type(idfdict) is str:
            jieba.analyse.set_idf_path(idfdict);
        else :
             jieba.analyse.set_idf_path("./data/dict/idf.txt.big");
             
        if type(stopdict) is str:
            jieba.analyse.set_stop_words(stopdict)
        else :
            jieba.analyse.set_stop_words("./data/dict/stop_words.txt")
        """
    
    
    def load_stop_words(self, stopwords_file):
        """
        Argument :

        stopwords_file : stop words file name
        
        
        loading stop words
        
        """

        self.stop_words = set()
        if type(stopwords_file) is str:
            filename = stopwords_file
        else :
            filename = util.get_default_stop_words_file()
           
        for word in codecs.open(filename, 'r', 'utf-8', 'ignore'):
            word = util.normalize_sentence(word.strip())

            if len(word) :
                self.stop_words.add(word)
        

    def load_suggest_words(self, suggestwords_file=None):
        """
        Argument :

        suggestwords_file : suggest words file name
        
        
        loading suggest words
        
        """

        if type(suggestwords_file) is str:
            filename = suggestwords_file
        else :
            filename = util.get_default_suggest_words_file()

        f = codecs.open(filename, 'r', 'utf-8')
        for word in f : 
            word = util.normalize_sentence(word.strip())
            if len(word) :
                if '\t' in word :
                    w = word.split('\t')
                    jieba.suggest_freq((w[0].strip(), w[1].strip()), True)
                else :
                    jieba.suggest_freq(word.strip(), True)
       

    def split_sentences(self, document):
        """
        arguments :
        
        document : a document
        

        return : split sentences  
        """
        
        document = util.as_text(document)
        if self.delimiters != None :
            res = [document]
            for sep in self.delimiters:
                document, res = res, []
                for seq in document:
                    res += seq.split(sep)
            sentences = [s.strip() for s in res if len(s.strip()) > 0]
        else :
            sentences = document.split('\n')
            ss = [self.normalize_sentence(s.strip()) for s in sentences]
            sentences = [s for s in ss if len(s) > 0]
        return sentences 



    def segment(self, sentences, wlen=0):
       
        """
        arguments :
        
        sentences : all sentences of a document 
        
        return sentences, words, words_no_stop, word_all_filters 
        
        """
        
        words_no_filter = []
        words_no_stop_words = []
        words_all_filters = []
        
        for s in sentences :
            if isinstance(s, string_types) :
                sentence = s
            else :
                sentence = s[0]     # document sentence format [text, number, type]
            
            sentence = sentence.strip()
            if len(sentence) < 2 :
                continue
            jieba_result = pseg.cut(sentence, HMM=False)
            jieba_result = [w for w in jieba_result]


            w_word_list = [w for w in jieba_result]
            word_list = [w.word.strip() for w in w_word_list if len(w.word.strip())>wlen]
            words_no_filter.append(word_list)
            
            # 去除 stop words
            word_list = [w for w in word_list if w not in self.stop_words]
            words_no_stop_words.append(word_list)

            # 去除 w.flag!='x'
            
            word_list = [w.word.strip() for w in w_word_list if w.flag!='x' and w.flag!='eng' and w.word not in self.stop_words]
            if len(word_list) > 0 :
                words_all_filters.append(word_list)



        return words_no_filter, words_no_stop_words, words_all_filters
                   
    def segment_words(self, sentences, wlen=0):
       
        """
        arguments :
        
        sentences : all sentences of a document 
        
        return sentences, words, words_no_stop, word_all_filters 
        
        """
        
        words_no_filter = []
        words_no_stop_words = []
        words_all_filters = []
        
        for s in sentences :
            if isinstance(s, string_types) :
                sentence = s
            else :
                sentence = s[0]     # document sentence format [text, number, type]
            
            sentence = sentence.strip()
            jieba_result = pseg.cut(sentence, HMM=False)
            jieba_result = [w for w in jieba_result]


            word_list = [w for w in jieba_result]
            word_list = [w for w in word_list if len(w.word.strip())>wlen]
            words_no_filter.append(word_list)
            
            # 去除 stop words
            word_list = [w for w in word_list if w.word not in self.stop_words]
            words_no_stop_words.append(word_list)

            # 去除 w.flag = 'x',  w.flag = 'eng'
            
            word_list = [w for w in word_list if w.flag!='x' and w.flag!='eng']
            if len(word_list) > 0 :
                words_all_filters.append(word_list)



        return words_no_filter, words_no_stop_words, words_all_filters

       
    def segment_ws(self, sentences):
       
        """
        arguments :
        
        sentences : all sentences of a document 
        
        return words
        
        """
        
        words = []

        for sentence in sentences :
        
            jieba_result = pseg.cut(sentence, HMM=False)
            jieba_result = [w for w in jieba_result]
            word_list = [w for w in jieba_result if len(w.word.strip())>0]
            words.append(word_list)


        return words
       

    
    
    
    