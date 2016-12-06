

#*************************** libraries importation*****************************#

#standard libraries
import subprocess
import time
import os

#********************** Functions Definitions **********************************#



#***********************************#
# Function name : submit_bash       #
# input : specification             #
# role : get specification of the   #
# submission, launch a shell        #
# subprocess and call the command   #
# corresponding to the              #
# selected batch                    #
#***********************************#


        
def submit_bash(my_file_sys, specification):
    

    #if gui problem (i.e invalid number for number of events)
    #is detected, do not quit gui application just do no submit
    #do not 'play' submit stuff, hence this variable
    
    replay = True

    #these 3 first are mandatory or have default values like batch

    chosen_batch = specification['batch']
    fcc_executable = specification['fcc_executable']
    fcc_conf_file = specification['fcc_conf_file']

    #not mandatory, have default values    

    fcc_input_files = specification['fcc_input_files']
    fcc_output_file = specification['fcc_output_file'] 
    batch_original_arguments = specification['batch_original_arguments'] 

    number_of_runs = specification['number_of_runs']
    number_of_events = "-N " + str(specification['number_of_events']) if specification['number_of_events'] != "" else "" 

    #**************************************************MINIMUM REQUIREMENTS CHECKING*******************************************************#



    #check if the executable is in known paths and return its absolute path
    fcc_executable, is_exist = my_file_sys.find_executable(fcc_executable)
    #if executable not found,print fcc error message (or try to install if heppy)
    #for the moment we do not install heppy 'code commented' print just heppy error message
    #try_install do not install, it checks just the environnement, install stuff has been commented
    replay = my_file_sys.try_install(fcc_executable,is_exist)
            
    upload_file_message = " does not exist\nPlease upload your file in an accessible file system (EOS or AFS)\n"
    
    #check if the configuration file exist
    fcc_conf_file , is_exist = my_file_sys.find_path(fcc_conf_file)
    if False == is_exist:
        message = "\nThe file '" + fcc_conf_file + "'" + upload_file_message
        replay =  my_file_sys.custom_print('Error',message,True)

    #do the same for input files...
    if '' != fcc_input_files :
        for file_index,file in enumerate(fcc_input_files):
            fcc_input_files[file_index], is_exist = my_file_sys.find_path(file)
            if False == is_exist:
                message = "\nThe file '" + file + "'" + upload_file_message
                replay = my_file_sys.custom_print('Error',message,True)


    #check if output folders provided by the user exist
    stdout = specification['stdout']
    stderr = specification['stderr']
    log = specification['log']
    outdir = specification['outdir']


    upload_folder_message = " does not exist\nPlease ensure that your folder exist in an accessible file system (EOS or AFS)\n"
    
    if '' != stdout :
            stdout , is_exist = my_file_sys.find_path(stdout,'dir')
            if False == is_exist: 
                message = "\nThe folder '" + stdout + "'" + upload_folder_message
                replay = my_file_sys.custom_print('Error',message,True)
            
    if '' != stderr :   
            stderr , is_exist = my_file_sys.find_path(stderr,'dir')
            if False == is_exist:
                message = "\nThe folder '" + stderr + "'" + upload_folder_message
                replay = my_file_sys.custom_print('Error',message,True)
            
    if '' != log :
            log , is_exist = my_file_sys.find_path(log,'dir')   
            if is_exist == False:
                message = "\nThe folder '" + log + "'" + upload_folder_message
                replay = my_file_sys.custom_print('Error',message,True)            

    if '' != outdir :
            outdir , is_exist = my_file_sys.find_path(outdir,'dir')
            if False == is_exist:   
                message = "\nThe folder '" + outdir + "'" + upload_folder_message
                replay = my_file_sys.custom_print('Error',message,True)
            
            if outdir.startswith('/afs/'):
                print '\nWARNING : DOWNLOAD FILES ON AFS IS DEPRECATED\n'
    #**************************************************MINIMUM REQUIREMENTS CHECKING*******************************************************#


    #once we checked folders, 
    #if user did not specified output folders, we create default folders
    my_file_sys.set_workspace(stdout,stderr,log,outdir)
    #we get absolute path of folders and additionnals used by the script    
    script_folder, batch_folder, stdout_folder, stderr_folder , log_folder , outdir_folder = my_file_sys.get_workspace()
    
 
    if True is replay:


        #------------------------------------- HTCondor Stuff -------------------------------------------#
        if 'htcondor' == chosen_batch:



            #submite file generation
            submitFile = ['executable = ' + my_file_sys.jobFileName]
            submitFile += ['output = ' + stdout_folder + '/job.$(ClusterId).$(ProcId).out']
            submitFile += ['log = '  + log_folder + '/job.$(ClusterId).$(ProcId).log']
            submitFile += ['error = '  + stderr_folder + '/job.$(ClusterId).$(ProcId).err']
            submitFile += ['send_credential = ' +  'True']
            
        
            
            #file transfer mechanism if needed
            if fcc_input_files != "" :
                submitFile += ['transfer_input_files = ' +  ','.join(fcc_input_files)]
                submitFile += ['should_transfer_files = ' +  'YES']
                submitFile += ['when_to_transfer_output = ' +  'ON_EXIT']

            
            #initialdir is default result folder  
            #eos output folder does not work for the moment  
            submitFile += ['initialdir = ' +  outdir_folder]
            #do not overwrite file, but rename them, attach job id or date and time etc...
            #submitFile += ['transfer_output_remaps = ' + '"' + outdir_folder + '/outputfile.txt=' + outdir_folder + '/outputfile.txt_$(ClusterId).$(ProcId)' + '"' ]


            submitFile += ['queue ' + number_of_runs]
            
            #we create the submitfile used by condor 
            my_file_sys.write2file('w',my_file_sys.submitFileName,'\n'.join(submitFile) + '\n')


            submitCommand = "condor_submit " + my_file_sys.submitFileName + " " + batch_original_arguments    
            status_command = 'python fcc_submit.py --cstat'
            history_command = 'python fcc_submit.py --chist'
            deletion_command = 'python fcc_submit.py --crm'
            
        #------------------------------------- HTCondor Stuff -------------------------------------------#



        #------------------------------------- LSF Stuff -------------------------------------------#
        elif 'lsf' == chosen_batch:


            #lsf bsub redirections
            redirections = " -o " + stdout_folder + '/job.%J.out' + " -e " + stderr_folder + '/job.%J.err'
            
            #in bsub : options before job name
            submitCommand = "bsub" + redirections +" "+ batch_original_arguments +" "+ my_file_sys.jobFileName 
            status_command = 'python fcc_submit.py --bstat'
            history_command = 'python fcc_submit.py --bhist'
            deletion_command = 'python fcc_submit.py --brm'    

        #------------------------------------- LSF Stuff -------------------------------------------#
        
        else:
            my_file_sys.custom_print('Error',"\nThe specified Batch system '" + chosen_batch + "' does not exist\n",True)
            

        #this temporary script is setting up environnement and run job command on the worker node
        #instead of setting up environnement on the worker, an other solution is to do it on the submitted machine as usual
        #and after we transfer the shell envrionnement to htcondor with getenv = True
        
        #tmp job script generation (the same for the 2 batchs)
        bash_commands = [fcc_executable + " " + fcc_output_file  +" " + fcc_conf_file +" "+ number_of_events]

        #generate bash script
        my_file_sys.generate_bash_script(bash_commands,my_file_sys.jobFileName)


        print "submitCommand"
        print submitCommand

    
    
        #shell process (runned from pyhon)
        #run the submit command of the selected batch
        #a new shell process pick even the umask value of python process(tested)
        process = subprocess.Popen(submitCommand,shell=True, stdout=subprocess.PIPE)

        batch_output,batch_error = process.communicate()

        #we pick the batch ouptut and add it to our custom output
        
        batch_output_str = str(batch_output)
        job_id = my_file_sys.get_job_id(batch_output_str)

        #features
        #monitoring files to pick status of jobs without user interaction (condor_q etc..)
        #we can use :
        #polling(cross-platform) method (in a other process), not ideal but :
        #libnotify work on linux only
        #pyinotify work only on linux too but not installed
        #cross-platform best solutions are watchdog and Qmy_file_systemWatcher but not installed on lxplus
        #fcc_file_monitor.py squelleton I wrote :        
        #subprocess.Popen(['python','fcc_file_monitor.py','--files' ,stdout_file_name ,stderr_file_name, '--dirs','output', 'error', '--jobid',job_id ,'--cwd', batchFolder ])
        #or for each call of the history, we read the status given by condor_q command

        #files generated by the batch
        stdout_file = stdout_folder + "/job." + job_id + ".out"  
        log_file = log_folder + "/job." + job_id + ".log"
        error_file = stderr_folder + "/job." + job_id + ".err"
        #outsubdir = outdir_folder + "_" + job_id
        
        #generation of the custom output


        information = ["\n---------------------------------------"+ chosen_batch.upper() +" SUBMISSION------------------------------------\n"]

        information+= ["\nYou are using the " + chosen_batch.upper() + " platform"]
        information+= [batch_output_str]

        information+= ["The global workspace is : " + script_folder]
        information+= ["The results are give back to this folder : " + outdir_folder]        
        information+= ["Default output, log and error subfolders contain informations related to your jobs"]
        
        information+= ["'" + stdout_folder + "' contains the standard ouput of your job"]
        information+= ["'" + stderr_folder + "' contains the standard error of your job"]
        information+= ["'" + log_folder + "' contains the standard log of your job"]

                
        
        if 'gui' == my_file_sys.interface :
              
            information+=["Click on 'Log/Output/Error buttons' to check the informations about your current job"] 
            
        else:    

            information+= ["For example check : " + stdout_file + " to check the standard output of your job"]        
            information+= ["Type '" + status_command + "' to see the status of your jobs"]
            information+= ["Type '" + history_command + "' to see the history of your jobs"]
            information+= ["Type '" + deletion_command + " " + job_id + "' to remove your job\n"]
            
        information+= ["\n---------------------------------------"+ chosen_batch.upper() +" SUBMISSION------------------------------------\n"]

        #we log the submission
        my_file_sys.save_history(job_id, chosen_batch.upper(), time.strftime("%m/%d/%y %H:%M:%S"), fcc_executable,outdir_folder,stdout_file,error_file,log_file)
    
        #we print custom output
        my_file_sys.custom_print('Information','\n'.join(information),True) 

    
def submit_from_python_api():
    print "Condor Python API not available now"
    """        TO DO             """


