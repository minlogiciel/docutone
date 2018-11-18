# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

import codecs
from io import StringIO
import shutil
from subprocess import Popen, PIPE
import subprocess
import sys, os, io
import zipfile, tempfile

from PIL import Image as PI
from docx import Document
import jieba
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pyocr import pyocr
from pyocr.builders import TextBuilder
try :
    from wand.image import Image
except ImportError :
    pass
import xlrd

from docutone.core.segmentation import Segmentation
from docutone.core import document as dtn_doc
from docutone.utils import variables, util, docx2text
#from docutone.utils import util

'''
文件转换使用
'''
sys.path.append("../")


try:
    from xml.etree.cElementTree import XML
except ImportError:
    from xml.etree.ElementTree import XML
    




    
    
""""
try:
    from PIL import Image
    pil_installed = True
except ImportError:
    pil_installed = False
"""
    
try:
    from pytesseract import image_to_string
except ImportError:
    from pytesseract.pytesseract import image_to_string


if sys.platform == "win32" :
    LIBREOFFICE = "C:\\Program Files (x86)\\LibreOffice 5\\program\\soffice"
else :
    LIBREOFFICE = "soffice"


class File(object):
    
    SEP = ['?', '!', ';', '？', '！', '。', '；', '……', '…', '"', '-', '_']
    WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    PARA = WORD_NAMESPACE + 'p'
    TEXT = WORD_NAMESPACE + 't'
    
    FILE_TYPES = {'.pdf':"PDF", '.doc':'DOC', '.rtf':'DOC', '.xls':'XLS', '.docx':'DOCX', '.xlsx':'XLSX', '.msg' :'MSG',
                    '.jpg':'IMG', '.png':'IMG', '.gif':'IMG', '.tif':'IMG', '.tiff':'IMG', '.txt':'TXT'}


    def __init__(self, filename, output, verbose=0, encoding='utf-8'):
        """ 
        
        """
        
        self._verbose = verbose
        self._encoding = encoding
        self._type = 'OTHER'
        self._error = 0
        self._texts = False
        
        self.set_file_type(filename)
        
        if output == None :
            self._tmpfilepath = os.path.join(tempfile.gettempdir(), "docutone")
            if not os.path.exists(self._tmpfilepath) :
                os.mkdir(self._tmpfilepath)
        else :
            self._tmpfilepath = output

       
        
    def set_file_type(self, filename): 
        
        self._filepath = os.path.dirname(filename)
        self._basename = os.path.basename(filename)
        
        basename = self._basename.lower()

        self._filename = filename
        for ext, name in self.FILE_TYPES.items() :
            if basename.endswith(ext)  :
                self._type = name
                break
    
    def get_output_txt_name(self, filename):
        # get pdf name from tmp directory 
        fname = os.path.basename(filename) + ".txt"
        return os.path.join(self._tmpfilepath, fname)
    
    def get_output_pdf_name(self, filename):
        # get pdf name from tmp directory 
        base = os.path.basename(filename)
        fname = os.path.splitext(base)[0]+".pdf"
        return os.path.join(self._tmpfilepath, fname)

    def get_file_type(self): 
        return self._type
    
    def get_file_name(self): 
        return self._basename

           
    def dt_image_to_text(self, filename, buff, lang='chi_sim'): # chinese simple
        """ 
        Argument :
        
        filename : input file name
                
        Return :
        
        return file text
        
        
        Note :
        image file to text file
        """
        
        tools = pyocr.get_available_tools()[:]
        document = ""
        if len(tools) > 0:
            builder=TextBuilder()
            if type(filename) is str:
                document = tools[0].image_to_string(PI.open(filename), lang=lang, builder=builder) 
            elif buff :
                document = tools[0].image_to_string(PI.open(io.BytesIO(buff)), lang=lang, builder=builder) 
            
        return document
 

    def dt_pdf_image_to_txt(self, filename, codec='utf-8'):
        """ 
        Argument :
        
        filename : input file name
        
        Return :
        
        return file text
        
        
        Note :
        pdf file to text file
        """
        document = ""
        try :
            
            filename = filename.encode('utf-8')
            image_pdf = Image(filename=filename, resolution=300)
            image_jpeg = image_pdf.convert('jpeg')
            texts = []
            for img in image_jpeg.sequence:
                img_page = Image(image = img)
                blob = img_page.make_blob('jpeg')
                txt = self.dt_image_to_text(None, blob)
                if txt :
                    texts.append(txt)
            document = ''.join(texts)
        except :
            pass
            
        finally :
            pass
        
        return document
    
     
    def dt_pdf_to_txt(self, filename, codec='utf-8'):
        """ 
        Argument :
        
        filename : input file name
                
        Return :
        
        return file text
        
        
        Note :
        pdf file to text file
        """
        

        rsrcmgr = PDFResourceManager()
        retstr = StringIO()
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
        fp = open(filename, 'rb')
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        document = ""
        try :
            password = ""
            pagenos=set()
            maxpages = 0
            caching = True
            for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages,   password=password,caching=caching, check_extractable=True):
            #for page in PDFPage.get_pages(fp):
                interpreter.process_page(page)
    
            document = retstr.getvalue()
        except :
            pass
            
        finally :
            fp.close()
            device.close()
            retstr.close()
        
        if len(document) < 32 :
            print("Call pdf to image to text : %s " % filename)
            document = self.dt_pdf_image_to_txt(filename)
            
        return document


    #WORD/XLX/RTF 文件转换
    def dt_doc_to_text(self,filename):
        """
        filename : input word file
        
        return document text :
        
        
        call libreoffice change doc/xlx/rtf to pdf
        args = ['soffice'   --headless
                            --invisible
                            --convert-to pdf filename 
                            --outdir outpath
                            shell=True]
        """
        
                
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
        


    def dt_docx_to_text(self, filename, codec='utf-8' ):
        """ 
        Argument :
        
        filename : input file name
        
        Return :
        
        return file text
        
        
        Note :
        
        docx file to text 
        
        """

        texts = ""
        try :
            
            document = Document(filename)
            
            for section in document.sections:
                #text = util.normalize_sentence(section.text)
                texts += section.text + '\n'
            
        except :
            
            pass
        finally:
            pass
            
        
        return texts

    def dt_docxml_to_text(self, filename, codec='utf-8' ):
        """ 
        Argument :
        
        filename : input file name
        
        Return :
        
        return file text
        
        
        Note :
        
        docx file to text 

        """

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
 
    def dt_excelxml_to_text(self, filename, codec='utf-8'):
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


    def convert(self):

        """
        Argument :
        
        Return
        
        document text
        """
            
        filename = self._filename
        if self._verbose > 1 :
            print("convert file name : "+ filename)

        if self._type == 'PDF'  :
            texts = self.dt_pdf_to_txt(filename)
            self._texts = self.norm_document(texts, test=False)
            pass
        
        elif self._type == 'IMG' :
            itexts = self.dt_image_to_text(filename, None)
            self._texts = self.norm_document(itexts)
            pass
        
        elif self._type == 'DOCX':
            #texts = self.dt_docx_to_text(filename)
            texts = self.dt_docxml_to_text(filename)
            
            # texts = docx2text.process(filename)
            
            self._texts = self.norm_document(texts, test=False)
            pass
        
        elif self._type == 'XLSX' :
            self._texts = self.dt_excelxml_to_text(filename)
            pass
        
        elif self._type == 'DOC' :
            self._texts = self.dt_doc_to_text(filename)
            pass

        elif self._type == 'XLS':
            self._texts = self.dt_doc_to_text(filename)
            pass

        elif self._type == 'TXT' :
            
            pass
        elif self._type == 'MSG' :

            pass

        return self._texts
    
    

    def norm_document(self, document, test=True):
        """
        Arguments :
        
        document : converted document
        
        return normalize document
        
        """
        norm_sentences = document.split('\n')
        sentences = ""
 
        if test :
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
    
        else :
            for sentence in norm_sentences :
                s = sentence
                if s: 
                    sentences += s + '\n'
           
        return sentences

    def _set_categorie(self, sentences):
        from docutone.utils import synonyms
        from docutone.document import dtn_document
        
        self.categorie = None
        if sentences :
            stop = False
            labor_contract = synonyms.get_contract_infos("LABOR_NAME")
            for s in sentences :
                if dtn_document.TRANSFER_AGREEMENT in s: 
                    self.categorie = dtn_document.TRANSFER_AGREEMENT
                    stop = True
                elif dtn_document.COMPANY_POLICY in s :
                    self.categorie = dtn_document.COMPANY_POLICY
                    stop = True
                elif dtn_document.LOAN_AGREEMENT in s or dtn_document.CREDIT_AGREEMENT in s :
                    self.categorie = dtn_document.LOAN_AGREEMENT
                    stop = True
                else :
                    for name in labor_contract :
                        if name in s :
                            self.categorie = dtn_document.LABOR_CONTRACT
                            stop = True
                            break
                if stop :
                    break

    def get_document_words(self):        
        doc_words = False
        sentences = None
        if self._type == 'TXT' :
            '''doc_words = dtn_doc.get_document_words(self._filename)'''
            sentences = dtn_doc.get_file_sentences(self._filename)
        else :
            outfile = self.get_output_txt_name(self._filename)
            if os.path.exists(outfile) :
                '''doc_words = dtn_doc.get_document_words(outfile)'''
                sentences = dtn_doc.get_file_sentences(outfile)
            else :
                docs = self.convert()
                if docs :
                    fp = codecs.open(outfile, 'w', self._encoding)
                    fp.write(docs)
                    fp.close()
                    sentences = docs.split('\n')
        
        self._set_categorie(sentences)
        if sentences :
            doc_words = dtn_doc.get_sentences_words(sentences)
        
        return doc_words

        
    def test_document(self, document) :
        """
                    检查转换文字 is ok 
        
        """
        ret = 0
        if len(document) > 1 :
            
            sentences = document.split("\n")
            norm_sentences = [s for s in sentences]

            seg = Segmentation()
            words, words_no_stop, words_all_filter = seg.segment(norm_sentences)
            
            total = 0;
            f_total = 0;
            nb = 0;
            lines = ""
            for sentence in words:
                if len(sentence) > 0 :
                    total += len(sentence)
                    ss = [w for w in sentence if len(w) > 1]
                    nb += len(ss)
                    lines += ' '.join(sentence) +"\n"
            
            for sentence in words_all_filter:
                f_total += len(sentence)
       
            total = total/5
            
            if f_total < total or  nb < total :
                l = len(lines)
                if l > 500 :
                    l = 500
                print(lines[0:l])
            else :
                ret = 1
        return ret
 
            
    def test_bad_file(self) :
        f = codecs.open(self._filename, 'r', self._encoding)
        document = f.read()
        f.close()
        
        ret = self.test_document(document)
        if ret == 0 :
            shutil.move(self._filename, (self._filename+".bad"))
            if self._verbose > 1 :
                print("set to bad file : %s\n" % (self._filename))
        else :
            pass



if __name__ == "__main__":
    
    flist = [variables.CORPUS_DIR + "\\保险\\中国人民财产保险股份有限公司机动车第三者责任保险条款.doc",
             variables.CORPUS_DIR + "\\公司章程\\amended Articles 14 Oct 2004 revised.pdf",
             variables.CORPUS_DIR + "\\批文\\77254508.jpg"]
    
    verbose = 0
    filename = 'D:/DocutoneSoftware/SmartDoc/home/data/Corpus/doc/证照与批文/税务登记证/17549.jpg'

    conv = File(filename, None, verbose=verbose) 
    texts = conv.convert()
    print(texts)
    '''
    for filename in flist : 
        conv = File(filename, None, verbose=verbose) 
        texts = conv.convert()
        print(texts)

    '''



