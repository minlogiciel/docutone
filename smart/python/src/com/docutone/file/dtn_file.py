# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

import codecs
import shutil
import sys, os
import tempfile
import jieba
from pyocr import pyocr
from pyocr.builders import TextBuilder

from pytesseract import image_to_string

sys.path.append("../")



from docutone.core.segmentation import Segmentation
from docutone.core import document as dtn_doc


    
FILE_TYPES = {'.pdf':"PDF", 
              '.doc':'DOC', 
              '.rtf':'DOC', 
              '.xls':'XLS', 
              '.docx':'DOCX', 
              '.xlsx':'XLSX', 
              '.msg' :'MSG',
              '.jpg':'IMG', 
              '.png':'IMG', 
              '.gif':'IMG', 
              '.tif':'IMG', 
              '.tiff':'IMG', 
              '.txt':'TXT'}


class DTNFile(object):
    


    def __init__(self, output=None):
        
        if output == None :
            self._tmpfilepath = os.path.join(tempfile.gettempdir(), "docutone")
        else :
            self._tmpfilepath = output
        
        if not os.path.exists(self._tmpfilepath) :
            os.mkdir(self._tmpfilepath)

       
    def reset(self, filename): 
        
        self._type = 'OTHER'
        self._error = 0
        self._texts = False
        self._filename = filename
        self._filepath = os.path.dirname(filename)
        self._basename = os.path.basename(filename)
        
        basename = self._basename.lower()

        for ext, name in FILE_TYPES.items() :
            if basename.endswith(ext)  :
                self._type = name
                break
    
    
    def get_output_txt_name(self):
        fname = self._basename + ".txt"
        return os.path.join(self._tmpfilepath, fname)
    
    def get_output_pdf_name(self):
        fname = os.path.splitext(self._basename)[0]+".pdf"
        return os.path.join(self._tmpfilepath, fname)


    def ocr_image(self, buff, lang='chi_sim'): # chinese simple
        
        tools = pyocr.get_available_tools()[:]
        document = ""
        if len(tools) > 0:
            builder=TextBuilder()
            document = tools[0].image_to_string(buff, lang=lang, builder=builder) 
            
        return document
 

    def norm_document(self, document):
        norm_sentences = document.split('\n')
        sentences = ""
 
        seg = Segmentation()
        words = seg.segment(norm_sentences)[0]
        for sentence in words :
            hasword = False
            for w in sentence :
                if w in self.SEP :
                    sentences += w
                elif len(w) == 1 :
                    # 去掉不常用的单字
                    n = jieba.get_FREQ(w)
                    if n != None and n > 10 :
                        sentences += w
                else :
                    hasword = True
                    sentences += w
            if hasword :
                sentences += '\n'
    
        return sentences


    def get_document_words(self, sentences):        
        doc_words = False
        if sentences :
            doc_words = dtn_doc.get_sentences_words(sentences)
        
        return doc_words

        



if __name__ == "__main__":
    

    verbose = 0
    filename = 'D:/DocutoneSoftware/SmartDoc/home/data/Corpus/doc/证照与批文/税务登记证/17549.jpg'

    


