
from __future__ import unicode_literals
import sys,os
import codecs
import numpy as np
#import pandas
#import matplotlib.pyplot as plt
import itertools
import math

np.random.seed(1337)

from keras.models import Sequential
from keras.layers import Dense

from keras.layers import Dense, Dropout, Input, Flatten, Activation
from keras.models import Model, model_from_json

from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.utils.np_utils import to_categorical
from keras.layers import Conv1D, MaxPooling1D, Embedding, GlobalMaxPooling1D
from keras.callbacks import EarlyStopping
from keras.layers.recurrent  import SimpleRNN, GRU, LSTM
from keras.layers.convolutional import Convolution1D


sys.path.append("../")

from docutone.core.document import LawDocument

from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder


from docutone.utils import variables

from docutone.utils import model as md

class EnbedTraining(object):
    

    def __init__(self, filename = None):
        
        self.MAX_SEQUENCE_LENGTH = 1000
        self.MAX_NB_WORDS = 20000
        self.EMBEDDING_DIM = 100
        self.VALIDATION_SPLIT = 0.25
        
        self.embeddings_index = self.load_embedding_base()
        
        self._document = LawDocument()   
        
        self.label_name = []
        self.texts = []          # list of text samples
        self.labels_index = {}   # dictionary mapping label name to numeric id
        self.labels = []         # list of label ids
        self._debug  = 1

        pass
        
        
            
    def load_embedding_base(self) :
        
        embeddings_index = {}
        
        f = codecs.open(os.path.join(variables.BASE_DIR, 'data/document_classification.txt'), 'r', 'utf-8')
        for line in f:
            values = line.split()
            if len(values) > 2 :
                word = values[0]
                coefs = np.asarray(values[1:], dtype='float32')
                embeddings_index[word] = coefs
        f.close()
    
        return embeddings_index
        
    
    
    
    def _load_directory(self, path, label, label_id) :
              
        for fname in sorted(os.listdir(path)):
            fpath = os.path.join(path, fname)
            if os.path.isdir(fpath):
                self._load_directory(fpath, label, label_id)
            elif fname.endswith(".txt"):
                words = self._document.get_normalize_document(fpath, outtype=0)
                if len(words) > 0 :
                    self.texts.append(words)
                    self.classifiers.append(label)
                    self.labels.append(label_id)
                    self.file_label.append(fname)
                    
                
         

    def load_data(self, path) :

        self.label_name = []
        self.texts = []          # list of text samples
        self.labels_index = {}   # dictionary mapping label name to numeric id
        self.labels = []         # list of label ids
        self.classifiers = []
        self.file_label = []
        for fname in os.listdir(path):
            fpath = os.path.join(path, fname)
            if os.path.isdir(fpath):
                label_id = len(self.labels_index)
                self.labels_index[fname] = label_id
                self._load_directory(fpath, fname, label_id)
         
        # tokenizer
        tokenizer = Tokenizer(num_words=self.MAX_NB_WORDS)
        tokenizer.fit_on_texts(self.texts)
        self.sequences = tokenizer.texts_to_sequences(self.texts)
        self.word_index = tokenizer.word_index

    def create_traning_data(self) :
    
        labels = to_categorical(np.asarray(self.labels))
        
        # create data
        data = pad_sequences(self.sequences, maxlen=self.MAX_SEQUENCE_LENGTH)
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
        nb_words = min(self.MAX_NB_WORDS, len(self.word_index))
        embedding_matrix = np.zeros((nb_words + 1, self.EMBEDDING_DIM))
        for word, i in self.word_index.items():
            if i > self.MAX_NB_WORDS:
                continue
            embedding_vector = self.embeddings_index.get(word)
            if embedding_vector is not None:
                # words not found in embedding index will be all-zeros.
                embedding_matrix[i] = embedding_vector
    
        # load pre-trained word embeddings into an Embedding layer
        # note that we set trainable = False so as to keep the embeddings fixed
        embedding_layer = Embedding(nb_words + 1,
                                self.EMBEDDING_DIM,
                                weights=[embedding_matrix],
                                input_length=self.MAX_SEQUENCE_LENGTH,
                                trainable=False)
    
        return embedding_layer
    

    def LSTMTraining(self, x_train, y_train, x_val, y_val) :
        
        model = Sequential()
        
        # 词向量嵌入层，输入：词典大小，词向量大小，文本长度
        model.add(Embedding(self.MAX_SEQUENCE_LENGTH, 100, input_length=self.MAX_NB_WORDS)) 
        #model.add(Dropout(0.25))
 
        model.add(LSTM(100)) 
        #model.add(Flatten())

        model.add(Convolution1D(128, 5, border_mode="valid", activation="relu"))


        
        # 全连接层
        model.add(Dense(128))
        model.add(Dropout(0.25))
        model.add(Activation('relu'))
        model.add(Dense(128))
        model.add(Activation('softmax'))
        model.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=['acc'], verbose=1)
        
        
        result = model.fit(x_train, y_train, validation_data=(x_val, y_val), nb_epoch=2, batch_size=128, verbose=1)

       
    def test (self):
        
        # input: meant to receive sequences of 100 integers, between 1 and 10000.

        main_input = Input(shape=(100,), dtype='int32', name='main_input')

        # this embedding layer will encode the input sequence
        # into a sequence of dense 512-dimensional vectors.
        x = Embedding(output_dim=512, input_dim=10000, input_length=100)(main_input)

        # LSTM will transform the vector sequence into a single vector,
        # containing information about the entire sequence
        lstm_out = LSTM(32)(x)
        
        #insert the auxiliary loss, allowing the LSTM and Embedding layer to be trained 
        #smoothly even though the main loss will be much higher in the model.
        auxiliary_output = Dense(1, activation='sigmoid', name='aux_output')(lstm_out)
        
        #we feed into the model our auxiliary input data by concatenating it with the LSTM output:

        auxiliary_input = Input(shape=(5,), name='aux_input')
        #x = merge([lstm_out, auxiliary_input], mode='concat')

        # we stack a deep fully-connected network on top
        x = Dense(64, activation='relu')(x)
        x = Dense(64, activation='relu')(x)
        x = Dense(64, activation='relu')(x)

        # and finally we add the main logistic regression layer
        main_output = Dense(1, activation='sigmoid', name='main_output')(x)

        #This defines a model with two inputs and two outputs:
        model = Model(input=[main_input, auxiliary_input], output=[main_output, auxiliary_output])

        model.compile(optimizer='rmsprop', loss='binary_crossentropy', loss_weights=[1., 0.2])

        #We can train the model by passing it lists of input arrays and target arrays:
        
        '''
        model.fit([headline_data, additional_data], [labels, labels], nb_epoch=50, batch_size=32)


        model.compile(optimizer='rmsprop',
              loss={'main_output': 'binary_crossentropy', 'aux_output': 'binary_crossentropy'},
              loss_weights={'main_output': 1., 'aux_output': 0.2})

        # and trained it via:
        model.fit({'main_input': headline_data, 'aux_input': additional_data},
            {'main_output': labels, 'aux_output': labels},
            nb_epoch=50, batch_size=32)

        '''

    
    def clause_training(self, path) :
        #from keras.utils.vis_utils import plot_model

        # 1, loading text samples and their labels
        self.load_data(path)
        
        # 2. create data into a training set and a validation set
        x_train, y_train, x_val, y_val = self.create_traning_data()   
        
        
        # 4. create embedding layer 
        embedding_layer = self.preparing_matrix()
    
    
        # 5. train a 1D convnet with global maxpooling
        sequence_input = Input(shape=(self.MAX_SEQUENCE_LENGTH,), dtype='int32', name='main_input')
        embedded_sequences = embedding_layer(sequence_input)
        
        #lstm_out = LSTM(32)(embedded_sequences)
        #x = MaxPooling1D(5)(lstm_out)

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
        model.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=['acc'])
    

        #plot_model(model, to_file='model_plot.png', show_shapes=True, show_layer_names=True)
    
        '''
        history = model.fit(x_train, y_train, validation_data=(x_val, y_val), nb_epoch=2, batch_size=128)
        
        # Estimate model performance
        #trainScore = model.evaluate(x_train, y_train, verbose=0)
        #print('Train Score: %.2f MSE (%.2f RMSE)' % (trainScore, math.sqrt(trainScore)))
        #testScore = model.evaluate(x_val, y_val, verbose=0)
        #print('Test Score: %.2f MSE (%.2f RMSE)' % (testScore, math.sqrt(testScore)))

        # generate predictions for training
        
        trainPredict = model.predict(x_train)
        testPredict = model.predict(x_val)
        '''
        

        md.save_json_model(model, "clause_model")
        #md.save_yaml_model(model, "embedded_model")
        return model
        
    def loading(self):
        from keras.datasets import imdb
        from keras.preprocessing import sequence
        max_features = 5000
        maxlen = 400
        
        (x_train, y_train), (x_test, y_test) = imdb.load_data(num_words=max_features)
        if self._debug :
            print(len(x_train), 'train sequences')
            print(len(x_test), 'test sequences')

            print('Pad sequences (samples x time)')
        x_train = sequence.pad_sequences(x_train, maxlen=maxlen)
        x_test = sequence.pad_sequences(x_test, maxlen=maxlen)
        
        if self._debug :
            print('x_train shape:', x_train.shape)
            print('x_test shape:', x_test.shape)

        return x_train, y_train, x_test, y_test
    
    
    
    def training_model(self):
        max_features = 5000
        maxlen = 400
        batch_size = 32
        embedding_dims = 50
        filters = 250
        kernel_size = 3
        hidden_dims = 250
        epochs = 2
        

        model = Sequential()
        
        '''we start off with an efficient embedding layer which maps our vocab indices into embedding_dims dimensions'''
        model.add(Embedding(max_features, embedding_dims, input_length=maxlen))
        model.add(Dropout(0.2))

        '''we add a Convolution1D, which will learn filters word group filters of size filter_length: '''
        model.add(Conv1D(filters, kernel_size, padding='valid', activation='relu', strides=1))
        # we use max pooling:
        model.add(GlobalMaxPooling1D())

        # We add a vanilla hidden layer:
        model.add(Dense(hidden_dims))
        model.add(Dropout(0.2))
        model.add(Activation('relu'))

        # We project onto a single unit output layer, and squash it with a sigmoid:
        model.add(Dense(1))
        model.add(Activation('sigmoid'))

        model.compile(loss='binary_crossentropy',  optimizer='adam',  metrics=['accuracy'])
        

        x_train, y_train, x_test, y_test = self.loading()
        model.fit(x_train, y_train, batch_size=batch_size, epochs=epochs, validation_data=(x_test, y_test))
        
        md.save_json_model(model, "json_model")
        md.save_yaml_model(model, "yaml_model")

        del model


    def test_imdb(self) :

        from keras.callbacks import ModelCheckpoint
        from keras.utils import np_utils
        
        law_document = LawDocument()   
        
        fname = os.path.join(variables.BASE_DIR, 'data/Corpus/TEXT/合同、协议/劳动合同/1. 劳动合同- 最终版.DOC.txt')
        sentences = law_document.get_sentences(fname)
        
        # tokenizer
        tokenizer = Tokenizer(nb_words=self.MAX_NB_WORDS)
        tokenizer.fit_on_texts([sentences])
        self.sequences = tokenizer.texts_to_sequences([sentences])
        self.word_index = tokenizer.word_index

        seq_length = 10
        data = [m for m in self.word_index.values()]

        index_word = {}
        for w, id in list(self.word_index.items()):
            index_word[id] = w
            
            
        dataX = []
        dataY = []
        length = len(data) - seq_length
        for i in range(0, length, seq_length) :
            seq_in = data[i:i + seq_length-1]
            seq_out = data[i + seq_length]
            dataX.append(seq_in)
            dataY.append(seq_out)


        """
        raw_text = sentences
        
        chars = sorted(list(set("word telphone main")))
        
        # create mapping of unique chars to integers
        chars = sorted(list(set(raw_text)))
        char_to_int = dict((c, i) for i, c in enumerate(chars))
        int_to_char = dict((i, c) for i, c in enumerate(chars))
        # summarize the loaded data
        n_chars = len(raw_text)
        n_vocab = len(chars)
        print ("Total Characters: ", n_chars)
        print ("Total Vocab: ", n_vocab)
        # prepare the dataset of input to output pairs encoded as integers
        seq_length = 100
        dataX = []
        dataY = []
        for i in range(0, n_chars - seq_length, 1):
            seq_in = raw_text[i:i + seq_length]
            seq_out = raw_text[i + seq_length]
            dataX.append([char_to_int[char] for char in seq_in])
            dataY.append(char_to_int[seq_out])
        """
        
        n_patterns = len(dataX)
        print ("Total Patterns: ", n_patterns)
        
        # reshape X to be [samples, time steps, features]
        X = np.reshape(dataX, (n_patterns, seq_length-1, 1))
        n_vocab = len(index_word)
        # normalize
        X = X / float(n_vocab)

        # one hot encode the output variable
        y = np_utils.to_categorical(dataY)
        # define the LSTM model
        model = Sequential()
        model.add(LSTM(256, input_shape=(X.shape[1], X.shape[2])))
        model.add(Dropout(0.2))
        model.add(Dense(y.shape[1], activation='softmax'))
        model.compile(loss='categorical_crossentropy', optimizer='adam')
        # define the checkpoint
        filepath="weights-improvement-{epoch:02d}-{loss:.4f}.hdf5"
        checkpoint = ModelCheckpoint(filepath, monitor='loss', verbose=1, save_best_only=True, mode='min')
        callbacks_list = [checkpoint]
        # fit the model
        #model.fit(X, y, nb_epoch=20, batch_size=128, callbacks=callbacks_list)

        start = np.random.randint(0, len(dataX)-1)
        pattern = dataX[start]
        print ("Seed:")
        print ("\"", ''.join([index_word[value] for value in pattern]), "\"")
        # generate characters
        for i in range(1000):
            x = np.reshape(pattern, (1, len(pattern), 1))
            x = x / float(n_vocab)
            prediction = model.predict(x, verbose=0)
            index = np.argmax(prediction)
            result = index_word[index]
            seq_in = [index_word[value] for value in pattern]
            sys.stdout.write(result)
            pattern.append(index)
            pattern = pattern[1:len(pattern)]
        print ("\nDone.")
 
    '''
    def prefict_math(self):
        
        model = md.load_json_model("addition")
        for iteration in range(1, 200):
            print()
            print('-' * 50)
            print('Iteration', iteration)
            # Select 10 samples from the validation set at random so we can visualize errors.
            for i in range(10) :
                ind = np.random.randint(0, len(x_val))
                rowx, rowy = x_val[np.array([ind])], y_val[np.array([ind])]
                preds = model.predict_classes(rowx, verbose=0)
                q = ctable.decode(rowx[0])
                correct = ctable.decode(rowy[0])
                guess = ctable.decode(preds[0], calc_argmax=False)
                print('Q', q[::-1] if INVERT else q, end=' ')
                print('T', correct, end=' ')
                if correct == guess:
                    print(colors.ok + '☑' + colors.close, end=' ')
                else:
                    print(colors.fail + '☒' + colors.close, end=' ')
                print(guess)
    '''
    
if __name__ == '__main__':
    
    path = "D:/DTNSoftware/smart/python/src/data/Template/TEXT"
    embedding = EnbedTraining()
    
    #model = embedding.training_model()
    
    model = embedding.training(path)

    
    #embedding.test_imdb()


    print("----end-----")
   
