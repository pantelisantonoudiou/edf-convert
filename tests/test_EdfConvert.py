# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 11:24:20 2020

@author: Pante
"""

### ------------------------------------------- Imports ----------------------------------------- ###
import os
import numpy as np
import json
import tables
import pytest
import pyedflib
import pandas as pd
from scipy import signal
from edf_convert_main import EdfConvert
### --------------------------------------------------------------------------------------------- ###

### ------------------------------------------ Fixtures ----------------------------------------- ###

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
def edfobj_fixed_params(prop_dict):
    
    # get object
    obj = EdfConvert(prop_dict)
    
    # pass fixed values
    obj.fs = 2000
    obj.new_fs = 100
    obj.win = 5
    obj.scale = 1
    
    return obj

@pytest.fixture
def prop_dict(config_file_path):

    # load properties from configuration file
    openpath = open(config_file_path, 'r').read(); 
    prop_dict = json.loads(openpath)
    return prop_dict

@pytest.fixture # get EdfConvert object
def edf_obj(prop_dict, edf_dir_path, edf_file_name):
    
    # add main path to dict
    prop_dict.update({'main_path': edf_dir_path})
    
    # init object
    obj = EdfConvert(prop_dict)
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

### -------------------------------------------------------------------------------------------- ###
### -------------------------------------------------------------------------------------------- ###


### ------------------------------------------- Get Data --------------------------------------- ###

# convert edf data to csv
def test_convert_data_to_csv(edf_obj, edf_dir_path, edf_file_name):
    # convert data
    edf_obj.edf_to_csv(edf_file_name)
    
    assert 1 == 1 

# convert edf data to h5
def test_convert_data_to_h5(edf_obj, edf_dir_path, edf_file_name):
    # convert data
    edf_obj.edf_to_h5(edf_file_name)
    
    assert 1 == 1 

# create decimated data 
def test_create_signal(decimated_data):
    decimated_data.shape
    assert 1 == 1 
    
### ---------------------------------------------- Tests ----------------------------------------- ###
def test_fs(prop_dict, edf_obj):
    assert edf_obj.fs == prop_dict['fs']
    
def test_newfs(prop_dict, edf_obj):
    assert edf_obj.new_fs == prop_dict['new_fs']
    
def test_win(prop_dict, edf_obj):
    assert edf_obj.win == prop_dict['win']

def test_scale(prop_dict, edf_obj):
    assert edf_obj.scale == prop_dict['scale']
    
def test_downfactor_fixed(edfobj_fixed_params): 
    assert edfobj_fixed_params.down_factor == 20

def test_winsize_fixed(edfobj_fixed_params): 
    assert edfobj_fixed_params.winsize == 500
### ---------------------------------------------------------------------------------------------- ###
    
### ----------------------------------------- csv Tests ------------------------------------------ ###    
# test if csv file has correct shape  
def test_csv_file_shape(edf_dir_path, edf_obj, decimated_data):
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


# test if data are reshaped in the right order
def test_csv_data_placement(edf_dir_path, edf_obj, decimated_data, chnl):
    
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
    
    
# test if data are scaled correctly after conversion
def test_csv_data_scaling(edf_dir_path, edf_obj, decimated_data, chnl):
    
    # get number of csv files
    filelist = list(filter(lambda k: '.csv' in k, os.listdir(edf_dir_path)))
    
    # get data frame
    df = pd.read_csv(os.path.join(edf_dir_path, filelist[chnl]), header=None)
    
    # get sum of data from csv file
    csv_data = df.to_numpy().flatten()

    assert np.sum(decimated_data) == (np.sum(csv_data) * edf_obj.scale)

### ---------------------------------------------------------------------------------------------- ###

### ------------------------------------------ h5 Tests ------------------------------------------ ###   
# test if h5 file has correct shape  
def test_h5_file_shape(edf_dir_path, edf_file_name, edf_obj, decimated_data, channels):
    
    # get h5 file
    f = tables.open_file(os.path.join(edf_dir_path,edf_file_name.replace('.edf','.h5') ), mode='r')
    data_shape = f.root.data.shape;  f.close()
 
    # get number of rows and columns
    columns = int(edf_obj.winsize)
    rows = int(decimated_data.shape[0]/columns)
       
    assert data_shape == (rows, columns, channels)

# test if data are reshaped in the right order
def test_h5_data_placement(edf_dir_path, edf_file_name, edf_obj, decimated_data, chnl):
    
    # number of rows to test
    rows = 5;

    # get h5 file
    f = tables.open_file(os.path.join(edf_dir_path,edf_file_name.replace('.edf','.h5') ), mode='r')
    h5_data = f.root.data[:];  f.close()
    
    # get sum of data from csv file for n rows
    h5_data = h5_data[0:rows,:,chnl].flatten()
    
    # get equivalent data sum for length of n rows x column size
    dec_data = decimated_data[0:h5_data.shape[0]]
    
    assert np.sum(dec_data) == (np.sum(h5_data) * edf_obj.scale)
    
    
# test if data are scaled correctly after conversion
def test_h5_data_scaling(edf_dir_path, edf_file_name, edf_obj, decimated_data, chnl):
    
    # get h5 file
    f = tables.open_file(os.path.join(edf_dir_path,edf_file_name.replace('.edf','.h5') ), mode='r')
    h5_data = f.root.data[:,:,chnl];  f.close()
    
    # get sum of data from csv file for n rows
    h5_data = h5_data.flatten()
    
    assert np.sum(decimated_data) == (np.sum(h5_data) * edf_obj.scale)

### ---------------------------------------------------------------------------------------------- ###







