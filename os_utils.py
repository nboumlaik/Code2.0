'''
os_utils includes all functions that could be useful to the os management
'''
import os
import sys
import glob
import psutil

def suppress_all_files(dir_path):
	'''
	Function used to suppress all files in the directory
	and also all files in all sub-directories.
	
	Parameters
	----------
	dir_path : {string type}
			   Absolute path of the parent directory
	'''
	
	#We get the list of all files and subdirectories in the dir_path
	#Control the syntax of dir_path
	if dir_path[-1] == '/':
		file_list = glob.glob(dir_path + '*')
	else:
		file_list = glob.glob(dir_path + '/*')
	
	for f in file_list:
		if os.path.isfile(f):
			#Remove the file f
			os.remove(f)
		elif os.path.isdir(f):
			#suppress_all_files in the directory f
			suppress_all_files(f)
		else:
			#f is neither a file nor a directory 
			print '%s not suppress' %f

def find_dir(dir_name):
	'''
	Function used to find the path of a directory
	
	Parameters
	----------
	dir_name : {string type}
			   the name of the directory

	Return
	------
	return : {string type}
			 Absolute paths to the directory named dir_name

	Example
	-------
	find_directory('Dropbox')
	'''
	
	#Find all disk in the computer
	all_disk = psutil.disk_partitions()
	
	#For each disk...
	for disk in all_disk:
		#... scroll all directories
		for dir_path in os.walk(disk.mountpoint):
			#Test if the good one is found
			if os.path.split(dir_path[0])[-1] == dir_name:
				#Add the path to the list
				path = dir_path[0]
				return path.replace(dir_name,'')
	
	print('Directory %s not fund' %dir_name)
	sys.exit()




