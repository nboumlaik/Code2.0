'''
Created on 27 janv. 2017

@author: VMargot
'''

try:
    import pandas as pd
except ImportError:
    raise ImportError, "The pandas package is required to run this program"

try:
    import data_utils
except ImportError:
    raise ImportError, "Don't find the package data_utils"

class Variables():
    '''
    classdocs
    '''
    
    def __init__(self, **parameters):
        for arg, val in parameters.items():
            setattr(self, '_'+arg, val)
    
    def load(self):
        data_path = self.get_param('data_path')
        var_name = self.get_param('csv_name')
        data = data_utils.load_var(data_path, var_name)
    
    def update(self):
        pass
    
    def save_data(self):
        pass
    
    def save_parameters(self, dict_path):
        line_name = self.get_param('SQL_Name')
    
    '''------   Getters   -----'''               
    def get_param(self, param):
        assert type(param) == str, 'Must be a string'
        return getattr(self, '_'+param)
    
    def get_params(self, deep=True):
        out = {}
        for key in self.__dict__.keys():
                out[key] = self.__dict__[key]
        return out
    
    '''------   Setters   -----'''
    def set_params(self, **parameters):
        for parameter, value in parameters.items():
            setattr(self, '_'+parameter, value)
        return self