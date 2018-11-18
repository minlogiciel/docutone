# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import sys, os, time


sys.path.append("../")

from gensim.models import doc2vec

from docutone.document import dtn_document

from docutone.core.contract import Contract
from docutone.utils import docutonejson, variables, dtn_sentence
from docutone.core.document import LawDocument
from docutone.utils import docutonelocate, util
from docutone.core.segmentation import Segmentation

from docutone.utils.extract_data import ExtractData
from docutone.logging import dtn_logging as dtn_logger
from docutone import config
'''
this class verify document type 
法律文件条款提取验证
'''        

class TermsVerification(object):      
    
    SIMU_SEUIL = 0.6
    

    def __init__(self):
        
        self.contract = Contract(0)
        
        self.verified_terms = {}
        self._filetime = None
        self.fullname = None
        self.filename = None
        self._title = None
        self._contract_date = None
        self.keywords = []
        
        self.segment = Segmentation()
        self.document = LawDocument()
                
                
    def _init_terms_table(self, filename, termtype) :
        self.categorie = termtype
        # get file name

        self.fullname = filename
        self.filename = os.path.basename(filename).split('.')[0]
        # get file created date
        self._filetime = util.get_creation_file_date(filename)
       
        # init verfying tab
        self.verified_terms = {}
        self.keywords = dtn_sentence.get_document_categorie(termtype)
        for key in self.keywords :
            self.verified_terms[key] = ExtractData(key, termtype)
       
        dtn_logger.logger_info("VERIFY", "%s (%s)" %(filename, termtype))
        

                
    def _load_terms_model(self, doctype=None)  :
        
        self.contract.doc_path = doctype
        
        self.term_names = self.contract.load_term_label()
        self.term_set = self.contract.load_term_set()
        self.term_list = self.contract.load_term_list()

        fname = self.contract.get_term_model_name()
        self.model = doc2vec.Doc2Vec.load(fname)
      
   
    def similar_term(self, term_words, termtype)  :
        
        tname = None
        ttype = None
        simu = 0.0
        docvec = self.model.infer_vector(doc_words=term_words)
        sims = self.model.docvecs.most_similar(positive=[docvec], topn=5)
        
        for i in range(len(sims)) :
            n_term = int(sims[i][0])
            f_simu = sims[i][1]
            if f_simu > self.SIMU_SEUIL :
                if (n_term >= len(self.term_list)) :
                    continue
                
                '''term = self.term_names[self.term_set[n_term]-1]'''
                term_name = self.term_list[n_term]
                if ':' in term_name :
                    tab = term_name.split(':',1)
                    if tab[1] == termtype :
                        if tname == None :
                            tname = tab[0]
                            ttype = tab[1]
                            simu = f_simu
                            break
                        
                    
                elif term_name ==  termtype :
                    tname = term_name
                    ttype = term_name
                    simu = f_simu
                    break

            else :
                break

        return tname, ttype, simu
                
                
    def verify_term(self, text)  :

        term_words = self.contract.get_term_words(text)   
    
        return self.similar_term(term_words)
                
    
    def _add_verified_sentences(self, termname, n_start, end_char, simu):

        nl = n_start
        st = self.document.norm_sentences[nl]
        ps = self.document.parser_sentence(st)
        if ps :
            st = ps[1]
            if ps[1][-1] is not ' ' and ps[2][0] is not ' ':
                st += ' '
            st += ps[2]
            
        self.verified_terms[termname].add_value(st, simu)  
        while len(st) == 0 or st[-1] != end_char :
            nl += 1
            st = self.document.norm_sentences[nl]
            self.verified_terms[termname].add_value(st, 1)  

    
    
       
    ''' get document term '''
    def get_terms(self, filename, filetype):
                   
        
        if (filename.endswith(".txt")) :
            ofile = filename
        else :
            ofile = docutonelocate.convert_file(filename)
            
        #lawdocument.create_document(ofile, filetype)
        self.document.read_section(ofile)
            
        self._title = self.document.document_name
        self._contract_date = self.document.document_date
        if self._title:
            if '文件名称' in self.keywords :
                self.verified_terms['文件名称'].add_value(self._title, 1)
            elif '合同名称' in self.keywords : 
                self.verified_terms['合同名称'].add_value(self._title, 1)
        if self._contract_date :
            if '签约日期' in self.keywords :
                self.verified_terms['签约日期'].add_value(self._contract_date, 1)
            elif '签发日期' in self.keywords : 
                self.verified_terms['签发日期'].add_value(self._contract_date, 1)
            elif '合同日期' in self.keywords : 
                self.verified_terms['合同日期'].add_value(self._contract_date, 1)

        
        terms = []
        '''
        prev_sentence = ''
        for s in ld.document_header :
            prev_sentence += s
            if ld._is_sentence_end(s) :
                terms.append([prev_sentence])
                prev_sentence = ''
        if prev_sentence :
            terms.append([prev_sentence])
        '''
        nb = len(self.document.sections)
        if nb > 0 :
            index = 0    
            while index < nb :
                p = self.document.sections[index]
                index += 1
                ''' if section title = term name add it to verfied table ''' 
                if p.title :
                    termname = dtn_sentence.get_keywords_by_name(p.title, self.keywords)
                    if termname :
                        if len(p.sentences) > 0 :
                            for s in p.sentences :
                                if isinstance(s, str) :
                                    self.verified_terms[termname].add_value(s, 1)
                                else :
                                    s_line = s[0]
                                    self._add_verified_sentences(termname, s[1], s_line[-1], 1)

                        while index < nb :
                            sp = self.document.sections[index]
                            index += 1
                            if sp.level > p.level :
                                for s in sp.sentences :
                                    if isinstance(s, str) :
                                        self.verified_terms[termname].add_value(s, 1)
                                    else :
                                        s_line = s[0]
                                        self._add_verified_sentences(termname, s[1], s_line[-1], 1)
                            else :
                                ''' back to prev section '''
                                index -= 1
                                break

                        
                if len(p.sentences) > 0 :
                    terms.append(p.sentences)
                
        return terms

    
               
    def _verified_clauses(self, filename, termtype) :
          
        terms = self.get_terms(filename, termtype)
        for term in terms :
            sentences = [s[0] for s in term]
 
            n_start = term[0][1]
            end_char = sentences[-1][-1]
            
            term_words = self.contract.get_term_words(sentences)   
            
            tname, ttype, simu = self.similar_term(term_words, termtype)
            if ttype != None and tname != None :
                if ttype == termtype :
                    if tname in self.verified_terms.keys() :
                        '''
                        for s in sentences :
                            self.verified_terms[tname].add_value(s, simu)
                        '''
                        self._add_verified_sentences(tname, n_start, end_char, simu)
                        
    
    def create_contract_model(self, fpath) :
      
        self.contract.create_terms(fpath)  
 
    def get_contract_date(self) :

        return time.strftime("%Y-%m-%d   %H:%M:%S", time.gmtime(self._filetime))

    
    def verify_document(self, filename,  doctype, termtype) :

        # init clause table
        self._init_terms_table(filename, termtype)
              
        # load lagal terms training model 
        self._load_terms_model(doctype)
        
        
        self._verified_clauses(filename, termtype)
      
        sorted_list = []
        
        for key in self.keywords :
            if key in self.verified_terms.keys() :
                term = self.verified_terms[key].term_value
                if (len(term) > 0):
                    sorted_list.append((key, 1, term))
                else :
                    sorted_list.append((key, 0))
            
        
        
        return sorted_list
       
    def _to_html_text(self, term_list) :
        
        lists = []
        for elem in term_list :
            if len(elem) == 3 :
                name, _, data = elem
            else :
                continue
                
            text = ""
            if len(data) > 0 :
                for v, s_simu in data :
                    if s_simu > 0: # is term name and find term string
                        s = dtn_sentence.get_sentence(v)
                        ss = dtn_document.law_document.parser_sentence(s)
                        text +=  '<p>'
                        if ss :
                            text +=  '<b>' + ss[1] + ' ' + ss[2] + '</b></p>'
                            text += '<p>' # empty line
                        else :
                            text +=  s
                        text +=  '</p>'
         
                lists.append([name, text])
            else :
                lists.append([name, text])
        
        return lists
 

    def to_json(self, term_list) :
        result = {}
        '''
        result["FILE"] = [self.fullname]
        result["TEMPS"] = [str(self._filetime)]
        result["TTILE"] = [self._title]
        '''
        
        result["filename"] = [self.filename, self.fullname, self.categorie]
        result["result"] = self._to_html_text(term_list)
        #result["result"] = self._to_list(lists)


        docutonejson.print_json(result)

    def example0(self):

        fname = config.TEST_PATH + "/劳动合同/Chanel劳动合同.docx.txt"
        ftype = "劳动合同"
        term_list = self.verify_document(fname, None, ftype)
        self.to_json(term_list)

    def example1(self):

        fname = config.TEST_PATH + "/章程/华能国际电力股份有限公司章程.pdf.txt" 
        ftype = "有限责任公司章程"
        term_list = self.verify_document(fname, None, ftype)
        self.to_json(term_list)

    def example2(self):

        fname = config.TEST_PATH + "/章程/华能国际电力股份有限公司章程.docx.txt" 
        ftype = "有限责任公司章程"
        term_list = self.verify_document(fname, None, ftype)
        self.to_json(term_list)

    
if __name__ == "__main__":
    
    terms = TermsVerification()
    #terms.example1()
    terms.example2()
    

    print("=== end ====")
    
   
    
    
    