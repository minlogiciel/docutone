#-*-coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import sys
import unittest

from domain import test_var

sys.path.insert(0, test_var.PROG_PATH)

from docutone.domain.verifying import TermsVerification
from docutone import config


class DcoumentTestCase(unittest.TestCase):
    
    TEST_PATH = config.TEST_PATH  
    TEXT_FUNC = [1, 0, 0]
    
    def setUp(self):

        pass

    def tearDown(self):
        pass
    
    def test_extraction1(self):
        fname = self.TEST_PATH + "/章程/创业环保公司章程.txt"
        ftype = "有限责任公司章程"
        if self.TEXT_FUNC[0] :
            print("TEST FILE : %s (%s)" %(fname, ftype))
            extr = TermsVerification()
            term_list = extr.verify_document(fname, None, ftype)
            
            for elem in term_list :
                if (len(elem) > 2) :
                    e = [el[0] for el in elem[2]]
                    s = ' '.join(e)
                    print(elem[0] + " : " + s)
                    if elem[0] == '文件名称' :
                        self.assertTrue("天津创业环保股份有限公司章程" in s)
                    elif elem[0] == '公司名称' :
                        self.assertTrue("天津创业环保股份有限公司" in s)
                    elif elem[0] == '公司地址' or elem[0] == '公司住所' :
                        self.assertTrue("300051" in s)
                        self.assertTrue("天津市和平区贵州路" in s)
                    elif elem[0] == '公司性质' :
                        self.assertTrue("公司为永久存续的股份有限公司" in s)
                    elif elem[0] == '公司经营范围' :
                        self.assertTrue("利用中国境内外资金" in s)
                        self.assertTrue("基础设施领域高新技术产品" in s)

            
    def test_extraction2(self):
        #fname = self.TEST_PATH + "/章程/华能国际电力股份有限公司章程.pdf.txt" 
        fname = self.TEST_PATH + "/章程/华能国际电力股份有限公司章程.docx.txt" 
        
        ftype = "有限责任公司章程"
        if self.TEXT_FUNC[1] :
            print("TEST FILE : %s (%s)" %(fname, ftype))
            extr = TermsVerification()
            term_list = extr.verify_document(fname, None, ftype)
            
            for elem in term_list :
                if (len(elem) > 2) :
                    e = [el[0] for el in elem[2]]
                    s = ' '.join(e)
                    print(elem[0] + " : " + s)
                    if elem[0] == '文件名称' :
                        self.assertTrue("华能国际电力股份有限公司章程" in s)
                    elif elem[0] == '公司名称' :
                        self.assertTrue("华能国际电力股份有限公司" in s)
                    elif elem[0] == '公司住所' :
                        self.assertIn("北京市西城区复兴门内大街", s)
                    elif elem[0] == '公司性质' :
                        self.assertIn("公司为永久存续的股份有限公司", s)
                    elif elem[0] == '法定代表人' :
                        self.assertIn("公司董事长是公司的法定代表人", s)
                    elif elem[0] == '公司经营范围' :
                        self.assertIn("发展电力事业", s)
                        self.assertIn("吸收国内外资金", s)
                        pass
          
                
                
    def test_extraction3(self):
        fname = self.TEST_PATH + "/劳动合同/Chanel劳动合同.docx.txt"
        ftype = "劳动合同"

        if self.TEXT_FUNC[2] :
            print("TEST FILE : %s (%s)" %(fname, ftype))
            extr = TermsVerification()
            term_list = extr.verify_document(fname, None, ftype)
            
            for elem in term_list :

                if (len(elem) > 2) :
                    e = [el[0] for el in elem[2]]
                    s = ' '.join(e)
                    print(elem[0] + " : " + s)
                    if elem[0] == '合同名称' :
                        self.assertTrue("劳动合同" in s)
                    elif elem[0] == '合同期限' :
                        self.assertTrue("本合同期限" in s)
                    elif elem[0] == '岗位' :
                        self.assertIn("部门从事工作", s)
                        pass
                    elif elem[0] == '工作时间' :
                        self.assertIn("平均每周工作时间40小时的工作制", s)
                        self.assertIn("每天平均8小时", s)
                    elif elem[0] == '争议解决' :
                        self.assertIn("发生劳动争议", s)
                    elif elem[0] == '违约责任' :
                        self.assertIn("承担违约赔偿责任", s)
                    elif elem[0] == '劳动纪律' :
                        self.assertIn("各项规章制度", s)
          
 
 
if __name__ == "__main__":
    unittest.main()
