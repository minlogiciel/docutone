# -*- coding: utf-8 -*-

import sys

sys.path.append("../")

from keras.models import model_from_yaml
from keras.models import model_from_json
from docutone.utils import variables
from sklearn import preprocessing


OPTIMIZER_ADAM = 'adam'
OPTIMIZER_PROP = 'rmsprop'

def get_model_json_file(fname):
    name = fname +".json"
    return variables.get_data_file_name(dataname=name, categorie="model")

def get_model_yaml_file(fname):
    name = fname +".yaml"
    return variables.get_data_file_name(dataname=name, categorie="model")


def get_model_weight_file(fname):
    name = fname +".h5"
    return variables.get_data_file_name(dataname=name, categorie="model")

def get_model_embedded_file(fname):
    name = fname +".w2v"
    return variables.get_data_file_name(dataname=name, categorie="model")

def get_model_label_file(fname):
    name = fname +".txt"
    return variables.get_data_file_name(dataname=name, categorie="model")


def save_json_model(model, fname="model"):
    filename = get_model_json_file(fname)
    print(filename)
    # serialize model to JSON
    model_json = model.to_json()
    with open(filename, "w") as json_file:
        json_file.write(model_json)
    
    
    filename = get_model_weight_file(fname)
    # serialize weights to HDF5
    model.save_weights(filename)



def load_json_model(fname="model"):
    # load json and create model
    filename = get_model_json_file(fname)
    json_file = open(filename, 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    model = model_from_json(loaded_model_json)

    
    # load weights into new model
    filename = get_model_weight_file(fname)
    model.load_weights(filename)
    return model


def save_yaml_model(model, fname="model"):
    filename = get_model_yaml_file(fname)
    print(filename)
    # serialize model to YAML
    model_yaml = model.to_yaml()
    with open(filename, "w") as yaml_file:
        yaml_file.write(model_yaml)

    filename = get_model_weight_file(fname)
    # serialize weights to HDF5
    model.save_weights(filename)

 

def load_yaml_model(fname="model"):
    filename = get_model_yaml_file(fname)
    print(filename)
    # load YAML and create model
    yaml_file = open(filename, 'r')
    loaded_model_yaml = yaml_file.read()
    yaml_file.close()
    model = model_from_yaml(loaded_model_yaml)

    # load weights into new model
    filename = get_model_weight_file(fname)
    model.load_weights(filename)
    return model
 
 
def label_encoder(bases, labels):
    le = preprocessing.LabelEncoder()
    le.fit(bases)
    return le.transform(labels) 


def label_decoder(bases, labels):
    le = preprocessing.LabelEncoder()
    le.fit(bases)
    return le.inverse_transform(labels) 


 