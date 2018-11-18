# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import sys,os
import codecs
import numpy

sys.path.append("../")

from docutone.core.document import LawDocument



class Summarize(object):
    
    CLUSTER_THRESHOLD = 5  # Distance between words to consider


    def __init__(self, filename = None):
        """
        """
        self.law_document = LawDocument()
        self.important_word = []
        self.top_n_scored = []
        self.mean_scored = []
        
        
    def load_keywords(self) :
 
        filename = self.law_document.get_keywords_file_name()
        f = codecs.open(filename, 'r', 'utf-8')

        self.important_word = []
        for line in f :
            if line.strip() :
                tokens = line.strip().split(" ")
                if tokens[0].strip() :
                    word = [tokens[0].strip()]
                        
                    if len(tokens) > 1 and tokens[1].strip() :
                        word.append(int(tokens[1].strip()))
                    else :
                        word.append(0)
            
                    if len(tokens) > 2 and tokens[2].strip() :
                        word.append(int(tokens[2].strip()))

                    self.important_word.append(word)
        f.close()
        return self.important_word

        
    def _cluster_sentences(self, s, important_word):
        
        word_idx = []
        clusters = []
        # For each word in the keyword list
        for [w, n] in important_word:
            word = w.strip()
            if word : 
                try:
                    index = s.index(word)
                    word_idx.append(index)
                    if n ==1 :
                        index = index + 1
                        word_idx.append(index)
                except ValueError: # w not in this particular sentence
                    pass
    
        # Using the word index, compute clusters by using a max distance threshold, 
        # for any two consecutive words
        if len(word_idx ) > 0: 
            word_idx.sort()
            cluster = [word_idx[0]]
            i = 1
            while i < len(word_idx) :
                if word_idx[i] - word_idx[i - 1] < self.CLUSTER_THRESHOLD:
                    cluster.append(word_idx[i])
                else:
                    clusters.append(cluster[:])
                    cluster = [word_idx[i]]
                i += 1
            clusters.append(cluster)
            
        return clusters
    
    
    
    def _score_sentences(self, sentences, important_word):
        scores = []
        sentence_idx = -1
    
        for [s, idx, type] in  sentences:
            sentence_idx += 1
            clusters = self._cluster_sentences(s, important_word)
            
            if len(clusters) == 0:  
                continue
            # Score each cluster. The max score for any given cluster is the score 
            # for the sentence
    
            max_cluster_score = 0
            for c in clusters:
                significant_words_in_cluster = len(c)
                total_words_in_cluster = c[-1] - c[0] + 1
                score = 1.0 * significant_words_in_cluster \
                    * significant_words_in_cluster / total_words_in_cluster
                if score > max_cluster_score:
                    max_cluster_score = score
    
                if score > max_cluster_score:
                    max_cluster_score = score
    
            scores.append((sentence_idx, score))
    
        return scores



    

    def analyze(self, filename, withWeight=True, encoding="utf-8"):
    
        self.law_document.analyze_file(filename)
        
        self.load_keywords()
       
        
        scored_sentences = self._score_sentences(self.law_document.sentences, self.important_word)
    
        # Summaization Approach 1:
        # Filter out non-significant sentences by using the average score plus a
        # fraction of the std dev as a filter
    
        avg = numpy.mean([s[1] for s in scored_sentences])
        std = numpy.std([s[1] for s in scored_sentences])
        
        ff = avg + 0.5 * std
        self.mean_scored = []
        for (sent_idx, score) in scored_sentences :
            if score > ff :
                self.mean_scored.append((sent_idx, score))
        
    
        # Summarization Approach 2:
        # Another approach would be to return only the top N ranked sentences
        
        self.top_n_scored = sorted(scored_sentences, key=lambda s: s[1])
        self.top_n_scored = sorted(self.top_n_scored, key=lambda s: s[0])
    
        

    def write_top_summarize(self, show_nb = 5, outputfile = None, mode = "a+"): 
        if outputfile != None :
            f = codecs.open(outputfile, mode, 'utf-8')
            f.write(' '.join(self.law_document.document_title) + "\n")
            f.write('\n'.join(self.law_document.table_contents))
            f.write("\n\n摘要 ： \n")
                
            
        else :
            f = None
            print( '摘要 ： ' + ' '.join(self.law_document.document_title)  + "\n")
        
        
        
        n_sentence = 0
        for (idx, score) in self.top_n_scored:
            if n_sentence < show_nb :
                sentence = self.law_document.get_document_chapiter(idx)
                if sentence :
                    if f != None :
                        f.write(sentence+"\n\n")
                    else :                  
                        print (sentence)
                        print ("="*20)
                    
                    n_sentence += 1
            else :
                if f != None :
                    f.write("\n" + "*"*30 + "\n\n")
                break
                
                
    def write_summarize(self, show_nb = 5, outputfile = None, mode="a+"): 
        
        if outputfile != None :
            f = codecs.open(outputfile, mode, 'utf-8')
            f.write('摘要 ： \n' + ' '.join(self.law_document.document_title) + "\n")
        else :
            f = None
            print( '摘要 ： ' + ' '.join(self.law_document.document_title)  + "\n")

        self.law_document.init_sentence_index()
        n_sentence = 0
        for (idx, score) in self.mean_scored:
            if n_sentence < show_nb :
                sentence = self.law_document.get_document_chapiter(idx)
                if sentence :
                    if f != None :
                        f.write(sentence)
                    else :                  
                        print (sentence)
                        print (" "*20)
                    n_sentence += 1
                    
            else :
                if f != None :
                    f.write("*"*30)
                break

   
if __name__ == '__main__':
        
    sm = Summarize()
    
    sm.analyze("../text/zhangcheng.txt")
    sm.write_top_summarize(5, "../temp/out.txt", "w+")
    #sm.write_summarize()
   
    sm.analyze("../text/hetong.txt")
    sm.write_top_summarize(5, "../temp/out.txt")
    
    sm.analyze("../text/hezihetong.txt")
    sm.write_top_summarize(5, "../temp/out.txt")
    #sm.write_top_summarize()
  
    






