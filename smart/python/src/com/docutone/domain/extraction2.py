# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import sys,os
import codecs
import numpy
from PIL.WmfImagePlugin import word

sys.path.append("../")

from docutone.core.document import LawDocument
from docutone.core.segmentation import Segmentation

from docutone.utils import util



class Extraction(object):
    

    def __init__(self):
        """
        """
        self.law_document = LawDocument()        
        self.all_keywords = util.load_legalterm_type()
       

    
    def score_sentences(self, sentences, important_word):
        
        scores = {}
    
        for s in  sentences:
            for word in important_word:
                word = word[0]
                if word in s :
                    index = s.index(word)                 
                    index = index + len(word)
                    
                    sentence = s[index:]
                    seg = Segmentation()                 
                    #compare prev sentence
                    if word in scores :
                        n = scores[word][1]
                        if index < n :
                            scores[word] = [sentence, index]
                    else :
                        scores[word] = [sentence, index]
                    # find only one word 
                    break

        return scores



    

    def extraction(self, filename, doctype='营业执照', encoding="utf-8"):
    
        document = self.law_document.get_segment_document(filename) [0]
        sentences = []
        for sentence in document :
            s = ""
            for word in sentence :
                if word in util.sentence_delimiters :
                    s += word + ' '
                else :
                    s += word
            sentences.append(s)
        
                
        important_words = self.all_keywords[doctype]
        scored_sentences = self.score_sentences(sentences, important_words)
        
        return scored_sentences
                

    def extraction_documents(self, fpath, doctype='营业执照') :
    
        data = {}
        for name in sorted(os.listdir(fpath)):
            if name.endswith('.txt') :
                fname = os.path.join(fpath, name)
                data[fname] = self.extraction(fname, doctype) 

        return data
 
    def write_result(self, scored_sentences, important_word, outputfile = None): 
        f = None

        for word in important_word :
            word = word[0]
            if word in scored_sentences :
                sentence = scored_sentences[word][0]

                if f != None :
                    f.write(sentence)
                else :                  
                    print (word + " : " + sentence)
        
        print ("="*40)
 
    def write_documents_info(self, data, doctype) :
    
        important_words = self.all_keywords[doctype]
        for fname, scored_sentences in data.items() :
            self.write_result(scored_sentences, important_words)

    
    
        
    def extraction_ner(self, st, filename, doctype='营业执照') :
    
        document = self.law_document.get_segment_document(filename) [0]

        prevtype = 'O'
        string = ""
        for sentence in document :
            sttag = st.tag(sentence)
            for word, type in sttag :
                if type == 'GPE' or  type == 'ORG' or type == 'PRESON' :
                    if prevtype == 'O' or prevtype == type :
                        string += word
                        prevtype = type
                    else :
                        print('%s %s ' % (string, prevtype))
                        string = ""
                        prevtype = 'O'
                else :
                    if len(string) > 0 :
                        print('%s %s ' % (string, prevtype))
                    string = ""
                    prevtype = 'O'


    def test_ner(self, fpath, doctype='营业执照') :
        from nltk.tag.stanford import StanfordNERTagger
        st = StanfordNERTagger('D:/WORK/docutone/java/classifiers/chinese.misc.distsim.crf.ser.gz', 'D:/WORK/docutone/java/lib/stanford-ner-3.7.0.jar')
     
        data = {}
        for name in sorted(os.listdir(fpath)):
            if name.endswith('.txt') :
                fname = os.path.join(fpath, name)
                data[fname] = self.extraction_ner(st, fname, doctype) 

        return data

    def test_polyglot1(self) :
        import polyglot
        from polyglot.text import Text, Word
     
        text = Text("Bonjour, Mesdames.")
        print("Language Detected: Code={}, Name={}\n".format(text.language.code, text.language.name))

        text = Text("第一条  机动车第三者责任保险合同（以下简称本保险合同）由保险条款、投保单、保险单、批单和特别约定共同组成。 "
                    "本保险合同争议处理适用中华人民共和国法律。")
        #print(text.entities)
        """
        print("{:<16}{}".format("Word", "POS Tag")+"\n"+"-"*30)
        for word, tag in text.pos_tags:
            print(u"{:<16}{:>2}".format(word, tag))
        """
        word = Word("Obama", language="en")
        word = Word("中华人民共和国", language="zh")
        print("Neighbors (Synonms) of {}".format(word)+"\n"+"-"*30)
        for w in word.neighbors:
            print("{:<16}".format(w))
            print("\n\nThe first 10 dimensions out the {} dimensions\n".format(word.vector.shape[0]))
            print(word.vector[:10])
            
    def test_polyglot(self) :
        from polyglot.mapping import Embedding
        embeddings = Embedding.load("/home/rmyeid/polyglot_data/embeddings2/en/embeddings_pkl.tar.bz2")
        
        neighbors = embeddings.nearest_neighbors("green")

        
        
if __name__ == '__main__':
        
    testfiles = {
        'D:\\DOCUTONE\\Corpus\\TEXT\\证照与批文\\营业执照' :  '营业执照' ,
        'D:\\DOCUTONE\\Corpus\\TEXT\\证照与批文\\建设工程规划许可证' : '建设许可证', 
        'D:\\DOCUTONE\\Corpus\\TEXT\\证照与批文\\商品房销售(预售)许可证' : '土地房产许可证'
    }
    norm = Extraction()
   
    #norm.test_polyglot()
   
    for fpath , doctype in testfiles.items() :
        """
        data = norm.extraction_documents(fpath, doctype)
        print("="*20 + doctype + "="*20)
        norm.write_documents_info(data, doctype)
        """
        norm.test_ner(fpath, doctype)
        pass
    
    
  






