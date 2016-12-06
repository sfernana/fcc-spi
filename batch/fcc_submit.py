#!/usr/bin/env python


#******************** SOFTWARE INFORMATIONS ********************************#
#                                                                           #
#                       Property of CERN                                    #
#                                                                           #
#    EP-SFT Group (Experimental Physics - SoFTware)                         #
#                                                                           #
#    Simplified Submission Script for using Batchs systems                  #
#    at CERN.                                                               #
#                                                                           #
#    FCC group can use it to run jobs on LXBatch.                           #
#                                                                           #
#    This script provides a simple interface for the submission             #
#    of jobs on HTCondor or LSF :                                           #
#                                                                           #
#    -> A simple way to submit a job :                                      #
#    ie. python fcc_submit.py --exec executable --conf configuration_file   #
#                                                                           #
#    For more information, please contact us                                #
#    at fcc-experiments-sw-devATSPAMNOTcern.ch                              #
#                                                                           #
#***************************************************************************#



#******************************* libraries importation ******************************#

#standard libraries
import argparse
import subprocess
import getpass
import shutil
import os

#user libraries
import fcc_file_system as filesys

#create instance of FileSystem Class 
#cli and gui can access on it like a 'global' script
#because they use the same functions
my_file_sys = filesys.FileSystem()

#************************************* Functions Definition ***********************************#


#***********************************#
# Function name : parser            #
# input : arguments of the "main"   #
# fcc_submit.py script              #
# role : parse arguments, save      #
# executable and other arguments    #    
# in a 'configuration' dictionnary  #
#***********************************#

