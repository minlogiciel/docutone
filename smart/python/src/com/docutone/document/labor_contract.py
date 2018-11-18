# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import sys


sys.path.append("../")

''' labor contract document '''


from docutone.document import dtn_document as dtnd
from docutone.utils import crf_utils, synonyms





class LaborContract(dtnd.DTNDocument) :

    TITLE_NAME = synonyms.get_contract_infos("LABOR_NAME")
    
    EMPLOYER_INFO = synonyms.get_contract_infos("EMPLOYER_INFO")
    SOCIETY_INFO = synonyms.get_contract_infos("SOCIETY_INFO")
    EMPLOYER_NAME = synonyms.get_contract_infos("EMPLOYER_NAME")
    SOCIETY_NAME =  synonyms.get_contract_infos("SOCIETY_NAME")

    SOC = ['下称“甲方”', '下称“公司”', '下称“聘用方”', '下称“用人单位”']
    EMP = ['下称“乙方”', '下称“受聘方”', "下称“劳动者”", "下称“员工”"]
    SOC_START = '由'
    EMP_START = '与'
    TIME_START = '于'
    TIME_START = '以下双方'
    TIME_START = '签订'
    
    

    def __init__(self):
        
        super().__init__(dtnd.LABOR_CONTRACT)
        self.employer = None
        self.society = None
        self.contract_period = None
        self.probation = None
              
    
    def _reset(self):
        self.employer = None
        self.society = None
        self._init_results()
        
    def _is_title(self, s):
        return self._find_end_info(s, self.TITLE_NAME)
        
    
    def _is_employer_info(self, s):
        return self._find_info(s, self.EMPLOYER_INFO)
    
    def _is_society_info(self, s):
        return self._find_info(s, self.SOCIETY_INFO)
    
    def _is_employer(self, s):
        if self.employer :
            return False
        else :
            return self._find_info(s, self.EMPLOYER_NAME, test_synonym=False)
    
    def _is_society(self, s):
        if self.society :
            return False
        else :
            return self._find_info(s, self.SOCIETY_NAME, test_synonym=False)
    
    
    def _is_employer_sentence(self, s):
        if self.employer :
            return False
        else :
            return self._find_in_info(s, self.EMPLOYER_NAME)
    
    def _is_society_sentence(self, s):
        if self.society :
            return False
        else :
            return self._find_in_info(s, self.SOCIETY_NAME)
    
    
    
    def _add_society_info(self, sentences, index):
        s = sentences[index]
        self.society = [s]
        crf_utils.add_clause_string(self.CONTRACT_AB, s, self._results)
        index += 1
        prev = s
        while s :
            s = sentences[index]
            if self._is_society_info(s) :
                self.society.append(s)
                crf_utils.add_clause_string(self.CONTRACT_AB, s, self._results)
            else:
                if prev.endswith(':') or prev.endswith('：') :
                    self.society.append(s)
                    crf_utils.add_clause_string(self.CONTRACT_AB, s, self._results)
                else :
                    index -= 1
                    break
            prev = s
            index += 1
        return index
    
    def _add_employer_info(self, sentences, index):
        s = sentences[index]
        self.employer = [s]
        crf_utils.add_clause_string(self.CONTRACT_AB, s, self._results)
        index += 1
        while s :
            s = sentences[index]
            if self._is_employer_info(s) :
                self.employer.append(s)
                crf_utils.add_clause_string(self.CONTRACT_AB, s, self._results)
            else:
                index -= 1
                break
            index += 1
        return index


    def _is_society_employer_sentence(self, s):
        if self.society or self.employer :
            return False
        elif self._find_in_info(s, self.SOC) and self._find_in_info(s, self.EMP) :
            return True
        elif self._all_elements_in_sentence(s) :
            return True
        else :
            return False
    
    def _add_society_employer(self, sentence):
        start = sentence.find(self.SOC_START)
        if start < 0 :
            start = 0
        end = sentence.find(self.EMP_START)
        if end < 0 : 
            end = len(sentence) - 1
        nb = sentence.find(self.TIME_START)
        if nb < end:
            nb = len(sentence) - 1

        soc = sentence[start+1:end]
        tab = soc.split('，')
        self.society = []
        if tab and len(tab) :
            for s in tab:
                s = s.strip()
                if len(s) > 0 :
                    self.society.append(s)
                    crf_utils.add_clause_string(self.CONTRACT_AB, s, self._results)
        else :
            self.society.append(soc)
            crf_utils.add_clause_string(self.CONTRACT_AB, soc, self._results)

        emp = sentence[end+1:nb]
        tab = emp.split('，')
        self.employer = []
        if tab and len(tab) :
            for s in tab:
                s = s.strip()
                if len(s) > 0 :
                    self.employer.append(s)
                    crf_utils.add_clause_string(self.CONTRACT_AB, s, self._results)
        else :
            self.employer.append(emp)
            crf_utils.add_clause_string(self.CONTRACT_AB, emp, self._results)
            
    def _add_society_employer_sentences(self, sentences, index):
        self.employer = []
        self.society = []
        
        index += 1
        while True :
            s = sentences[index]
            if self._is_employer_sentence(s) :
                self.employer.append(s)
                crf_utils.add_clause_string(self.CONTRACT_AB, s, self._results)
            elif self._is_society_sentence(s) :
                self.society.append(s)
                crf_utils.add_clause_string(self.CONTRACT_AB, s, self._results)
            else :
                break
            index += 1
        
        return index
        
        
    def analyse_header(self, s, sentences, index):

        isEnd = False
        
        if self.set_contract_date(s, index) :
            if self._is_society_employer_sentence(s)  :
                self._add_society_employer(s)
        elif not self._title and self._is_title(s):
            self._title = s
            ''' add to extraction '''
            crf_utils.add_clause_string(self.CONTRACT_NAME, self._title, self._results)
           
        elif self._is_society_employer_sentence(s)  :
            index = self._add_society_employer_sentences(sentences, index)

        elif self._is_society(s)  :
            index = self._add_society_info(sentences, index)
            
        elif self._is_employer(s)  :
            index = self._add_employer_info(sentences, index)
            
        elif not self._has_table_contents and self.is_table_contents(s) :
            index = self.pass_table_contents(sentences, (index+1))

        elif self.is_end_header(s, sentences, (index+1)) :
            isEnd = True
        
        
        return isEnd, index
    
    
    def debug(self, doc=None):
        print('*** %s ***' %(self._title))
        print('日期 : %s' %(self._contract_date))
        print('甲方 : %s' %('\n'.join(self.society)))
        print('乙方 : %s' %('\n'.join(self.employer)))
   
    
if __name__ == "__main__":

    path = 'D:/DTNSoftware/dtn-smart/python/src-test/TESTFile/TEXT/劳动合同/'
    filename = '20180330182146676238076801002_00.docx.txt'
    filename = '20180525041445419598774291886_00.pdf.txt'
    filename = '20180525072320850728550180498_00.docx.txt'
    filename = path + filename
    employement = LaborContract()
    doc = employement.read(filename)
    employement.debug(doc)
    #print(doc[0:10])
 
    