#-*-coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import os, codecs, sys
import unittest

from domain import test_var

sys.path.insert(0, test_var.PROG_PATH)


from docutone.utils import util


class DcoumentTestCase(unittest.TestCase):
    def setUp(self):
        #self.ld = LawDocument()
        pass

    def tearDown(self):
        pass
    

    def test_convert_chinese_unm(self):
        
        t_list = [230, 109, 100, 1000, 10000, 100000, 1000000, 1019, 54, 9, 13, 256, 3002]
        for d in t_list :
            v = util.convert_english_num(d)
            s = util.convert_chinese_num(v)
            self.assertEqual(d, s)
    
 

if __name__ == "__main__":
    unittest.main()
