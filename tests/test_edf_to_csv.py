# -*- coding: utf-8 -*-
"""
Created on Fri Dec  4 15:24:16 2020

@author: Pante
"""

### ------------------------ Imports ---------------------- ###
import os
import numpy as np
import pandas as pd
import json
import pytest
import pyedflib
from scipy import signal
from edf_convert_main import edfConvert
### ------------------------------------------------------- ###


### ----------------------- Fixtures ---------------------- ###

@pytest.fixture
def config_file_path():
    return 'config.json'

@pytest.fixture
def edf_dir_path():
    return 'tests'

@pytest.fixture
def edf_file_name():
    return 'example.edf'

@pytest.fixture
def chnl():
    return 0

@pytest.fixture
def prop_dict(config_file_path):

    # load properties from configuration file
    openpath = open(config_file_path, 'r').read(); 
    prop_dict = json.loads(openpath)
    return prop_dict

@pytest.fixture # get edfConvert object
def edf_obj(prop_dict, edf_dir_path, edf_file_name):
    
    # init object
    obj = edfConvert(prop_dict)
    return obj

@pytest.fixture # get decimated data from channel 'chnl'
def decimated_data(edf_dir_path, edf_file_name, edf_obj, chnl):
    
    # load properties from configuration file
    edf = pyedflib.EdfReader(os.path.join(edf_dir_path, edf_file_name))
    
    # get decimated data
    data = signal.decimate(edf.readSignal(chnl), edf_obj.down_factor)
    
    # delete edf object
    del edf;
    return data

@pytest.fixture # get number of channels
def channels(edf_dir_path, edf_file_name):
    
    # load properties from configuration file
    edf = pyedflib.EdfReader(os.path.join(edf_dir_path, edf_file_name))
    
    # pass channels and delete edf object
    chnls = len(edf.getSignalHeaders()); del edf
    return chnls

### ------------------------------------------------------ ###


### ------------------------ Tests ----------------------- ###

# convert edf data to csv
def test_convert_data_to_csv(edf_obj, edf_dir_path, edf_file_name):
    # convert data
    edf_obj.edf_to_csv(edf_dir_path, edf_file_name)
    
    assert 1 == 1 

# create decimated data 
def test_create_signal(decimated_data):
    decimated_data.shape
    
    assert 1 == 1 
   
# test if number of channels is the same as number of csv files
def test_num_of_chnls_equal_to_files(edf_dir_path, channels):
    # get number of csv files
    filelist = list(filter(lambda k: '.csv' in k, os.listdir(edf_dir_path)))
    
    assert len(filelist) == channels
   
# test if csv file has correct shape  
def test_file_shape(edf_dir_path, edf_obj, decimated_data):
    # get number of csv files
    filelist = list(filter(lambda k: '.csv' in k, os.listdir(edf_dir_path)))
   
    # get number of rows and columns
    columns = int(edf_obj.winsize)
    rows = int(decimated_data.shape[0]/columns)
   
    # create empty lists for strage
    csv_size = []
    true_size = []
   
    for i in range(len(filelist)):
        # read excel file
        df = pd.read_csv(os.path.join(edf_dir_path, filelist[i]), header=None)
       
        # extend lists
        csv_size.extend(df.shape)
        true_size.extend((rows, columns))
       
    assert csv_size == true_size 


# test if data are scaled correctly after conversion (from the first n rows)
def test_data_unchanged(edf_dir_path, edf_obj, decimated_data, chnl):
    
    # rows to measure sum
    rows = 5
    
    # get number of csv files
    filelist = list(filter(lambda k: '.csv' in k, os.listdir(edf_dir_path)))
    
    # get data frame
    df = pd.read_csv(os.path.join(edf_dir_path, filelist[chnl]), header=None)
    
    # get sum of data from csv file for n rows
    csv_data = df.loc[0:rows-1].to_numpy().flatten()
    
    # get equivalent data sum for length of n rows x column size
    dec_data = decimated_data[0:csv_data.shape[0]]
    
    assert np.sum(dec_data) == (np.sum(csv_data) * edf_obj.scale)
    

### ------------------------------------------------------ ###


    
    
    
    
