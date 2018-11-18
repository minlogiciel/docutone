# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import sys, os
import optparse

SRC_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, SRC_PATH)
sys.path.append(SRC_PATH)



from docutone.domain.verifying import TermsVerification
from docutone.domain.training import Training
from docutone.domain.classifier import Classifier
from docutone.domain.extraction import Extraction

from docutone.utils.convert import Convert, variables

#from docutone.core.ner import NER

from docutone.core.crf import CRF
from docutone.domain.crf_extract import CRFExtract

from docutone.core.text4words import Text4Words
from docutone.core.text4sentences import Text4Sentences
from docutone.core.contract import Contract
from docutone.utils import docutonelocate
from docutone.logging import dtn_logging as dtn_logger

def print_usage():
    usage = 'usage: %prog -a action -i inputfile [-o outputfile] [-v] [-d dictionary]'
    print(usage)



if __name__ == "__main__":
    

    usage = 'usage: %prog -a action -i inputfile [-o outputfile] [-t doctype] [-v] [-d dictionary]'
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-a", type="str", dest="action", help='action.')
    parser.add_option("-i", type="str", dest="input_dir", help='input files or directory.', default=None)
    parser.add_option("-o", type="str", dest="output_dir",help='output files or directory.', default=None)
    parser.add_option("-r", type="str", dest="restart", help='restart', default=0)
    parser.add_option("-v", "--verbose", dest="verbose", help='verbose', default=0)
    parser.add_option("-d", type="str", dest="dict_name", help='dictionary name')
    parser.add_option("-e", type="str", dest="extdict_name", help='extention dictionary name')
    parser.add_option("-t", type="str", dest="doc_type", help='docutoment categorie', default=None)

    (options, args) = parser.parse_args()
        
    verbose = int(options.verbose)
    
    infile = options.input_dir
    o_file = options.output_dir
    
    if options.input_dir == None:
        infile = variables.CORPUS_DIR
        if options.action != 'convert':
            infile = os.path.join(variables.CORPUS_DIR, 'TEXT')

    commd = "-a " +options.action 
    if infile :
        commd += " -i " + infile 
    if o_file :
        commd += " -o " + o_file
    if options.doc_type :
        commd += " -t " + options.doc_type
    
    dtn_logger.logger_info("MAIN", commd)

    if options.action == 'convert' :
        
        '''
        conv = Convert(verbose=verbose, restart=options.restart)   
        o_file = conv.open_output(infile, o_file)
        conv.files_to_text(infile, o_file)    
        conv.close_output()  
        '''
        ofile = docutonelocate.convert_file(infile, True)  

    elif options.action == 'testfile' :
    
        conv = Convert(verbose=verbose, restart=options.restart)   

        conv.test_files_in_directory(infile, o_file)    

    elif options.action == 'changebad' :
                   
        conv = Convert(verbose=verbose, restart=options.restart)   

        conv.change_root_bad_files(infile, o_file)    

 
    elif options.action == 'text4sentences':
        
        ts = Text4Sentences()
        ts.analyze_file(infile)
        ts.show_key_sentences()
    
    elif options.action == 'recognition' :
        
        #norm = NER()
        #norm.create_ner(infile)
        pass
        
    elif options.action == 'training':

        training = Training()
        training.create_datasets(infile)
        training.training_svc()
    
    elif options.action == 'dictionary' :
        
        dictname = options.output_dir
        tw = Text4Words()
        tw.create_dictionary(infile, dictname)

    elif options.action == 'keywords' :
        
        tw = Text4Words()
        tw.get_keywords(infile)
        tw.to_json(10)
 
    elif options.action == 'contract':

        doctype = options.doc_type
        '''
        crf = CRF()
        if doctype :
            infile = infile + "/" + doctype 
            crf.create_categorie_tagging(infile, doctype)
        else :
            crf.create_crf_model()
        '''

    elif options.action == 'classifying':
        classifying = Classifier()
        classifying.classification(infile, o_file)
        classifying.to_json()

    elif options.action == 'extract' or options.action == 'verifying' :
        doctype = options.doc_type
        if doctype == '劳动合同' :
            extr = CRFExtract()
            lists = extr.extraction(infile, doctype)
        else : 
            extr = TermsVerification()
            lists = extr.verify_document(infile, None, doctype)
        extr.to_json(lists)
    '''
    elif options.action == 'verifying' or options.action == 'extract' :
        doctype = options.doc_type
        terms = TermsVerification()
        term_list = terms.verify_document(infile, None, doctype)
        terms.to_json(term_list)
    ''' 
     
        




