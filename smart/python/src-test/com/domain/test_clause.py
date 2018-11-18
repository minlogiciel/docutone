#-*-coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import sys
import unittest

from domain import test_var

sys.path.insert(0, test_var.PROG_PATH)


from docutone.utils import variables
from docutone.core.clause import Clause
from docutone.utils.focus import Focus

class DcoumentTestCase(unittest.TestCase):
    
    TEMPLATE_PATH = variables.PYTHON_SRC + "/data/Template/TEXT"
    focus = Focus()
    focus.load()
    def setUp(self):

        pass

    def tearDown(self):
        pass
    
    
    def test_clause1(self):
        
        filename = self.TEMPLATE_PATH + "/劳动合同/【【1. 刘岩宏劳动合同-中文版】】.txt"
        clause = Clause()
        item = self.focus.get_template_item('劳动合同')

        clause.create_clauses(filename)
    
        titles = [section.title for section in clause.sections]
        for elem in item.children :
            if (elem.name not in titles) :
                print(elem.name  + " MISSING ")
        
        names = item.get_item_names()
        for name in titles :
            if name not in names :
                print(name  + " ERROR ")
            #self.assertTrue(elem.name in titles)
    
    

  
if __name__ == "__main__":
    unittest.main()
