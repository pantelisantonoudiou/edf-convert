# -*- coding: utf-8 -*-
"""
Created on Fri Dec  4 10:55:13 2020

@author: Pante
"""

### ----------------------- Imports ---------------------- ###
import json
import pytest
from edf_convert_main import EdfConvert
### ------------------------------------------------------ ###

### ----------------------- Fixtures ---------------------- ###
@pytest.fixture
def config_file_path():
    return 'config.json'

@pytest.fixture
def prop_dict(config_file_path):

    # load properties from configuration file
    openpath = open(config_file_path, 'r').read(); 
    prop_dict = json.loads(openpath)
    return prop_dict

@pytest.fixture
def edfobj(prop_dict):
    
    # init object
    obj = EdfConvert(prop_dict)
    return obj


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
### ------------------------------------------------------ ###


### ------------------------ Tests ----------------------- ###
def test_fs(prop_dict, edfobj):
    assert edfobj.fs == prop_dict['fs']
    
def test_newfs(prop_dict, edfobj):
    assert edfobj.new_fs == prop_dict['new_fs']
    
def test_win(prop_dict, edfobj):
    assert edfobj.win == prop_dict['win']

def test_scale(prop_dict, edfobj):
    assert edfobj.scale == prop_dict['scale']
    
def test_downfactor_fixed(edfobj_fixed_params): 
    assert edfobj_fixed_params.down_factor == 20

def test_winsize_fixed(edfobj_fixed_params): 
    assert edfobj_fixed_params.winsize == 500
### ------------------------------------------------------ ###




