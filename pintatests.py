import os
import sys
import shutil

def test_dir(folder):
    print('[CHECK] Checking directory %s for permissions...'%folder, end=" ")
    if not os.access(folder, os.F_OK):
        print("%s does not exist... Quitting..."%folder)
    elif not os.path.isdir(folder):
        print("%s is not a directory... Quitting..."%folder)
    elif not os.access(folder, os.R_OK):
        print("%s not readable... Quitting..."%folder)
    elif not os.access(folder, os.W_OK):
        print("%s not writable... Quitting..."%folder)
    else:
        print("OK... ")
        return folder
    raise OSError()
    
def test_read_dir(folder):
    print('[CHECK] Checking directory %s for permissions...'%folder, end=" ")
    if not os.access(folder, os.F_OK):
        print("%s does not exist... Quitting..."%folder)
    elif not os.path.isdir(folder):
        print("%s is not a directory... Quitting..."%folder)
    elif not os.access(folder, os.R_OK):
        print("%s not readable... Quitting..."%folder)
    else:
        print("OK... ")
        return folder
    raise OSError()
     
def test_input_file(file_path):
    print('[CHECK] Checking file %s for permissions...'%file_path, end=' ')
    if not os.access(file_path, os.F_OK):
        print("%s does not exist... Quitting..."%file_path)
    elif not os.path.isfile(file_path):
        print("%s is not a file... Quitting..."%file_path)
    elif not os.access(file_path, os.R_OK):
        print("%s not readable... Quitting..."%file_path)
    else:
        print("OK... ")
        return file_path
    raise OSError()

def check_program(program):
    print("[CHECK] Checking for %s..."%program, end=" ")
    program_found = shutil.which(program) is not None
    if program_found:
        print("OK...")
    else:
        print("Not found... Quitting...")
    return program_found
