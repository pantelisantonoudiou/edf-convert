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


class EdfConvert:
    """ Class for conversion of .edf files to .csv or .h5 format.
    """
    
    def __init__(self, prop_dict):
        """

        Parameters
        ----------
        prop_dict : Dict, with properties from config.json file

        Returns
        -------
        None.

        """
        
        # get values from dictionary
        for key, value in prop_dict.items():
               setattr(self, key, value)
                
        self.down_factor = int(self.fs/self.new_fs)                   # down sampling factor
        self.winsize = int(self.new_fs*self.win)                      # window size in samples
        
        
    def _read_edf(self, file_name):
        """
        Opens edf file using pyedflib and returns a reference object.
        ----------------------------------------------------------------------

        Parameters
        ----------
        file_name : Str, file name

        Returns
        -------
        fread : pyedflib obj

        """
        
        fread = pyedflib.EdfReader(os.path.join(self.main_path, file_name))
        
        return fread
        
        
    def edf_check(self, file_name):
        """
        Checks if an edf file can be read successfully.
        ----------------------------------------------------------------------
        
        Parameters
        ----------
        file_name : Str, file name

        Returns
        -------
        Bool, False/True if the reading operation is successful/unsuccessful

        """
        
        # get reading length for testing        
        read_length = 1000 
        
        try: 
            # open edf reader
            f = self._read_edf(file_name)
            
            for i in range(len(f.getSignalHeaders())): # iterate over channels
            
                # get signal length
                signal_length = f.getNSamples()[i]
                
                # read signal samples
                f.readSignal(chn = i, start = 0, n = read_length)                                        # start
                f.readSignal(chn = i, start = int(signal_length/2), n = read_length)                     # mid
                f.readSignal(chn = i, start = int(signal_length - read_length - 1) , n = read_length)    # end

            # delete read object
            del f
            
            return False
        
        except Exception as err:
            
            print('\n -> Error! File:', file_name, 'could not be read.\n')
            print(err,'\n')
            
            return True
            

    def edf_to_csv(self, file_name):
        """
        Convert an edf to csv file(s), one csv file per channel.
        
        csv file shape:
        rows = nSamples/columns
        columns = win * new_fs
        Where 'nSamples' is the number of samples in one channel of the edf file.
        ----------------------------------------------------------------------
        
        Parameters
        ----------
        file_name : Str, file name

        Returns
        -------
        Bool, False/True if the reading operation is successful/unsuccessful

        """
        
        # open edf reader
        f = self._read_edf(file_name)
        
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
            np.savetxt(os.path.join(self.main_path, save_name + '.csv'), data, delimiter =',')
            
        # delete file read
        del f
        
        return False
    
    
    def edf_to_h5(self, file_name):
        """
        Convert edf to h5 file.
        
        h5 file shape:
        1st-dimension, X = nSamples/Y
        2nd-dimension, Y = win * new_fs
        3rd-dimension, Z = number of channels
        Where 'nSamples' is the number of samples in one channel of the edf file.
        ----------------------------------------------------------------------
        
        Parameters
        ----------
        file_name : Str, file name

        Returns
        -------
        Bool, False/True if the reading operation is successful/unsuccessful

        """
        
        # open edf reader
        f = self._read_edf(file_name)
        
        # get rows and chanels
        rows = int(f.getNSamples()[0]/self.down_factor/self.winsize)
        channels = len(f.getSignalHeaders())
        
        # open tables object for saving
        fsave = tables.open_file(os.path.join(self.main_path, file_name.replace('.edf','.h5')), mode='w') 
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
        
        return False
        
        
                
    def all_files(self, func):
        """
        Run func opeartion on all edf files in self.main_path.
        ----------------------------------------------------------------------

        Parameters
        ----------
        main_path : Str, path to parent directory
        func : Function or method for manipulation of one edf file

        Returns
        -------
        bool_array : ndarray, False/True for successful/unsuccessful operations

        """
        
        # get file list
        filelist = list(filter(lambda k: '.edf' in k, os.listdir(self.main_path)))
        
        # create empty array to store True/False
        bool_array = np.zeros(len(filelist), dtype = bool)
        
        # convert all files
        for i in tqdm(range(len(filelist)), desc = 'Progress', file=sys.stdout):
            
            # convert edf to csv
            bool_array[i] = func(filelist[i])
            
        return bool_array
                
    
if __name__ == '__main__':
    
    # load properties from configuration file
    openpath = open('config.json' , 'r').read(); 
    prop_dict = json.loads(openpath)
        
    # get paths
    main_path = input('Please enter path of folder containing edf files: \n')
    
    if os.path.isdir(main_path) == 0:
        print('-> Path:', "'" + main_path + "'", 'is not valid.\n Please enter a valid path.')
        sys.exit()
    
    # add main path to properties dictionary
    prop_dict.update(main_path)
    
    # init object
    obj = EdfConvert(prop_dict)

    print('\n---------------------------------------------------------------------')
    print('------------------------ Initiate Error Check -----------------------\n')
    
    success = obj.all_files(main_path, obj.edf_check)

    print('\n------------------------ Error Check Finished -----------------------')
    print('---------------------------------------------------------------------\n')
    
    if np.any(success) == False:
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
            

           
       
       
    
    
    
    
