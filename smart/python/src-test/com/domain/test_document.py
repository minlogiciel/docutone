#-*-coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import sys, os
import unittest

from domain import test_var

sys.path.insert(0, test_var.PROG_PATH)


from docutone import config
from docutone.document import dtn_document, labor_contract, loan_agreement, transfer_agreement

class DcoumentTestCase(unittest.TestCase):
    
    TEST_PATH = 'D:/DTNSoftware/dtn-smart/python/src-test/TESTFile/TEXT/'
    employement = labor_contract.LaborContract()
    loan = loan_agreement.LoanAgreement()
    transfer = transfer_agreement.TransferAgreement()

    TEST_EMPLOYEE2 = True
    TEST_LOAN = False
    TEST_TRANSFER = False
    
    def setUp(self):

        pass

    def tearDown(self):
        pass
    


    def test_employement2(self):
        
        if self.TEST_EMPLOYEE2 :
            fpath = self.TEST_PATH + dtn_document.LABOR_CONTRACT
            for name in os.listdir(fpath):
                fname = os.path.join(fpath, name)
                doc = self.employement.read(fname)
                print('------ %s -----------' %fname)
                self.debug(doc)
           

    def debug(self, doc=None):
        print('*** %s ***' %(self.employement._title))
        print('日期 : %s' %(self.employement._contract_date))
        print('甲方 : %s' %('\n'.join(self.employement.society)))
        print('乙方 : %s' %('\n'.join(self.employement.employer)))
        
        
    def debug_loan(self, doc=None):
        print('*** %s ***' %(self.loan._title))
        print('日期 : %s' %(self.loan._contract_date))
        print('借款人 : %s' %(self.loan.borrower))
        print('贷款人 : %s' %(self.loan.lender))
        print('保证人 : %s' %(self.loan.guarantor))
        print('协调安排行 : %s' %(self.loan.arranger))
        print('贷款代理行 : %s' %(self.loan.loan_bank))
        print('担保代理行 : %s' %(self.loan.guarant_bank))



    def test_loan(self):
        if self.TEST_LOAN :
            fpath = self.TEST_PATH + dtn_document.LOAN_AGREEMENT
            for name in os.listdir(fpath):
                fname = os.path.join(fpath, name)
                doc = self.loan.read(fname)
                print('------ %s -----------' %name)
                self.debug_loan(doc)

        
    def debug_tranfer(self, doc=None):
        print('*** %s ***' %(self.transfer._title))
        print('日期 : %s' %(self.transfer._contract_date))
        print('转让方 : %s' %('\n'.join(self.transfer.transfor)))
        print('受让方 : %s' %('\n'.join(self.transfer.assignee)))



    def test_transfer(self):
        if self.TEST_TRANSFER :
            fpath = self.TEST_PATH + dtn_document.TRANSFER_AGREEMENT
            for name in os.listdir(fpath):
                fname = os.path.join(fpath, name)
                doc = self.transfer.read(fname)
                print('------ %s -----------' %name)
                self.debug_tranfer(doc)


        
  
if __name__ == "__main__":
    unittest.main()
