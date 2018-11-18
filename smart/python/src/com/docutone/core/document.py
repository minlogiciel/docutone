# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

import os, sys, codecs, re



sys.path.append("../")

from docutone.core.segmentation import Segmentation

from docutone.utils import util, variables, dtn_sentence, synonyms

#from docutone.core.ner import NER


DT_PATTERN = "^第[\d一二三四五六七八九十百]{1,7}条"
DT_PATTERN = "^第[\d一二三四五六七八九十百]{1,7}条"
DZ_PATTERN = "^第[\\d一二三四五六七八九十百]{1,7}章"
DJ_PATTERN = "^第[\\d一二三四五六七八九十百]{1,7}节"
DN_PATTERN = '^[一二三四五六七八九十百]{1,7}[\.、．]{1}'
DD_PATTERN = '^[0-9]{1,3}[^\.\d%,)]{1}'
DD2_PATTERN = '^[0-9]{1,3}[\.．、][\D]{1}'  
DDD_PATTERN = '^[0-9]{1,3}\.[0-9]{1,3}[^\.%]'
DDD2_PATTERN = '^[0-9]{1,3}\.[0-9]{1,3}\.[\D]{1}'
DDDD_PATTERN = '^[0-9]{1,3}(\.[0-9]{1,3}){2,4}'



def trim(sentence):
    return sentence.replace(' ', '').replace('\t','')

def is_clause_start(sentence) :
    if sentence.startswith('[[') or sentence.startswith('【【') :
        return True
    elif '[[' in sentence and sentence.index('[[') < 2 :
        return True
    elif '【【' in sentence and sentence.index('【【') < 2 :
        return True
    else :
        return False 

def is_clause_end(sentence) :
    if sentence.endswith(']]')  or sentence.endswith("】】")  :
        return True
    else :
        return False 
    
def sentencesTowords(sentences, toLine= True):

    seg = Segmentation()
    words = seg.segment(sentences)[0]
    if toLine :
        sect = ""
        for word in words :
            sect += " ".join(word) + ' '
        return sect
    else :
        return words
    
def get_file_sentences(filename, is_test=True, encoding="utf-8"):
     
    f = codecs.open(filename, 'r', encoding, 'ignore')
    
    sentences = []
    for s in f :
        s = util.normalize_sentence(s)
        if len(s) > 0 :
            if is_test and (is_clause_start(s) or is_clause_end(s)) :
                pass
            else :
                sentences.append(s)
    
    f.close()

    return sentences


def get_sentences_words(sentences):
    
    norm_sentences = []
    for s in sentences :
        s = util.normalize_sentence(s)
        if is_clause_start(s) or is_clause_end(s) :
            pass
        else :
            norm_sentences.append(s)
 
    seg = Segmentation()
    allwords = seg.segment(norm_sentences)[2]
    doc_words = []
    for words in allwords :
        for word in words :
            doc_words.append(word)
    return doc_words


def get_document_words(filename):

    sentences = get_file_sentences(filename)
    return get_sentences_words(sentences)


   
''' analyse document, create a list of section '''
class Definitions(object):

    def __init__(self, title='定义'):

        self.title = trim(title)
        self.definitions = {}
        pass
    
    def add_definition(self, name, value):
        if value.strip() :
            if ' ' in name :
                name = name.split(' ')[-1]
                
            
            if name in self.definitions.keys() :
                self.definitions[name].append(value)
            else :
                self.definitions[name] = [value]

class Signatories (object):
    def __init__(self, title='定义'):

        self.title = trim(title)
        self.signatories = {}
        pass
    
    def add_signatorie(self, name, value):
        if value.strip() :
            if ' ' in name :
                name = name.split(' ')[-1]
                
            
            if name in self.definitions.keys() :
                self.signatories[name].append(value)
            else :
                self.signatories[name] = [value]
    


