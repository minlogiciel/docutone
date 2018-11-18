# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import sys,os,io,codecs
import random

from gensim import corpora, models
from gensim.models import word2vec
from gensim.models import doc2vec
from gensim.models.doc2vec import TaggedDocument

sys.path.append("../")
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding = 'utf-8')

from docutone.core import document
from docutone.core.document import LawDocument
from docutone.utils import convert, variables, util
from docutone.utils.folder import Folder
from docutone.logging import dtn_logging as dtn_logger
from docutone.utils.base import File

'''
所有的文件
'''

class Datasets(object):
 
    '''
    create all types of document data set
    
    doc2vec label document type
    
    save to dataset data/dataset directory 
   
    '''
    NB_LOOP = 7
    V_ALPHA = 0.2
    V_MIN_ALPHA = 0.05
    V_ALPHA_RATE = 0.005

    def __init__(self):
        
        self.texts = []         # list of text samples
        self.labels_index = {}  # dictionary mapping label name to numeric id
        self.labels_files = {}   # dictionary mapping label name to numeric id
        self.labels_name = {}   # dictionary mapping label name to numeric id
        self.file_label = []      # file label id
        self.labels = []        # list of label ids
        self.classifiers = []    # list of classifier
        self.law_doc =  LawDocument()
        self.folder_structure = {}
        self.folder_order = []
     
        pass
    
    def get_data_file_name(self, fname, isdataset=True) :
        path = os.path.join(variables.BASE_DIR, variables.MODEL_DATA_DIR)
        if not os.path.exists(path) :
            os.mkdir(path)
        if isdataset :
            path = os.path.join(path, 'datasets')
            if not os.path.exists(path) :
                os.mkdir(path)
        return os.path.join(path, fname)

    def get_svc_file_name(self) :
        return self.get_data_file_name(variables.SVC_MODEL)

    def get_model_file_name(self) :
        return self.get_data_file_name(variables.DOC_MODEL)

    def get_word_model_name(self) :
        return self.get_data_file_name(variables.WORD_MODEL)

    def get_dict_file_name(self) :
        return self.get_data_file_name(variables.MODEL_DICT)

    def get_mm_file_name(self) :
        return self.get_data_file_name(variables.MODEL_MM)

    def get_model_list_name(self) :
        return self.get_data_file_name(variables.MODEL_LSI)

    
    """
    all files in this directory are a classifier document
    
    """   
    def load_directory_for_document(self, path, label, label_id) :
   
        nb_files = 0

        for fname in sorted(os.listdir(path)):
        
            fpath = os.path.join(path, fname)
            if os.path.isdir(fpath):
                 
                if fname in self.folder_structure.keys() :
                    sublabel = self.folder_structure[fname][0]
                    if sublabel == None :
                        sublabel = label
                else :
                    sublabel = label
                    
                nb_files += self.load_directory_for_document(fpath, sublabel, label_id)
   
            elif fname.lower().endswith(".txt"):
                words = document.get_document_words(fpath)
                if len(words) > 10 :
                    self.texts.append(words)

                    self.classifiers.append(label)
                    self.labels.append(label_id)
                    self.file_label.append(fname)
                    nb_files += 1
            else :
                #is not text file
                pass
        return nb_files
    
    '''
    
    '''
    def load_document_directorie(self, fpath, label) :
        
        if label in self.labels_index.keys() :
            label_id = self.labels_index[label]
            nb = self.labels_files[label]
        else :
            label_id = len(self.labels_index)+1
            nb = 0;
                    
        n = self.load_directory_for_document(fpath, label, label_id)
        if n > 5 :
            self.labels_index[label] = label_id
            self.labels_name[label_id-1] = label
            self.labels_files[label] = nb + n
            print(" === " + label + " : " + str(label_id) + "   === ") 


    def load_directories(self, path) :
        for name in sorted(os.listdir(path)):
            fpath = os.path.join(path, name)
            if os.path.isdir(fpath):
                if name in self.folder_structure.keys() :
                    label, level = self.folder_structure[name]
                    if level == 0 :
                        continue
                    elif not label :
                        self.load_directories(fpath)
                        continue
                else :    
                    label = name
    
                self.load_document_directorie(fpath, label)
                
    
    
    def load_text_files(self, text_path) :

        self.texts = []        
        self.labels_index = {}  
        self.labels_name = {}   
        self.labels = []
        self.file_label = []
        
        # load defined directory type 
        folder = Folder()
        
        # folder structure define classifier document type
        self.folder_structure = folder.load_folder_structure(text_path)
        
        for name in sorted(os.listdir(text_path)):
            path = os.path.join(text_path, name)
            if name != variables.TEMP_DIR and name != variables.DATA_DIR and os.path.isdir(path):
                if name in self.folder_structure.keys() :
                    label, level = self.folder_structure[name]
                    if level == 0 :
                        continue
                    else :
                        if label :
                            self.load_document_directorie(path, label)
                        else :
                            self.load_directories(path) 
    
    
    '''
    load all file from merged files
    
    '''
    def load_data_files(self, text_path) :

        self.texts = []        
        self.labels_index = {}  
        self.labels_name = {}   
        self.labels = []
        self.file_label = []
        
        # load defined directory type 
        folder = Folder()
        
        # folder structure define classifier document type
        self.folder_structure = folder.load_folder_structure(text_path)
        
        folder_order = folder.folder_order
        
        prevlabel = None
        for fname in sorted(os.listdir(text_path)):
            if (folder.CORPUS_FILE_NAME in fname) :
                filename = os.path.join(text_path, fname)
                docs = folder.load_corpus_file(filename)
                
                for doc in docs :
                    fname = doc[0][0]   # file name
                    name = doc[0][1]    # type of file
                    label = doc[0][2]   # file label
                    level = doc[0][3]   # file level in directory
                          
                    if name in self.folder_structure.keys() :
                        categorie, level = self.folder_structure[name]
                        if categorie and ';' in categorie:
                            label = categorie.split(';')[0]
                        else :
                            label = categorie
                            
                    if not categorie :
                        savecat = None
                            
                        if name in self.folder_structure.keys() :
                            
                            for fn in folder_order :
                                if fn == name and savecat != None:
                                    categorie = savecat
                                    if ';' in categorie:
                                        label = categorie.split(';')[0]
                                    else :
                                        label = categorie
                                    break
                                else :
                                    categorie, level = self.folder_structure[fn]
                                    if categorie :
                                        savecat = categorie
                                
                        else :   
                            categorie = doc[0][2]
                            label = categorie;
   
                    
                    sentences = doc[1:]
                    norm_sentences = [util.normalize_sentence(s) for s in sentences]
                    words = self.law_doc.get_normalize_document_from_sentences(norm_sentences, outtype=2)
                    if len(words) > 0 :
                        
                        # find same classifier 
                        if label in self.labels_index.keys() :
                            label_id = self.labels_index[label]
                        else :
                            label_id = len(self.labels_index)+1
                        
                            self.labels_index[label] = label_id
                            self.labels_name[label_id] = label
                      
                        # add document to text
                        self.texts.append(words)
                        # add label 
                        self.classifiers.append(categorie)
                        # add label id
                        self.labels.append(label_id)
                        # add file name
                        self.file_label.append(fname)
                        
                           
                        if label in self.labels_files.keys() :
                            self.labels_files[label] += 1
                        else :
                            self.labels_files[label] = 1

                        if (prevlabel != label) :
                            print(" === " + label + " : " + str(label_id) + "   === ")
                            prevlabel = label
                            
                        
        
    
    
    def load_documents(self, text_path) :
     
        if (text_path.endswith("training_data") ) :
            self.load_data_files(text_path)
        else :
            self.load_text_files(text_path) 
        
        alldocs = []
        doclists = []
        for index in range(len(self.texts)) :
            words = self.texts[index]
            if len(words) > 10 :
                        
                #string = 'doc_' + str(index+1)
                docs = TaggedDocument(words, tags = [index])         
                doclists.append(docs)
                alldocs.append(words)
        return alldocs, doclists
    

    def get_document_words(self, filename, f=None) :
        
        f = File(filename, None, verbose=0)
        words = f.get_document_words()
        if len(words) > 10 :
            return words
        else :
            return None  

          
    def getTaggedDocuments(self, filename, index) :
        
        words = self.get_document_words(filename)
        if words : 
            return TaggedDocument(words, tags = [index])
        else :
            return None    
    
    def TrainingDoc2Vec(self, documents, size, window, nb_loop=NB_LOOP):
    
        #doc to vector 
        #model = doc2vec.Doc2Vec(documents, size=size, window=window)
        alpha = self.V_ALPHA
        min_alpha = self.V_MIN_ALPHA
        model = doc2vec.Doc2Vec(documents, size=size, window=window, alpha=alpha, min_alpha=min_alpha)
        #model.sort_vocab()
        #model.build_vocab(documents)

        for epoch in range(nb_loop):
            random.shuffle(documents)
            model.train(documents, total_examples=len(documents), epochs=1, start_alpha=alpha, end_alpha=min_alpha)
            alpha -= self.V_ALPHA_RATE
            min_alpha = alpha
            # decrease the learning rate
            model.alpha -= self.V_ALPHA_RATE            # decrease the learning rate
            model.min_alpha = model.alpha   # fix the learning rate, no decay   
            #err, err_count, test_count, predictor = error_rate_for_model(model, documents, test_docs)
            print("epoch = %d alpha = %f\n" % (epoch, model.alpha))
    
        return model
    
    
    def create_dataset(self, text_path, min_count=2, sg=0, workers=1, size=256, window=5) :    
        """
            
        min_count : ignore all words with total frequency lower than this.
        sg : sg = O CBOW, sg=1 skip-gram 
        workers: thread
        size : dimension feature vectors.
        window : maximum distance between the current and predicted word within a sentence.
    
        """
        dtn_logger.logger_info("DATASET", "create dataset " + text_path)
        
    
        lists, doclists = self.load_documents(text_path)
                  
        dictionary = corpora.Dictionary(lists)
        corpus = [dictionary.doc2bow(text) for text in lists]
        
        # save corpus
        corpusfname = self.get_mm_file_name()
        corpora.MmCorpus.serialize(corpusfname, corpus) 
    
        
        # save dictionay
        dictfname = self.get_dict_file_name()
        dictionary.save(dictfname)
        
    
    
        dictfname = self.get_model_list_name()        
        # initialize a model
        tfidf = models.TfidfModel(corpus, normalize=True)
            
        # use the model to transform vectors        
        corpus_tfidf = tfidf[corpus]
            
        # initialize an LSI transformation, LSI 2-D space
        lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=300) 
        lsi.save(dictfname) # same for tfidf, lda, ...
    
        #training doc2vec
        model = self.TrainingDoc2Vec(doclists, size=size, window=window, nb_loop=32) 
        # save doc vector
        vectfname = self.get_model_file_name()
        model.save(vectfname)
    
        # word to vector 
        model = word2vec.Word2Vec(lists, min_count=min_count, sg=sg, workers=workers, size=size, window=window)
        # save words vector
        vectfname = self.get_word_model_name()
        model.wv.save_word2vec_format(vectfname, binary=False)
        #model.sort_vocab()
        #model.build_vocab(sentences, update=False)
        
        # save file label 
        self.save_filelabel()
    
        # save doc label 
        self.save_doclabel()
    
        # save vector labels  
        self.save_labelset()
        
        # save classifier labels  
        self.save_classifierlabel()
    
    
    
    
    def load_wordvect(self) :
        fname = self.get_word_model_name()
        f = codecs.open(fname, 'r', 'utf-8')
        sentences = f.read()
        sentences = sentences.split('\n')
        sentences = [s.split()[1:] for s in sentences]
        word2vec = [' '.join(s) for s in sentences if len(s) > 0]
        f.close()
    
        return word2vec
    
    def load_docvect(self) :
    
        fname = self.get_model_file_name()
        model = doc2vec.Doc2Vec.load(fname)
    
        nbdocs = len(model.docvecs)
        resultlist = []
        for i in range(nbdocs):
            #string = 'doc_' + str(i+1)
            #resultlist.append(model.docvecs[string])
            vv = model.docvecs[i]
            vv = [v for v in vv]
            resultlist.append(vv)
        
        return resultlist;
    
    
    def load_labelset(self) :
        fname = self.get_data_file_name(variables.VECT_LABEL, True)
        f = codecs.open(fname, 'r', 'utf-8')
        
        labelSet = [int(line) for line in f if len(line.strip()) > 0]
        f.close()
      
        return labelSet
    
    def save_labelset(self) :
        fname = self.get_data_file_name(variables.VECT_LABEL, True)
        f = codecs.open(fname, 'w', 'utf-8')
        
        for v in self.labels :
            f.write("%s\n" % (v))
        f.close()
    
    
    def load_doclabel(self) :
        fname = self.get_data_file_name(variables.DOC_LABEL, True)
        f = codecs.open(fname, 'r', 'utf-8')
        
        labelSet = [line.split('=')[0] for line in f if len(line.strip()) > 0]
        f.close()
    
        return labelSet
    
    
    def save_doclabel(self) :
    # save doc label 
        fname = self.get_data_file_name(variables.DOC_LABEL, True)
        f = codecs.open(fname, 'w', "utf-8")
        #for k, v in labels_index.items():
        for v, k in self.labels_name.items():
            f.write("%s=%d=%d\n" % (k, v, self.labels_files[k]))
        f.close()
    
    
    def load_filelabel(self) :
        fname = self.get_data_file_name(variables.FILE_LABEL, True)
        f = codecs.open(fname, 'r', 'utf-8')
        
        labelSet = [line.split('=')[0] for line in f if len(line.strip()) > 0]
        f.close()
    
        return labelSet
    
    def save_filelabel(self) :
        # save file label 
        fname = self.get_data_file_name(variables.FILE_LABEL, True)
        f = codecs.open(fname, 'w', "utf-8")
        for index in range(len (self.file_label)):
            k = self.file_label[index]
            v = self.labels[index]
            f.write("%s=%d\n" % (k, v))
        f.close()
        
    def load_classifierlabel(self) :
        fname = self.get_data_file_name(variables.CLASSIFY_LABEL, True)
        f = codecs.open(fname, 'r', 'utf-8')
        
        labelSet = [line.strip() for line in f if len(line.strip()) > 0]
        f.close()
    
        return labelSet
    
    def save_classifierlabel(self) :
        # save classifier label 
        fname = self.get_data_file_name(variables.CLASSIFY_LABEL, True)
        f = codecs.open(fname, 'w', "utf-8")
        for v in self.classifiers :
            f.write("%s\n" % (v))
        f.close()

        
        
    def test_corpus_dictionary(self) :
        
        dictfname = self.get_dict_file_name()
        if (os.path.exists(dictfname)):
            dictionary = corpora.Dictionary.load(dictfname)
            corpusfname = self.get_mm_file_name()
            corpus = corpora.MmCorpus(corpusfname)
            print(corpus)
        else:
            print("corpus dictionary does not exist")
            
            
                
    def test_word_vector_model(self) :
    
        vectfname = self.get_word_model_name()
        
        #sentences = LineSentence(vectfname)
        #sentences = Text8Corpus(vectfname)
        #sentences = LineSentence('compressed_text.txt.bz2')
        #sentences = LineSentence('compressed_text.txt.gz')
    
    
        model = word2vec.Word2Vec.load_word2vec_format(vectfname, binary=False)
        
        print ("Test word2vec most similar for 驾驶, 机动车, 交通运输")
        print (model.most_similar(positive=['驾驶']))
    
    
        

       
     
        
if __name__ == "__main__":
    
    ''' using training to test '''
    
    pass
    
