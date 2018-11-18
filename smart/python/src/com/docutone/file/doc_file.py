# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

import subprocess
import sys, os
import zipfile
import xlrd

try:
    from xml.etree.cElementTree import XML
except ImportError:
    from xml.etree.ElementTree import XML
    

if sys.platform == "win32" :
    LIBREOFFICE = "C:\\Program Files (x86)\\LibreOffice 5\\program\\soffice"
else :
    LIBREOFFICE = "soffice"


sys.path.append("../")

from docutone.utils import variables
from docutone.file import dtn_file as dtnf

class DOCFile(dtnf.DTNFile):
    

    def __init__(self):
        pass
        
   
    
    """
    filename : input file name for WORD/XLX/RTF         
    return document text :

    call libreoffice change doc/xlx/rtf to pdf
    args = ['soffice'   --headless
                        --invisible
                        --convert-to pdf filename 
                        --outdir outpath
                        shell=True]
    """
    def doc_to_text(self,filename):

        # get pdf name from tmp directory 
        pdfname = self.get_output_pdf_name(filename)

        # convert doc to pdf 
        subprocess.call('"' + LIBREOFFICE + '" --headless --invisible --convert-to pdf "'+filename+'" --outdir '+ self._tmpfilepath, shell=True)
    
        # convert pdf to text
        if os.path.exists(pdfname) :
            document = self.dt_pdf_to_txt(pdfname)
        else :
            document = ""

        return document
        


    def docxml_to_text(self, filename):

        texts = ""
        
        document = zipfile.ZipFile(filename)
        xml_content = document.read('word/document.xml')
        document.close()
        tree = XML(xml_content)

        sections = []    
        for section in tree.getiterator(self.PARA):
            texts = ''
            for node in section.getiterator(self.TEXT) :
                if node.text : 
                    texts += node.text
            sections.append(''.join(texts))
            
        '''
        for section in tree.getiterator(self.PARA):
            texts = [node.text for node in section.getiterator(self.TEXT) if node.text]
            if texts:
                sections.append(''.join(texts))
        '''
        texts = '\n\n'.join(sections)
            
        
        return texts
 
    def excelxml_to_text(self, filename):
        data = xlrd.open_workbook(filename)
        table = data.sheets()[0]
        nrows = table.nrows

        texts = ""
        for i in range(nrows):
            row = table.row_values(i)
            for cell in row:
                texts += str(cell) + '\t'
            texts+='\n'
        return texts


    def to_text(self, filename):
        lname = filename.toLower()
        texts = ''
        if lname.endswith('.docx') :
            texts = self.docxml_to_text(filename)
        elif lname.endswith('.xlsx') :
            texts = self.excelxml_to_text(filename)
        elif lname.endswith('.doc') or lname.endswith('.xls') or lname.endswith('.rtf'):
            texts = self.doc_to_text(filename)

        return texts
    


if __name__ == "__main__":
    

    filename = variables.CORPUS_DIR + "\\保险\\中国人民财产保险股份有限公司机动车第三者责任保险条款.doc"
    conv = DOCFile() 
    texts = conv.to_text(filename)
    print(texts)




