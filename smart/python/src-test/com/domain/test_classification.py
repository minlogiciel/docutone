#-*-coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import sys
import unittest

from domain import test_var

sys.path.insert(0, test_var.PROG_PATH)


from docutone.domain.classifier import Classifier
from docutone.utils import variables
from docutone.domain.verifying import TermsVerification

class DcoumentTestCase(unittest.TestCase):
    

    TEST_PATH = variables.HOME_DIR + "/TESTFile/TEXT"
    
    def setUp(self):

        pass

    def tearDown(self):
        pass
    
   
    def test_classification(self):
        classifying = Classifier()
        classifying.classification(self.TEST_PATH, None)
        classifying.to_json()
    
    '''
    def test_verification(self):
        
        fname = self.TEST_PATH + "/章程/创业环保公司章程.txt"
        ftype = "有限责任公司章程"
               
        terms = TermsVerification()
        term_list = terms.verify_document(fname, None, ftype)
        for elem in term_list :
            print(elem)

    '''
 
if __name__ == "__main__":
    unittest.main()
