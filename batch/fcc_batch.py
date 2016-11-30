

#*************************** libraries importation*****************************#

#standard libraries
import subprocess
import time
import os



#constants
submitFileName = 'user_submit_file.sub'
jobFileName = 'user_temp_job.sh'

#********************** Functions Definitions **********************************#



#***********************************#
# Function name : submit_bash       #
# input : configuration             #
# role : get configuration of the   #
# submission, launch a shell        #
# subprocess and call the command   #
# corresponding to the              #
# selected batch                    #
#***********************************#


        
def submit_bash(my_file_sys, specification):
    

    #if gui problem (i.e invalid number for number of events)
    #is detected, do not quit application just do no submit
    #do not 'play' submit stuff
    
    replay = True

    #these 3 first are mandatory or have default values
    chosen_batch = specification['batch']
    my_file_sys.set_batch(chosen_batch)

    fcc_executable = specification['fcc_executable']
    fcc_conf_file = specification['fcc_conf_file']

    number_of_runs = specification['number_of_runs']
    fcc_input_files = specification['fcc_input_files']

    #**************************************************MINIMUM REQUIREMENTS CHECKING*******************************************************#


    #check if the executable is in known paths
    if not my_file_sys.is_executable_exist(fcc_executable):
        replay = my_file_sys.search_executable(fcc_executable)
            

    #check if the configuration file exist
    if my_file_sys.find_file(fcc_conf_file) == False:
        message = "\nThe file '" + fcc_conf_file + "' does not exist\nPlease upload your file in an accessible file system (EOS or AFS)\n"
        replay =  my_file_sys.custom_print('Error',message,True)

    #do the same for input files...
    if '' != fcc_input_files :
        for file in fcc_input_files:
            if my_file_sys.find_file(file) == False:
                message = "\nThe file '" + file + "' does not exist\nPlease upload your file in an accessible file system (EOS or AFS)\n"
                replay = my_file_sys.custom_print('Error',message,True)


    stdout = specification['stdout']
    stderr = specification['stderr']
    log = specification['log']


    if '' != stdout:   
        if not os.path.isdir(stdout):
            message = "\nThe folder '" + stdout + "' does not exist\nPlease upload your file in an accessible file system (EOS or AFS)\n"
            replay = my_file_sys.custom_print('Error',message,True)
    if '' != stderr:   
        if not os.path.isdir(stderr):
            message = "\nThe folder '" + stderr + "' does not exist\nPlease upload your file in an accessible file system (EOS or AFS)\n"
            replay = my_file_sys.custom_print('Error',message,True)
            
    if '' != log:   
        if not os.path.isdir(log):
            message = "\nThe folder '" + log + "' does not exist\nPlease upload your file in an accessible file system (EOS or AFS)\n"
            replay = my_file_sys.custom_print('Error',message,True)            

    #**************************************************MINIMUM REQUIREMENTS CHECKING*******************************************************#


    #once we obtain folder names, we create them
    my_file_sys.set_workspace(stdout,stderr,log)
        

    number_of_events = "-N " + str(specification['number_of_events']) if specification['number_of_events'] != "" else "" 


    fcc_output_file = specification['fcc_output_file'] 

    
    batch_original_arguments = specification['batch_original_arguments'] 


    result_folder, batch_folder, output_folder, error_folder , log_folder = my_file_sys.get_workspace()    


        
    if replay == True:


        #------------------------------------- HTCondor Stuff -------------------------------------------#
        if chosen_batch == "htcondor":



            #submite file generation
            submitFile_configuration = {}
            submitFile_configuration['executable'] = jobFileName
            submitFile_configuration['output'] = output_folder + '/job.$(ClusterId).$(ProcId).out'
            submitFile_configuration['log'] = log_folder + '/job.$(ClusterId).$(ProcId).log'
            submitFile_configuration['error'] = error_folder + '/job.$(ClusterId).$(ProcId).err'
            submitFile_configuration['send_credential'] = 'True'
            submitFile_configuration['queue'] = str(number_of_runs)
        
            
            #file transfer mechanism if needed
            if fcc_input_files != "" :
                submitFile_configuration['transfer_input_files'] = ','.join(fcc_input_files)
                submitFile_configuration['should_transfer_files'] = 'YES'
                submitFile_configuration['when_to_transfer_output'] = 'ON_EXIT'

        


            submitFileList=[]
            for key, value in submitFile_configuration.iteritems():
                submitFileList += [key +" " + "=" + " " + value] if key != "queue" else [key + " " + value] 


            submitFileText = '\n'.join(submitFileList) + '\n'
            
            my_file_sys.write2file('w',submitFileName,submitFileText)


            submitCommand = "condor_submit " + submitFileName + " " + batch_original_arguments    
            status_command = 'python fcc_submit.py --cstat'
            history_command = 'python fcc_submit.py --chist'
            deletion_command = 'python fcc_submit.py --crm'
            
        #------------------------------------- HTCondor Stuff -------------------------------------------#



        #------------------------------------- LSF Stuff -------------------------------------------#
        elif chosen_batch == "lsf":


            #lsf bsub redirections
            redirections = " -o " + output_folder + '/job.%J.out' + " -e " + error_folder + '/job.%J.err'
            
            #in bsub : options before job name
            submitCommand = "bsub" + redirections +" "+ batch_original_arguments +" "+ jobFileName 
            status_command = 'python fcc_submit.py --bstat'
            history_command = 'python fcc_submit.py --bhist'
            deletion_command = 'python fcc_submit.py --brm'    

        #------------------------------------- LSF Stuff -------------------------------------------#
        
        

        #tmp job script generation (the same for the 2 batchs)
        bash_commands = [fcc_executable + " " + fcc_output_file  +" " + fcc_conf_file +" "+ number_of_events]

        #generate bash script
        my_file_sys.generate_bash_script(bash_commands,jobFileName)


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

        #special features
        #monitoring files to pick status of jobs without user interaction (condor_q etc..)
        #we can use :
        #polling(cross-platform) method (in a other process), not ideal but :
        #libnotify work on linux only
        #pyinotify work only on linux too but not installed
        #cross-platform best solutions are watchdog and Qmy_file_systemWatcher but not installed on lxplus
        #fcc_file_monitor.py squelleton I wrote :        
        #subprocess.Popen(['python','fcc_file_monitor.py','--files' ,stdout_file_name ,stderr_file_name, '--dirs','output', 'error', '--jobid',job_id ,'--cwd', batchFolder ])

        #generation of the custom output

        information = []

        information+= ["\n---------------------------------------"+ chosen_batch.upper() +" SUBMISSION------------------------------------\n"]

        information+= ["\nYou are using the " + chosen_batch.upper() + " platform"]
        information+= [batch_output_str]

        information+= ["The default folder of the script results is : " + result_folder] 
        information+= ["Default output, log and error subfolders contain informations related to your jobs"]
        
        if stdout !='': information+= ["You defined '" + output_folder + "' as the standard ouput of your job"]
        if stderr !='': information+= ["You defined '" + error_folder + "' as the standard error of your job"]
        if log !='': information+= ["You defined '" + log_folder + "' as the standard log of your job"]
        
        interface = my_file_sys.get_interface()
        
        if interface == 'gui':
              
            information+=["Click on 'Log/Output/Error buttons' to check the informations about your current job"] 
            
        else:    

            information+= ["For example check : " + output_folder + "/job." + job_id + ".out to check the standard output of your job"]        
            information+= ["Type '" + status_command + "' to see the status of your jobs"]
            information+= ["Type '" + history_command + "' to see the history of your jobs"]
            information+= ["Type '" + deletion_command + " " + job_id + "' to remove your job\n"]
            
        information+= ["\n---------------------------------------"+ chosen_batch.upper() +" SUBMISSION------------------------------------\n"]

        #we log the submission
        my_file_sys.save_history(job_id, chosen_batch.upper(), fcc_executable, time.strftime("%m/%d/%y %H:%M:%S"))
    
        #we print custom output
        my_file_sys.custom_print('Information','\n'.join(information),True) 

    
def submit_from_python_api():
    print "Condor Python API not available now"
    """        TO DO             """


