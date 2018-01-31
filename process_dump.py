import tarfile
import os

from parse_for_sentry import Breakpad_Sentry_Report

def process_file(pathname, delete = True):
	tar_tar = False
	prefix, filename = os.path.split(pathname)
	prefix += '/'
	print(filename)
	if tarfile.is_tarfile(pathname):
		
		file = tarfile.open(pathname)
		try:
			print(filename)
			file.extractall(prefix)
			filename = file.getnames()[0]
			os.rename(pathname, 'dump_files/processed/'+filename)
			tar_tar = True
		except:
			pass
	stack_trace = os.popen('./breakpad_processor/processor/minidump_stackwalk ' + prefix + filename + ' symfiles').read()
	print('hey')
	print(stack_trace)
	report = Breakpad_Sentry_Report()
	report.sentrify(stack_trace)
	if delete and tar_tar:
		os.remove(prefix+filename)
	else:
		print(pathname)
		os.rename(pathname, 'dump_files/processed/'+filename+'.dmp')

def process_folder(directory, delete = True):
	for filename in os.listdir(directory):
		process_file(filename)