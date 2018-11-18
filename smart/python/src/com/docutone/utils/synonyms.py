#-*- encoding:utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

import sys

sys.path.append("../")

from docutone.utils import docutonejson, docutonelocate



def load_dictionary(filename):
    fname = docutonelocate.dtn_locate_file(filename)
    return docutonejson.load_json(fname)
        
def save_dictionary(filename, lists):
    fname = docutonelocate.dtn_locate_file(filename)
    docutonejson.save_json_format(lists, fname, 4)

    
def get_sictionary(name, lists):
    if (name in lists.keys()) :
        return lists[name]
    else :
        return None
    
def add_dictionary(key, word, lists):
    if (key in lists.keys()) :
        syno = lists[key];
        if word not in syno :
            syno.append(word)
    else :
        lists[key] = [word]


synonym_file = "synonyms.json"
synonyms_words = load_dictionary(synonym_file)

contrac_info_file = "contract_info.json"
contract_infos = load_dictionary(contrac_info_file)


    

def load_synonyms():
    return load_dictionary(synonym_file)
    
def save_synonyms():
    save_dictionary(synonym_file, synonyms_words)
    
def add_synonym(key, word):
    add_dictionary(key, word, synonyms_words)
    
def get_synonyms(name):
    return get_sictionary(name, synonyms_words)




def load_contract_infos():
    load_dictionary(contrac_info_file)
    
def save_contract_infos():
    save_dictionary(contrac_info_file, contract_infos)
    
def add_contract_info(key, word):
    add_dictionary(key, word, contract_infos)
    
def get_contract_infos(name):
    return get_sictionary(name, contract_infos)


       
    
if __name__ == "__main__":
    
    

    
    if True :
        add_synonym("违约责任", "赔偿和救济")
        add_synonym("适用法律", "法律适用")
        add_synonym("适用法律", "适用的法律")
        add_synonym("转让标的", "购买和出售")
        add_synonym("转让标的", "股权的转让与受让")
        add_synonym("转让价格", "受让价格")
        add_synonym("支付", "受让价格的付款")
        add_synonym("生效", "生效日")
        add_synonym("交易完成", "政府批准和登记")
        add_synonym("交易完成", "股权转让的完成")
        
        add_synonym("各方义务", "卖方的义务")
        add_synonym("各方义务", "买方的义务")
        add_synonym("陈述与保证", "陈述和保证")
        add_synonym("陈述与保证", "声明与保证")
        add_synonym("前提条件", "报批条件")
     

        save_synonyms()
    
    
    else :
        add_contract_info("LABOR_NAME", "行政人员聘用合同")

        save_contract_infos()
    
    
    
    print("---end ---")
    