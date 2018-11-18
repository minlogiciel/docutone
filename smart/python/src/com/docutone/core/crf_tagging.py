# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import sys, os, codecs

sys.path.append("../")


from docutone.core import document as doc
from docutone.utils import util, crf_utils, variables, docutonelocate, dtn_sentence
from docutone.core.segmentation import Segmentation


class CRFTagging(object):
    
    
    def __init__(self, is_test=True):
        self.seg = Segmentation()
        self.seg.load_suggest_words()
        self.is_test = is_test
        self.categorie = None
        self._focus = None



    def set_categorie(self, categorie) :
        if (self.categorie == categorie) :
            pass
        else :
            self._focus = dtn_sentence.focus.get_template_item(categorie)

        
    def _read_file(self, filename):
        
        sentences = doc.get_file_sentences(filename, is_test=self.is_test)
        words = self.seg.segment(sentences)[0]
        clause_type = ''
        add_sentence = False
        documents = []
    
        for index, s in enumerate(sentences):
            if doc.is_clause_start(s) :
                clause_name = s[2:]
                clause_type = crf_utils.get_word_tagging(clause_name, self._focus)
                add_sentence = True
            elif doc.is_clause_end(s) :
                clause_type = ''
                add_sentence = False
            elif add_sentence and (index < len(words)) :
                documents.append([words[index], clause_type])


        return documents
 
    
    def tagging(self, filename, outputfile):

        ''' if this is not text convert it to text file '''
        if (filename.endswith(".txt")) :
            inputfilename = filename
        else :
            inputfilename = docutonelocate.convert_file(filename)
        
        documents = self._read_file(inputfilename)
        self.outputfile = outputfile
        self.file_tagging(documents)   

    
    def tagging_test(self, documents):

        out_path = variables.get_temp_path()
        testname = util.get_uid() + crf_utils.CRF_FILE_TAG_EXT

        outputfilename = os.path.join(out_path, testname)
        self.outputfile = codecs.open(outputfilename, 'w', 'utf-8')
        self.file_tagging(documents, is_test=True)   
        self.outputfile.close()
        
        return outputfilename

    '''
    tagging file
    '''
    def file_tagging(self, documents, is_test=False):
        '''
                    第一列是文字本身,
                    第二列文字类型，，
                    第三列是词位标记 4-tags : B代表开头，M代表中间，E代表结尾 , S(Single)。
        '''
        clause_type  = ''
        nb_line = len(documents) 
        n = 0
        while n < nb_line :
            if is_test :
                word_list = documents[n]
            else :
                word_list = documents[n][0]
                clause_type = documents[n][1]
            
            n += 1
            n_words = len(word_list)
            for i in range(0, n_words) :
                word = word_list[i]
                ty = crf_utils.get_character_type(word[0])
                if len(word) == 1:
                    ptype = crf_utils.CRF_TAG_SINGLE + clause_type
                    self.outputfile.write(word + "\t" + ty + "\t"+ ptype + "\n")
                else:                      
                    ptype = crf_utils.CRF_TAG_BEGIN + clause_type
                    self.outputfile.write(word[0] + "\t" + ty + "\t" + ptype + "\n")
                    for w in word[1:len(word)-1]:
                        ty = crf_utils.get_character_type(w)
                        ptype = crf_utils.CRF_TAG_MIDDLE + clause_type
                        self.outputfile.write(w  + "\t" + ty + "\t"+ ptype + "\n")
                    
                    w = word[len(word)-1]
                    ty = crf_utils.get_character_type(w)
                    ptype = crf_utils.CRF_TAG_END + clause_type
                    self.outputfile.write(w + "\t" + ty + "\t" + ptype + "\n")
            self.outputfile.write("\n")
            