def parser():


    #some functions like 'custom_print' do not have the same behaviour according to the chosen interface (cli or gui)
    #so set the interface type as cli at the beginning     
    
    my_file_sys.interface = 'cli'

    
    #parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--bh", "--bsubh", action="store_true",dest="bsub_help",help="The help of 'bsub' command.")
    parser.add_argument("--ch", "--condorh", action="store_true",dest="condor_submit_help",help="The help of 'condor_submit' command.")
    parser.add_argument("--exec", "--executable", action="store",dest="fcc_executable",help="The executable you want to use ie. FCCSW,FCCPHYSICS...")
    parser.add_argument("--conf", action="store",dest="fcc_conf_file",help="The configuration file you want to use.")             
    parser.add_argument("--ifiles", action="store",dest="fcc_input_files",nargs='*',type=str,default="",help="The input files the job needs ie. --ifiles file1 file2 file3 ...")
    parser.add_argument("--ofile", action="store",dest="fcc_output_file",default="",help="The output file you want to create.")
    parser.add_argument("--outdir", action="store",dest="outdir",default="",help="The output directory of your results")
    parser.add_argument("--spec", "--specification", action="store",dest="import_file",help="Import a job specification.")
    parser.add_argument("--sa", "--save", action="store",dest="save_file",help="Save the current job specification.")    
    parser.add_argument("-o", "--out", action="store",dest="stdout",default="",help="The directory of the standard output.")
    parser.add_argument("-e", "--err", action="store",dest="stderr",default="",help="The directory of the standard error.")
    parser.add_argument("-l", "--log", action="store",dest="log",default="",help="The directory of the log.")
    parser.add_argument("--batch", action="store",dest="batch",default="htcondor",help="The Batch System you want to use.")
    parser.add_argument("--gui", action="store_true",dest="gui",help="Launch the GUI Interface")
    parser.add_argument("-N", action="store",dest="number_of_events", default="", help="Number of events you want to generate")
    parser.add_argument("--runs", action="store",dest="number_of_runs",default="",help="The number of runs you want.")
    parser.add_argument("--hist","--history", action="store",dest="history",nargs='*',type=str,help="history of all submissions, ie --hist 2 (the last 2 jobs), --hist 11/21/2016 08:00:00 11/22/2016 08:00:00 (2 days history), --hist 10 20 (jobs from the 10th until 20st), --hist 11/21/2016 13:00:00 (all jobs from this date and time)")
    parser.add_argument("--more", action="store_true",dest="more",default=False,help="more detailled history, ie --hist 2 --more (detailled history of the last 2 jobs)")     
    parser.add_argument("--bhist","--bhistory", action="store_true",dest="lsf_history",help="history of your lsf submissions")
    parser.add_argument("--chist","--chistory", action="store_true",dest="condor_history",help="history of your condor submissions")
    parser.add_argument("--bstat","--bjobs", action="store_true",dest="lsf_status",help="Display the status of your lsf jobs")
    parser.add_argument("--cstat","--condor_q", action="store_true",dest="condor_status",help="Display the status of your condor jobs")
    parser.add_argument("--brm","--bremove", action="store",dest="bremove",help="Remove a specific lsf job ID")
    parser.add_argument("--crm","--cremove", action="store",dest="cremove",help="Remove condor job(s) given ID or ClusterID or username")
    parser.add_argument("--dbg","--debug", action="store_true",dest="debug",help="Debug a condor job")
    parser.add_argument("--cl","--clean", action="store_true",dest="clean",help="Clean the FCC_SUBMIT folder of this script")
    parser.add_argument("--resubmit" , action="store",dest="resubmit",help="Resubmit condor job(s) given ID or ClusterID or username")


    #we catch unknown arguments
    #in addition to the previous arguments, user can send supplementary arguments 
    #if he knows the arguments related to bsub or condor_submit command
    #specific batch subargments are : (ie. -J job_name (for bsub) or -pool pool_name (for condor_submit))
    args, unknown_args = parser.parse_known_args()
    
    #if gui is chosen, launch directly gui without parsing other cli arguments
    if args.gui:
        return 'gui'
    if args.bsub_help :
        #call create a child process of this script
        p = subprocess.call('bsub -h',shell=True)
        quit() 
    elif args.condor_submit_help :
        p = subprocess.call('condor_submit -h',shell=True)
        quit()
    elif args.condor_status :
        print "\n--------------------------------------CONDOR STATUS----------------------------------\n"
        p = subprocess.call('condor_q')
        print "\n--------------------------------------CONDOR STATUS----------------------------------\n"
        quit()
    elif args.lsf_status :
        print "\n---------------------------------------LSF STATUS-------------------------------------\n"
        p = subprocess.call('bjobs')
        print "\n---------------------------------------LSF STATUS-------------------------------------\n"
        quit()
    elif None != args.history :
        print "\n---------------------------------------FCC_SUBMIT HISTORY------------------------------------\n"
        my_file_sys.display_history(args.history,args.more)
        print "\n---------------------------------------FCC_SUBMIT HISTORY------------------------------------\n"
        quit()
    elif args.condor_history :
        print "\n---------------------------------------CONDOR HISTORY------------------------------------\n"
        username = getpass.getuser()
        p = subprocess.call('condor_history ' + username,shell=True)
        print "\n---------------------------------------CONDOR HISTORY------------------------------------\n"
        quit()
    elif args.lsf_history :
        print "\n---------------------------------------LSF HISTORY-----------------------------------\n"
        p = subprocess.call('bhist')
        print "\n---------------------------------------LSF HISTORY-----------------------------------\n"
        quit()
    elif None != args.cremove :
        print "\n---------------------------------------CONDOR JOB DELETION-----------------------------------\n"
        p = subprocess.call('condor_rm ' + args.cremove ,shell=True)
        print "\n---------------------------------------CONDOR JOB DELETION-----------------------------------\n"
        quit()
    elif None != args.bremove :
        print "\n---------------------------------------LSF JOB DELETION-----------------------------------\n"
        p = subprocess.call('bkill ' + args.bremove ,shell=True)
        print "\n---------------------------------------LSF JOB DELETION-----------------------------------\n"
        quit()
    elif args.debug :
        print "\n---------------------------------------CONDOR JOB DEBUGGING-----------------------------------\n"
        p = subprocess.call('condor_q -analyse -better',shell=True)
        print "\n---------------------------------------CONDOR JOB DEBUGGING-----------------------------------\n"
        quit()
    elif args.clean :
        print "\n---------------------------------------CLEANING FCC_SUBMIT FOLDER-----------------------------------\n"
        batch_folder = os.getcwd()+ '/FCC_SUBMIT'        
        if os.path.isdir(batch_folder):    
            shutil.rmtree(batch_folder)
            print "The FCC_SUBMIT folder has been deleted"
        else:
            print "The FCC_SUBMIT folder has already been deleted"

        print "\n---------------------------------------CLEANING FCC_SUBMIT FOLDER-----------------------------------\n"
        quit()
    elif None != args.resubmit :
        print "\n---------------------------------------CONDOR JOB RESCHEDULING------------------------------------\n"
        p = subprocess.call('condor_release ' + args.resubmit,shell=True)
        print "\n---------------------------------------CONDOR JOB RESCHEDULING------------------------------------\n"
        quit()
    elif None != args.import_file :

        print "\n---------------------------------------SPECIFICATION LOADING------------------------------------\n"

        file = args.import_file     
    
        if os.path.exists(file):        

            specification = my_file_sys.import_specification(file)

            if False is not specification :

                [chosen_batch, fcc_executable, fcc_conf_file ,fcc_output_file, NOR , NOE , fcc_input_files ,batch_original_arguments, stdout, stderr, log, outdir] = specification


                #when specification file is loaded
                #possibility to overwrite some arguments (not the batch for the moment)
                    
                
                fcc_executable = fcc_executable if None is args.fcc_executable else args.fcc_executable
                fcc_conf_file = fcc_conf_file if None is args.fcc_conf_file else args.fcc_conf_file
                fcc_output_file = fcc_output_file if "" is args.fcc_output_file else args.fcc_output_file
                NOR = NOR if "" is args.number_of_runs else args.number_of_runs
                NOE = NOE if "" is args.number_of_events else args.number_of_events


                batch_original_arguments = batch_original_arguments if not unknown_args else " ".join(map(str,unknown_args))

                fcc_input_files = fcc_input_files if "" is args.fcc_input_files else args.fcc_input_files
                stdout = stdout if "" is args.stdout else args.stdout
                stderr = stderr if "" is args.stderr else args.stderr
                log = log if "" is args.log else args.log
                outdir = outdir if "" is args.outdir else args.outdir
            

                print "You loaded the following specification from the file '" + file + "' :\n"
            
                spec = ["Batch : "+chosen_batch]
                spec +=["Executable : "+fcc_executable]
                spec +=["Configuration file : "+fcc_conf_file]
                spec +=["Output file : "+fcc_output_file]
                spec +=["Number of runs : "+NOR]
                spec +=["Number of events : "+NOE]
                spec +=["Input files :\n"+'\n'.join(fcc_input_files)]
                spec +=["Batch original arguments : "+batch_original_arguments]
                spec +=["Stdout : "+stdout]
                spec +=["Stderr : "+stderr]
                spec +=["Log : "+log]
                spec +=["Output directory : "+outdir]

                print '\n'.join(spec) + '\n'

                yes = set(['yes','y', 'ye', ''])

                answer = raw_input('Is this specification satisfies you ? (y/n)').lower()
                
                if answer not in yes:
                    my_file_sys.custom_print('Error','Importation of the specification aborted',True)                    
           
        else:
            print "The file " + file + " does not exist"
            print "\n---------------------------------------SPECIFICATION LOADING------------------------------------\n"
            quit()
                
        print "\n---------------------------------------SPECIFICATION LOADING------------------------------------\n"

    else:
    
    
        #no specification imported, so we take arguments given in the command
        chosen_batch = args.batch
        fcc_executable = args.fcc_executable
        fcc_conf_file = args.fcc_conf_file
        fcc_output_file = args.fcc_output_file
        NOR = args.number_of_runs
        NOE = args.number_of_events
        fcc_input_files = args.fcc_input_files
        batch_original_arguments = " ".join(map(str,unknown_args)) 
        stdout = args.stdout
        stderr =  args.stderr
        log =  args.log
        outdir =  args.outdir
        


    #**************************************************MINIMUM REQUIREMENTS CHECKING*******************************************************#
    if None==fcc_executable or None==fcc_conf_file:
        print "\nYou have to provide at least an executable and a configuration file, please refer to the usage of this script :\n"
        parser.print_help()
        quit()      
    #**************************************************MINIMUM REQUIREMENTS CHECKING*******************************************************#


    if None != args.save_file :
        print "\n---------------------------------------SPECIFICATION SAVING------------------------------------\n"
        file = args.save_file
        specification_values = [chosen_batch, fcc_executable, fcc_conf_file, fcc_output_file, NOR, NOE, ' '.join(fcc_input_files),batch_original_arguments,stdout,stderr,log,outdir]
        my_file_sys.save_specification(specification_values,file)

        print "The current specification has been saved in the file " + file
        print "\n---------------------------------------SPECIFICATION SAVING------------------------------------\n"

          
    specification = {}

    #mandatory keys and batch default value is htcondor    

    specification['batch'] = chosen_batch
    my_file_sys.chosen_batch = chosen_batch
       
    specification['number_of_events'] = NOE
    specification['fcc_executable'] = fcc_executable 
    specification['fcc_conf_file'] = fcc_conf_file
    

    #not mandatory, by default ''

    specification['fcc_output_file'] = fcc_output_file
    specification['fcc_input_files'] = fcc_input_files 
    specification['stdout'] = stdout 
    specification['stderr'] = stderr
    specification['log'] = log  
    specification['outdir'] = outdir 

    #by default number of runs is 1

    specification['number_of_runs'] = NOR
    specification['batch_original_arguments'] = batch_original_arguments

    #print batch_original_arguments

    return specification

