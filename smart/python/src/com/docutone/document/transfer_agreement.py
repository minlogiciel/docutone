# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import sys

sys.path.append("../")

''' transfer agreement document '''

from docutone.document import dtn_document
from docutone.utils import crf_utils, synonyms




class TransferAgreement(dtn_document.DTNDocument) :


    TITLE_NAME = [dtn_document.TRANSFER_AGREEMENT]
    TRANSFER_INFO = ['法定代表人', '职务', '国籍']
    ASSIGNEE_INFO = ['法定代表人', '职务',  '国籍']
    TRANSFER_NAME = ['转让方', '简称“甲方”', '下称“甲方”', '简称“卖方”', '合称“卖方”' ]
    ASSIGNEE_NAME = ['受让方', '“受让方”', '简称“乙方”', '下称“乙方”', '简称“买方”', '（“买方”）']
 
    
    def __init__(self):
        
        super().__init__(dtn_document.TRANSFER_AGREEMENT)
        
        self.assignee = None
        self.transfor = None
        self._start_header = 0
    
    def _reset(self):
        self.assignee = None
        self.transfor = None
        self._contract_date = None
        self._title = None
        self._start_header = 0
        self._init_results()
       
    def _is_transfor_info(self, s):
        return self._find_info(s, self.TRANSFER_INFO)
        
    
    def _is_assignee_info(self, s):
        return self._find_info(s, self.ASSIGNEE_INFO)
        
        
    def _is_transfor(self, s):
        if self._find_in_info(s, self.TRANSFER_NAME) :
            if self._start_header == 0 :
                self._start_header = 1
            return True
        else :
            return False
    
    def _is_assignee(self, s):
        if self._find_in_info(s, self.ASSIGNEE_NAME) :
            if self._start_header == 0 :
                self._start_header = 1
            return True
        else :
            return False
        
    def _add_transfor(self, s, sentences, index):
        if len(s) < 6 :
            d = 1
        else :
            d = 0
        ss = sentences[index+d]
        self.transfor = [ss]
        crf_utils.add_clause_string(self.CONTRACT_AB, ss, self._results)
        d += 1
        for i in range(d, 5) :
            ss = sentences[index + i]
            if self._is_transfor_info(ss) :
                self.transfor.append(ss)
            else:
                break
    
    def _add_assignee(self, s, sentences, index):
        if len(s) < 6 :
            d = 1
        else :
            d = 0
        ss = sentences[index+d]
        self.assignee = [ss]
        crf_utils.add_clause_string(self.CONTRACT_AB, ss, self._results)
        d += 1
        for i in range(d, 5) :
            ss = sentences[index + i]
            if self._is_transfor_info(ss) :
                self.assignee.append(ss)
            else:
                break
        
        
         
    def analyse_header(self, s, sentences, index):
        isEnd = False
        if self.set_contract_date(s, index) : 
            pass
        elif not self._title and self._find_in_info(s, self.TITLE_NAME):
            self._title = s
            crf_utils.add_clause_string(self.CONTRACT_NAME, self._title, self._results)
        elif not self.transfor and self._is_transfor(s) :
            self._add_transfor(s, sentences, index)
            
        elif not self.assignee and self._is_assignee(s) : 
            self._add_assignee(s, sentences, index)
        
        elif not self._has_table_contents and self.is_table_contents(s) :
            index = self.pass_table_contents(sentences, (index+1))

        elif self.is_end_header(s) :
            isEnd = True
            
        return isEnd, index
           




 
 
    