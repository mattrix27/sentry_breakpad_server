#YO YO, so this takes a crash dump from a directory, extracts it need be if it was tarballed, then uses an executable from the breakpad library to turn it into a stacktrace, which is then sent to another script to be parsed

import tarfile
import os

from parse_for_sentry import Breakpad_Sentry_Report

def process_file(pathname, delete = True):
        tar_tar = False
        prefix, filename = os.path.split(pathname)
        prefix += '/'
        print(filename)
        #if its a tar, save the tar file and extract the dump
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

        #Calls the executable, which returns the stack trace as a string
        #NOTICE, when you create a build or something, you should get symbol files, put then in the 'symfiles' folder so this executable can access them. If not, your stack trace might be lacking...
        stack_trace = os.popen('./breakpad_processor/processor/minidump_stackwalk ' + prefix + filename + ' symfiles').read()
        print('hey')
        print(stack_trace)

        ##TODO[OPTIONAL FEATURE]: Look at filename of dump, figure out what project it for and use API to get DSN, or if you want to make a new one, then create a new project/DSN
        #
	DSN = None

        #gets another script and send the stack trace to it in order to be parsed
        report = Breakpad_Sentry_Report()
        report.sentrify(stack_trace, DSN)

        #if you don't want it, deletes the dump for space purpose, defaulted to True
        if delete and tar_tar:
                os.remove(prefix+filename)
        else:
	#if you don't want to delete it, or it was not a tar, move it to the processed folder. This stuff is optional and can easily be commented out if you don't want to store these type of things
                print(pathname)
                os.rename(pathname, 'dump_files/processed/'+filename+'.dmp')

#Random function made if you just want to the above for all the stuff in a folder or something...has not been tested
def process_folder(directory, delete = True):
        for filename in os.listdir(directory):
                process_file(filename)

