# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import sys

sys.path.append("../")

''' other document '''


from docutone.document.dtn_document import DTNDocument
from docutone.document import dtn_document


class OtherDocument(DTNDocument) :

       
   
    def __init__(self):
        
        super().__init__(dtn_document.OTHER_DOCUMENT)
     
    
    def _reset(self):
        pass
      
    
    def analyse_header(self, s, sentences, index):

        isEnd = False
        
        if self.set_contract_date(s, index) :
            pass
                
        elif not self._title and self._is_title(s):
            self._title = s
            ''' add to extraction '''
            #crf_utils.add_clause_string(self.CONTRACT_NAME, self._title, self._results)
    
        elif not self._has_table_contents and self.is_table_contents(s) :
            index = self.pass_table_contents(sentences, (index+1))
            isEnd = True
            
        
        
        return isEnd, index



    
if __name__ == "__main__":
    filename = "D:/DTNSoftware/dtn-smart/python/src/data/Corpus/TEXT/合同、协议/劳动合同/3. 劳动合同模板-3 20180319.txt"
    filename = "D:/DTNSoftware/dtn-smart/python/src/data/Corpus/TEXT/司法、行政文件/仲裁申请书/B02412-仲裁申请书-021108.DOC.txt"
    docs = OtherDocument()
    doc = docs.read(filename)
    print(doc[0:10])

 
 
    