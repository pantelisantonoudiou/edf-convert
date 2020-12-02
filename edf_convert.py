# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 17:33:18 2020

@author: Pante
"""


### --------------- IMPORTS --------------- ###
import os, sys, json
import tables
import pyedflib
import numpy as np
from scipy import signal
from tqdm import tqdm
### --------------------------------------- ###


class edfConvert:
    """ Class for conversion of .edf files to .csv or .h5
    """
    
    def __init__(self, prop_dict):
        """

        Parameters
        ----------
        prop_dict : dict with properties

        Returns
        -------
        None.

        """
        
        # get values
        for key, value in prop_dict.items():
               setattr(self, key, value)
                
        self.down_factor = int(self.fs/self.new_fs)                   # down sampling factor
        self.winsize = int(self.new_fs*self.win)                      # window size in samples
        
        
    def edf_check(self, main_path, file_name):
        """
        
        Parameters
        ----------
        main_path : Str, path to file's parent directory
        file_name : Str, file name

        Returns
        -------
        Bool, 1 if the reading operation is successful 

        """
        
        # get reading length for testing        
        read_length = 1000 
        
        try: 
            # open reader
            f = pyedflib.EdfReader(os.path.join(main_path, file_name))
            
            for i in range(len(f.getSignalHeaders())): # iterate over channels
            
                # get signal length
                signal_length = f.getNSamples()[i]
                
                # read signal samples
                f.readSignal(chn = i, start = 0, n = read_length)                                        # start
                f.readSignal(chn = i, start = int(signal_length/2), n = read_length)                     # mid
                f.readSignal(chn = i, start = int(signal_length - read_length - 1) , n = read_length)    # end

            # delete read object
            del f
            
            return 1
        
        except Exception as err:
            
            print('\n -> Error! File:', file_name, 'could not be read.\n')
            print(err,'\n')
            
            return 0
            
   

    def edf_to_csv(self, main_path, file_name):
        """
        
        Parameters
        ----------
        main_path : Str, path to file's parent directory
        file_name : Str, file name

        Returns
        -------
        Bool, 1 if the convertion operation is successful 

        """
        
        # read edf
        f = pyedflib.EdfReader(os.path.join(main_path, file_name))
        
        for i in range(len(f.getSignalHeaders())): # iterate over channels
            
            # get channel number
            ch_num = i 
            
            # get save name
            save_name = file_name.replace('.edf','-ch_'+str(ch_num+1)) 
        
            print('\n-> Converting channel: '+ save_name)
            
            # decimate and scale
            data = signal.decimate(f.readSignal(ch_num) *self.scale, self.down_factor)
            
            # reshape
            data = np.reshape(data, (-1, self.winsize))
            
            # save to csv
            np.savetxt(os.path.join(main_path, save_name + '.csv'), data, delimiter =',')
            
        # delete file read
        del f
        
        return 1
    
    
    def edf_to_h5(self, main_path, file_name):
        """
        
        Parameters
        ----------
        main_path : Str, path to file's parent directory
        file_name : Str, file name

        Returns
        -------
        Bool, 1 if the convertion operation is successful 

        """
        
        # read edf
        f = pyedflib.EdfReader(os.path.join(main_path, file_name))
        
        # get rows and chanels
        rows = int(f.getNSamples()[0]/self.down_factor/self.winsize)
        channels = len(f.getSignalHeaders())
        
        # open tables object for saving
        fsave = tables.open_file(os.path.join(main_path, file_name + '.h5'), mode='w') 
        atom = tables.Float64Atom() # declare data type     
        ds = fsave.create_earray(fsave.root, 'data', atom, # create data store 
                                    shape = [rows, self.winsize, 0])
        
        for i in range(channels): # iterate over channels
            
            # get channel number
            ch_num = i 
            
            # get save name
            save_name = file_name.replace('.edf','-ch_'+str(ch_num+1)) 
        
            print('\n-> Converting channel: '+ save_name)
            
            # decimate and scale
            data = signal.decimate(f.readSignal(ch_num), self.down_factor) * self.scale
            
            # reshape
            data = np.reshape(data, (-1, self.winsize,1))
            
            # save to h5
            ds.append(data)
        
        # close tables save object
        fsave.close()
        
        # delete file read, 
        del f 
        
        return 1
        
        
                
    def all_files(self, main_path, func):
        """

        Parameters
        ----------
        main_path : Str, path to parent directory
        func : Function or method for manipulation of one edf file

        Returns
        -------
        bool_array : ndarray, 1/0 for successful and not successful operations respectively

        """
        
        # get file list
        filelist = list(filter(lambda k: '.edf' in k, os.listdir(main_path)))
        
        # create empty array to store 1/0
        bool_array = np.zeros(len(filelist))
        
        # convert all files
        for i in tqdm(range(len(filelist)), desc = 'Progress', file=sys.stdout):
            
            # convert edf to csv
            bool_array[i] = func(main_path, filelist[i])
            
        return bool_array
                
            
    
    
if __name__ == '__main__':
    
    # load properties from configuration file
    openpath = open('config.json' , 'r').read(); 
    prop_dict = json.loads(openpath)
        
    # get paths
    main_path = input('Please enter path of folder containing edf files: \n')
    
    if os.path.isdir(main_path) == 0:
        print('-> Path:', "'"+main_path+"'", 'is not valid.\n Please enter a valid path.')
        sys.exit()
    
    # init object
    obj = edfConvert(prop_dict)

    print('\n---------------------------------------------------------------------')
    print('------------------------ Initiate Error Check -----------------------\n')
    
    success = obj.all_files(main_path, obj.edf_check)

    print('\n------------------------ Error Check Finished -----------------------')
    print('---------------------------------------------------------------------\n')
    
    if np.all(success) == True:
        print('-> File Check Completed Successfully')  
    else:
        print('-> Warning!!! File Check was not Successful.')
        
    # create user options list
    options =['csv','h5','no']
    answer = ''
    
    # Verify how to proceed
    while answer not in options:
        answer = input('Would you like to proceed with File Conversion ' + str(options) + ' ? \n')
        
    if answer == 'no':
        
       print('---> No Further Action Will Be Performed.\n')
       sys.exit()

    elif answer == 'csv':
        
        print('\n--------------------------------------------------------------------------------')
        print('------------------------ Initiating edf -> csv Conversion ----------------------\n')
        
        obj.all_files(main_path, obj.edf_to_csv)
        
        print('\n************************* Conversion Completed *************************\n')
        
    elif answer == 'h5':
        
        print('\n-------------------------------------------------------------------------------')
        print('------------------------ Initiating edf -> h5 Conversion ----------------------\n')
        
        obj.all_files(main_path, obj.edf_to_h5)
        
        print('\n************************* Conversion Completed *************************\n')
            

           
       
       
    
    
    
    
