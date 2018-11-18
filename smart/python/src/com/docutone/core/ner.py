# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import sys,os, re, codecs

sys.path.append("../")

from nltk.tag.stanford import StanfordNERTagger

from docutone.utils import util, variables
from docutone.core.segmentation import Segmentation
from docutone.utils import docutonelocate
from docutone import config



SOURCE_CRF = config.NER_PATH + 'english.all.3class.distsim.crf.ser.gz'
SOURCE_CRF = config.NER_PATH + 'chinese.misc.nodistsim.crf.ser.gz'
SOURCE_CRF = config.NER_PATH + 'chinese.misc.distsim.crf.ser.gz'
SOURCE_JAR = config.JAR_PATH + 'stanford-ner-3.7.0.jar'


class NER(object):
    

    def __init__(self):
        """
        """
        self.ORG_END_NAME = self._load_ner_words("nerendname.txt") 
        self.NER_STOP_STARTS = self._load_ner_words("nerstopstart.txt") 
        self.NER_STOP_WORDS = self._load_ner_words("nerstopwords.txt") 

        self._seg = Segmentation()        
        self._tagger = StanfordNERTagger(SOURCE_CRF, SOURCE_JAR)

        self._ner = self.load_ners()
        

        self.new_ner = {}
 
 
 
    def _load_ner_words(self, filename) :
     
        words = set()
        fname = util.get_defined_ner_file(filename)
        if os.path.exists(fname) :
            f = codecs.open(fname, 'r', 'utf-8')
            for word in f :
                word = word.strip() 
                if len(word) > 0 :
                    if word[0] == '#' :
                        pass 
                    else :
                        words.add(word)
            f.close()
        return words
    
    def load_ners (self) :
     
        all_tags = {}
        filename  = util.get_ner_filename()
        if os.path.exists(filename) :
            f = codecs.open(filename, 'r', 'utf-8')
        
            for line in f :
                line = line.strip() 
                if len(line) > 0 :
                    if line[0] == '#' :
                        pass 
                    elif ' ' in line :
                        name, tag = line.split(' ', 1)
                        all_tags[name] = tag
            f.close()
        else :
            all_tags['上海三特金属贸易有限公司'] = 'ORG'
             
        return all_tags

    def write_ner(self): 
        filename = util.get_ner_filename()
        f = codecs.open(filename, 'a+', encoding='utf-8')
        for name,  tag in self.new_ner.items() :
            f.write("%s %s\n" % (name, tag))
 
        f.close()
        
    def write_new_ner(self, otype ="ORG"):
        filename = util.get_ner_filename()[0:-4]+ "_"
        if otype == None :
            filename += 'full.txt'
        else :
            filename += otype.lower()+ '.txt'
        f = codecs.open(filename, 'w', encoding='utf-8')
        
        sorted_tab = sorted(self._ner.items(), key=lambda x: x[0])
        #for name,  tag in sorted_tab.items() :
        for elem in sorted_tab :
            name = elem[0]
            tag = elem [1]
            if otype == tag or otype == None:
                f.write("%s %s\n" % (name, tag))
 
        f.close()
        
    def _is_clause_title(self, sentence):
        if re.search('第.{1,5}条', sentence) or re.search('第.{1,5}章', sentence) or re.search('第.{1,5}节', sentence) or re.search('第.{1,5}次', sentence) :
            return True
        return False
        
    def get_ner(self, name, tag) :
         
        str_ner = name.replace("/ORG", "").replace("/GPE","").replace("/O","")
        if str_ner in self.NER_STOP_STARTS :
            return False
        elif tag == "ORG" :
            if self._is_org_end(str_ner) and not self._is_clause_title(str_ner):
                print("%s %s" % (name, tag))
                return str_ner
        return False    

    '''
    add new NER
    '''
    def add_ner(self, name, tag) :
         
        str_ner = self.get_ner(name, tag)
        if str_ner :
            # searching in current NER list
            for s in self._ner.keys() :
                if str_ner in s :
                    break
        
            self._ner[str_ner] = tag
            self.new_ner[str_ner] = tag
    
        
    
    def _is_org_end(self, word):
        for name in self.ORG_END_NAME :
            if word.endswith(name) :
                return True
        return False

    def has_org_end(self, word):
        return self._is_org_end(word)
    
    def _is_ner_stop_start(self, word):
        for name in self.NER_STOP_STARTS :
            if word == name :
                return True
        if word in util.digital_char  or word.isdigit() or word in util.digital_romain:
            return True
        elif not self._is_valid_char(word) :
            return True
        return False
    

    def _is_ner_stop_word(self, word):
        for name in self.NER_STOP_WORDS :
            if word == name :
                return True
        if word.isdigit() : 
            return True
        if self._is_clause_title(word) :
            return True
        return False
    
    def _is_valid_char(self, word):
        w = word.strip()
        if len(w) == 1: 
            if w in util.sentence_delimiters or w in util.word_delimiters or w in util.simple_p :
                return False
            elif w in util.double_p :
                return False
        elif len(w) == 0 :
            return False
        return True
    
    def _is_delimiter(self, w):
        if len(w) == 1: 
            if w in util.sentence_delimiters or w in util.word_delimiters or w in util.simple_p :
                return True
            elif w == '(' or w == ')' or w == '(' or w == ')' :
                # NER name can have these
                return False
            elif w in util.double_p :
                return True
        return False
    
    def _is_name_delimiter(self, w):
        if len(w) == 1: 
            if w == '和' or w == '与' or w == '及' or w == '对':
                return True
        return False
 
    def get_sentence_named_tag(self, sentence) :

        output_tag_name = 'O'
        string = ""
        found = 0
        sttag = self._tagger.tag(sentence)
        for word, tag_name in sttag :
            word = word.strip();
            if self._is_delimiter(word) or self._is_name_delimiter(word) :
                if found > 2 and output_tag_name == 'ORG':
                    self.add_ner(string, output_tag_name)
                output_tag_name = 'O'
                string = ""
                found = 0
                continue
            elif found == 0 and self._is_ner_stop_start(word) :
                continue
            elif self._is_ner_stop_word(word) :
                output_tag_name = 'O'
                string = ""
                found = 0
                continue
            if tag_name == 'ORG' :
                string += word + "/ORG"
                output_tag_name = tag_name
                if self._is_org_end(word) :
                    if found > 1 :
                        self.add_ner(string, tag_name)
                    # reset string 
                    string = ""
                    found = 0
                    output_tag_name = 'O' 
                else :
                    found += 1
            elif tag_name == 'GPE' :
                string += word + "/GPE"
                if output_tag_name == tag_name :
                    self.add_ner(string, tag_name)
                elif not self._is_ner_stop_start(word) : 
                    self.add_ner(word, tag_name)
                    if output_tag_name == "O" :
                        output_tag_name = tag_name
                found += 1
            elif tag_name == 'PRESON' :
                if output_tag_name == tag_name :
                    string += word
                    self.add_ner(string, tag_name)
                else :
                    
                    self.add_ner(word, tag_name)
                    if found > 0 and output_tag_name == 'ORG' :
                        self.add_ner(string, output_tag_name)
                    string = word
                output_tag_name = tag_name
            else :
                if output_tag_name != 'O' :
                    if found > 0 and found < 10 :
                        string += word + "/O"
                        found += 1
                if string and (self._is_org_end(word) or found >=10) :
                    if self._is_org_end(word) :
                        output_tag_name = 'ORG'
                    self.add_ner(string, output_tag_name)
                    # reset after add to list 
                    string = ""
                    found = 0
                    output_tag_name = 'O'
           
        ''' add last NER tag '''
        if len(string) and output_tag_name != 'O' :
            self.add_ner(string, output_tag_name)


    def get_sentence_ner(self, sentence, named_tags) :

        
        output_tag_name = 'O'
        string = ""
        found = 0
        sttag = self._tagger.tag(sentence)
        for word, tag_name in sttag :
            word = word.strip();
            if self._is_delimiter(word) or self._is_name_delimiter(word) :
                if found > 2 and output_tag_name == 'ORG':
                    string = self.get_ner(string, output_tag_name)
                    if string and string not in named_tags:
                        named_tags.append(string)
                output_tag_name = 'O'
                string = ""
                found = 0
                continue
            elif found == 0 and self._is_ner_stop_start(word) :
                continue
            elif self._is_ner_stop_word(word) :
                output_tag_name = 'O'
                string = ""
                found = 0
                continue
            if tag_name == 'ORG' :
                string += word + "/ORG"
                output_tag_name = tag_name
                if self._is_org_end(word) :
                    if found > 1 :
                        string = self.get_ner(string, output_tag_name)
                        if string and string not in named_tags :
                            named_tags.append(string)
                    # reset string 
                    string = ""
                    found = 0
                    output_tag_name = 'O' 
                else :
                    found += 1
            elif tag_name == 'GPE' :
                string += word + "/GPE"
                if output_tag_name == tag_name :
                    self.add_ner(string, tag_name)
                elif not self._is_ner_stop_start(word) : 
                    self.add_ner(word, tag_name)
                    if output_tag_name == "O" :
                        output_tag_name = tag_name
                found += 1
            elif tag_name == 'PRESON' :
                if output_tag_name == tag_name :
                    string += word
                    self.add_ner(string, tag_name)
                else :
                    
                    self.add_ner(word, tag_name)
                    if found > 0 and output_tag_name == 'ORG' :
                        self.add_ner(string, output_tag_name)
                    string = word
                output_tag_name = tag_name
            else :
                if output_tag_name != 'O' :
                    if found > 0 and found < 10 :
                        string += word + "/O"
                        found += 1
                if string and (self._is_org_end(word) or found >=10) :
                    if self._is_org_end(word) :
                        output_tag_name = 'ORG'
                        string = self.get_ner(string, output_tag_name)
                        if string and string not in named_tags :
                            named_tags.append(string)
                    # reset after add to list 
                    string = ""
                    found = 0
                    output_tag_name = 'O'
           
        ''' add last NER tag '''
        if len(string) and output_tag_name != 'O' :
            string = self.get_ner(string, output_tag_name)
            if string and string not in named_tags :
                named_tags.append(string)

        return named_tags

    def file_named_tag(self, filename) :
        from docutone.core.document import LawDocument
        if (filename.endswith(".txt")) :
            ofile = filename
        else :
            ofile = docutonelocate.convert_file(filename)
        lawdoc = LawDocument()
        document = lawdoc.get_fusion_document(ofile)

        self.new_ner = {}
        for sentence in document :
            self.get_sentence_named_tag(sentence)

        self.write_ner()
        

    def create_ner_in_directory(self, path) :

        for fname in sorted(os.listdir(path)):
            fpath = os.path.join(path, fname)
            if variables.noloaddir(fname):
                continue
            if os.path.isdir(fpath):
                print("training => " + fname)
                self.create_ner_in_directory(fpath)
            elif fname.endswith('.txt') :
                self.file_named_tag(fpath)
                pass
    
    
    def create_ner(self, fpath) :
        # first level only for directory 
        for name in sorted(os.listdir(fpath)):
            if variables.noloaddir(name):
                continue
            path = os.path.join(fpath, name)
            if os.path.isdir(path):
                print("training => " + name)
                self.create_ner_in_directory(path)
            elif path.endswith('.txt') :
                self.file_named_tag(path)
                
                
    def test(self):    
        from scikitcrf_ner import entityRecognition as ner
        ner.train("sample_train.json")
        entities = ner.predict("show me some Indian restaurants")
        print(entities)
        
    def file_clean(self, filename) :
        from docutone.core.document import LawDocument
        if (filename.endswith(".txt")) :
            ofile = filename
        else :
            ofile = docutonelocate.convert_file(filename)
        lawdoc = LawDocument()
        document = lawdoc.get_fusion_document(ofile)

        for sentence in document :
            print (' '.join(sentence))

        
        
        
if __name__ == '__main__':
        
    fpath = variables.HOME_DIR + '/data/terms/Template/TEXT'
    fpath1 = variables.HOME_DIR + '/data/Corpus/TEXT/股东协议、章程'
    fpath2 = variables.HOME_DIR + '/data/Corpus/TEXT/决议'
    fpath3 = variables.HOME_DIR + '/data/Corpus/TEXT/单据'
    
    fname = fpath + "/司法、行政决定/起诉书/起诉书2.txt"
    fname = fpath1 + '/章程/章程-无标注文件（共3248）/创业环保公司章程(2007.11.08）.DOC.txt'
    #fname = fpath1 + '/章程/章程-无标注文件（共3248）/创业环保章程（2002.10.10）.PDF.txt'

    ner = NER()
    '''
    ner.create_ner(fpath2)
    ner.create_ner(fpath3)
    '''
    #ner.write_new_ner("ORG")

    #ner.file_named_tag(fname)
    ner.file_clean(fname)
    
    
    print( "---- end ----")






