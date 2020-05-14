import os
import sys
import shutil

from pintasession import session
import pintautils as utils

def test_dir(folder):
    print_log(session, '[CHECK] Checking directory %s for permissions...'%folder, end=" ")
    if not os.access(folder, os.F_OK):
        print_log(session, "%s does not exist... Quitting..."%folder)
    elif not os.path.isdir(folder):
        print_log(session, "%s is not a directory... Quitting..."%folder)
    elif not os.access(folder, os.R_OK):
        print_log(session, "%s not readable... Quitting..."%folder)
    elif not os.access(folder, os.W_OK):
        print_log(session, "%s not writable... Quitting..."%folder)
    else:
        print_log("OK... ")
        return folder
    raise OSError()
    
def test_read_dir(folder):
    print_log(session, '[CHECK] Checking directory %s for permissions...'%folder, end=" ")
    if not os.access(folder, os.F_OK):
        print_log(session, "%s does not exist... Quitting..."%folder)
    elif not os.path.isdir(folder):
        print_log(session, "%s is not a directory... Quitting..."%folder)
    elif not os.access(folder, os.R_OK):
        print_log(session, "%s not readable... Quitting..."%folder)
    else:
        print_log(session, "OK... ")
        return folder
    raise OSError()
     
def test_input_file(file_path):
    print_log(session, '[CHECK] Checking file %s for permissions...'%file_path, end=' ')
    if not os.access(file_path, os.F_OK):
        print_log(session, "%s does not exist... Quitting..."%file_path)
    elif not os.path.isfile(file_path):
        print_log(session, "%s is not a file... Quitting..."%file_path)
    elif not os.access(file_path, os.R_OK):
        print_log(session, "%s not readable... Quitting..."%file_path)
    else:
        print_log(session, "OK... ")
        return file_path
    raise OSError()

def check_program(program):
    print_log(session, "[CHECK] Checking for %s..."%program, end=" ")
    program_found = shutil.which(program) is not None
    if program_found:
        print_log(session, "OK...")
    else:
        print_log(session, "Not found... Quitting...")
        raise OSError()
    return program_found
