#!/usr/bin/python3
""" Generate and execute commands to reduce the raw uGMRT data into psrfits format.

    Original developer:  Abhimanyu Susobhanan

    Contributing developer: Yogesh Maan

    (included appropriate modules and commands to rfiClean the raw-gmrt-data and
     then generate a rfiCleaned fits file as well.  -- yogesh, July 28)
"""

import shutil
import sys
import os
import numpy as np
import parse
import getopt
import time
import glob
import yaml
import pintautils as utils

from pintasession import session


no_of_observations = len(session.pipeline_items)
 
for i,pipeline_input in enumerate(pipeline_in_data):
    
    psr_start_time = time.time()    
    
    psrj, rawdata_file, timestamp_file, frequency, nbins, nchannels, bandwidth, samplingtime, sideband_, pol_opt, integ_durn = pipeline_input
    print("\nProcessing %s (%d of %d)..."%(psrj,i+1,no_of_observations))

    rawdatafile = '{}/{}'.format(input_dir, rawdata_file)
    timestampfile = '{}/{}'.format(input_dir, timestamp_file)    

    ########################################################################################################

    #= Checking observation files for permissions ==========================================================
    for infile in [rawdatafile, timestampfile]:
        if not utils.check_input_file(infile):
            sys.exit(0)
    
    ########################################################################################################
    
    #= Checking the par file for permissions ===============================================================
    parfile = "%s/%s.par"%(par_dir,psrj)
    if not utils.check_input_file(parfile):
        sys.exit(0)

    ########################################################################################################

    #= Timestamp file =======================================================================================
    print("Processing timestamp file...", end=' ')
    try:
        timestamp_mjd = utils.process_timestamp(timestampfile)
    except Exception as e:
        print("Could not process timestamp file. Quitting...")
        sys.exit(0)
    print("Done.   Timestamp = ", timestamp_mjd)

    #########################################################################################################

    #= Sideband =============================================================================================    
    if sideband_ == 'USB':
        sideband = 'gmgwbf'
    elif sideband_ == 'LSB':
        sideband = 'gmgwbr'
    else:
        print("The given sideband is invalid. Quitting...")
        sys.exit(0)

    #########################################################################################################

    #= Running gptool =======================================================================================
    if run_gptool:
        gpt_start_time = time.time()
        freq_int = utils.choose_int_freq(float(frequency))
        print("Creating %s/gptool.in for frequency %d..."%(working_dir,freq_int),end=' ')
        try:
            gptool_in_src = "%s/gptool.in.%d"%(gptool_in_dir,freq_int)
            gptool_in_dst = "%s/gptool.in"%(working_dir)
            shutil.copy(gptool_in_src,gptool_in_dst)
        except Exception:
            print("Could not create. Quitting...")
            sys.exit(0)
        print("Done.")

        print("Running gptool...")
        cmd = "gptool -f %s -nodedisp -o %s"%(rawdatafile,  working_dir)
        print("cmd :: %s"%(cmd))
        # Run gptool here.
        if not test_run:
            os.system(cmd)
        gptfile = '{}/{}.gpt'.format(working_dir, rawdata_file)
        filterbank_in_file = gptfile
        gpt_stop_time = time.time()
        print("[TIME] Execution time for gptool = ",gpt_stop_time-gpt_start_time)

    else:
        filterbank_in_file = rawdatafile

    #########################################################################################################

    #= Running filterbank ===================================================================================
    fil_start_time = time.time()
    print("Creating filterbank file...")
    #rawdata_size = os.stat(rawdatafile).st_size//(1024**2)
    rawdata_size = os.stat("%s"%(rawdatafile)).st_size//(1024**2)
    out_file_root = "{}.{}.{}.{}M".format(psrj, str(timestamp_mjd), str(frequency), str(rawdata_size))
    fil_file = "{}/{}.fil".format(working_dir, out_file_root) 
    cmd = ("filterbank %s -mjd %0.15f -rf %s -nch %s -bw %s -ts %s -df %s > %s"%(filterbank_in_file,timestamp_mjd,frequency,nchannels,bandwidth,samplingtime,sideband,fil_file))
    print("cmd :: %s"%(cmd))
    # Run filterbank here.
    if not test_run:
        os.system(cmd)
    fil_stop_time = time.time()
    print("[TIME] Execution time for filterbank = ",fil_stop_time-fil_start_time)    

    #########################################################################################################

    #= Delete .gpt file =====================================================================================
    if run_gptool and delete_tmp_files:
        # Now delete gpt file
        print('Removing %s ...'%(filterbank_in_file), end=' ')
        if not test_run:
            try:
                os.remove(gptfile)
                print("Done.")
            except:
                print("Could not delete gpt file.")
        else:
            print('Done.')    
    
    #########################################################################################################

    #= Running dspsr =========================================================================================
    dspsr_start_time = time.time()
    print("Running dspsr...")    
    # This command produces output in the "TIMER" format and "PSRFITS" format.
    # For PSRFITS format use "-a PSRFITS" option. For some reason this fails with a segfault.
    # So we are stuck with the TIMER format for the time being. Need to debug this.
    cmd = "dspsr -N %s -d %s -b %s -E %s -L %s   -A %s -O %s/%s -e fits "%(psrj,pol_opt,nbins,parfile, integ_durn, fil_file, working_dir,out_file_root)
    print("cmd :: %s"%cmd)
    # Run dspsr here
    if not test_run:
        os.system(cmd)
    dspsr_stop_time = time.time()
    print("[TIME] Execution time for dspsr = ", dspsr_stop_time-dspsr_start_time)
    
    #########################################################################################################

    #= Deleting .fil file ===================================================================================
    if delete_tmp_files:
        print("Removing %s ..."%(fil_file), end=' ')
        if not test_run:
            try:
                os.remove(fil_file)
                print("Done.")
            except:
                print("Could not delete fil file.")
        else:
            print('Done.')

    #########################################################################################################
    
    #= Running rfiClean =====================================================================================
    if run_rficlean:
        #= Pulsar frequency and hdr file for rficlean =======================================================    
        print("Trying to get the pulsar's spin frequency...\n")
        try:
            f0psr = utils.fetch_f0(parfile)
        except:
            print("Could not fetch F0 from the parfile. Quitting...")
            sys.exit(0)
        if f0psr<0.0:
            print("could not fetch F0 from the parfile. Quitting...")
            sys.exit(0)
        
        print("Trying to make the rficlean-gmhdr file ...\n")
        if not utils.make_rficlean_hdrfile(("%s/%s-ttemp-gm.info"%(working_dir,psrj)), psrj,frequency,nchannels,bandwidth,samplingtime,sideband_):
            print ("Could not make the rficlean-gmhdr file!")
            sys.exit(0)

        # Now get a rfiCleaned filterbank file
        rficlean_start_time = time.time()
        cleanfil_file = out_file_root+'.rfiClean.fil' 
        Nprocess = 16
        # rfiClean execuable is in /home/ymaan/bin/ .
        #cmd = ("rficlean -t 16384  -ft 6  -st 10  -rt 4  -white  -pcl  -psrf %f  -psrfbins 32  -o %s/%s  -ps %s.rfiClean.ps -gm %s/ttemp-gm.info  -gmtstamp %s/%s   %s/%s"%(f0psr, working_dir,cleanfil_file, out_file_root, working_dir,psrj, input_dir,timestamp_file,  input_dir,rawdatafile))
        #cmd = ('crp_rficlean_gm.sh  %s/%s  /home/ymaan/inpta_pipeline/inpta_rficlean.flags  %d  %s/%s  %s/%s-ttemp-gm.info  "-psrf %f  -psrfbins 32  -gmtstamp %s/%s"'%(working_dir,cleanfil_file,  Nprocess,  input_dir,rawdatafile,   working_dir,psrj,  f0psr,  input_dir,timestamp_file))
        cmd = ('crp_rficlean_gm.sh  %s/%s  %s  %d  %s  %s/%s-ttemp-gm.info  "-psrf %f  -psrfbins 32  -gmtstamp %s"'%(working_dir,cleanfil_file, rfic_conf_file, Nprocess, rawdatafile,  working_dir, psrj,  f0psr, timestampfile))
        print("cmd :: %s"%(cmd))
        # run the command to generate rfiCleaned filterbank file...
        if not test_run:
            os.system(cmd)
        rficlean_stop_time = time.time()
        print("[TIME] Execution time for rfiClean = ", rficlean_stop_time-rficlean_start_time)
        
        # Now generate the rfiClean-ed fits file using dspsr
        dspsr_rc_start_time = time.time()
        print("Running dspsr on rfiCleaned filterbank file...")
        cmd = "dspsr -N %s -d %s -b %s -E %s -L %s   -A %s/%s -O %s/%s.rfiClean -e fits "%(psrj,pol_opt,nbins,parfile, integ_durn, working_dir, cleanfil_file, working_dir,out_file_root)
        print("cmd :: %s"%cmd)
        # Run dspsr here
        if not test_run:
            os.system(cmd)
        dspsr_rc_stop_time = time.time()
        print("[TIME] Execution time for dspsr (rfiClean) = ", dspsr_rc_stop_time-dspsr_rc_start_time)
        # =================================================================================

        if delete_tmp_files:
            # Now delete rfiCleaned filterbank file
            print("Removing %s/%s ..."%(working_dir, cleanfil_file), end=' ')
            if not test_run:
                try:
                    os.remove("%s/%s"%(working_dir, cleanfil_file))
                    print("Done.")
                except:
                    print("Could not delete rfiCleaned filterbank-file.")
            else:
                print('Done.')
    
    #############################################################################################################

    print("Creating summary plots...")
    cmd = "pdmp -mc 64 -g %s/%s_summary.ps/cps %s.fits"%(working_dir, out_file_root, out_file_root)
    print("cmd :: ",cmd)
    if not test_run:
        os.system(cmd)    
    
    if run_rficlean:    
        cmd = "pdmp -mc 64 -g %s/%s.rfiClean_summary.ps/cps %s.rfiClean.fits"%(working_dir, out_file_root, out_file_root)
        print("cmd :: ",cmd)
        if not test_run:
            os.system(cmd)
    # #################################################################################

    print("Processing %s (%d of %d) successful."%(psrj,i+1,no_of_observations))
    
    psr_stop_time = time.time()
    print("[TIME] Total processing time = ", psr_stop_time-psr_start_time)
    
    print('Moving auxiliary output file to aux/ ...')
    aux_dir_i = '{}/{}'.format(aux_dir, i)
    if os.access(aux_dir_i, os.F_OK):
        shutil.rmtree(aux_dir_i)
    os.mkdir(aux_dir_i)
    aux_files_wcards = ['b*.gpt','log.gpt', 'gptool.*', 'stats.gpt', 'J*.info', 'pdmp.*', 'rfiClean_ps']
    aux_files = sum(map(glob.glob, aux_files_wcards), [])
    for aux_file in aux_files:
        shutil.move(aux_file, aux_dir_i)

print("Process finished.")
#print("Removing lock file...")
#os.remove(lockfile)
