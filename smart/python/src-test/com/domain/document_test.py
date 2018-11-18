#-*-coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import os, codecs, sys
import unittest

from domain import test_var

sys.path.insert(0, test_var.PROG_PATH)


from docutone.domain.classifier import Classifier
from docutone.domain.extraction import Extraction
from docutone.domain.training import Training
from docutone.utils.base import File
from docutone.core.segmentation import Segmentation
from docutone.utils import variables
from docutone.core.document import LawDocument
from docutone.core.crf import CRF

class DcoumentTestCase(unittest.TestCase):
    
    TEST_PATH = variables.HOME_DIR + "/TESTFile/TEXT"
    TEMPLATE_PATH = variables.HOME_DIR + "/data/terms/Template/TEXT"

    def setUp(self):

        pass

    def tearDown(self):
        pass
    

    def test_segmentation(self):
        filename = self.TEST_PATH + "/司法、行政文件/仲裁申请书.txt"
        f = codecs.open(filename, 'r', encoding='utf-8')
        sentences = [s for s in f if len(s.strip())]
        seg = Segmentation()
        words = seg.segment(sentences)
        
        print(words[0][:10])
 
 
 
   
    def test_simulation_datasets(self):
        
        fpath = variables.CORPUS_DIR + "\\TEXT\\保险"
        
        '''     
        classifying = Classifier()
        classifying.classification(fpath)
        classifying.debug()
        '''
        

    '''
    def test_simulation_terms1(self):
 

        path = variables.get_data_file_name(dataname="Template/TEXT", categorie="terms")
        filename = path + "/A股公司章程/【【A股国投新集能源股份有限公司章程】】.docx.txt"
    
        terms = TermsVerification()

        term_list = terms.verify_document(filename, None, "A股公司章程")
        terms.to_json(term_list)

 
    def test_simulation_terms2(self):
        
        path = variables.get_data_file_name(dataname="Template/TEXT", categorie="terms")

        filename = path + "/司法、行政决定/判决书/【【判决书(与银行理财产品相关的争议解决)-蔡黎】】.docx.txt"
    
        terms = TermsVerification()
    
        term_list = terms.verify_document(filename, None, "判决书")
        terms.to_json(term_list)

    '''
                
    def test_convert_file(self):
        
        flist = [variables.CORPUS_DIR + "\\DOC\\保险\\中国人民财产保险股份有限公司机动车第三者责任保险条款.doc",
             variables.CORPUS_DIR + "\\DOC\\公司章程\\amended Articles 14 Oct 2004 revised.pdf",
             variables.CORPUS_DIR + "\\DOC\\批文\\77254508.jpg"]
        '''
        filename = ""
        for filename in flist : 
            conv = File(filename, None) 
            texts = conv.convert()
            if texts :
                print(texts[1:100])
        pass
        '''

    
    def test_read_document(self):
 
        filename = variables.HOME_DIR + "/TESTFile/TEXT/司法、行政文件/仲裁申请书.txt"

        ld = LawDocument()
        ld.create_document(filename)
        ld.show_document()
   
       
    def test_terms_name(self) :
        lawdocument = LawDocument()
        for fname in sorted(os.listdir(self.TEMPLATE_PATH)):
            fpath = os.path.join(self.TEMPLATE_PATH, fname)
            if os.path.isdir(fpath):
                for fn in sorted(os.listdir(fpath)):
                    filename = os.path.join(fpath, fn)
                    if  filename.endswith(".txt"):
                        lawdocument.test_document_term(filename)
    
            elif fname.endswith(".txt"):
                lawdocument.test_document_term(fpath)



    def test_documents(self) :
    
        ld = LawDocument()
        
        for name in os.listdir(self.TEST_PATH):
            fpath = os.path.join(self.TEST_PATH, name)           
            if os.path.isdir(fpath) and name != variables.DATA_DIR and name != variables.TEMP_DIR :
                for fname in os.listdir(fpath):
                    filename = os.path.join(fpath, fname)
                    if os.path.isdir(filename) :
                        pass
                    elif fname.endswith(".txt") :
                        print(fpath)
                        ld.create_document(filename)
                        #ld.show_document()
            elif name.endswith(".txt") :
                print(fpath)
                ld.create_document(fpath)
                ld.show_document()



 
if __name__ == "__main__":
    unittest.main()
