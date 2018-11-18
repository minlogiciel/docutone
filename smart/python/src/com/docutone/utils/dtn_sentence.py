# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import sys

sys.path.append("../")

from docutone.utils.terms import Terms
from docutone.utils import synonyms
from docutone.utils.focus import Focus


term_instance = Terms()
focus = Focus()
focus.load()

def get_document_categorie(termtype):
    item = focus.get_template_item(termtype)
    if item :
        names = item.get_item_names()
    else :
        names = term_instance.get_document_categorie(termtype)
    return names


def get_all_term_items():
    return term_instance.get_all_term_items()


def is_keyword_in_sentence(key, sentence):
    if key in sentence :
        # if keyword in the beginning of sentence
        n = sentence.index(key)
        if n < 5 :
            return True
    return False

    
def is_keyword_title_sentence(sentence):
    s = sentence.strip()
    if s[-1] == ':'  or s[-1] =='：':
        return True
    return False



def get_sentence(p):
    if isinstance(p, str) :
        s = p
    else :
        s = p[0]
    return s
    
        
def get_keywords_by_name(title, keywords):
        
    for key in keywords :
        if key == title :
            return key
            
        synonym_words = synonyms.get_synonyms(key)
        if (synonym_words) :
            for s_key in synonym_words :
                if s_key == title :
                    return key
            
    return None
    
    
def get_keyword_from_sentence(sentence, keywords):
    
    ''' sort keywords frol long to short '''
    key_list = sorted(keywords, key=len, reverse=True)
    for key in key_list :
        if is_keyword_in_sentence(key, sentence) :
            return key
            
        # all words in sentence
        s_keywords = synonyms.get_synonyms(key)
        if s_keywords and len(s_keywords) > 0 :
            syno_list = sorted(s_keywords, key=len, reverse=True)
            for s_key in syno_list :
                if is_keyword_in_sentence(s_key, sentence) :
                    return key

    return None

    
    

    






