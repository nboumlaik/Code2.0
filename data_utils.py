'''
data_utils includes all functions that could be useful to the data management
'''
import os
import sys
import warnings

try:
	import csv
except ImportError:
	raise ImportError, "The csv package is required to run this program"

try:
	import numpy as np
except ImportError:
	raise ImportError, "The numpy package is required to run this program"

try:
	import pandas as pd
except ImportError:
	raise ImportError, "The pandas package is required to run this program"

def find_delim(csv_path, delimiters=',;'):
	'''
	Function used to find a delimiters in a csv file
	
	Parameters
	----------
	csv_path : {strin type}
			   Path of the csv file
			   
	delimiters : {string type}
				 String with different possibles delimiters
				 ex: ',;' means that the function will test ',' and ';'

	Return
	------
	dialect.delimiter : {string type}
						The best delimiter of the csv among the given delimiters
	'''
	#Test if the file exists
	assert os.path.isfile(csv_path), 'No csv file here %s' % csv_path
	f = open(csv_path, "rb")
	#Creation of a Sniffer object
	csv_sniffer = csv.Sniffer()
	#It reads nb_bytes bytes of the csv file and ...
	#... chooses the best delimiter among the given delimiters
	dialect = csv_sniffer.sniff(f.readline(), 
				    delimiters=delimiters)
	f.close()
	return dialect.delimiter

def make_index(csv_path, path_out=None, save=False):
	'''
	Function used to make an index for multi-asset learning
	
	Parameters
	----------
	csv_path : {string type}
			   Path of the csv file.
			   ex: path to the file price.csv
			   
	path_out : {string type}, optional
			   Path to write the file (used is save=True)
			   
	save : {bool type} optional, default False
		   Option to write the file

	Return
	------
	index : {pandas Multiindex type}
			The index for the multi-assets DataFrame
	'''
	#Find the delimiter for the csv
	sep = find_delim(csv_path)
	#Loading the csv
	df = pd.read_csv(csv_path, sep = sep)
	#Drop the NaN line
	df.fillna(0, inplace = True)
	#First column (Date) in index / Stock in columns
	df.set_index(df.columns[0], inplace = True)
	df_stack = df.stack()
	#Get the multiIndex
	df_index = df_stack.index
	
	#Making of the index file
	index = pd.DataFrame()
	index['Dates'] = df_index.get_level_values(0)
	index['Ids'] = df_index.get_level_values(1)
	index.set_index('Dates', inplace = True)
	
	if save:
		assert path_out is not None, \
		'You must give a path_out to write the index'
		#Saving of the index file
		#Name with the last date
		csv_name = 'Index '+ str(max(df.index)) +'.csv'
		path = os.path.join(path_out,csv_name)
		index.to_csv(path)

	return index

def find_bins(xcol, nb_bucket):
	'''
	Function used to find the bins to discretize xcol in nb_bucket modalities
		
	Parameters
	----------
	xcol : {pandas Series, numpy array type}
		   Data which will be discretized
		   
	nb_bucket : {int type}
				number of modalities for the 
				discretization

	Return
	------
	bins : {pandas Series, numpy array type}
	       bins for disretization
	'''
	#Find the bins for nb_bucket
	bins = np.percentile(xcol, np.arange(100.0/(nb_bucket),
										  100.0,100.0/(nb_bucket)))
	
	if bins.min() != 0:
		test_bins = bins/bins.min()
	else:
		test_bins = bins
	
	#Test if we have same bins...
	while len(set(test_bins.round(5))) != len(bins):
		#Try to decrease the number of bucket to have unique bins
		nb_bucket -= 1
		bins = np.percentile(xcol, np.arange(100.0/(nb_bucket),
										  100.0,100.0/(nb_bucket)))
		if bins.min() != 0:
			test_bins = bins/bins.min()
		else:
			test_bins = bins
	
	return bins

def discretize(xcol, nb_bucket, bins=None):
	'''
	Function used to have discretize xcol in nb_bucket values
		
	Parameters
	----------
	xcol : {pandas Series, numpy array type}
		   Data which will be discretized
		   
	nb_bucket : {int type}
				number of modalities for the 
				discretization
				
	bins : {pandas Series, numpy array type}, optional
	       bins for disretization
	
	Return
	------
	xcol_discretized : {pandas Series, numpy array type}
					   the discretization of xcol, if it is a real series
					   do nothing if xcol is a string series
	'''
		
	if xcol.dtype.type != np.str_:
		#extraction of the list of xcol values
		notNan_vect = np.extract(np.isfinite(xcol), xcol)
		
		#Test if xcol have more than nb_bucket different values
		if len(set(notNan_vect)) > nb_bucket:
			if bins is None:
				bins = find_bins(xcol, nb_bucket)
				#discretization of the xcol with bins
			xcol_discretized = xcol.apply(lambda x: 
										np.digitize(x, bins=bins, right=False))

			return xcol_discretized
		
		#warnings.warn('Variable %s not discretize' %xcol.name)
		return xcol
	
	else:
		return xcol

def load_var(path, var_name, times_series=True):
	'''
	Function used to load a variable from a path
		
	Parameters
	----------
	path : {string type}
		   Path to a csv or a directory
	
	var_name : {string type}
			   Name of a column or a csv
	
	times_series : {bool type} optional, default True
				   Option to parse dates
	
	Return
	------
	return : {pandas Serie type}
	'''
	#test if the path is to a file...
	if os.path.isfile(path):
		return load_from_file(path, var_name, times_series)
	
	#... or to a directory
	elif os.path.isdir(path):
		return load_from_dir(path, var_name, times_series)
	
	else:
		warnings.warn('Path error: %s' %path)
		sys.exit()

