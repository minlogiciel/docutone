# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import sys,os, io
import codecs
import jieba

import subprocess
from subprocess import Popen, PIPE

import xlrd
import shutil
        

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO

sys.path.append("../")

from docx import Document

try:
    from xml.etree.cElementTree import XML
except ImportError:
    from xml.etree.ElementTree import XML
import zipfile

from docutone.core.segmentation import Segmentation
from docutone.utils import util, variables



from pyocr import pyocr
from pyocr.builders import TextBuilder
    
from wand.image import Image
from PIL import Image as PI
    
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
    try:
        import OleFileIO_PL
    except ImportError:
        import OleFileIO_PL2 as OleFileIO_PL

    import comtypes.client, win32com.client, fnmatch, pythoncom

    LIBREOFFICE = "C:\\Program Files (x86)\\LibreOffice 5\\program\\soffice"
else :
    LIBREOFFICE = "soffice"


class Convert(object):
    
    SEP = ['?', '!', ';', '？', '！', '。', '；', '……', '…', '"', '-', '_']
    
    WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    PARA = WORD_NAMESPACE + 'p'
    TEXT = WORD_NAMESPACE + 't'
    

    def __init__(self, verbose=0, restart=0, encoding='utf-8'):
        """ 
        init all variable
        
        """
        
        self._verbose = verbose
        self._encoding = encoding
        self._total = 0
        self._error = 0
        self._doc = 0
        self._docx = 0
        self._pdf = 0
        self._image = 0
        self._xlsx = 0
        self._msg = 0
        self._other = 0
        self._all_ok = 0
        
        
    def open_output(self, infile, outpath) :
        """ 
        init all variable
        
        """
          
        self._total = 0
        self._error = 0
        self._doc = 0
        self._docx = 0
        self._pdf = 0
        self._image = 0
        self._xlsx = 0
        self._msg = 0
        self._other = 0
        self._all_ok = 0

        if outpath == None :
            outpath = os.path.join(infile, variables.OUTPUT_DIR)
            
        if not os.path.exists(outpath) :
            os.mkdir(outpath)
        
        self._tmpfilepath = os.path.join(outpath, variables.TEMP_DIR)
        
        if not os.path.exists(self._tmpfilepath) :
            os.mkdir(self._tmpfilepath)

        # open output result file 
        if self._verbose > 0 :
            path = os.path.join(outpath, variables.OUTPUT_RESULT)
            self.outout_result = codecs.open(path, 'w', "utf-8")
        
                
    def close_output(self)         :   
    
        if self._verbose > 0:
            self.outout_result.write("\n\nTotal Files : %d, Error Files : %d \n\n"  % (self._total, self._error))
            self.outout_result.write("\n\nDOC(%d), DOCX(%d),  PDF(%d), IMG(%d), MSG(%d) XLSX(%d)\n\n"  
                    % (self._doc, self._docx, self._pdf, self._image, self._msg, self._xlsx))
            self.outout_result.close()

        if self._verbose > 1:
            print("\n\nTotal Files : %d, Error Files : %d \n\n"  % (self._total, self._error))
            print("\n\nDOC(%d), DOCX(%d),  PDF(%d), IMG(%d), MSG(%d) XLSX(%d)\n\n"  
                    % (self._doc, self._docx, self._pdf, self._image, self._msg, self._xlsx))
        
 
 
 
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
        
        subprocess.call('"' + LIBREOFFICE + '" --headless --invisible --convert-to pdf "'+filename+'" --outdir '+ self._tmpfilepath, shell=True)
        
        # get pdf name from tmp directory 
        base = os.path.basename(filename)
        fname = os.path.splitext(base)[0]+".pdf"
        pdfname = os.path.join(self._tmpfilepath, fname)
        
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
                text = util.normalize_sentence(section.text) 
                texts += text + '\n\n'
            
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
            texts = [node.text for node in section.getiterator(self.TEXT) if node.text]
            if texts:
                sections.append(''.join(texts))

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


    def document_to_text(self, filename, o_file):

        """
        Argument :
        
        filename : input file or path
        
        o_file : output text file
        
        
        Return
        
        document text
        """
            
        texts = "";
        if self._verbose > 1 :
            print("convert file name : "+ filename)
        fname = filename.lower()
        if fname.endswith(".pdf")  :
            texts = self.dt_pdf_to_txt(filename)
            self._pdf += 1
            pass
        elif fname.endswith(".jpg") or fname.endswith(".png") or fname.endswith(".gif") or fname.endswith(".tif") or fname.endswith("tiff") :
            itexts = self.dt_image_to_text(filename, None)
            texts = self.norm_document(itexts)
            self._image += 1
            pass
        elif fname.endswith("docx") :
            #texts = self.dt_docx_to_text(filename)
            texts = self.dt_docxml_to_text(filename)
            self._docx += 1
            pass
        elif fname.endswith("xlsx"):
            texts = self.dt_excelxml_to_text(filename)
            self._xlsx += 1
            pass
        elif fname.endswith(".doc") or fname.endswith(".rtf") or fname.endswith(".xls"):
            texts = self.dt_doc_to_text(filename)
            self._doc += 1
            pass

        elif fname.endswith(".msg"):
            self._msg += 1
            pass
        else :
            self._other += 1
            texts = False
            pass

        return texts
    
    

    def norm_document(self, document):
        """
        Arguments :
        
        document : converted document
        
        return normalize document
        
        """
        norm_sentences = document.split('\n')
        
        seg = Segmentation()

        words, words_no_stop, words_all_filter = seg.segment(norm_sentences)
        
        sentences = ""
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

        if self._verbose > 1 :
            print(sentences)
        return sentences


    def test_document(self, document) :
        """
        检查转换文字 is ok 
        
        """
        
        ret = 0
        if len(document) > 1 :
            
            sentences = document.split("\n")
            norm_sentences = [util.normalize_sentence(s) for s in sentences]

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
       
            total = total/10
            
            if f_total < total or  nb < total :
                l = len(lines)
                if l > 500 :
                    l = 500
                print(lines[0:l])
            else :
                ret = 1
        return ret
 
            
    def test_document_file(self, filename, encoding="utf-8"):


        f = codecs.open(filename, 'r', encoding)
        document = f.read()
        f.close()
        
        ret = self.test_document(document)
        if ret == 0 :
            self._error += 1
            shutil.move(filename, (filename+".bad"))
            print("%d. bad file : %s\n" % (self._error, filename))
        else :
            pass
            """
            fp = codecs.open(filename, 'w', encoding)
            fp.write(ret)
            fp.close()
            """

    def test_all_files(self, fpath):
          
        for name in os.listdir(fpath):
            path = os.path.join(fpath, name)
            if os.path.isdir(path):
                self.test_all_files(path)
            elif name.endswith('.txt') :
                self.test_document_file(path)
    
    def test_files_in_directory(self, infile, fpath):
          
        if fpath == None :
            fpath = os.path.join(infile, variables.OUTPUT_DIR)
            
        for name in os.listdir(fpath):
            path = os.path.join(fpath, name)
            if os.path.isdir(path) and name != variables.DATA_DIR and name != variables.TEMP_DIR :
                self.test_all_files(path)

 
    def change_bad_files(self, fpath):
        
        for name in os.listdir(fpath):
            path = os.path.join(fpath, name)           
            if os.path.isdir(path):
                self.change_bad_files(path)
            elif name.endswith('.bad') :
                textfile = path[0:-4]
                shutil.move(path, textfile)

    def change_root_bad_files(self, infile, fpath):
        
        if fpath == None :
            fpath = os.path.join(infile, variables.OUTPUT_DIR)
        for name in os.listdir(fpath):
            path = os.path.join(fpath, name)           
            if os.path.isdir(path) and name != variables.DATA_DIR and name != variables.TEMP_DIR :
                self.change_bad_files(path)

    
                
    def write_text_file(self, path, outfile, document) :
                
        isok = self.test_document(document)
        if  isok :
            # write text file
            fp = codecs.open(outfile, 'w', self._encoding)
            fp.write(document)
            fp.close()

            if self._verbose > 0 :
                self.outout_result.write(path + " => OK \n")
                if self._verbose > 1 :
                    print("%d write text to %s "  % (self._total, outfile));
        else :
            self._error += 1
            if self._verbose > 0 :
                self.outout_result.write(path + " => ERROR\n")
                if self._verbose > 1 :
                    print("%d. convert error : %s " % (self._error, path));


    def files_to_text(self, fpath, ofile):
        """
        fpath : input file or directory
        
        ofile : output text file or directory
        
        
        """

        if not os.path.exists(ofile) :
            os.mkdir(ofile)
            
        for name in os.listdir(fpath):
            if name[0] == '.' or name[0] == '~' or name == variables.OUTPUT_DIR or name == variables.TEMP_DIR or name == variables.DATA_DIR :
                continue
            path = os.path.join(fpath, name)
            o_file = os.path.join(ofile, name)
            if os.path.isdir(path):
                self.files_to_text(path, o_file)
            else :
                self._total += 1
                o_file += ".txt"
                
                if os.path.exists(o_file) :
                    print("find file : "+ o_file)
                else :
                    document = self.document_to_text(path, o_file)
                    if document == False :
                        self._total -= 1
                    else :
                        self.write_text_file(path, o_file, document);

                


if __name__ == "__main__":
    
    verbose = 0
    if len(sys.argv) > 1 :
        fpath = sys.argv[0]
        if len(sys.argv) > 2 :
            o_file = sys.argv[1]
        else :
            o_file = os.path.join(fpath, variables.OUTPUT_DIR)

    else :
        print("usage: python convert.py inpath outpath")
        if sys.platform == "win32" :
            fpath = "D:\\DOCUTONE\\Corpus\\证照与批文"
            o_file = "D:\\DOCUTONE\\Corpus\TEXT\\证照与批文"
        elif sys.platform == "linux" :
            fpath = "/doc/合同、协议/劳动合同"
            o_file = "/doc/TEXT/合同、协议/劳动合同"
        else :
            fpath = "/Volumes/Macintosh HD/Volumes/DISK_IMG/Docutone/src/docutone/ocr_python"
        

    
    conv = Convert(verbose=verbose, restart=0) 

    conv.open_output(o_file)
    conv.files_to_text(fpath, o_file)    
    conv.close_output()
    
      
    """
    conv.test_root_directory(o_file)    
    conv.change_root_bad_files(o_file)    
    """








