
from __future__ import unicode_literals
import sys

import numpy as np

sys.path.append("../")

np.random.seed(1337)



from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.utils.np_utils import to_categorical


from docutone.utils import model as md
from docutone.utils import docutonelocate
from docutone.core import clause_training
from docutone.core import document as doc
from docutone.core.document import LawDocument
from docutone.logging import dtn_logging as dtn_logger
from docutone import config


class ClauseVerifying(object):
    

    def __init__(self, modelname=None):
        
        self._document = LawDocument()   
        self.clause_model = clause_training.ClauseTraining()
        self.clause_model.load_model_label()

        pass
        
  


    def load_predict_document(self, filename) :
        if (filename.endswith(".txt")) :
            ofile = filename
        else :
            ofile = docutonelocate.convert_file(filename)
        self._document.read_section(ofile)
        
  
        texts = []
        if len(self._document.sections) > 0 :
            for section in self._document.sections :
                ss = []
                if section.title :
                    pass
                if len(section.sentences) > 0 :
                    ss = [p[0] for p in section.sentences]
                    if len(ss) > 0:
                        texts.append(doc.sentencesTowords(ss))
                
        else :
            for s in self._document.document_header:
                texts.append(doc.sentencesTowords([s]))
                
        return texts
    
    def predict(self, filename) :

        
        texts = self.load_predict_document(filename)
        
        tokenizer = Tokenizer(num_words=self.clause_model.MAX_NB_WORDS)
        tokenizer.fit_on_texts(texts)
        sequences = tokenizer.texts_to_sequences(texts)

        # create data
        data = pad_sequences(sequences, maxlen=self.clause_model.MAX_SEQUENCE_LENGTH)

        dtn_logger.logger_info("PREDICT", "Verification document : " + filename)
        dtn_logger.logger_info("PREDICT", "Predict Data : " + str(data.shape))


        model = md.load_json_model(self.clause_model.MODEL_NAME)
        #model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=['accuracy'])
        model.compile(loss='binary_crossentropy', optimizer=md.OPTIMIZER_ADAM, metrics=['accuracy'])

        for i, s in enumerate(data) :
            s = data[np.array([i])]
            preds = model.predict(s)
            


            n = self.sample(preds[0])
            print("*** " + self.clause_model.label_name[n] + "***")
            n = self.sample(preds[0], 0.8)
            print("*** " + self.clause_model.label_name[n] + "***")
            n = self.sample(preds[0], 0.2)
            print("*** " + self.clause_model.label_name[n] + "***")
                
           
            print(texts[i])
            if i > 5 :
                break

            
    def sample(self, p, temperature=1.0) :
        # helper function to sample an index from a probability array
        preds = np.asarray(p).astype('float64')
        preds = np.asarray(preds).astype('float64')
        preds = np.log(preds) / temperature
        exp_preds = np.exp(preds)
        preds = exp_preds / np.sum(exp_preds)
        probas = np.random.multinomial(1, preds, 1)
        
        mmm = np.argmax(probas)
        print(mmm)
        return mmm

    
if __name__ == '__main__':
    
    filename = config.TEST_PATH + "/章程/A股国投新集能源股份有限公司章程.txt"
    ftype = "有限责任公司章程"
    verifying = ClauseVerifying()
    verifying.predict(filename)
    

    print("----end-----")
   