def load_from_file(path, var_name, times_series):
	'''
	Function used to load a variable from a csv
		
	Parameters
	----------
	path : {string type}
		   Path to a csv or a directory
	
	var_name : {string type}
			   Name of a column or a csv
	
	times_series : {bool type} optional, default False
				   Option to parse dates
	
	Return
	------
	return : {pandas Serie type}
	'''
	sep = find_delim(path)
	extension = os.path.splitext(path)[1]
	
	#Test the type a file
	if extension == '.csv':
		col = pd.read_csv(path, sep=sep, parse_dates=times_series,
						  index_col=0)[var_name]
		
		col.name = var_name
		return col
	
	warnings.warn('Unknown extension: %s' %extension)
	sys.exit()

def load_from_dir(path, var_name, times_series):   
	'''
	Function used to load a variable from a csv
		
	Parameters
	----------
	path : {string type}
		   Path to a csv or a directory
	
	var_name : {string type}
			   Name of a column or a csv
	
	times_series : {bool type} optional, default False
				   Option to parse dates
	
	Return
	------
	return : {pandas Serie type}
	'''
	path = os.path.join(path,var_name)
	extension = os.path.splitext(path)[1]
	
	if extension != '.csv':
		path += '.csv'
	
	sep = find_delim(path)
	f = open(path)
	first_line = f.readline()
	splited_line = first_line.split(sep)
	f.close()
	
	if len(splited_line) > 3:
		col = pd.read_csv(path, sep=sep, parse_dates=times_series,
						  index_col=0)
		col = col.stack()
		
	else:
		col = pd.read_csv(path, sep=sep, parse_dates=times_series,
						  index_col=[0,1])
		col.sort_index(0, inplace=True)
		col = col[col.columns[0]]
	
	col.name = var_name
	return col

def load_index(path, times_series):
	'''
	Function used to load a index 
		
	Parameters
	----------
	path : {string type}
		   Path to a csv or a directory
	
	var_name : {string type}
			   Name of a column or a csv
	
	times_series : {bool type} optional, default False
				   Option to parse dates
	
	Return
	------
	return : {pandas Serie type}
	'''
	sep = find_delim(path)
	index_mat = pd.read_csv(path, index_col = [0],
							sep=sep, parse_dates=times_series)

	#To convert stock name in str
	col_name = index_mat.columns[0]
	index_mat[col_name] = index_mat[col_name].astype('str')

	index_mat.set_index(keys=col_name, append=True, inplace=True)
	index_mat.sortlevel([0, 1], inplace=True)

	return index_mat

def apply_index(xcol, index):
	'''
	Function used to apply an index to xcol
		
	Parameters
	----------
	xcol : {pandas Series, pandas DataFrame type}
		   Data
		   
	index : {pandas Series}
			The index Series
	
	Return
	------
	return : {pandas Series, pandas DataFrame type}
			 The indexed data
	'''
			
	col_name = xcol.name
	index[col_name] = np.NaN
		
	index.update(xcol) 
	indexed_col = index[col_name]
		
	return indexed_col
	
def take_interval(xcol, dtend=None, dtstart=None):
	'''
	Function used to take an interval of xcol
		
	Parameters
	----------
	xcol : {pandas Series, pandas DataFrame type}
		   Data
		   
	dtend : {string or timestamp type}
			the first date not included in the data
			
	dtstart : {string or timestamp type}
			  the first date included in the data
			  
	Return
	------
	return : {pandas Series, pandas DataFrame type}
			 The data in the good range of time
	'''
	is_multiIndex = isinstance(xcol.index, pd.core.index.MultiIndex)
	if is_multiIndex:
		first_index = xcol.index.get_level_values(0)
	else:
		first_index = xcol.index
	
	if len (xcol.index) == 0:
		warnings.warn('xcol is empty')
		return xcol
	
	if dtstart is None or dtstart =='':
		dtstart = first_index[0]
	elif type(first_index[0]) == pd.tslib.Timestamp:
		dtstart = pd.to_datetime (dtstart)
	
	if dtend is None or dtend =='':
		dtend = first_index[-1]
	elif type(first_index[-1]) == pd.tslib.Timestamp:
		dtend = pd.to_datetime (dtend)
		
	if (dtstart <= first_index[0]) and (dtend >= first_index[-1]):
		warnings.warn('The chosen period is bigger or equal than the %s variable' 
					%xcol.name)
		return xcol
	else:
		if is_multiIndex:
			xcol = xcol.loc[xcol.index.get_level_values(0) < dtend]
			xcol = xcol.loc[xcol.index.get_level_values(0) >= dtstart]
		else:
			xcol = xcol.loc[xcol.index < dtend]
			xcol = xcol.loc[xcol.index >= dtstart]
		
		return xcol

def get_nb_assets(serie):
	'''
	Function used to get the number of stock
	
	Parameters
	----------
	serie : {pandas Series or pandas DataFrame}
			Data with or without multiindex
	
	Return
	------
	return : The number of stocks
	'''
	if isinstance(serie.index, pd.core.index.MultiIndex) is False:
		return 1
	else:
		return int(len(set(serie.index.levels[1])))

def get_time_index(serie):
	'''
	Function used to get the time index for a multiindex serie
		
	Parameters
	----------
	serie : {pandas Series or pandas DataFrame}
			Data with or without multiindex
	
	Return
	------
	time_index : {list type}
				 The list of unique sorted date
	'''
	if isinstance(serie.index, pd.core.index.MultiIndex):
		time_index = list(set(serie.index.levels[0]))
		time_index.sort()
	else:
		time_index = serie.index
	
	return time_index