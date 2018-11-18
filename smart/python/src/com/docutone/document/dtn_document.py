# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import sys, codecs, os, re



sys.path.append("../")

''' common docutone document
'''

from docutone.utils import util, docutonejson, docutonelocate
from docutone.core.segmentation import Segmentation
from docutone.core import document
from docutone.utils import synonyms
from docutone.utils.focus import Focus
from docutone.utils.extract_data import ExtractData
from docutone.utils import crf_utils





LABOR_CONTRACT = "劳动合同"
LABOR_CONTRACT_NAME = ["劳动合同", "劳动合同书", "劳务聘用协议", "劳务合同", "劳务合同书", "国际劳务合同", "劳务派遣合同", "合同制工人招聘合同", "聘任合同"]

PARTNER_AGREEMENT = "合伙人协议"
LOAN_AGREEMENT = "贷款协议" 
CREDIT_AGREEMENT = "授信协议"
TRANSFER_AGREEMENT = "转让协议"
COMPANY_POLICY = "有限责任公司章程"
OTHER_DOCUMENT = "other"

INOF_PREV_NAME = "作为"

segment = Segmentation()
segment.load_suggest_words()
law_document = document.LawDocument()

focus = Focus()
focus.load()


class ContractTime(object):
    PERIOD_TYPE = ['无固定期限', '无固定期限']
    DATE_TYPE = ['起始日', '终止日']
    def __init__(self, sentence):
        self.contract_type = self.PERIOD_TYPE[0]
        self.starting = 20160101
        self.termination = 20181231
        self.duration = 2
        self.probation = 3
        

