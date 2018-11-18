# -*- coding: UTF-8 -*-
from __future__ import unicode_literals


import sys
from PIL import Image as PI


sys.path.append("../")



from docutone.file import dtn_file as dtnf

class ImageFile(dtnf.DTNFile):
    

    def __init__(self):
        pass
        

    def to_text(self, filename): # chinese simple
        
        document = self.ocr_image(PI.open(filename), lang='chi_sim') 
            
        return document
 
    
    

if __name__ == "__main__":
    

    filename = 'D:/DocutoneSoftware/SmartDoc/home/data/Corpus/doc/证照与批文/税务登记证/17549.jpg'

    conv = ImageFile() 
    texts = conv.to_text(filename)
    print(texts)



