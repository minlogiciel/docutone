# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import sys, os, codecs, shutil

sys.path.append("../")


from docutone.utils import variables
from docutone.utils.base import File
from docutone.logging import dtn_logging as dtn_logger
from docutone import config
'''
文件转换
'''

class Convert(object):
    
    def __init__(self, verbose=0, restart=0, encoding='utf-8'):
        """ 
        init all variable
        
        """
        
        self._restart = restart
        self._verbose = verbose
        self._encoding = encoding
        self._ftypes = {"PDF":0, 'DOC':0, 'XLS':0, 'DOCX':0, 'XLSX':0, 'MSG':0, 'IMG':0, 'TXT':0, 'OTHER':0}
        self._total = 0
        self._error = 0
        
        self._tmpfilepath = variables.get_temp_path()
        
    def open_output(self, infile, outpath) :
        """ 
        init all variable
        
        """ 
        self._ftypes = {"PDF":0, 'DOC':0, 'XLS':0, 'DOCX':0, 'XLSX':0, 'MSG':0, 'IMG':0, 'TXT':0, 'OTHER':0}
        self._total = 0
        self._error = 0
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
        
        return outpath
                
    def close_output(self)         :   
    
        if self._verbose > 0:
            dtn_logger.logger_info("CONVERT", "Total Files : %d, Error Files : %d \n\n"  % (self._total, self._error))
            dtn_logger.logger_info("CONVERT", "DOC(%d), DOCX(%d),  PDF(%d), IMG(%d),  XLSX(%d), TXT(%d), MSG(%d)"  
                     % (self._ftypes['DOC'], self._ftypes['DOCX'], self._ftypes['PDF'], self._ftypes['IMG'], self._ftypes['XLSX'], self._ftypes['TXT'], self._ftypes['MSG']))
            self.outout_result.close()

        if self._verbose > 1:
            print("\n\nTotal Files : %d, Error Files : %d \n\n"  % (self._total, self._error))
            print("\n\nDOC(%d), DOCX(%d),  PDF(%d), IMG(%d), XLSX(%d), MSG(%d), MSG(%d) \n\n"  
                    % (self._ftypes['DOC'], self._ftypes['DOCX'], self._ftypes['PDF'], self._ftypes['IMG'], self._ftypes['XLSX'], self._ftypes['TXT'], self._ftypes['MSG']))
        
 
 
    def write_text_file(self, path, outfile, document, f) :
                
        #isok = f.test_document(document)
        isok = False
        if document and len(document) > 100:
            isok = True
        if  isok :
            # write text file
            fp = codecs.open(outfile, 'w', self._encoding)
            fp.write(document)
            fp.close()
            dtn_logger.logger_info("CONVERT", "%s => %s"  % (path, outfile))

            if self._verbose > 0 :
                self.outout_result.write(path + " => OK \n")
                if self._verbose > 1 :
                    print("%d write text to %s "  % (self._total, outfile));
        else :
            dtn_logger.logger_error("CONVERT", "%s => %s"  % (path, outfile))
            self._error += 1
            if self._verbose > 0 :
                self.outout_result.write(path + " => ERROR\n")
                if self._verbose > 1 :
                    print("%d. convert error : %s " % (self._error, path));


    def file_to_text(self, filename, ofile):
        """
        filename : input file
        
        ofile : output text file
        
        """
             
        f = File(filename, output=self._tmpfilepath, verbose=self._verbose)
        self._ftypes[f.get_file_type()] += 1
        if os.path.exists(ofile) :
            if self._verbose > 1 :
                print("find file : "+ ofile)
        else :
            if filename.lower().endswith(".txt") :
                shutil.copyfile(filename, ofile)
            else :
                document = f.convert()
                if document == False :
                    self._total -= 1
                else :
                    self.write_text_file(filename, ofile, document, f)
                        
                        
    def files_to_text(self, fpath, ofile):
        """
        fpath : input file or directory
        
        ofile : output text file or directory
        
        """

        if not os.path.exists(ofile) :
            os.mkdir(ofile)
            
        for name in os.listdir(fpath):
            if variables.noloaddir(name) :
                continue
            path = os.path.join(fpath, name)
            o_file = os.path.join(ofile, name)
            if os.path.isdir(path):
                self.files_to_text(path, o_file)
            else :
                self._total += 1
                if path.lower().endswith(".txt") == False :
                    o_file += ".txt"
                    
                self.file_to_text(path, o_file)
                

    def test_all_files(self, fpath):
          
        for name in os.listdir(fpath):
            path = os.path.join(fpath, name)
            if os.path.isdir(path):
                self.test_all_files(path)
            elif name.endswith('.txt') :
                f = File(path, output=None, verbose=self._verbose)
                f.test_bad_file()
    
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
                print("back to text file %s" % (textfile))
                shutil.move(path, textfile)

    def change_root_bad_files(self, infile, fpath):
        
        if fpath == None :
            fpath = os.path.join(infile, variables.OUTPUT_DIR)
        for name in os.listdir(fpath):
            path = os.path.join(fpath, name)           
            if os.path.isdir(path) and name != variables.DATA_DIR and name != variables.TEMP_DIR :
                self.change_bad_files(path)


def ocr_image(image):
    #import urllib2
    import time
    import urllib
    import json
    import hashlib
    import base64
    
    
    f = open(image, 'rb')
    file_content = f.read()
    base64_image = base64.b64encode(file_content)
    #body = urllib.urlencode({'image': base64_image})
    body = urllib.parse.urlencode({'image': base64_image})
    
    url = 'http://webapi.xfyun.cn/v1/service/v1/ocr/idcard'
    api_key = 'API_KEY'
    param = {"engine_type": "idcard", "head_portrait": "0"}

    x_appid = 'APPID'
    toto = json.dumps(param).replace(' ', '')
    print (toto)
    x_param = base64.b64encode(toto)
    x_param = base64.b64encode(json.dumps(param).replace(' ', ''))
    x_time = int(int(round(time.time() * 1000)) / 1000)
    x_checksum = hashlib.md5(api_key + str(x_time) + x_param).hexdigest()
    x_header = {'X-Appid': x_appid,
                'X-CurTime': x_time,
                'X-Param': x_param,
                'X-CheckSum': x_checksum}
    req = urllib.request(url, body, x_header)
    result = urllib.request.urlopen(req)
    #req = urllib2.Request(url, body, x_header)
    #result = urllib.urlopen(req)
    result = result.read()
    print (result)

    

if __name__ == "__main__":
    
    verbose = 2

    fpath = "D:/DocutoneSoftware/SmartDoc/home/data/Documents/doc/北京星火科技开发服务公司"
    
    o_file = "D:/DocutoneSoftware/SmartDoc/home/data/Documents/TEXT"
    
    '''
    conv = Convert(verbose=verbose)
    o_file = conv.open_output(fpath, o_file)
    conv.files_to_text(fpath, o_file)    
    conv.close_output()
    '''
    
    fname = 'D:/TestUnit/OCRNuance/vpfapi/opWD/test/vpfapi/printer/IMP3.jpg'
    ocr_image(fname)
    
    print ("==== end ====")





