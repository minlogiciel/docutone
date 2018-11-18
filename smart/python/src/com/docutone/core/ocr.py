# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import sys

sys.path.append("../")

import time
#import urllib
from six.moves import urllib
import json
import hashlib
import base64


class OCR(object):
    
    ID_CART = 1
    HAND_WRITTING = 2
    BANK_CARD = 3
    XUNFEI_URL = 'http://webapi.xfyun.cn/v1/service/v1/ocr/'
    def __init__(self):
        """
        """
        self.api_key = 'abcd1234'
        self.x_appid = 'APPID'
       
        

    def _get_url(self, i_type):

        if i_type == self.ID_CART :
            url = self.XUNFEI_URL + 'idcard'
        elif i_type == self.BANK_CARD :
            url = self.XUNFEI_URL + 'bankcard'
        else :
            url = self.XUNFEI_URL + 'handwriting'
        return url
    
    def _get_req_header(self, i_type):
         
        param = {"language": "cn", "location": "true"}
        if i_type == self.ID_CART :
            param = {"engine_type": "idcard", "head_portrait": "0"}
        elif i_type == self.BANK_CARD :
            param = {"engine_type": "bankcard", "card_number_image": "0"}

        
        v = json.dumps(param)
        v = bytes(v, 'utf-8')
        #v = v.encode('utf-8')
        x_param = base64.b64encode(v)

        x_time = int(int(round(time.time() * 1000)) / 1000)
        s = (self.api_key + str(x_time) + x_param).decode('utf-8')
        #x_checksum = hashlib.md5(self.api_key + str(x_time) + str(x_param)).hexdigest()
        x_checksum = hashlib.md5(s).hexdigest()
        x_header = {'X-Appid':self.x_appid, 
                    'X-CurTime': x_time,
                    'X-Param': x_param,
                    'X-CheckSum': x_checksum}
 
        
        return x_header


    def _read_image(self, image):
        f = open(image, 'rb')
        file_content = f.read()
        base64_image = base64.b64encode(file_content)
        body = urllib.parse.urlencode({'image': base64_image})
        return body
 
    
    
    def do_hand_writting_ocr(self, image):

        url = self._get_url(self.HAND_WRITTING)
        x_header = self._get_req_header(self.HAND_WRITTING)
        body = self._read_image(image)

        req = urllib.request.Request(url, body, x_header)
        result = urllib.request.urlopen(req)
        result = result.read()
        print(result)
        
        

        
    def do_idcard_ocr(self, image):
        body = self._read_image(image)
        url = self._get_url(self.ID_CARD)
        x_header = self._get_req_header(self.ID_CARD)
        
        req = urllib.request.Request(url, body, x_header)
        result = urllib.request.urlopen(req)
        result = result.read()
        print(result)


    def do_bankcard_ocr(self, image):

        body = self._read_image(image)
    
        url = self._get_url(self.BANK_CARD)
        x_header = self._get_req_header(self.BANK_CARD)

        req = urllib.request.Request(url, body, x_header)
        result = urllib.request.urlopen(req)
        result = result.read()
        print (result)

        
        
        
if __name__ == '__main__':
        
    path = 'D:/DocutoneSoftware/SmartDoc/home/data/Corpus/doc/证照与批文/商品房销售(预售)许可证'
    filename = '111729285979.jpg'
    ocr = OCR()
    ocr.do_hand_writting_ocr(path+'/'+filename)
    
    
    print( "---- end ----")






