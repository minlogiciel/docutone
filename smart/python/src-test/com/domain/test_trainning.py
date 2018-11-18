#-*-coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import os, codecs, sys
import unittest

from domain import test_var

sys.path.insert(0, test_var.PROG_PATH)


from docutone.domain.training import Training
from docutone.utils import variables
from docutone.core.contract import Contract

class DcoumentTestCase(unittest.TestCase):
    
    CORPUS_PATH = variables.CORPUS_DIR + "/TEXT"
    TEMPLATE_PATH = variables.HOME_DIR + "/data/terms/Template/TEXT"
    
    def setUp(self):

        pass

    def tearDown(self):
        pass
    
 
    def test_create_datasets(self):
        training = Training()
        training.create_datasets(self.CORPUS_PATH)
        training.training_svc()
    
    def test_create_model(self):
        cont = Contract(debug=1)
        cont.create_terms(self.TEMPLATE_PATH)

 
if __name__ == "__main__":
    unittest.main()