#*******************************************#
# Function name : launchCLI                 #
# input : arguments of the "main"           #
# fcc_submit.py script                      #
# role : get the specification of           #
# the submission from the parser            #
# method and send it to                     #
# the final submission "level" : fcc_batch  #
#*******************************************#

def launchCLI():

    
    #get the specification from the argument parser
    specification = parser()
    #print specification

    #at this point, after 'routines' checking done, we check fcc environnement 
    my_file_sys.init_fcc_stack()
    
    #if the option "gui" is chosen, launch the GUI
    if 'gui' == specification:
        #we do not import at the beginning else it will import tk libraries
        #and maybe they will be not used if cli is chosen    
        #so import gui packages only when gui is asked

        try:    
            import fcc_submit_gui
        except ImportError as e:
            #if packages are not available print installation error
            #error raised by fcc_submit_gui , check this script to see the content of e
            print e
            quit()
            
        #if gui is ready, we set the current interface type    
        my_file_sys.interface = 'gui'    
        
        #we launch the gui
        fcc_submit_gui.launchGUI(my_file_sys)
        
    else:
        #if gui is not chosen, we submit the specification from argument parser       
        #user libraries
        import fcc_batch as batch
        batch.submit_bash(my_file_sys,specification)


#********************************** MAIN **************************************#

launchCLI()    





