# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import sys

from sklearn import svm
from sklearn import metrics
from sklearn import preprocessing
from sklearn import cross_validation
import pickle

sys.path.append("../")

from docutone.core.datasets import Datasets
from docutone.utils import variables
from docutone.logging import dtn_logging as dtn_logger

'''
文件条款和文件分类训练
'''
    
class Training(object):
    '''
    
    '''
    def __init__(self):
        
        self.datasets = Datasets()
     
        pass
    
    '''
    svc line mode 
    '''
    
    def training_svc_line(self, text_path) :
        
        
        dataSet = self.datasets.load_docvect(text_path)
    
        labelSet = self.datasets.load_labelset(text_path)
        target_names = self.datasets.load_doclabel(text_path)
    
        lin_svc = svm.LinearSVC(C=1.0)
    
        for epoch in range(1):
    
    
            X_train, X_test, y_train, y_test = cross_validation.train_test_split(dataSet, labelSet, test_size=0.2, random_state=0)
    
            min_max_scaler = preprocessing.MinMaxScaler(feature_range=(-1, 1))
            X_train = min_max_scaler.fit_transform(X_train)
            X_test = min_max_scaler.fit_transform(X_test)
    
            lin_svc.fit(X_train, y_train)
            predicted = lin_svc.predict(X_test)
            #report = classification_report(y_test, predicted, target_names=target_names, digits=5)
            report = metrics.classification_report(y_test, predicted, target_names=target_names)
            print("Classification report for classifier %s:\n%s\n" % (lin_svc, report))
           
        print("Confusion matrix:\n%s" % metrics.confusion_matrix(y_test, predicted))
        
    
    '''
    svc training mode 
    '''
           
    def training_svc(self, size=0.30, state=0) :
        
        
        dataSet = self.datasets.load_docvect()
        labelSet = self.datasets.load_labelset()
        
        target_names = self.datasets.load_doclabel()

        C = 1.0  # SVM regularization parameter
        svc = svm.SVC(kernel='linear', C=C)
    
  
        X_train, X_test, y_train, y_test = cross_validation.train_test_split(dataSet, labelSet, test_size=size, random_state=state) # 7
    
        min_max_scaler = preprocessing.MinMaxScaler(feature_range=(-1, 1))
        X_train = min_max_scaler.fit_transform(X_train)
        X_test = min_max_scaler.fit_transform(X_test)
    
        svc.fit(X_train, y_train)
        
        predicted = svc.predict(X_test)
        #report = classification_report(y_test, predicted, target_names=target_names, digits=5)
        report = metrics.classification_report(y_test, predicted, target_names=target_names, digits=5)
        dtn_logger.logger_info("DATASET Training", "Classification report for classifier %s:\n%s\n" % (svc, report))
        print("Classification report for classifier %s:\n%s\n" % (svc, report))
            
        print("Confusion matrix:\n%s" % metrics.confusion_matrix(y_test, predicted))
        dtn_logger.logger_info("DATASET Training", "Confusion matrix:\n%s" % metrics.confusion_matrix(y_test, predicted))
    
        # save the model to disk
        filename = self.datasets.get_svc_file_name()
        pickle.dump(svc, open(filename, 'wb'))
        
    
    
    def save_model(self, size=0.30, state=0) :
        from sklearn.externals import joblib
        # save the model to disk
        filename = 'finalized_model.sav'
        '''joblib.dump(model, filename)'''
 
        # some time later...
 
        # load the model from disk
        loaded_model = joblib.load(filename)
        '''result = loaded_model.score(X_test, Y_test)
        print(result) '''
    
    def load_svc_model(self, size=0.30, state=0) :
        
        filename = self.datasets.get_svc_file_name()
        
        dataSet = self.datasets.load_docvect()
        labelSet = self.datasets.load_labelset()
        X_train, X_test, y_train, y_test = cross_validation.train_test_split(dataSet, labelSet, test_size=size, random_state=state) # 7

        svc = pickle.load(open(filename, 'rb'))
        result = svc.score(X_test, y_test)

        target_names = self.datasets.load_doclabel()
        predicted = svc.predict(X_test)
        #report = classification_report(y_test, predicted, target_names=target_names, digits=5)
        report = metrics.classification_report(y_test, predicted, target_names=target_names, digits=5)
        print("Classification report for classifier %s:\n%s\n" % (svc, report))


 
    def create_datasets(self, text_path) :
        
        self.datasets.create_dataset(text_path)


         
if __name__ == "__main__":
    
    fpath = variables.CORPUS_DIR + "/TEXT"
    
    print(fpath)
    
    training = Training()
    #training.create_datasets(fpath)
    training.training_svc(size=0.3)
    training.load_svc_model(size=0.3)
    

    print("===== end ==== ")

     
    
    