class Section(object):
    
    def __init__(self, label, num, title, level):
        
        
        self.title = title
        self.label = label
        self.num = num
        self.level = level
        self.sentences = []
        self.verified = False  # verified term name is OK
        
    def setVerified(self, verified):
        self.verified = verified
        
    def addSentence(self, s):
        self.sentences.append(s)
        
    def toString(self):
        # ss = self.title
        ss = ""
        for s in self.sentences :
            if type(s) == Section :
                ss += s.toString()
            elif isinstance(s, str) :
                ss += s
            else :
                ss += s[0]
        if len(ss.strip()) == 0 :
            ss = self.title
        return ss
    
    def toWords(self): 
        ss = []
        ss.append(self.title)
        for s in self.sentences :
            if type(s) == Section :
                ss.append(s.title)
                for s1 in s.sentences :
                    ss.extend(s1[0])
            elif isinstance(s, str) :
                ss.append(s)
            else :
                ss.append(s[0])
        return sentencesTowords(ss)
        
    
    def display(self, title_num):
        # ss = self.title
        if (title_num) :
            if title_num[-1] == '.' :
                path = title_num + str(self.num)
            else :
                path = title_num + "." + str(self.num)
        else :
            path = str(self.num) + "."
        ss = path + " " + self.title + "\n"
        for s in self.sentences :
            if type(s) == Section :
                ss += s.display(path)
            elif isinstance(s, str) :
                ss += s + "\n"
            else :
                ss += s[0] + "\n"
        return ss
                
    def toLists(self):
        ss = []
        for s in self.sentences :
            if type(s) == Section :
                ss.extend(s.toLists())
            else :
                if isinstance(s, str) :
                    ss.append(s)
                else :
                    ss.append(s[0])
        return ss
                 
    
 

