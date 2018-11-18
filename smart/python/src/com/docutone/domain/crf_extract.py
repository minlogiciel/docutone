# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import sys,os
import codecs

#import CRFPP  



sys.path.append("../")

import shlex
from subprocess import Popen, PIPE
from docutone.utils import docutonejson, dtn_sentence, util

from docutone.utils import crf_utils, docutonelocate, variables
from docutone.logging import dtn_logging as dtn_logger
from docutone import config, working

from docutone.core.crf_tagging import CRFTagging
from docutone.core.clause import Clause

from docutone.document import labor_contract, loan_agreement, transfer_agreement, dtn_document, other_document


class CRFExtract(object):
    
    
    def __init__(self):
        """
        """
        self.tagging = CRFTagging()
        self.dtn_doc = None
        self.categorie = ''
        self.filename = None
        self.fullname = None
        
        
    def create_test_tagging(self, filename, ftype) :
        
        self.fullname = filename
        self.filename = os.path.basename(filename).split('.')[0]
        if ";" in ftype :
            parent, cat = ftype.split(";", 1)
            self.categorie = cat.strip()
            self.ftype = parent.strip()
        else :
            if '（' in ftype :
                index = ftype.find('（')
            elif '(' in ftype :
                index = ftype.find('(')
            else :
                index = 0
            if index > 3 :
                self.categorie = ftype[0:index].strip()
            else :
                self.categorie = ftype.strip()
            self.ftype = None


        ''' if this is not text convert it to text file '''
        if (filename.endswith(".txt")) :
            inputfilename = filename
        else :
            inputfilename = docutonelocate.convert_file(filename)
            

        self.dtn_doc = None
        if self.categorie == dtn_document.LABOR_CONTRACT :
            self.dtn_doc = labor_contract.LaborContract()
        elif self.categorie == dtn_document.LOAN_AGREEMENT :
            self.dtn_doc = loan_agreement.LoanAgreement()
        elif self.categorie == dtn_document.TRANSFER_AGREEMENT :
            self.dtn_doc = transfer_agreement.TransferAgreement()
        else :
            self.dtn_doc = other_document.OtherDocument()

        documents = self.dtn_doc.read(inputfilename)

        self._add_new_clauses(documents, self.dtn_doc._results)
        
        result = self.tagging.tagging_test(documents)
        
        return result

    
    def _add_clause_text(self, documents, sentences, xdata):
        
        i = 0
        nb_s = len(sentences)
        clause_sentences = []
        for words in documents :
            sentence = sentences[i]
            nb = len(words)
            n_in = 0
            n_no = 0
            n_sep = 0
            for nw in range(nb) :
                word = words[nw]
                #if util.is_delimiter(word) :
                    #n_sep += 1

                if word in sentence :
                    if (nw < nb-1) and (n_no < 2) and (n_in > 1) and sentence.endswith(word): 
                        i += 1
                        if i < nb_s :
                            sentence = sentences[i]
                    n_in += 1
                else :
                    n_no += 1
                    if n_no > 3 :
                        break;
            simu = (n_in+n_sep) / nb * 100
            if n_no > 3 or simu < 80 :
                clause_sentences = []
                if i > 1 :
                    for s in clause_sentences :
                        xdata.add_value(s, 1)
                    xdata.set_full()
                    break
                i = 0
            else :
                i += 1
                clause_sentences.append(''.join(words))
                if i >= len(sentences) :
                    for s in clause_sentences :
                        xdata.add_value(s, 1)
                    xdata.set_full()
                    break

    
    def _can_add_clause(self, data):
        if len(data.term_value) == 0 :
            return True
        else :
            for v, s_simu in data.term_value :
                if s_simu != 1 : 
                    return True;
        return False
                            

    def _add_new_clauses(self, documents, result) :
        
        sections = self._load_new_clauses(self.categorie)
        
        if sections and len(sections) > 0 :
            for name, data in result.items() :
                if self._can_add_clause(data) :
                    for section in sections :
                        if name == section.title :
                            self._add_clause_text(documents, section.sentences, data)
   
    
    
   
    def _load_new_clauses(self, categorie) :
        root = os.path.join(working.WORKING_DIR, 'home/data/terms/Template/TEXT')
        path = os.path.join(root, categorie)
        if os.path.exists(path) :
            clause = Clause()
            clause.loading_clauses(path)
            return clause.sections
        else :
            return None
        

    
    def _get_clause_name_for_line(self, sentences):   
        max_n = 1
        clause_name = ''
        first_val = 0
        total = 0
        first_name = None
        if (len(sentences) > 0) :
            for key in sentences.keys() :
                val = sentences.get(key)
                total += val
                if (not first_name and key != crf_utils.NO_NAME) :
                    first_name = key
                    first_val = val
                if val > max_n :
                    max_n = val
                    ''' max used clause name '''
                    clause_name = key
            
            if clause_name != first_name :
                ''' if first used clause name in line > 33% ,take it '''
                if ((first_val / total) > 0.33) :
                    clause_name = first_name
        return clause_name
    
            
    def _parse_output1(self, output, results):
        sentence = ''
        for s in output:
            s = s.decode('utf-8')
            clause_name = ''
            sentences = {}
            for line in s.splitlines():
                if line.strip():
                    pieces = line.split('\t')
                    key = pieces[-1]
                    n = 1
                    clause_name = crf_utils.get_tagging_name (key, self.keywords, self._focus)
                    if (clause_name in sentences.keys()) :
                        n += sentences[clause_name]
                    sentences[clause_name] = n
                    sentence += pieces[0]
                else:
                    clause_name = self._get_clause_name_for_line(sentences)                    
                    crf_utils.add_clause_string(clause_name, sentence, results)
                    sentences = {}
                    sentence = ''
                    
            if len(sentence) > 0 :
                clause_name = self._get_clause_name_for_line(sentences)   
                crf_utils.add_clause_string(clause_name, sentence, results)
  
    def _parse_output(self, document, results):
        sentence = ''
        clause_name = ''
        sentences = {}
        for line in document.splitlines():
            if line.strip():
                n = 1
                pieces = line.split('\t')
                key = pieces[-1]
                clause_name = crf_utils.get_tagging_name (key, self.dtn_doc._keywords, self.dtn_doc._focus_points)
                if (clause_name in sentences.keys()) :
                    n += sentences[clause_name]
                sentences[clause_name] = n
                sentence += pieces[0]
            else:
                clause_name = self._get_clause_name_for_line(sentences)                    
                crf_utils.add_clause_string(clause_name, sentence, results)
                sentences = {}
                sentence = ''
                
        if len(sentence) > 0 :
            clause_name = self._get_clause_name_for_line(sentences)   
            crf_utils.add_clause_string(clause_name, sentence, results)
  
  
    def _parse_buffer(self, output, results):
        document = ''
        for s in output:
            document += s.decode('utf-8')

        self._parse_output(document, results)
          
    def _parse_file(self, fname, results):
        f = codecs.open(fname, 'r', 'utf-8')
        document = ''
        for sentence in f:
            document += sentence
        f.close()
        self._parse_output(document, results)
          
    def extraction(self, filename, ftype, delete_file=True):
        pprocess = False
        output_file = None
        
        test_file = self.create_test_tagging(filename, ftype)
        results = self.dtn_doc._results
        
        
        model_name = crf_utils.get_crf_model_name(self.categorie)
        if not model_name and self.ftype :
            model_name = crf_utils.get_crf_model_name(self.ftype) 
        
        if model_name :
            out_path = crf_utils.get_crf_training_directory()
            model = os.path.join(out_path, model_name+crf_utils.CRF_MODEL_EXT)

            if pprocess :
                command_line = crf_utils.CRF_TEST + ' -m "%s" "%s"' % (model, test_file)
            else :
                output_file = test_file+".out"
                command_line = crf_utils.CRF_TEST + ' -m "%s" -o "%s" "%s"' % (model, output_file, test_file)
                
            command_line = command_line.replace("\\", "/")
            dtn_logger.logger_info("CRF", command_line)
            
            # run CRF++
            if pprocess :
                args = shlex.split(command_line)
                p = Popen(args, shell=True, bufsize=4096, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                output = p.communicate()
                if (p.returncode == 0 or p.returncode == 255) :
                    #self._parse_output(output, results)
                    self._parse_buffer(output, results)
                    
                    dtn_logger.logger_info("CRF", "crf test exit code : %d" %(p.returncode))
                else :
                    dtn_logger.logger_error("CRF", "crf test exit code : %d" %(p.returncode))
            else :
                os.system(command_line)
                self._parse_file(output_file, results)

        else :
            dtn_logger.logger_error("CRF", "crf model file is not found (%s)" %(ftype))
        
        ''' remove test file '''
        
        if delete_file :
            os.remove(test_file)
            if output_file :
                os.remove(output_file)
        return results
 
    
    
    def _to_list(self, extractdata) :
        lists = [] 
        for name, data in extractdata.items() :
            val = []
            simu = 0
            if len(data.term_value) > 0 :
                for v, s_simu in data.term_value :
                    if s_simu > 0: # is term name and find term string
                        simu = s_simu
                        val.append(dtn_sentence.get_sentence(v))
                       
                lists.append([name, val,  simu])
            elif data.level :
                lists.append([name, val,  0])
        return lists
 
    def _to_html_text(self, extractdata) :
        
        lists = []
        for name, data in extractdata.items() :
            text = ""
            if len(data.term_value) > 0 :
                n = 0
                for v, s_simu in data.term_value :
                    if s_simu > 0: # is term name and find term string
                        s = dtn_sentence.get_sentence(v)
                        ss = dtn_document.law_document.parser_sentence(s)
                        text +=  '<p>'
                        if ss :
                            if n == 0 :
                                text +=  '<b>' + ss[1] + ' ' + ss[2] + '</b></p>'
                                n += 1
                            else :
                                text +=  ss[1] + ' ' + ss[2] + '</p>'
                            text += '<p>' # empty line
                        else :
                            text +=  s
                        text +=  '</p>'
         
                lists.append([name, text])
            elif data.level :
                lists.append([name, text])
                pass
        
        return lists
 
 
   
    def to_json(self, lists) :        
        result = {}
        
        result["filename"] = [self.filename, self.fullname, self.categorie]
        #result["result"] = self._to_list(lists)
        result["result"] = self._to_html_text(lists)
        
        docutonejson.print_json(result)

      
    def example(self):
        filename = "/1. 刘岩宏劳动合同-中文版.txt"
        path =  config.CORPUS_DIR + "/TEXT/合同、协议/劳动合同"
        fname = path + filename
        ftype = dtn_document.LABOR_CONTRACT


        fname = 'D:/DTNSoftware/dtn-smart/python/src-test/TESTFile/TEXT/劳动合同/20180105142432809721997560872_00.docx.txt'
        ftype = "劳动合同 （聘用合同）"
        fname = 'D:/DTNSoftware/dtn-smart/python/src-test/TESTFile/doc/劳动合同/6. 长春德而塔-富奥江森高新科技有限公司劳动合同.txt'
        fname = 'D:/DTNSoftware/dtn-smart/python/src-test/TESTFile/doc/劳动合同/1. 刘岩宏劳动合同-中文版.doc'
        #fname = 'D:/DTNSoftware/dtn-smart/python/src-test/TESTFile/doc/劳动合同/4. 劳动合同法模板20180319.docx'
        
        fname = 'D:/DTNSoftware/dtn-smart/python/src-test/TESTFile/doc/劳动合同/孙胜利劳动合同20140210.docx'
        fname = 'D:/DocutoneSoftware/SmartDoc/home/log/TEXT/20180611050815343528435940874_00.docx.txt'
        fname = 'D:/DocutoneSoftware/SmartDoc/home/log/TEXT/test.txt'
      
       
        term_list = self.extraction(fname, ftype, False)
        print("TEST FILE : %s (%s)" %(fname, ftype))
        self.to_json(term_list)
        
    def example1(self):
        fpath = 'D:/DTNSoftware/dtn-smart/python/src-test/TESTFile/TEXT/劳动合同'
        ftype = "劳动合同"

        for name in os.listdir(fpath):
            fname = os.path.join(fpath, name)
            term_list = self.extraction(fname, ftype, False)
            print("TEST FILE : %s (%s)" %(fname, ftype))
        
    def example_transfer(self):
        ftype = dtn_document.TRANSFER_AGREEMENT
        path =  config.TEMPLATE_DIR + "/TEXT/" + ftype
        filename = "/clean_Equity Transfer Agreement-Buy Out 20180319.txt"
        filename = "/a2. Equity Transfer Agreement (Ch. May 31)-Delphi revised1JR4.txt"
        fname = path + filename

        term_list = self.extraction(fname, ftype, False)
        print("TEST FILE : %s (%s)" %(fname, ftype))
        self.to_json(term_list)
        
if __name__ == '__main__':

    extract = CRFExtract()
    extract.example_transfer()
    print("---- Test test_crf.py ----")
    
    

    
  






