#-*-coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import sys
import unittest

from domain import test_var

sys.path.insert(0, test_var.PROG_PATH)


from docutone import config
from docutone.domain.crf_extract import CRFExtract

class DcoumentTestCase(unittest.TestCase):
    
    TEST_PATH = config.TEST_PATH
    extract = CRFExtract()

    def setUp(self):

        pass

    def tearDown(self):
        pass
    
    
    def test_crf1(self):
        fname = self.TEST_PATH + "/营业执照/二连浩通年检后营业执照副本.JPG.txt"
        ftype = "政府批准证书-批文;营业执照"
        term_list = self.extract.extraction(fname, ftype)
        results = self.extract._to_list(term_list)
        print("TEST FILE : %s (%s)" %(fname, ftype))
       
     
        for elem in results :
            s = ''.join(elem[1])
            print("%s : %s" %(elem[0], s))
            if elem[0] == '文件名称' :
                self.assertTrue("企业法人营业执副本" in s)
            elif elem[0] == '法定代表人' :
                self.assertTrue("法定代表人彭踹" in s)
                self.assertTrue("罗伊斯石化有限公司" in s)
            elif elem[0] == '经营范围'  :
                self.assertTrue("铁矿石" in s)
                self.assertTrue("矿产品" in s)
            elif elem[0] == '注册资本'  :
                self.assertTrue("陆仟壹伍拾万元" in s)
           
       
  
        
    def test_crf2(self):
        fname = self.TEST_PATH + "/司法、行政文件/仲裁裁决书.txt"
        ftype = "司法、行政文件;仲裁裁决书"
        term_list = self.extract.extraction(fname, ftype)

        results = self.extract._to_list(term_list)
        print("TEST FILE : %s (%s)" %(fname, ftype))

        for elem in results :
            s = ''.join(elem[1])
            print("%s : %s" %(elem[0], s))
            if elem[0] == '被申请人及其住所地' :
                self.assertTrue("中国移动通信集团" in s)
                self.assertTrue("南京市虎踞路59号" in s)
                self.assertTrue("南京分公司" in s)
            elif elem[0] == '申请人及其住所地' :
                self.assertTrue("周兵" in s)
                self.assertTrue("同舟知识产权事务" in s)
            elif elem[0] == '裁决书编号' :
                self.assertTrue("宁裁字第370" in s)
            elif elem[0] == '裁决书日期'  :
                self.assertTrue("二〇一〇年十二月二十日" in s)
            elif elem[0] == '仲裁机构名称'  :
                self.assertTrue("南京仲裁委员会" in s)
            elif elem[0] == '被申请人法定代表人'  :
                self.assertTrue("王建中国移动通信集团" in s)
            elif elem[0] == '被申请人委托代理人'  :
                self.assertTrue("张晓蒙江苏法德永衡律师事务所" in s)
                self.assertTrue("帆江苏法德永衡律师事务所律师" in s)
       

    def test_crf3(self):
        fname = self.TEST_PATH + "/司法、行政文件/仲裁申请书.txt"
        ftype = "司法、行政文件;仲裁申请书"
        term_list = self.extract.extraction(fname, ftype)
        results = self.extract._to_list(term_list)
        print("TEST FILE : %s (%s)" %(fname, ftype))
        for elem in results :
            s = ''.join(elem[1])
            print("%s : %s" %(elem[0], s))
            if elem[0] == '文件名称' :
                self.assertTrue("仲裁申请书" in s)
            elif elem[0] == '仲裁机构名称'  :
                self.assertTrue("北京仲裁委员会" in s)
            elif elem[0] == '申请人'  :
                self.assertTrue("创发展顾问有限公司" in s)
            elif elem[0] == '申请人地址'  :
                self.assertTrue("香港中环云咸街19-27号" in s)
                self.assertTrue("28800326" in s)
            elif elem[0] == '被申请人'  :
                self.assertTrue("中国国际航空公司" in s)
                self.assertTrue("北京市朝阳区东三环北路甲2号京信大厦" in s)
       
        

    def test_crf4(self):
        fname = self.TEST_PATH + "/司法、行政文件/起诉书.txt"
        ftype = "起诉书"
        term_list = self.extract.extraction(fname, ftype)
        results = self.extract._to_list(term_list)
        print("TEST FILE : %s (%s)" %(fname, ftype))

        for elem in results :
            s = ''.join(elem[1])
            print("%s : %s" %(elem[0], s))
            if elem[0] == '文件名称' :
                self.assertTrue("起诉书" in s)
            elif elem[0] == '原告名称'  :
                self.assertTrue("太维资讯公司" in s)
                self.assertTrue("开曼群岛" in s)
            elif elem[0] == '被告名称'  :
                self.assertTrue("鸿联九五信息产业股份有限公司" in s)
                self.assertTrue("北京市朝阳区团结湖南里五号京龙大厦五层" in s)
       


  
if __name__ == "__main__":
    unittest.main()