class LawDocument(object):
    
    END_DOCUMENT = -1
    START_DEFINED_CLAUSE = -2
    END_DEFINED_CLAUSE = -3
    IS_DEFINITION = -4
    DOCUMENT_END_FLAG = ["附件清单", "附件1", "附件一"]
    DOCUMENT_TITLE_FLAG = ["合同", "协议", "章程"]
    

    def __init__(self, filename=None):
        """
        filename : document file name
        """
        
        self.document_type = None
        self.document_keywords = None
        self.file_name = filename
        self.table_contents = []
        self.document_header = []
        self.document_body = []
        self.document_footer = []
        self.sections = []
        self.chapitre = {}
        self.document_name = None;
        self.document_date = None;
        self.curr_chapiter = 0
        self.curr_term_num = 1
        self.level = 2

        #self._ner = NER()
        self.societes = []
        self.seg = Segmentation()
        self.seg.load_suggest_words()
        self._is_contract_doc = 1;

    def get_segment_document(self, filename=None, contents=None, encoding="utf-8"):
        """
        Arguments :
        
        filename : input document file name
        
        contents : document text
        
        
        return list sentences of document
        
        """
        if filename != None :
            f = codecs.open(filename, 'r', encoding, 'ignore')
            sentences = [s for s in f if len(s.strip()) > 0]
            f.close()
        else :
            sentences = contents.split("\n")
           
        norm_sentences = [util.normalize_sentence(s) for s in sentences]

        return self.seg.segment(norm_sentences)


        
    
 
    def _set_document_title(self, section):
        if section.title == '文件名称': 
            self.document_name = section.toString();
            
            
    def is_definition(self, sentence):
        ret = 0
        st = self.parser_sentence(sentence)
        if st :
            title = trim(st[2])
            if title == "定义" :
                ret = 1
        else :
            title = trim(sentence)
            if title.startswith("定义") or title.startswith("释义")  :
                ret = 1
        return ret
    
    
    def get_date(self, sentence):
        content = None
        s = trim(sentence)
        m = re.search('.{1,4}年.{0,2}月.{0,2}日', s)
        if m :
            content = m.group(0)
        m = re.search('.{1,4}年.{0,2}月', s)
        if m :
            content = m.group(0)

        content = None #@ TODO
        return content
    
    
    def has_table_contents(self, sentence):
        ret = 0
        if len(sentence) < 10 :
            title = trim(sentence)
            if ("目录" == title) :
                ret = 1
        return ret


    def parser_sentence(self, sentence):
        """
        Arguments:
        sentence : sentence       
        return type of line : D, DD, DDD, T, Z, J, C
        
        """

        s = sentence.strip()      
        # format 1
        m = re.search(DD2_PATTERN, s)
        if m :
            content = m.group(0)
            n = len(content)-1
            return 'D', s[0:n], s[n:]
        
        m = re.search(DD_PATTERN, s)
        if m :
            content = m.group(0)
            n = len(content)-1
            return 'D', s[0:n], s[n:]
        
       
        m = re.search(DDD2_PATTERN, s)
        if m :
            content = m.group(0)
            n = len(content)-1
            return 'DD', s[0:n], s[n:]
        
        m = re.search(DDD_PATTERN, s)
        if m :
            content = m.group(0)
            n = len(content)-1
            return 'DD', s[0:n], s[n:]
           
        # format 1.1.1        
        m = re.search(DDDD_PATTERN, s)
        if m :
            return None
           
        # 第.... 条 title
        m = re.search(DT_PATTERN, s)
        if m :
            content = m.group(0)
            n = s.index(content) + len(content)
            return 'T', content, s[n:].strip()
                        
        # 第.... 章 title
        m = re.search(DZ_PATTERN, s)
        if m :
            content = m.group(0)
            n = s.index(content) + len(content)
            return 'Z', content, s[n:].strip()
        # 第.... 节 title
        m = re.search(DJ_PATTERN, s)
        if m :
            content = m.group(0)
            n = s.index(content) + len(content)
            return 'J', content, s[n:].strip()
           
        # 一二三... title
        m = re.search(DN_PATTERN, s)
        if m :
            content = m.group(0)
            n = s.index(content) + len(content)
            return 'C', content, s[n:].strip()
        
        return None

    def get_sentence_type(self, sentence, chapitres):
        """
        Arguments:
        
        sentence : a sentence
        
        titles : defined chapiter title 
        
        return type of line : 0: normal sentence, 1: first level title, 2: second level title, -1 end document body
        
        """
        ret = 0
        s = trim(sentence)
                    
        if self._is_document_end(s) :
            return self.END_DOCUMENT, '', ''
                
        if is_clause_start(s) :
            return self.START_DEFINED_CLAUSE, '', s[2:]
        
        if is_clause_end(s) :
            return self.END_DEFINED_CLAUSE, '', ''

        if self.is_definition(s): 
            return self.IS_DEFINITION,  '', ''
        
        if self._is_contract_doc :
            st = self.parser_sentence(s)
            if st != None :
                ret = 1
                if len(chapitres) == 0 : 
                    chapitres[st[0]] = 1
                if st[0] in chapitres.keys() : 
                    ret = chapitres[st[0]]
                else :
                    ret = len(chapitres) + 1
                    chapitres[st[0]] = ret
                     
            # only 2 level 
            if ret > self.level :
                ret = 0
            if ret == 0 :
                return ret, '', ''
            else :
                return ret, st[1], st[2]
        else :
            return 0, '', ''

    def add_document_table_contents(self, sentence) :
        """
        Arguments :
        
        sentences : sentences of a document
        add chapter title to table content
        """          

        new_cont = [c for c in sentence.strip().split(' ') if len(c.strip()) > 0 and c.isdigit() == False]
        found = 0
        for content in self.table_contents :
            found = 1
            if len(content) > len(new_cont) :
                found = 0
                break
                
            for n in range(0, len(content)):
                if content[n] != new_cont[n]:
                    found = 0
                    break
            if found == 1 :
                break
        if found == 0:
            self.table_contents.append(new_cont)
    
    def _add_definition(self, sentences, start, nb_sentence):
        ret = start
        self.definitions = Definitions()
        for index in range(start, nb_sentence) :
            sentence = sentences[index]
            if len(sentence) > 0 :
                stype = self.get_sentence_type(sentence, self.chapitre)
                if (stype[0] == 1):
                    break
                elif ':' in sentence :
                    title, content = sentence.split(':', 1)
                    self.definitions.add_definition(title, content)
                    ret = index
                elif '：' in sentence :
                    title, content = sentence.split('：', 1)
                    self.definitions.add_definition(title, content)
                    ret = index
                    pass

        return ret
    
    def _add_signatorie(self, sentences, start, nb_sentence):
        ret = start
        self.definitions = Definitions()
        for index in range(start, nb_sentence) :
            sentence = sentences[index]
            if len(sentence) > 0 :
                stype = self.get_sentence_type(sentence, self.chapitre)
                if (stype[0] == 1):
                    break
                elif ':' in sentence :
                    title, content = sentence.split(':', 1)
                    self.definitions.add_definition(title, content)
                    ret = index
                elif '：' in sentence :
                    title, content = sentence.split('：', 1)
                    self.definitions.add_definition(title, content)
                    ret = index
                    pass

        return ret

     
        
    def _is_document_end(self, sentence):
        ret = 0
        if len(sentence) < 10 :
            title = trim(sentence)
            for name in self.DOCUMENT_END_FLAG :
                if (title.startswith(name)):
                    ret = 1
        return ret
        
    def _check_term_element_name(self, name):

        if self.document_keywords :
            if name in self.document_keywords :
                return True;
            else :
                r_words = synonyms.get_synonyms(name)
                if (r_words) :
                    for w in r_words :
                        if w in self.document_keywords :
                            return True        
        return False;

       
    def _analyze_document_header(self, sentences, nb_sentence):
        """
        Arguments :
        
        sentences : sentences of a document
        
        return index of end header
        """
        
        prev_sentence = ""
        has_content = 0
        first_section_num = None
        named = []
        for index in range(0, nb_sentence) :
            sentence = sentences[index]
            if len(sentence) > 0 :
                # test if there is a table of contents
                if self.has_table_contents(sentence) :
                    has_content = 1
                    continue
                                
                ''' get document name '''
                if self.document_name == None:
                    self.document_name = self.get_document_title(sentence, prev_sentence)
                    if self.document_name :
                        continue
                    else :
                        prev_sentence = sentence
                
                ''' get document date '''
                if self.document_date == None:
                    self.document_date = self.get_date(sentence)
                    if self.document_date :
                        continue
                    
                # if there is no table of contents
                stype = self.get_sentence_type(sentence, self.chapitre)
                if (stype[0] > 0):
                    if has_content :
                        if first_section_num == None :
                            ''' memory first section number '''
                            first_section_num = stype[1] 
                        elif first_section_num == stype[1] :
                            ''' find second first section number, end header ''' 
                            break
                    else :
                        ''' if there is no table of contents, find first section end header '''
                        break
                elif stype[0] == self.END_DEFINED_CLAUSE or stype[0] == self.START_DEFINED_CLAUSE :  # ignore 
                    pass
                else :
                    '''if self._ner.has_org_end(sentence):
                        named.append(sentence)'''
                    ''' if section type is not found, add text to header '''
                    self.document_header.append([sentence, index])
        
        # @TODO NER for next time
        if False and len(named) > 0 : 
            ss = self.seg.segment(named)[0];
            named = []
            for words in ss :
                #self._ner.get_sentence_ner(words, named)
                pass

        return index

    
    def _add_document_footer(self, sentences, n_start, nb_sentence):
        prev_sentence = ''
        n_line = n_start
        for index in range(n_start, nb_sentence) :
            sentence = sentences[index]
            if not prev_sentence :
                n_line = index
            prev_sentence += sentence
            if self._is_sentence_end(sentence) :
                self.document_footer.append([prev_sentence, n_line])
                prev_sentence = ''
        
        if prev_sentence :
            self.document_footer.append([prev_sentence, n_line])

        return index
   

    def get_section_number(self, word, level=1):
        num = 0
        if type(word) is int :
            num = word
        else :
            w = word.strip()
            if '第' in w :
                w = w[1:-1]
            elif '.' in w :
                n = 0
                for c in w :
                    n += 1
                    if c == '.' :
                        p = n
                        if level == 1 :
                            break
                if level == 1 :
                    w = w[:p-1]
                else :
                    w = w[p:]
            elif '、' in w :
                w = w[:-1]
            if w.isdigit() :
                num = w
            else :
                ss = ""
                for m in w :
                    if m in util.chinese_num_char:
                        ss += m
                if len(ss) > 0 :
                    num = util.convert_chinese_num(ss)
        return num
    
    def _is_sentence_end(self, sentence):
        s = sentence.strip()
        if s[-1] in util.sentence_delimiters :
            return True
        return False
        
    def split_sentence_title(self, sentence):
        title = sentence
        ss = ''
        nb = len(sentence)
        if nb > 1 :
            for n in range(1, nb) : 
                ch = sentence[n]
                if ch == ':' or ch == '：' or ch in util.sentence_delimiters :
                    title = sentence[:n]
                    ss = sentence
                    break
                elif nb > 15 and ch in util.word_delimiters :
                    title = sentence[:n]
                    ss = sentence
                    break
        return title, ss
    
    
    # section in section
    def create_section_2(self, norm_sentences, n_sentence, s_index, total, parent, stype):
        ret = total
        num = self.get_section_number(stype[1], 2)
        title, ss = self.split_sentence_title(stype[2])
        section = Section(stype[1], num, title, stype[0])
        
        s_prev = ""
        if ss :
            if self._is_sentence_end(ss) :
                section.addSentence([ss, s_index, 0])
            else :
                s_prev = ss
        
        if title :
            self.add_document_table_contents(title)
            section.verified = self._check_term_element_name(title)
        
        for index in range((n_sentence + 1), total) :
            s = norm_sentences[index]
            if len(s) > 0 :
                # test if sentence is terms title 
                n_title = self.get_sentence_type(s, self.chapitre)
                if n_title[0] > 0 :
                    if s_prev :
                        section.addSentence([s_prev, s_index, 0])
                        s_prev = ""
                    parent.addSentence(section)
                    
                    if n_title[0] == 1 :
                        ret = index;
                    # third level section
                    else :
                        ret = self.create_section_2(norm_sentences, index, s_index, total, parent, n_title)
                    return ret
                elif n_title[0] == self.END_DOCUMENT :
                    if s_prev :
                        section.addSentence([s_prev, s_index, 0])
                        s_prev = ""
                    parent.addSentence(section)
                    self._add_document_footer(norm_sentences, index, total)
                    return total
                else :
                    s_prev += s
                    if self._is_sentence_end(s) :
                        section.addSentence([s_prev, s_index, 0])
                        s_prev = ""

            else :
                if s_prev == "" :
                    section.addSentence(["", s_index, 0])
                
            s_index += 1
        
        parent.addSentence(section)
               
        return ret
    
    # first level section 
    def create_section(self, norm_sentences, n_sentence, s_index, total, section):
        ret = total
        s_prev = ""
        
        for index in range((n_sentence + 1), total) :
            s = norm_sentences[index]
            if len(s) > 0 :
                # test if sentence is terms title 
                n_title = self.get_sentence_type(s, self.chapitre)
                if n_title[0] > 0 :
                    if s_prev :
                        section.addSentence([s_prev, s_index, 0])
                        s_prev= ""
                    if n_title[0] == 1 :
                        ret = index;
                    # second level section
                    else :
                        ret = self.create_section_2(norm_sentences, index, s_index, total, section, n_title)
                    break
                elif n_title[0] == self.IS_DEFINITION :  # find definition
                    index = self._add_definition(norm_sentences, index + 1, total)

                elif n_title[0] == self.END_DEFINED_CLAUSE  or n_title[0] == self.START_DEFINED_CLAUSE :  # ignore 
                    pass
                elif n_title[0] == self.END_DOCUMENT :
                    if s_prev :
                        section.addSentence([s_prev, s_index, 0])
                        s_prev= ""
                    self._add_document_footer(norm_sentences, index, total)
                    ret = total
                    break
                else :
                    s_prev += s
                    if self._is_sentence_end(s) :
                        section.addSentence([s_prev, s_index, 0])
                        s_prev= ""
                
            s_index += 1
        if s_prev :
            section.addSentence([s_prev, s_index, 0])
        return ret
    

    def _is_contract_end(self, s):
        for name in self.DOCUMENT_TITLE_FLAG :
            if s.endswith(name) :
                return True
        return False;
                
    def get_document_title(self, sentence, prev_sentence, doctype=None):
        title = None
        if len(sentence) > 0 :
            s = trim(sentence)
            if self._is_contract_end(s) or (doctype is not None and s.endswith(doctype)) :
                if prev_sentence and len(s) < 4 :
                    title = prev_sentence + s
                else :
                    title = s
        
            items = dtn_sentence.get_all_term_items()
            for item in items :
                if item in s :
                    if title == None :
                        title = s
                        self._is_contract_doc = self._is_contract_end(item)
                    if self.document_type != item :
                        self.document_type = item 
                        self.document_keywords = dtn_sentence.get_document_categorie(self.document_type)
                    
                    break
           
        return title
    
        

        
    def create_document(self, filename, doctype=None, encoding="utf-8"):
        """
        Arguments :
        
        filename : input document file name
        doctype : document type
        
        """
        
        self.sections = []
        self.chapitre = {}
        self.table_contents = []
        self.document_header = []
        self.document_body = []
        self.document_footer = []
        self.document_name = None
        self.document_date = None
        self.curr_chapiter = 0
        self.curr_term_num = 1
        self._is_contract_doc = 1
        self.level = 2
        
        self.file_name = os.path.basename(filename)
        if doctype :
            self.document_type = doctype
        else :
            self.document_type = os.path.basename(os.path.dirname(filename))

        if self.document_type :
            self.document_keywords = self.term_instance.get_document_categorie(self.document_type)

            
        norm_sentences = get_file_sentences(filename, encoding)
        
        total = len(norm_sentences)
        # analyze header then return header end line number
        start = self._analyze_document_header(norm_sentences, total)
        if start < total - 5 :
            while start < total :
                s = norm_sentences[start]
                stype = self.get_sentence_type(s, self.chapitre)
                if (stype[0] == 1) :
                    
                    num = self.get_section_number(stype[1])
                    if len(stype[2]) > 1:
                        title, ss = self.split_sentence_title(stype[2])
                    else :
                        title, ss = '', ''
            
                    section = Section(stype[1], num, title, stype[0])
                    if ss :
                        section.addSentence([ss, start, 0])
                    if title :
                        self.add_document_table_contents(title)
                        section.verified = self._check_term_element_name(title)
                    self.sections.append(section)
                    start = self.create_section(norm_sentences, start, start, total, section)
                else :
                    start += 1
                    if stype[0] == self.END_DOCUMENT :
                        self._add_document_footer(norm_sentences, start, total)
                        start = total
                    elif stype[0] == 0 :
                        self.document_body.append([s, start, 0])

    
    def add_section_sentence(self, norm_sentences, start, total, section):       
        prev_sentence = ''
        n_line = start+1
        index = n_line
        for index in range((start+1), total) :
            s = norm_sentences[index]
            if len(s) > 0 :
                # test if sentence is terms title 
                stype = self.get_sentence_type(s, self.chapitre)
                if stype[0] == 0 :
                    if not prev_sentence :
                        n_line = index
                    ''' fusion sentence '''
                    prev_sentence += s
                    if self._is_sentence_end(s) :
                        section.addSentence([prev_sentence, n_line])
                        prev_sentence = ''
                elif stype[0] == self.END_DEFINED_CLAUSE  or stype[0] == self.START_DEFINED_CLAUSE :  # ignore 
                    continue
                else :
                    break
                
        if prev_sentence :
            section.addSentence([prev_sentence, n_line])
        return index

                
    def read_section(self, filename, encoding="utf-8"):
        """
        Arguments :
        
        filename : input document file name
        doctype : document type
        
        """
        
        self.sections = []
        self.chapitre = {}
        self.table_contents = []
        self.document_header = []
        self.document_body = []
        self.document_footer = []
        self.document_name = None
        self.document_date = None
        self.curr_chapiter = 0
        self.curr_term_num = 1
        self.level = 3
        num = 0
           
        self.norm_sentences = get_file_sentences(filename, encoding)
        total = len(self.norm_sentences)
        # analyze header then return header end line number
        start = self._analyze_document_header(self.norm_sentences, total)
        if start < total - 5 :            
            while start < total :
                s = self.norm_sentences[start]

                stype = self.get_sentence_type(s, self.chapitre)
                if (stype[0] > 0) :
                    num += 1
                    if len(stype[2]) > 1:
                        title, ss = self.split_sentence_title(stype[2])
                    else :
                        title, ss = '', ''
                    section = Section(stype[1], num, title, stype[0])
                    if ss :
                        section.addSentence([ss, start])
                    
                    self.sections.append(section)
                    start = self.add_section_sentence(self.norm_sentences, start, total, section)
                elif stype[0] == self.END_DOCUMENT :
                    self._add_document_footer(self.norm_sentences, start, total)
                    start = total
                elif stype[0] == self.IS_DEFINITION : 
                    start = self._add_definition(self.norm_sentences, start + 1, total)
                else :
                    start += 1
                    self.document_body.append(s)
   
   
    def read_document(self, filename, doctype=None, encoding="utf-8"):
        """
        Arguments :
        
        filename : input document file name        
        """
        
        self.sections = []
        self.document_header = []
           
        self.norm_sentences = get_file_sentences(filename, encoding)
        total = len(self.norm_sentences)
       
        prev_sentence = ""
        for index in range(0, total) :
            sentence = self.norm_sentences[index]
            if len(sentence) > 0 :
                                
                ''' get document name '''
                if self.document_name == None:
                    self.document_name = self.get_document_title(sentence, prev_sentence, doctype)
                    if self.document_name :
                        continue
                    else :
                        prev_sentence = sentence
                
                ''' get document date '''
                if self.document_date == None:
                    self.document_date = self.get_date(sentence)
                    if self.document_date :
                        continue
                    
                stype = self.get_sentence_type(sentence, self.chapitre)
                if (stype[0] > 0):
                    self.document_header.append([sentence, index])
                else :
                    self.document_header.append([sentence, index])
        


       

            
    def get_normalize_document_from_sentences(self, norm_sentences, outtype=0):


        words = self.seg.segment(norm_sentences)

        
        if outtype == 0 :
            texts = ""
            for sentence in words[0] :
                texts += ' '.join(sentence) + "\n"
        elif outtype == 1 : 
            texts = []
            for s in words[0] :
                s_len = len(s)
                if s_len > 1 :
                    
                    st = s[0] 
                    i = 1
                    while i < s_len and (s[i] == '.' or s[i].isdigit()) :
                        st += s[i]
                        i += 1
                    
                    if i < s_len :
                        st += ' ' + ''.join(s[i:])
                        
                    if self.get_sentence_type(st)[0] == 0 :
                        st = ''.join(s[i:])
                   
                else :
                    st = s[0]
                texts.append(st)
        elif outtype == 2 :
            texts = words[2] # filter
        elif outtype == 3 :  
            texts = words[0] # no filter
        else  :
            texts = words[1] # no stop words
            
        return texts
    
    
    def get_normalize_document(self, filename, outtype=0, encoding="utf-8"):
        """
        Arguments :
        
        filename : input document file name
        
        outtype : 0: 分词 document, 1: 有题目 documet, other: 分词数组
        
        
        return list sentences of document
        
        """
        
        f = codecs.open(filename, 'r', encoding, 'ignore')
        sentences = [s for s in f if len(s.strip()) > 0]
        norm_sentences = [util.normalize_sentence(s) for s in sentences]
        f.close()


        
        return self.get_normalize_document_from_sentences(norm_sentences, outtype);

    def get_fusion_document(self, filename, encoding="utf-8"):
        
        sentences = []
        
        f = codecs.open(filename, 'r', encoding, 'ignore')
        p = ""
        for s in f :
            s = util.normalize_sentence(s)
            if len(s) > 0 :
                if self.parser_sentence(s) :
                    if len(p) :
                        sentences.append(p)
                        p = ""
                    sentences.append(s)
                else :
                    p += s
                    if s[-1] in util.sentence_delimiters :
                        sentences.append(p)
                        p = ""
                
        if len(p) > 0 :
            sentences.append(p)
        
        f.close()


        
        return self.get_normalize_document_from_sentences(sentences, 3);

        
    '''test converted document is OK'''
    def test_document(self, filename, encoding="utf-8"):
        import shutil
 
        f = codecs.open(filename, 'r', encoding)
        sentences = [s for s in f if len(s.strip()) > 0]
        norm_sentences = [util.normalize_sentence(s) for s in sentences]
        f.close()

        
        words = self.seg.segment(norm_sentences)
        
        n_words = len(words[0])
        n_f_words = len(words[2])
        
        document = ""
        for s in words:
            if len(s) > 0 :
                document += ''.join(s) + "\n"
        
        if (n_f_words < n_words / 2) :
            shutil.move(filename, (filename + ".bad"))
            print(document[0:100])
        

    def get_segmented_document(self):
        
        doc = [];
        for section in self.sections :
            for p in section.sentences :
                if type(p) == Section :
                    for s in  p.sentences :
                        # doc.append(s[0])
                        doc.append(s[0])
                else :
                    doc.append(p[0])
                    # doc.append(p[0])
                
        return doc       

                    
    def show_document(self) :
        if len(self.sections) > 0 :    
            for section in self.sections :
                print(section.display(None))
        else :
            for s in self.document_header :
                print(s)

    def debug(self) :
        if len(self.sections) > 0 :    
            for section in self.sections :
                print(str(section.label) + " " + section.title);
                for s in section.sentences :
                    if (type(s) is Section) :
                        print("\t" + str(s.label) + " " + s.title);
                    elif isinstance(s, str) :
                        print("\t" + s);
                    else : 
                        print("\t" + s[0]);
                        
 
    def test_document_term(self, filename):

        if filename.endswith(".txt") :
         
            self.create_document(filename)
            if len(self.sections) > 0 :    
                print("========" + self.file_name + " [" + self.document_type + "]===========");
                n = 0
                for p in self.sections :
                    
                    if not p.verified :
                        n += 1
                        print(str(n) + ". " + p.title + " " + str(p.verified));
                    
                if n == 0 :
                    print("========" + self.file_name + " [OK]===========");

            else :
                self.show_document()
                
                
