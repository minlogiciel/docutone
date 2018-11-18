# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import sys

sys.path.append("../")

''' loan agreement document '''


from docutone.document.dtn_document import DTNDocument
from docutone.document import dtn_document
from docutone.utils import synonyms

class LoanAgreement(DTNDocument) :

    TITLE_NAME = [dtn_document.LOAN_AGREEMENT, dtn_document.CREDIT_AGREEMENT ]
    BORROWER_NAME = synonyms.get_contract_infos("BORROWER_NAME")
    LENDER_NAME = synonyms.get_contract_infos("LENDER_NAME")
    GUARANTOR_NAME = synonyms.get_contract_infos("GUARANTOR_NAME")
    ARRANGER_NAME = synonyms.get_contract_infos("ARRANGER_NAME")
    LOANBANK_NAME = synonyms.get_contract_infos("LOANBANK_NAME")
    GURANTBANK_NAME = synonyms.get_contract_infos("GURANTBANK_NAME")
        
   
    def __init__(self):
        
        super().__init__(dtn_document.LOAN_AGREEMENT)
        
        self.borrower = ""
        self.lender = ""
        self.guarantor = ""
        self.loan_bank = ""
        self.guarant_bank = ""
        self.arranger = ""
    
    def _reset(self):
        self.borrower = ""
        self.lender = ""
        self.guarantor = ""
        self.loan_bank = ""
        self.guarant_bank = ""
        self.arranger = ""
        self._contract_date = ""
        self._title = ""
        self._init_results()
    
    def analyse_header(self, s, sentences, index):
        
        isEnd = False
        if self.set_contract_date(s, index) : 
            pass

        elif not self._title and self._find_in_info(s, self.TITLE_NAME):
            if len(s) > 8 :
                self._title = s
            elif index > 0 :
                self._title = sentences[index-1] + s
                        
        elif not self.borrower and self._find_in_info(s, self.BORROWER_NAME) :
            self.borrower = self._get_info_content(s, sentences, index, self.BORROWER_NAME)
            
        elif not self.lender and self._find_in_info(s, self.LENDER_NAME) :
            self.lender = self._get_info_content(s, sentences, index, self.LENDER_NAME)
            
        elif not self.guarantor and self._find_in_info(s, self.GUARANTOR_NAME) :
            self.guarantor = self._get_info_content(s, sentences, index, self.GUARANTOR_NAME)
            
        elif not self.arranger and self._find_in_info(s, self.ARRANGER_NAME) :
            self.arranger = self._get_info_content(s, sentences, index, self.ARRANGER_NAME)

        elif not self.loan_bank and  self._find_in_info(s, self.LOANBANK_NAME) :
            self.loan_bank = self._get_info_content(s, sentences, index, self.LOANBANK_NAME)

        elif not self.guarant_bank and self._find_in_info(s, self.GURANTBANK_NAME) :
            self.guarant_bank = self._get_info_content(s, sentences, index, self.GURANTBANK_NAME)
        
        elif not self._has_table_contents and self.is_table_contents(s) :
            index = self.pass_table_contents(sentences, (index+1))

        elif self.is_end_header(s) :
            isEnd = True
            
        return isEnd, index

    def debug(self):
        print('*** %s ***' %(self._title))
        print('日期 : %s' %(self._contract_date))
        print('借款人 : %s' %(self.borrower))
        print('贷款人 : %s' %(self.lender))
        print('保证人 : %s' %(self.guarantor))
        print('协调安排行 : %s' %(self.arranger))
        print('贷款代理行 : %s' %(self.loan_bank))
        print('担保代理行 : %s' %(self.guarant_bank))

if __name__ == "__main__":

    path = 'D:/DTNSoftware/dtn-smart/python/src/data/Template/TEXT/贷款协议/'
    filename = '美元银团贷款协议.txt'

    filename = path + filename
    loan = LoanAgreement()
    doc = loan.read(filename)
    loan.debug()
    #print(doc[0:10])


 
 
    