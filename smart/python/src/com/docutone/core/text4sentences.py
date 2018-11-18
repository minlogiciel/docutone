#-*- encoding:utf-8 -*-
from __future__ import (unicode_literals)


import sys

sys.path.append("../")

from docutone.core.segmentation import Segmentation
from docutone.utils import util
from docutone.core.document import LawDocument

class Text4Sentences(object):
    

    def __init__(self, stopwords_file = None):
        """
        Keyword arguments:
        stopwords_file :    stopwords file name
        """
        
        self.pagerank_config = {'alpha': 0.85,}
        
        self.seg = Segmentation(stopwords_file=stopwords_file)
        self.law_document = LawDocument()
        self.sentences = None
        self.words_no_filter = None     # 2维列表
        self.words_no_stop_words = None
        self.words_all_filters = None
        
        self.key_sentences = None


    def create_segment_sentences(self, sentences, sim_func=util.get_similarity):
        
        """
        Keyword arguments:
        
        sentences : sentences of document
        
        sim_func 指定计算句子相似度的函数。
        
        """
            
        self.words_no_filter, self.words_no_stop_words,  self.words_all_filters = self.seg.segment(sentences)
        self.sentences = sentences

        self.key_sentences = util.sort_sentences(sentences = self.sentences,
                                                 words     = self.words_no_filter,
                                                 sim_func  = sim_func,
                                                 pagerank_config = self.pagerank_config)

  
    def analyze_file(self, filename, encoding='utf-8'):
        
        """
        Keyword arguments:
        
        filename : input file name
        
        
        """
        
        f = self.law_document.create_document(filename=filename)
        
    
        self.create_segment_sentences(self.law_document.get_segmented_document())
        
        
           
    def get_key_sentences(self, num = 6):
        """
        num : 个句子用来生成摘要。

        Return: important sentences。
        """
        
        result = []
        count = 0
        for item in self.key_sentences:
            if count >= num:
                break
            result.append(item)
            count += 1
        return result
    
    
    def show_key_sentences(self):
    
        for item in self.get_key_sentences(2) :
            [sentence, idx, stype] = item['sentence']
            print(sentence)
            print ("="*20)
            print(self.law_document.get_document_chapiter(idx, chapiter=True))
            print ("--"*20)

   

if __name__ == '__main__':
    
    tw = Text4Sentences()    
    tw.analyze_file("../text/hetong/hetong.txt")
    tw.show_key_sentences()

    pass