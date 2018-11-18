# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import sys, os
import codecs

#import CRFPP  

sys.path.append("../")

from tempfile import NamedTemporaryFile, mkstemp

from docutone import config
from docutone.utils import variables
from docutone.utils import crf_utils
from docutone.logging import dtn_logging as dtn_logger
from docutone.core.crf_tagging import CRFTagging

class CRF(object):
    
    
    def __init__(self):
        """
        """
        self.tagging = CRFTagging(is_test=False)
    
    
    
    def _train(self, trainf, model, threads=8, cost=16.0):
        '''
        -a CRF-L2 or CRF-L1 默认是CRF-L2, 一般来说L2算法效果要比L1算法稍微好一点，虽然L1算法中非零特征的数值要比L2中大幅度的小。
        -c float 这个参数设置CRF的hyper-parameter。c的数值越大，CRF拟合训练数据的程度越高。
        -f NUM 这个参数设置特征的cut-off threshold。CRF++使用训练数据中至少NUM次出现的特征。默认值为1。
        -p NUM 多个CPU，那么那么可以通过多线程提升训练速度。NUM是线程数量。
        '''
        # run CRF++
        #os.system(self.crf_learn + " -t -p %d -c %f %s %s %s" % (threads, cost, self.templatef, trainf, model))
        templatef = crf_utils.get_crf_template_file()
        
        commd = crf_utils.CRF_LEARN + " -p %d -c %f %s %s %s" % (threads, cost, templatef, trainf, model)
        dtn_logger.logger_info("CRF Training", commd)
        
        #os.system(crf_utils.CRF_LEARN + " -p %d -c %f %s %s %s" % (threads, cost, templatef, trainf, model))
        os.system(commd)
            
    
    def folder_tagging(self, path, categorie, output_data) :
        
        self.tagging.set_categorie(categorie)
        
        for fname in sorted(os.listdir(path)):
            fpath = os.path.join(path, fname)
            
            if os.path.isdir(fpath):
                if variables.noloaddir(fpath)  :
                    continue
                self.folder_tagging(fpath, categorie, output_data)
            else :
                self.tagging.tagging(fpath, output_data)   
    
    ''' training a type of document '''
    def create_categorie_tagging(self, fpath, categorie) :
        
        dataname = crf_utils.add_crf_model_name(categorie)
            
        dtn_logger.logger_info("CRF Training", "%s => %s" %(categorie, dataname))
    
        out_path = crf_utils.get_crf_training_directory()
                    
        output_file = os.path.join(out_path, dataname+crf_utils.CRF_FILE_TAG_EXT)
        
        output_data = codecs.open(output_file, 'w', 'utf-8')
        
        self.folder_tagging(fpath, categorie, output_data)
        
        output_data.close()
        
        model = os.path.join(out_path, dataname+crf_utils.CRF_MODEL_EXT)
        
        self._train(output_file, model)
    

    ''' test if folder contains only text file '''
    def _is_categorie_folder(self, path) :
            
        for fname in sorted(os.listdir(path)):
            fpath = os.path.join(path, fname)
            if os.path.isdir(fpath) and not variables.noloaddir(fpath)  :
                return False
        return True
    
    ''' trainig subset document '''
    def create_subset_model(self, path, categorie) :
        
        if self._is_categorie_folder(path) :
            self.create_categorie_tagging(path, categorie)
        else :
            for fname in sorted(os.listdir(path)):
                fpath = os.path.join(path, fname)
                if os.path.isdir(fpath):
                    if variables.noloaddir(fpath) :
                        continue
                    else :
                        self.create_categorie_tagging(fpath, fname)
 
            
    
    ''' training all type of document '''
    def create_crf_model(self, path=None, subset=True):
        if path == None :
            path = config.TEMPLATE_DIR + "/TEXT"
        for fname in sorted(os.listdir(path)):
            fpath = os.path.join(path, fname)
            if variables.noloaddir(fpath) :
                continue

            if os.path.isdir(fpath):
                if subset :
                    self.create_subset_model(fpath, fname)
                else :
                    self.create_categorie_tagging(fpath, fname)



    ''' following function is not used '''

    def make_template(self):
        templatef = NamedTemporaryFile()
        for idx, f in enumerate(self.features):
            print >>templatef, "U%d:%%x[0,%d]" % (idx, idx)

        for idx, t in enumerate(self.template):
            # templates are (func, pos_idx)
            # composite templates: [(f1, p1), (f2, p2), ...]
            try:
                t[0][0]
            except TypeError:
                t = (t,)
            print >>templatef, "Ut%d:" % idx + \
                  "/".join(["%%x[%d,%d]" % (pi, self.features.index(func))
                                for func,pi in t])
        templatef.flush()
        return templatef             

        
    def token_accuracy(self, evaled_seqs):
        """evaled_seqs should be like output from evaluate(): a list of
        sequences, where each sequence is
        [(token1, label1, goldlabel1), (token2, label2, goldlabel2), ...]"""
        total = 0
        right = 0
        for sequence in evaled_seqs:
            for inputtoken, outputlabel, goldlabel in sequence:
                if outputlabel == goldlabel:
                    right += 1
                total += 1
        return right / total


    def frange(self, start, end=None, inc=None):
        "A range function, that does accept float increments..."
        if end == None:
            end = start + 0.0
            start = 0.0
        if inc == None:
            inc = 1.0
        L = []
        while 1:
            next = start + len(L) * inc
            if inc > 0 and next >= end:
                break
            elif inc < 0 and next <= end:
                break
            L.append(next)
        return L

    def tune_cost_parameter(self, features, template, accuracyfunc,  trainset, devset,  mincost, maxcost, step):
        models = {} # cost values to CRF objects
        '''
        for cost in frange(mincost, maxcost+step, step):
            print ("training with cost", cost, len(trainset))
            c = CRF(mkstemp(prefix='crf-', suffix="-%s" % cost)[1],  features, template, cost)
            c.train(trainset)
            score = accuracyfunc(c.evaluate(devset))
            print (cost, score)
            models[cost] = c, score
        return models
        '''
        
    def training_labor(self):
        root = config.TEMPLATE_DIR + "/TEXT/"
        fpath = root + "劳动合同" 
        ftype = "劳动合同"
        crf.create_categorie_tagging(fpath, ftype)
        
    def training_transfer(self):
        root = config.TEMPLATE_DIR + "/TEXT/"
        fpath = root + "转让协议" 
        ftype = "转让协议"
        crf.create_categorie_tagging(fpath, ftype)
        

    
if __name__ == '__main__':

    crf = CRF()
    
    #crf.create_crf_model()

    #crf.training_labor()
    
    crf.training_transfer()


    print("---- END ----")
    
  






