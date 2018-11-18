
from __future__ import unicode_literals
import sys,os
import codecs
import numpy as np

sys.path.append("../")

np.random.seed(1337)


from keras.layers import Dense, Input, Flatten, Dropout, Activation, LSTM
from keras.models import Model

from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.utils.np_utils import to_categorical
from keras.layers import Conv1D, MaxPooling1D, Embedding




from docutone.core.document import LawDocument
from docutone.core.text4words import Text4Words
from docutone.utils import model as md
from docutone.utils import docutonelocate

from docutone.core.clause import Clause

from docutone.logging import dtn_logging as dtn_logger
from docutone import config

from keras.models import Sequential
from keras import layers


RNN = layers.LSTM
HIDDEN_SIZE = 128


class ClauseTraining(object):
    

    def __init__(self, modelname=None):
        
        self.MAX_SEQUENCE_LENGTH = 1000
        self.MAX_NB_WORDS = 20000
        self.EMBEDDING_DIM = 100
        self.VALIDATION_SPLIT = 0.25
        self.EPOCHS = 64
        self.BATCH_SIZE = 32
        self.POOL_SIZE = 5
        self.FILTERS = 64
        self.LSTM_OUTPUT_SIZE = 70
        
        if modelname == None :
            self.MODEL_NAME = "clause_model"
        else :
            self.MODEL_NAME = modelname
        
        self._document = LawDocument()   
        self._clause = Clause()   
        
        self.texts = []          # list of text samples
        self.labels_index = {}   # dictionary mapping label name to numeric id
        self.labels = []         # list of label ids
        self.label_name = []
        self._debug  = 1
        self._save_model = False

            
    def create_embedding_words(self, path, created=True) :
        
        fname = md.get_model_embedded_file(self.MODEL_NAME)
        tw = Text4Words()
        if created :
            dtn_logger.logger_info("TRAINING", "Create Embedded Words " + fname)
            tw.load_directory(path)
            tw.train_word_vector_embedding(vectfname=fname)
        else :
            tw.load_word_vector_embedding(vectfname=fname)
     
    def load_embedding_words(self) :
        
        embeddings_index = {}
        fname = md.get_model_embedded_file(self.MODEL_NAME)           
        dtn_logger.logger_info("TRAINING", "Load Embedded Words " + fname)
        f = codecs.open(os.path.join(fname), 'r', 'utf-8')
        for line in f:
            values = line.split()
            if len(values) > 2 :
                word = values[0]
                coefs = np.asarray(values[1:], dtype='float32')
                embeddings_index[word] = coefs
        f.close()
    
        return embeddings_index
        
    
    def _load_document_clauses(self, filename, label) :
    
        if (filename.endswith(".txt")) :
            ofile = filename
        else :
            ofile = docutonelocate.convert_file(filename)
            
        self._clause.create_clauses(ofile)
    
        if len(self._clause.sections) > 0 :
            for section in self._clause.sections:
                name = label + ":" +section.title
                name = section.title
                if name in self.labels_index.keys() :
                    label_id = self.labels_index[name]
                else :
                    label_id = len(self.labels_index)
                    self.labels_index[name] = label_id
                
                self.label_name.append(name)
                self.labels.append(label_id)
                words = section.toWords()
                self.texts.append(words)
            
            
    
    def _load_directory(self, path, label) :
        for fname in sorted(os.listdir(path)):
            fpath = os.path.join(path, fname)
            if os.path.isdir(fpath):
                self._load_directory(fpath, label)
            else :
                self._load_document_clauses(fpath, label)
                
                    
                
    def load_clauses(self, path) :

        self.texts = []          # list of text samples
        self.labels_index = {}   # dictionary mapping label name to numeric id
        self.labels = []         # list of label ids
        self.label_name = []


        for fname in os.listdir(path):
            fpath = os.path.join(path, fname)
            if os.path.isdir(fpath):
                self._load_directory(fpath, fname)
         
        # tokenizer
        tokenizer = Tokenizer(num_words=self.MAX_NB_WORDS)
        tokenizer.fit_on_texts(self.texts)
        self.sequences = tokenizer.texts_to_sequences(self.texts)
        self.word_index = tokenizer.word_index
    
    
    # term name [termname=termid]
    def load_model_label(self) :
        self.labels = []
        self.label_name = []
        self.label_index = {}
        
        fname =  md.get_model_label_file(self.MODEL_NAME+"_label")
        f = codecs.open(fname, 'r', 'utf-8')
        for line in f :
            line = line.strip()
            if len(line) > 0 :
                k, v = line.split('=', 1)
                self.labels.append(v)
                self.label_name.append(k)
                self.label_index[k] = v
        f.close()

    def save_model_label(self) :
        fname = md.get_model_label_file(self.MODEL_NAME+"_label")
        f = codecs.open(fname, 'w', 'utf-8')
        for index in range(len (self.labels)):
            k = self.label_name[index]
            v = self.labels[index]
            f.write("%s=%d\n" % (k, v))
        f.close()
    
    # term list 
    def _create_training_data(self) :
    
        labels = to_categorical(np.asarray(self.labels))
               
        # create data
        data = pad_sequences(self.sequences, maxlen=self.MAX_SEQUENCE_LENGTH)
        dtn_logger.logger_info("TRAINING", "loading data " + str(data.shape))
        indices = np.arange(data.shape[0])
        np.random.shuffle(indices)
        data = data[indices]
        labels = labels[indices]
        nb_validation_samples = int(self.VALIDATION_SPLIT * data.shape[0])
        
        # training size and values 
        x_train = data[:-nb_validation_samples]
        y_train = labels[:-nb_validation_samples]
        x_val = data[-nb_validation_samples:]
        y_val = labels[-nb_validation_samples:]
        
        return x_train, y_train, x_val, y_val
    
    
    def preparing_matrix(self) :
    
        # prepare embedding matrix
        nb_words = min(self.MAX_NB_WORDS, len(self.word_index)) + 1
        embedding_matrix = np.zeros((nb_words, self.EMBEDDING_DIM))
        for word, i in self.word_index.items():
            if i > self.MAX_NB_WORDS:
                continue
            embedding_vector = self.embeddings_index.get(word)
            if embedding_vector is not None:
                # words not found in embedding index will be all-zeros.
                embedding_matrix[i] = embedding_vector
    
        # load pre-trained word embeddings into an Embedding layer
        # note that we set trainable = False so as to keep the embeddings fixed
        embedding_layer = Embedding(nb_words, self.EMBEDDING_DIM,
                                weights=[embedding_matrix],
                                input_length=self.MAX_SEQUENCE_LENGTH, trainable=False)
    
        return embedding_layer
    
    
        
        
    def create_LSTM(self, x_train, y_train, x_val, y_val):
        
        model = Sequential()
        
        model.add(RNN(HIDDEN_SIZE, input_shape=(self.MAX_SEQUENCE_LENGTH, len(self.labels_index))))
        
        model.add(layers.RepeatVector(len(self.labels_index)))


        for _ in range(5):
            model.add(RNN(HIDDEN_SIZE, return_sequences=True))
    
        model.add(layers.TimeDistributed(layers.Dense(128)))
        model.add(layers.Activation('softmax'))
        #model.compile(loss='categorical_crossentropy',  optimizer='adam', metrics=['accuracy'])
        model.compile(loss='categorical_crossentropy', optimizer=md.OPTIMIZER_PROP, metrics=['acc'])
 
        model.fit(x_train, y_train, validation_data=(x_val, y_val), epochs=self.EPOCHS, batch_size=self.BATCH_SIZE)

 
 
    def create_model(self, x_train, y_train, x_val, y_val) :
        
        nb_words = min(self.MAX_NB_WORDS, len(self.word_index)) + 1

        model = Sequential()
        model.add(Embedding(nb_words, self.EMBEDDING_DIM, input_length=self.MAX_SEQUENCE_LENGTH))
        model.add(Dropout(0.25))
        model.add(Conv1D(self.FILTERS, self.POOL_SIZE, padding='valid', activation='relu', strides=1))
        model.add(MaxPooling1D(pool_size=self.POOL_SIZE))
        model.add(LSTM(self.LSTM_OUTPUT_SIZE))
        model.add(Dense(len(self.labels_index)))
        model.add(Activation('sigmoid'))

        model.compile(loss='binary_crossentropy', optimizer=md.OPTIMIZER_ADAM, metrics=['accuracy'])

        model.fit(x_train, y_train, batch_size=self.BATCH_SIZE, epochs=15, validation_data=(x_val, y_val))
        score, acc = model.evaluate(x_val, y_val, batch_size=self.BATCH_SIZE)
        print('Test score:', score)
        print('Test accuracy:', acc)
 
 
 
    def create_model1(self, x_train, y_train, x_val, y_val) :
        
        
        nb_words = min(self.MAX_NB_WORDS, len(self.word_index)) + 1
        
        model = Sequential()
        model.add(Embedding(nb_words, self.EMBEDDING_DIM))
        model.add(RNN(128, dropout=0.2, recurrent_dropout=0.2))
        model.add(Dense(len(self.labels_index), activation='sigmoid'))

        # try using different optimizers and different optimizer configs
        model.compile(loss='binary_crossentropy', optimizer=md.OPTIMIZER_ADAM, metrics=['accuracy'])

        model.fit(x_train, y_train, batch_size=self.BATCH_SIZE, epochs=15, validation_data=(x_val, y_val))
        if self._save_model :
            md.save_json_model(model, self.MODEL_NAME)
            #md.save_yaml_model(model, "clause_model")
            self.save_model_label()

 
    def create_model2(self, x_train, y_train, x_val, y_val) :
                
        # create embedding layer 
        embedding_layer = self.preparing_matrix()
    
    
        # train a 1D convnet with global maxpooling
        sequence_input = Input(shape=(self.MAX_SEQUENCE_LENGTH,), dtype='int32', name='main_input')
        embedded_sequences = embedding_layer(sequence_input)
        

        x = Conv1D(128, 5, activation='relu')(embedded_sequences)
        x = MaxPooling1D(5)(x)
        
        x = Conv1D(128, 5, activation='relu')(x)
        x = MaxPooling1D(5)(x)

        x = Conv1D(128, 5, activation='relu')(x)
        x = MaxPooling1D(35)(x)
        x = Flatten()(x)
        
        x = Dense(128, activation='relu')(x)
        preds = Dense(len(self.labels_index), activation='softmax')(x)
    
        model = Model(sequence_input, preds)
        model.compile(loss='categorical_crossentropy', optimizer=md.OPTIMIZER_PROP, metrics=['acc'])
    
        
        model.fit(x_train, y_train, validation_data=(x_val, y_val), epochs=self.EPOCHS, batch_size=self.BATCH_SIZE)

        if self._save_model :
            md.save_json_model(model, self.MODEL_NAME)
            #md.save_yaml_model(model, "clause_model")
            self.save_model_label()

        
 
    def training(self, path=None, modelname=None) :
        if modelname :
            self.MODEL_NAME = modelname
        
        if path == None :
            path = config.TEMPLATE_DIR + "/TEXT"
        # create embedded words 
        self.create_embedding_words(path, False)
        
        # load embedded words 
        self.embeddings_index = self.load_embedding_words()

        # load text samples and their labels
        self.load_clauses(path)
        
        # create data into a training set and a validation set
        x_train, y_train, x_val, y_val = self._create_training_data()   
        
        
        # create model
        self.create_model(x_train, y_train, x_val, y_val)


    
if __name__ == '__main__':
    
    clause = ClauseTraining()    
    clause.training()

    print("----end-----")
   
