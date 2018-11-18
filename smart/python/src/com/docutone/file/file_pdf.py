# -*- coding: UTF-8 -*-
from __future__ import unicode_literals


from io import StringIO
import sys, io


from PIL import Image as PI
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


sys.path.append("../")

from docutone.file import dtn_file as dtnf


class PDFFile(dtnf.DTNFile):
    
 
    def __init__(self, output=None):
        super().__init__(output)
        


    def pdf_image_to_text(self, filename, lang, encoding='utf-8', resolution=300):
        super().reset(filename)
        document = ""
        try :           
            filename = filename.encode(encoding)
            image_pdf = Image(filename=filename, resolution=resolution)
            image_jpeg = image_pdf.convert('jpeg')
            texts = []
            for img in image_jpeg.sequence :
                img_page = Image(image = img)
                buff = img_page.make_blob('jpeg')
                txt = self.ocr_image(PI.open(io.BytesIO(buff)), lang=lang) 
                if txt :
                    texts.append(txt)
            document = ''.join(texts)
        except :
            pass
            
        finally :
            pass
        
        return document
    
     
    def pdf_to_text(self, filename, encoding='utf-8'):
        super().reset(filename)
        rsrcmgr = PDFResourceManager()
        retstr = StringIO()
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, codec=encoding, laparams=laparams)
        fp = open(filename, 'rb')
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        document = ""
        password = ""
        try :
            pagenos = set()
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
            
        return document

    def to_text(self, filename, isscan=0, encoding='utf-8'):
        if (isscan) :
            self.pdf_image_to_text(filename, lang='chi_sim', encoding=encoding)
        else :
            self.pdf_to_text(filename, encoding)




if __name__ == "__main__":
    

    filename1 = "D:/downloads/Chrome/50岁的祝福-80.pdf"
    filename = "D:/DocutoneSoftware/SmartDoc/home/data/Corpus/doc/公司章程/Articles of Amendment 12-15-03 JCI.pdf"
   

    conv = PDFFile() 
    texts = conv.to_text(filename1)
    print(texts)
    print("================")
    texts = conv.to_text(filename, 1)
    print(texts)
    print(" **** END **** ")