if __name__ == '__main__':
    
    path = "D:/DTNSoftware/smart/python/src/data/Corpus/TEXT"
    #filename = variables.CORPUS_DIR + "/TEXT/股东协议、章程/股东协议（新设公司）/股东协议v1.docx.txt"
    filename = variables.CORPUS_DIR + "/TEXT/股东协议、章程/发起人协议/发起人协议_JH Comments_071101.txt"
    filename = variables.CORPUS_DIR + "/TEXT/股东协议、章程/发起人协议/发起人协议-无标注文件（共142个）/发起人协议(junhe).DOC.txt"
    filename = variables.CORPUS_DIR + "/TEXT/股东协议、章程/有限责任公司章程/【【中外合资企业章程】】.docx.txt"
    filename = path + "/合同、协议/劳务合同/2008劳务协议范本-退休返聘.doc.txt"
    filename = path + "/股东协议、章程/有限合伙协议/01 有限合伙协议 Final 20150803.txt"
    filename = variables.HOME_DIR + "/import/testproject/TEXT/章程/宝钢股份章程.txt"
    filename = variables.HOME_DIR + "/import/testproject/TEXT/司法、行政文件/仲裁申请书.txt"

    #filename = variables.CORPUS_DIR + "/TEXT/股东协议、章程/A股公司章程/A股国投新集能源股份有限公司章程.txt"
    #filename = variables.CORPUS_DIR + "/TEXT/股东协议、章程/股东协议（新设公司）/股东协议－标准文本－翁亚军、章忠敏.docx.txt"
    
    fpath = variables.CORPUS_DIR + "/TEXT/股东协议、章程"
    filename = variables.HOME_DIR + '/data/terms/Template/TEXT/股东协议（新设公司）/股东协议新设公司1.txt'
    fpath = variables.HOME_DIR + "/data/terms/Template/TEXT"
    fpath = "D:/DTNSoftware/smart/python/src/data/Corpus/TEXT/合同、协议/土地租赁合同";
    filename = "D:/DTNSoftware/smart/python/src/data/Corpus/TEXT/合同、协议/供应合同/产品供应合同.DOC.txt"

    path = "D:/DTNSoftware/smart/python/src/data/Corpus/TEXT/合同、协议/土地租赁合同";
    
    
    FLISTS = [
        #"【【国有土地使用权出让合同（格式）】】.docx.txt", 
        #"【【国有建设用地使用权出让合同GF-2008-2601】】.docx.txt", 
        "【【深圳市土地使用权出让合同书】】.docx.txt"
        ]  
    
    ld = LawDocument()
    
    filename = "D:/DocutoneSoftware/SmartDoc/home/import/59b9b3129a1d3f5825c5306a/TEXT/【【A股国投新集能源股份有限公司章程】】.docx.txt"

    filename = variables.HOME_DIR + "/data/Corpus/TEXT/合同、协议/劳动合同/B02003-高级管理人员劳动合同-011107.DOC.txt"

    path = "D:/DTNSoftware/smart/python/src/data/Corpus/TEXT/合同、协议/土地租赁合同";
    filename = path + "/土地及厂房租赁合同.DOC.txt";
   
    
    ld.read_section(filename)
    ld.debug()
     
    '''
    for name in FLISTS :
        filename = variables.CORPUS_DIR + "/TEXT/合同、协议/土地使用权出让合同/" + name;
        
        #ld.create_document(filename)
        ld.read_section(filename)
        #ld.debug()
        ld.show_document()
       
        #ld.test_document_term(filename)
    
    '''
    
    
        
    print('--- end ----')