class DTNDocument(object) :
    
    SIGNATURE_NAME = ['签订时间：', '签订日期：', '签订', '达成', '签署']
    FORCE_SENTENCE = ['甲方', '乙方']
    BOTH_PARTIES_KEYWORDS = ['由', [['与', '于'], ['以下双方']] , '签订']

    CONTRACT_NAME = synonyms.get_contract_infos("CONTRACT_NAME")
    CONTRACT_DATE = synonyms.get_contract_infos("CONTRACT_DATE")
    CONTRACT_AB = synonyms.get_contract_infos("CONTRACT_AB")

    def __init__(self, categorie):

        self._categorie = categorie
        self._focus_points = focus.get_template_item(categorie)
        if self._focus_points :
            self._keywords = self._focus_points.get_item_names()
        else :
            self._keywords = []
        self._init_results()
        

    def _init_results(self):
        self._title = ""
        self._contract_date = ""
        self._has_table_contents = False
        self._first = None
        self._results = {}
        if self._focus_points :
            for key in self._keywords :
                elem = self._focus_points.getItem(key)
                if elem :
                    level = elem.level
                else :
                    level = 0
                self._results[key] = ExtractData(key, self._categorie, level)

    def _is_title(self, s):
        if s.endswith('合同') or  s.endswith('协议') or s.endswith('章程') : 
            return True
        else :
            return False

    def _is_employer(self, s):
        return False

    def _add_employer_info(self, sentences, index) :
        return index
    
    def _is_society(self, s):
        return False

    def _add_society_info(self, sentences, index) :
        return index


    def _all_elements_in_sentence(self, s) :
        found = True
        for elems in self.BOTH_PARTIES_KEYWORDS :
            if type(elems) is str :
                if elems not in s :
                    found = False
                    break
            else :
                for elem in elems :
                    found = True
                    for name in elem :
                        if name not in s :
                            found = False
                            break
                    if found :
                        break
        return found
                    
                    
                    
    def _is_both_parties(self, s) :
        if s.endswith('签约双方') or s.endswith('签约双方:') : 
            return True
        else :
            if self._all_elements_in_sentence(s) :
                return True
        return False
        
        
        
    def _add_both_parties_info(self, tag, sentences, index, nbs) :
        
        while index < nbs :
            s = sentences[index]
            p = law_document.parser_sentence(s)
            if p and p[0] == tag : # same type section 
                index -= 1
                break
            else :
                if self._is_employer(s) :
                    index = self._add_employer_info(sentences, index)
                elif self._is_society(s) :
                    index = self._add_society_info(sentences, index)
            index +=1

        return index

    def _is_sentence_end(self, prev, word, sentence):
        
        ret = law_document.parser_sentence(sentence)
        if ret :
            if ',' in sentence or '，' in sentence :
                return 1
            else :
                return 2
        elif prev.word[0] == ',' or prev.word[0] == '，' :
            return 0
        elif prev.word[0] in util.sentence_delimiters :
            return True
        elif prev.flag == 'l' :
            return 1
        elif word.flag == 'l' :
            return 2
        elif prev.word[0] == '：' :
            return 1
        elif self._find_info(word.word, self.FORCE_SENTENCE) :
            return 1
        return 0
    
    def get_date(self, sentence):
        content = None
        m = re.search('.{1,4}年.{0,3}月.{0,3}日', sentence)
        if m :
            content = m.group(0)
        else :
            m = re.search('.{1,4}年.{0,2}月', sentence)
            if m :
                content = m.group(0)
        return content
    
    
    def get_contract_time(self, s, index):
        if self._find_in_info(s, self.SIGNATURE_NAME) :
            return self.get_date(s)
        elif index < 10 :
            return self.get_date(s)
        return None
  
    def set_contract_date(self, s, index):
        if not self._contract_date :
            self._contract_date = self.get_contract_time(s, index)
            if self._contract_date :
                ''' add to extraction '''
                crf_utils.add_clause_string(self.CONTRACT_DATE, self._contract_date, self._results)
                return True
        return False
   
    def is_table_contents(self, name):
        self._has_table_contents = law_document.has_table_contents(name)
        return self._has_table_contents

    def pass_table_contents(self, sentences, index):
        self._first = None
        while index < len(sentences) :
            s = sentences[index]
            p = law_document.parser_sentence(s)
            if p :
                if not self._first :
                    self._first = p
                else :
                    if self._first[0] == p[0] and self._first[1] == p[1] :
                        return index # end header
            elif self._first :
                index -= 1
                return index
            index += 1
        
        return index
            
    
    def is_end_header(self, s, sentences=None, index=0):
        if len(s) < 4 and sentences :
            if s.isdigit() :
                return False
            loop = True
            nb = len(sentences)
            while (loop and index < nb) :
                next = sentences[index]
                if len(next) > 0 :
                    s += next
                    loop = False
                    break;
                index += 1
        p = law_document.parser_sentence(s)
        if p :
            if not self._has_table_contents or (self._first[0] == p[0] and self._first[1] == p[1]) :
                return True
        return False
    

    def _find_info(self, s, tabs, test_synonym=True):
        for name in tabs :
            if len(name) < 4 :
                n1 = name + ':'
                n2 = name + '：'
                if s == name or s.startswith(n1) or s.startswith(n2) :
                    return True
            else :
                if s.startswith(name) :
                    return True
            if test_synonym :
                synonym = self.get_synonyms(name)
                if synonym and len(synonym) :
                    for key in synonym :
                        if s.startswith(key) :
                            return True
        return False
    
    def _find_in_info(self, s, tabs):
        for name in tabs :
            if name in s :
                return True
        return False
    
    def _find_end_info(self, s, tabs):
        for name in tabs :
            if s.endswith(name) : 
                return True
        return False

    
    def _get_info_content(self, s, sentences, index, tabs):
        for name in tabs :
            if name in s :
                if len(s) > 10 :
                    content = s
                else :
                    name = INOF_PREV_NAME + name
                    if name in s :
                        content = sentences[index-1]
                    else :
                        content = sentences[index+1]
                return content
        return None
    

   
    def add_synonyms(self, key, value):
        synonyms.add_synonym(key, value)
        
    def get_synonyms(self, key):
        return synonyms.get_synonyms(key)
    
    
    def find_clause_name(self, name):
        for key in self._keywords :
            if key == name :
                return key
            synos = self.get_synonyms(key)
            if synos :
                for n in synos :
                    if n == name :
                        return key
        return None

   
    def add_clause_all_string(self, clause_name, tag, sentences, index, nbs):
        xdata = crf_utils.get_extract_data(clause_name, self._results)
        if xdata :
            s = sentences[index]
            xdata.add_value(s, 1)
            index += 1
            while index < nbs:
                s = sentences[index]
                pp = law_document.parser_sentence(s)
                if pp and (pp[0] == tag or pp[0] == self.first_tag) : # same type section 
                    index -= 1
                    break
                elif pp :
                    name = self.find_clause_name(pp[2].strip())
                    if (name and name != clause_name) :
                        index = self.add_clause_all_string(name, pp[0], sentences, index, nbs)
                    else :
                        xdata.add_value(s, 1)
                else :
                    xdata.add_value(s, 1)
                index +=1
            xdata.set_full()
        return index 

    
    def read(self, filename): 
        self._reset()
        self.first_tag = None
        sentences = document.get_file_sentences(filename, is_test=True)
        documents= []
        words_list = segment.segment_ws(sentences)
        prev_words = None
        nbs = len(sentences)
        end_head = False
        index = 0
        while index < nbs:
            s = sentences[index]
            if end_head == False :
                end_head, index = self.analyse_header(s, sentences, index)
            if end_head :
                s = sentences[index]
                ''' contract date can be at the end of document '''
                if (index > nbs - 11) and self.set_contract_date(s, (nbs-index)):
                    index += 1
                    continue
                
                words = words_list[index]
                p = law_document.parser_sentence(s)
                if p :
                    if prev_words :
                        documents.append([w.word for w in prev_words])
                    clause_name = self.find_clause_name(p[2].strip())
                    if clause_name :
                        self.first_tag = p[0]
                        index = self.add_clause_all_string(clause_name, p[0], sentences, index, nbs)
                    elif self._is_both_parties(p[2].strip()) :
                        index += 1
                        index = self._add_both_parties_info(p[0], sentences, index, nbs)
                    else :
                        documents.append([w.word for w in words])
                        prev_words = None
                else :
                    if prev_words :
                        prev = prev_words[-1]
                        word = words[0]
                        ret = self._is_sentence_end(prev, word, s)
                        if ret > 0 :
                            documents.append([w.word for w in prev_words])
                            if ret > 1 :
                                documents.append([w.word for w in words])
                                prev_words = None
                            else :
                                prev_words = words
                        else  :
                            prev_words += words
                    else :
                        prev_words = words
            
            index += 1
            
        if (prev_words) :
            documents.append([w.word for w in prev_words])
            
        return documents


        

    
 
    