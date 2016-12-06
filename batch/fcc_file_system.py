

#************************** libraries importation **************************#

#standard libraries
import os
import re
import subprocess
import sys
import stat
import getpass
import shutil
import datetime 
import json        
from operator import itemgetter
                
#Xrootd python api used for eos
from XRootD import client
from XRootD.client.flags import DirListFlags, OpenFlags, MkDirFlags, QueryCode



#**************************************#
# Class name : FileSystem              #
# input : none                         #
# role : global class mainly used for  #
# 'file/filesystem' operations         #
#**************************************#

class FileSystem():



    def __init__(self):
    
        #constants

        #default fccsw environnement printed to the user as 'help' if environnement is not set
        HARD_CODED_SOFTWARE_PATH_AFS = "/afs/cern.ch/exp/fcc/sw/0.7"
        self.sourcingFCCStack = 'source ' + HARD_CODED_SOFTWARE_PATH_AFS + '/init_fcc_stack.sh'
        self.fccsw_sourcing_message = "\nPlease ensure that you set up correctly your environnement in order to use FCC softwares ie.: \n" + self.sourcingFCCStack + '\n'


        #default HEPPY environnement

        #default heppy environnement printed to the user as 'help' if environnement is not set
        username = getpass.getuser()
        initial = username[0]

        self.HARD_CODED_HEPPY_PATH_AFS="/afs/cern.ch/user/"+initial+"/"+username+"/heppy" 
        self.sourcingHEPPY = 'source ' + self.HARD_CODED_HEPPY_PATH_AFS + '/init.sh'
        self.heppy_sourcing_message = "\nPlease ensure that you set up correctly your environnement in order to use HEPPY software ie.: \n" + self.sourcingHEPPY + '\n'
        self.setHEPPY = ''

        #workspace
        self.stdout_folder = ''
        self.stderr_folder = ''
        self.log_folder = ''
        self.batch_folder = ''
        self.outdir_folder = ''
        
        self.current_job_id = ''

        #pwd
        self.cwd = os.getcwd()

        #default script working directory
        self.script_folder = self.cwd + '/FCC_SUBMIT/'

        #default log of the script
        self.log_file_name = self.script_folder + 'fcc_submit_log.json'
        
        #default batch files
        self.submitFileName = self.script_folder + 'user_submit_file.sub'
        self.jobFileName = self.script_folder + 'user_temp_job.sh'

        #eos location
        self.EOS_MGM_URL= 'root://eospublic.cern.ch'
        #eos environnement
        self.setEOS = 'export EOS_MGM_URL=' + self.EOS_MGM_URL
        self.myclient = client.FileSystem(self.EOS_MGM_URL + ':1094')

    #************************************* Functions Definition ***********************************#



    #***************************************#
    # Function name : init_fcc_stack        #
    # input : none                          #
    # role : look for the fcc environnement #
    # before running the script             #
    #***************************************#

    def init_fcc_stack(self):

        #FCCSW environement
        try:
            SOFTWARE_PATH_AFS=os.environ["FCCSWPATH"]
            self.sourcingFCCStack = 'source ' + SOFTWARE_PATH_AFS + '/init_fcc_stack.sh'

        except:
            #print default path of source script as 'help'
            print self.fccsw_sourcing_message
            quit()
            
    #*****************************************#
    # Function name : init_heppy              #
    # input : none                            #
    # role : look for the heppy environnement #
    # before running the script               #
    #*****************************************#


    def init_heppy(self,executable):

        #HEPPY environement
        try:
            HEPPY_PATH_AFS=os.environ["HEPPY"]
            self.setHEPPY = 'export HEPPY=' + HEPPY_PATH_AFS
            return True
        except:
            return self.custom_print('Error',self.heppy_sourcing_message,True)
            #for the moment do no install, print error message which says : 'set heppy environnement'
            #return self.install_software(executable)
            

       
       
       
    #*****************************************#
    # Function name : mkdir                   #
    # input : folder                          #
    # role : used to create default folder of #
    # the script if they are not existing     #
    #*****************************************#
    
        
    def mkdir(self,folder_name):
    
        #because sometimes condor output error like : 'file not writtable'
        
        #umask stuff may not be necessary
            
        #default permission for folder creation
        old_mask = os.umask(0)
        #a second call to change the default permissions (0 similar to chmod 777)
        #like that condor,etc... can write on files ??
        os.umask(0)
        
        try:
            
            #if the folder exist do not overwrite it
            #so check if it exist

            if not os.path.isdir(folder_name):
                os.makedirs(folder_name)
        except OSError, e:
            raise    


    #********************************************#
    # Function name : set_workspace              #
    # input : folder names                       #
    # role : create default folders of           #
    # the script and not user folders            #
    # user folders are only checked and if they  #
    # do not exist, script prints error message  #
    #********************************************#

    def set_workspace(self,stdout,stderr,log,outdir_folder):
        
         
        #script default subfolder
        self.batch_folder = self.script_folder + self.chosen_batch.upper()
        self.mkdir(self.batch_folder)

        #create only default subfolders if user did not specified output folders
        if "" == stdout:
            self.stdout_folder = self.batch_folder + '/output'
            self.mkdir(self.stdout_folder)
        else:
            self.stdout_folder = stdout
            
        if "" == stderr:
            self.stderr_folder = self.batch_folder + '/error'
            self.mkdir(self.stderr_folder)
        else:
            self.stderr_folder = stderr
            
        if "" == log:
            self.log_folder = self.batch_folder + '/log'
            self.mkdir(self.log_folder)
        else:
            self.log_folder = log
            
        if "" == outdir_folder:
            self.outdir_folder = self.batch_folder + '/results'
            self.mkdir(self.outdir_folder)
        else:
            self.outdir_folder = outdir_folder
        

    #*****************************************#
    # Function name : get_workspace           #
    # input : folder names                    #
    # role : return user/default folders      #
    #*****************************************#
        

    def get_workspace(self):  
     return self.script_folder, self.batch_folder, self.stdout_folder, self.stderr_folder, self.log_folder, self.outdir_folder

    #*************************************************#
    # Function name : XRootDStatus2Dictionnary        #
    # input : xroot status                            #
    # role : parse status object generated by         #
    # xrootd                                          #
    #*************************************************#


    def XRootDStatus2Dictionnary(self,XRootDStatus):

        start = '<'
        end = '>'

        XRootDStatus2str = str(XRootDStatus)
        s = XRootDStatus2str


        #print XRootDStatus
        #check the expected line
        try:
            
            status_str = re.search('%s(.*)%s' % (start, end), s).group(1)
            
            #print status_str
        
            status_list = status_str.split(",")

            status_dict = {}

            #print status_list
   
            #== 2 , ensure that split result to a (key,value) format for the dictionnary
            status_dict = dict(  (info.split(': ')) for info in status_list if ':' in info and len(info.split(': '))==2)

            return status_dict    
        except:
            return self.custom_print('Error',"Path error, please enter a valid path",True) 
            



    #*************************************************#
    # Function name : find_eos_file                   #
    # input : file_name                               #
    # role : check if file exists on eos              #
    # before sending the job to the worker            #
    #*************************************************#


    def find_eos_file(self,file_name):
        #then the file is in eos


        eos_file_full_path = self.EOS_MGM_URL + '/' + file_name

        with client.File() as eosFile:
            file_status = eosFile.open(eos_file_full_path,OpenFlags.UPDATE)


        #problem with file created directly on eos
        #no problem with uploded files with xrdcp cmd

        #print eos_file_full_path
        #print file_status
        status = self.XRootDStatus2Dictionnary(file_status)

        if 'False' == status[' ok'] or False == status:
            return file_name,False
        else:
            return eos_file_full_path,True

    #*************************************************#
    # Function name : find_eos_folder                 #
    # input : folder_name                             #
    # role : check if folder exists on eos            #
    # before sending the job to the worker            #
    #*************************************************#


    def find_eos_folder(self,folder_name):
        #then the file is in eos
        
        eos_folder_full_path = self.EOS_MGM_URL + '/' + folder_name

        status, listing = self.myclient.dirlist(folder_name, DirListFlags.STAT)
   
        if None == listing:
            return folder_name,False 
        else:
            return  eos_folder_full_path,True       
   
    


    #*************************************************#
    # Function name : find_path                       #
    # input : file_name                               #
    # role : check if file/folder exists on afs       #
    # before checking on eos                          #
    #*************************************************#

    def find_path(self,path,file_or_dir='file'):
        
        

        #we suppose that the user enter absolute or relative afs path
        #or only absolute eos path

        if not path.startswith('/eos/'):
        #afs path are absolute or relative
        #because software are stored in this filesystem
        #and users generally submit their job from lxplus

            
            #absolute path provided
            #os.isabs not cross platform
            #i used startwith...
            if path.startswith('/afs/') and os.path.exists(path):
                return os.path.abspath(path), True
            #if relative (does not start with /afs/)
            #add cwd    
            elif os.path.exists(os.path.abspath(path)):            
                return os.path.abspath(path), True
            #maybe local user machine, print upload error message    
            else:
                return path,False

        #absolute path
        elif path.startswith('/eos/'):
            #print "the file is in eos"        
            
            #eos path are absolute
            
            if 'file' == file_or_dir:
                return self.find_eos_file(path)
            else:
                return self.find_eos_folder(path) 
            
        else:#other file system
            return path,False


    #*******************************************************#
    # Function name : import_specification                  #
    # input : file_name                                     #
    # role : import specification from a file               #
    # a specification file store arguments of the command   #
    #*******************************************************#


    def import_specification(self,file_name):


            imported_specification = self.load_json(file_name)

            if False is not imported_specification :
    
                #print imported_specification

                chosen_batch = imported_specification['chosen_batch'] if 'chosen_batch' in imported_specification else ''
                fcc_executable = imported_specification['executable'] if 'executable' in imported_specification else ''
                fcc_conf_file = imported_specification['fcc_conf_file'] if 'fcc_conf_file' in imported_specification else ''
                fcc_output_file = imported_specification['fcc_output_file'] if 'fcc_output_file' in imported_specification else ''
                NOR = imported_specification['number_of_runs'] if 'number_of_runs' in imported_specification else ''
                NOE = imported_specification['number_of_events'] if 'number_of_events' in imported_specification else ''
                temp_fcc_input_files = imported_specification['fcc_input_files'] if 'fcc_input_files' in imported_specification else ''
                fcc_input_files = temp_fcc_input_files.split(' ') if temp_fcc_input_files != '' else ''


                batch_original_arguments = imported_specification['batch_original_arguments'] if 'batch_original_arguments' in imported_specification else ''
                stdout = imported_specification['stdout'] if 'stdout' in imported_specification else ''
                stderr = imported_specification['stderr'] if 'stderr' in imported_specification else ''
                log = imported_specification['log'] if 'log' in imported_specification else ''
                outdir = imported_specification['outdir'] if 'outdir' in imported_specification else ''
                

                return [chosen_batch, fcc_executable, fcc_conf_file ,fcc_output_file, NOR , NOE , fcc_input_files ,batch_original_arguments, stdout, stderr, log, outdir]

            else:
                return self.custom_print('Error',"Invalid specification file !",True)


    #*******************************************************#
    # Function name : save_specification                    #
    # input : file_name                                     #
    # role : save spec in the specified file                #
    # a specification file store arguments of the command   #
    #*******************************************************#

    def save_specification(self,specification_values,file_name):

        specification_keys = ['chosen_batch', 'executable', 'fcc_conf_file', 'fcc_output_file', 'number_of_runs', 'number_of_events', 'fcc_input_files', 'batch_original_arguments', 'stdout', 'stderr', 'log','outdir']

        specification_dict = {}

        for key,value in zip(specification_keys,specification_values):
            specification_dict[key] = value

        if False is self.save_json(specification_dict,file_name):
            self.custom_print('Error','Error in saving specification',False)

        

    #************************************#
    # Function name : write2file         #
    # input : file_name and its content  #
    # role : write the content in a file #
    #************************************#

    def write2file(self,operation,file_name,filetext):

        try:

            #create file with w permission
            with open(file_name,operation) as text_file:
                text_file.write(filetext)
        except:
             self.custom_print('Error','Error in writting file',True)    
        
        
    #********************************************#
    # Function name : read_from_file             #
    # input : file_name                          #
    # role : read a file and return its content  #
    #********************************************#

    def read_from_file(self,file_name):

        try:
            
            with open(file_name, 'r') as f:
                content = f.read()
            return content
        except:
            return False

    #*************************************************#
    # Function name : load_json                       #
    # input : file_name                               #
    # role : load json object and return its content  #
    #*************************************************#
    
    def load_json(self,file_name):

        try:
         
            with open(file_name, 'r') as f:
                data = json.load(f)
            return data    
        except:
            return False
            
    #*************************************************#
    # Function name : save_json                       #
    # input : file_name                               #
    # role : save data to a json object               #
    #*************************************************#
                    
    def save_json(self,data,file_name):
        try:
            with open(file_name, 'w') as f:
                json.dump(data, f)
        except:
            return False

    #**********************************************************#
    # Function name : log                                      #
    # input : submission                                       #
    # role : log submission (specification,time...) to a file  #
    #**********************************************************#
    
    def log(self,submission):    
    
        
        old_log = self.load_json(self.log_file_name)
        job_id = submission['job_id']
 
        #if log exists
        #append new log to old log                  
        if False is not old_log:
           old_log[job_id] = {}
        else:
        #create a new log
            old_log = {}
            old_log[job_id] = {}
        
        for key, value in submission.items():
            old_log[job_id][key] = value
        
        #print old_log        
        return self.save_json(old_log,self.log_file_name)    

    #**********************************************#
    # Function name : load_history                 #
    # input : arguments                            #
    # role : read all logs and save it into a list #
    # for the display                              #
    #**********************************************#
    
    def load_history(self,details):    
    
        histories = self.load_json(self.log_file_name)
        
        if histories is False:
            return False

        listed_histories = []
        
        for k,v in histories.items():
            listed_histories += [v]

        #sort history by time
        #to facilitate the 'by intervalle' research history
        sorted_histories = sorted(listed_histories, key=lambda k: k['date_time']) 

                
        
        histories_list = []
        
        for history in sorted_histories:
            temp_list = [history['job_id'], history['batch'], history['date_time'], history['executable'] , history['output']  ]
            #if user specifies 'more' options, print additionnal informations
            if details:
                temp_list += [history['stdout'], history['stderr'] , history['log']]
            
            temp_str = '\t\t\t\t'.join(temp_list)
            histories_list += [temp_str]

        return histories_list 

        
    #**********************************************#
    # Function name : custom_print                 #
    # input : message and options                  #
    # role : print message to gui or shell         #
    # if shell, quit in case of error              #
    # but in gui do not quit,                      #
    # we can 'replay' action, hence the 'replay'   #
    # variable in fcc_batch script                 #
    #**********************************************#

    def custom_print(self,message_type,message,exit):
        
 

        if self.interface == 'cli':
            print message
            if True == exit:
                quit()
        else:
            #if interface is gui, it means that gui has perfectly been loaded so no need to make 'try' import
            #import directly
            import fcc_submit_gui as gui
            gui.display_error_message(message_type,message)
            return False


    #********************************************#
    # Function name : get_answer                 #
    # input : question                           #
    # role : query the user on shell or gui      #
    # and get the answer                         #
    #********************************************#

    def get_answer(self,question,answer_type):


        if self.interface == 'cli':
            return raw_input(question).lower()
        else:
            #if interface is gui, it means that gui has perfectly been loaded so no need to make 'try' import
            #import directly
            import fcc_submit_gui as gui
            return gui.display_question(question,answer_type)


    #**********************************************************#
    # Function name : install_software                         #
    # input : software                                         #
    # role : install software (from github) not present        #
    # in afs to the user home directory                        #
    # ie. heppy                                                #
    #**********************************************************#

    def install_software(self,executable_name):
        

        is_heppy_installed = False
        replay = True

        yes = set(['yes','y', 'ye', ''])
        no = set(['no','n'])


        heppy_path = self.HARD_CODED_HEPPY_PATH_AFS

        answer = self.get_answer('\nYou plan to use '"heppy"', as it not installed on afs, it must be installed on your user directory :\nIs heppy already installed ? (y/n)\n','short')
                


        if answer in yes:

            is_heppy_installed = True
            
            answer = self.get_answer('\nThe script will take this location as the default heppy folder :\n' + heppy_path + ' \nEnter yes if you want to continue else no if you want to specify another heppy path) (y/n)\n','short')
        
            if answer in no:

                heppy_path = self.get_answer('Enter the full path of your heppy folder:','long')

                #make sure that the provided folder is a heppy folder and not whatever
                if not os.path.isdir(heppy_path) or not os.path.isfile(heppy_path + '/bin/' + executable_name) :

                    message = '\nThe path "'+ heppy_path +'" is not valid\nInstallation aborted\n'
                    replay = self.custom_print('Error',message,True)

            

            elif answer in yes:
                if not os.path.isdir(heppy_path):
                    message = '\nHeppy is not installed\nInstallation aborted'
                    replay = self.custom_print('Error',message,True)
            else :
                message = '\nbad answer\nInstallation aborted'
                replay = self.custom_print('Error',message,True)

        elif answer in  no:
            answer = self.get_answer('Do you want an automatic installation ? (y/n)','short')


            
            if answer in yes:

        
                        

                try:                         
                    from git import Repo     
                except:                         
                    #when we source the bash script init_fcc_stack.sh                         
                    #it modifies the python path and GIT module can no longer be imported                         
                    #so try to re-add lost GIT paths to python path
                        
                    GIT_MODULE_LOCATION = '/usr/lib/python2.6/site-packages/'                          
                    GITDB_MODULE_LOCATION = '/usr/lib64/python2.6/site-packages/'

                    sys.path.append(GIT_MODULE_LOCATION)
                    sys.path.append(GITDB_MODULE_LOCATION)                              
                
                    try:                             
                        from git import Repo                         

                    except ImportError:
                        message = '\nMissing git libraries\nPlease try manual installation\n'                            
                        replay = self.custom_print('Error',message,True)                      

                try:

                    if os.path.isdir(heppy_path):
                        answer = self.get_answer('\nHeppy is already installed on this location :\n'+heppy_path+'\nRemove it and process to a new installation ? (y/n)\n','short')
                
                        if answer in yes:
                            #remove folder and clone from github
                            shutil.rmtree(heppy_path)

                            print 'Installation in progress...' 
                            Repo.clone_from('https://github.com/HEP-FCC/heppy', heppy_path)

                        elif answer in no:
                            message = '\nInstallation canceled'
                            replay = self.custom_print('Error',message,True)
                        else:
                            message = '\nbad answer\nInstallation aborted'
                            replay = self.custom_print('Error',message,True)

                    else:
                        print 'Installation in progress...' 
                        Repo.clone_from('https://github.com/HEP-FCC/heppy', heppy_path)
            
                except:
                    message = '\nCloning from the https://github.com/HEP-FCC/heppy git repository produces an error\nHeppy seems to be already installed\nInstallation aborted\n'
                    replay = self.custom_print('Error',message,True)
                        
            elif answer in no:
                #if manual instalation but heppy installed , continue and do not quit
               
                message = """\nPlease follow the instructions in this tutorial :
    https://github.com/HEP-FCC/heppy
    Install the repository on your home directory ~:
    Re-run the script and choose yes when "Is Heppy already installed" is asked
    After this script will automatically source the file : ~/heppy/init.sh\n"""

                replay = self.custom_print('Information',message,True)
        
            else:
                message = '\nbad answer\nInstallation aborted\n'
                replay = self.custom_print('Error',message,True)
        
            

        else:
            message = '\nbad answer\nInstallation aborted\n'
            replay = self.custom_print('Error',message,True)
        

        if True == replay:

            self.setHEPPY = 'export HEPPY=' + heppy_path
            

        return replay

    #*************************************************#
    # Function name : try_install                     #
    # input : executable                              #
    # role : check heppy else print sourcing message  #
    #*************************************************#

    def try_install(self,executable,is_exist):
    #if executable not found in environnement path or filesystem
    #do not print fccsw sourcing message because this is already checked in init_fcc_stack()
  

        #for non heppy software print error message
        if executable != 'heppy_loop.py':

            if False is is_exist:
                self.custom_print('Information',"Your executable " + executable + " must be a 'pre-existing' software",False)

                message = "\nThe executable '" + executable + "' does not exist\nPlease upload your executable in an accessible file system (EOS or AFS)\n"

                return self.custom_print('Error',message,True)
            else:
                return True                
        #for heppy, try to install ?
        else:            
            #heppy install stuff
            #for the moment just check heppy environnement and send to the worker
            return self.init_heppy(executable)
            


    #*************************************************#
    # Function name : generate_bash_script            #
    # input : bash commands and script name           #
    # role : generate bash script                     #
    #*************************************************#


    def generate_bash_script(self,commands,script_name):

        
        #in addition to the job command, we set the environnement for FCC,HEPPY and EOS

        shebang = "#!/bin/bash"
        bash_script_text = [shebang, self.sourcingFCCStack, self.setHEPPY, self.setEOS] + commands    


        #write the temporary job
        self.write2file('w',script_name,'\n'.join(bash_script_text) + '\n')    

        #make the job executable and readable for all
        self.chmod(script_name,'R')    
        self.chmod(script_name,'X')



    #****************************************************#
    # Function name :  get_job_id                        #
    # input : output                                     #
    # role : search id in the standard ouput of batch    #
    #****************************************************#

    def get_job_id(self,batch_output):



        start = '<'
        end = '>'
        
        s = batch_output

        if self.chosen_batch == 'lsf':
            job_id_str = re.search('%s(\d+)%s' % (start, end), s)
        else:    
            job_id_str = re.search('cluster (\d+\.\d*)',s)


        #check the expected line
        try:
            job_id = job_id_str.group(1)
            
            if job_id.endswith('.') : job_id = job_id + '0'


        except:
            self.custom_print('Error',"\nYour job has probably not been submitted\n"+ self.chosen_batch.upper() + " outputs an error, please check your configuration\n",False)     
            job_id = "unkown_id"

        self.current_job_id = job_id
        return job_id


    def get_job_state(batch_output):

        LSF_STATES = ['PEND', 'PSUSP' , 'RUN' , 'USUSP', 'SSUSP' , 'DONE' , 'EXIT', 'UNKWN', 'ZOMBI']
        HTcondor_STATES = ['U','I', 'R', 'X', 'C', 'H', 'E']
        
         """        TO DO             """
    
        print 'status'    

    #****************************************************#
    # Function name :  find_executable                   #
    # input : executable                                 #
    # role : search executable in the environnement      #
    #****************************************************#

    def find_executable(self,executable_name):

        #if we do not have a space here (else see after how to manage)
        #./run gaudirun.py
       
        if not ' ' in executable_name:

            for path in os.environ["PATH"].split(os.pathsep):
            #print path
                for root, dirs, files in os.walk(path):
                    if executable_name in files:
                    #print files
                        return executable_name, True
            return executable_name,False 
                
        #ie.  ./run gaudirun.py           
        elif ' ' in executable_name:

            dot_slash = './'
            temp_executable_name = executable_name.split()
        

            #the first may be the executable
            file_name = temp_executable_name[0]

            if dot_slash in file_name:
                file_name = file_name.replace(dot_slash,'')
        
            #now we extract executable name (run), executable will not have a space from now
            #look on the path (recursivity)
            searched_file,is_exist = self.find_executable(file_name)
            
            #if the executable definitely not in paths,
            #look for the provided executable absolute path
            if False is is_exist: 
                searched_file,is_exist = self.find_path(file_name)
    
            return searched_file,is_exist
            
        else:
           return executable_name,False

    #****************************************************#
    # Function name :  chmod                             #
    # input : permission                                 #
    # role : change permission                           #
    # function created when condor outputs error like :  #
    # 'files not writtable by condor'                    #
    #****************************************************#

    def chmod(self,file,permission):

        #reflet chmod a+permission 
        #make the file x,r, or w for everyone
        USER_PERMISSION = eval('stat.S_I'+permission+'USR')
        GROUP_PERMISSION = eval('stat.S_I'+permission+'GRP')
        OTHER_PERMISSION = eval('stat.S_I'+permission+'OTH')

        PERMISSION = USER_PERMISSION | GROUP_PERMISSION | OTHER_PERMISSION

        #get actual mode of the file
        mode = os.stat(file).st_mode

        #append the new permission to the existing one
        os.chmod(file,mode | PERMISSION)


    #****************************************************#
    # Function name :  save_history                      #
    # input : job id, batch used ...                     #
    # role : log each submissions                        #
    #****************************************************#

    def save_history(self,job_id, batch,submitted_time,executable, outdir, stdout_file, error_file,log_file):

       
        submission_log = {'job_id':job_id, 'batch':batch, 'date_time':submitted_time,'executable':executable,'output':outdir,'stdout':stdout_file,'stderr':error_file,'log':log_file}
    
        #try to log else output error message
        if False is self.log(submission_log):
            self.custom_print('Error','Error in saving history',False)



    #*******************************************************#
    # Function name :  display_history                      #
    # input : intervalle                                    #
    # role : display history of user submissions            #
    #*******************************************************#

    def display_history(self,intervalle,details):

        

        default_min = 0
        full = False
        date_and_time = False
        date_only = False
        since = False
        since_to = False
        to = False
        replay =  True
        invalid_values = False
        
        values = intervalle

        #--hist 11/24/16 10:00:00 11/25/16 19:00:00 (from to)
        if len(values) == 4:
            user_start_date = values[0]
            user_start_time = values[1]

            user_end_date = values[2]
            user_end_time = values[3]

            full = True

            since_to = True
            
            if not (self.format(user_start_date,'check',"%m/%d/%y") and  self.format(user_start_time,'check',"%H:%M:%S") and self.format(user_end_date,'check',"%m/%d/%y") and self.format(user_end_time,'check',"%H:%M:%S")):
                invalid_values = True
        
        #--hist 11/24/16 10:00:00 (from this date and time) or --hist 1 10 (from job 1 to 10)
        elif len(values) == 2:
            user_min = values[0]
            user_max = values[1]

            if self.format(user_min,'check',"%m/%d/%y") and self.format(user_max,'check',"%H:%M:%S"):
                date_and_time = True
                since = True
            elif not self.is_int(user_min) or not self.is_int(user_max):
                invalid_values = True

        #--hist 11/24/16 (from this date) or --hist 10 (10 last jobs)    
        elif len(values)== 1:

            user_min = values[0]

            if self.format(user_min,'check',"%m/%d/%y"):
                date_only = True
                since = True
            elif not self.is_int(user_min):
                invalid_values = True
      
        
        #no values entered so display all history --hist
        elif len(values)== 0:
            user_min = 'min'
            user_max = 'max'

        else:
            invalid_values = True

        if invalid_values:    
            return self.custom_print('Error','\nInvalid values\n',True)
        
    
        
        #if log or folder script has been deleted 
        if not os.path.isfile(self.log_file_name):
            self.custom_print('Error','\nHistory not available\n',True)
        else:
            
            
            histories = self.load_history(details)

            if False is histories:    
                return self.custom_print('Error','\nImpossible to load history\n',True)
            
            default_max = len(histories) - 1

            #history according to job number
            if not(date_only or date_and_time or full):

                if 'min' == user_min and 'max' == user_max:
                    user_min = default_min
                    temp_user_max = default_max
                else:

                    if 'user_max' not in locals():
                        temp_user_max = default_max + 1
                        user_min= temp_user_max - int(user_min)
                    else:
                        temp_user_max = int(user_max) - 1
                        user_min= int(user_min) - 1


                end = temp_user_max  if (temp_user_max <= default_max and temp_user_max >= default_min) else default_max
                start = user_min if (user_min <= end and user_min >= default_min) else default_min
        
                
            #history according to date and time
            else:
            
                mytimes = []
                mydates = []
                
                for history in histories :
                    
        
                    try:
                        if '' != history:
                            mydates += [re.search('\d+/\d+/\d+',history).group(0)]
                            mytimes += [re.search('\d+:\d+:\d+',history).group(0)]

                    except:                    
                        self.custom_print('Error','Invalid values',True)


                if date_and_time or date_only :


                    #date indexes of interest                
                    date_indexes, time_research = self.get_closest_date(user_min,mydates,since,since_to,default_max,to)
                    
                    if time_research == None:
                        start, end = date_indexes[0], date_indexes[1] 
                    else:
                        if date_only:
                            start, end = self.get_closest_time('00:00:00',date_indexes,mytimes,mydates,since,since_to,default_max,to)
                        else:
                            start, end = self.get_closest_time(user_max,date_indexes,mytimes,mydates,since,since_to,default_max,to)
                    

                elif full:

                    invalid_order = False

                    #date indexes of interest                
                    date_indexes, time_research = self.get_closest_date(user_start_date,mydates,since,since_to,default_max,to)
                    
                    if time_research == None:
                        start = date_indexes
                    else:
                        start = self.get_closest_time(user_start_time,date_indexes,mytimes,mydates,since,since_to,default_max,to)
                                          
                    to = True                        
                    #date indexes of interest                
                    date_indexes, time_research = self.get_closest_date(user_end_date,mydates,since,since_to,default_max,to)
                    
                    if time_research == None:
                        end = date_indexes
                    else:
                        end = self.get_closest_time(user_end_time,date_indexes,mytimes,mydates,since,since_to,default_max,to)
                         
                    #check invalid order           
                    if  self.format(user_start_date,'format',"%m/%d/%y") > self.format(user_end_date,'format',"%m/%d/%y") :           
                        invalid_order = True
                    elif ( self.format(user_start_date,'format',"%m/%d/%y") == self.format(user_end_date,'format',"%m/%d/%y") ) and ( self.format(user_start_time,'format',"%H:%M:%S") > self.format(user_end_time,'format',"%H:%M:%S") ):    
                        invalid_order = True
                    
                    if invalid_order:    
                        self.custom_print('Error','\nInvalid Date Sequence\n',True)
                                            
            #end depend on start for no time found in a day
            end = -1 if (None == start or None == end) else end
            start = start if None != start else 0        
            
                                            
            if start >= default_min and end <= default_max:

                if start == 0 and end == -1 or start > end:
                    header = '\nNO HISTORY FOR THESE DATES\n'  
                else:
                    header = 'JOB ID\t\t\t\tBATCH\t\t\t\tSUMITTED TIME\t\t\t\tExecutable\t\t\t\tOutput Results'
                    if details:
                        header += '\t\t\t\tStandard Output\t\t\t\tStandard Error\t\t\t\tStandard Log'       
                                
                history =  header + '\n' + '\n'.join(histories[start:end+1])
                
                if 'cli' == self.interface:
                    print history
                else:
                    return history    
                
            else:
                self.custom_print('Error','\nInvalid Dates\n',True)
            
    #*********************************************************#
    # Function name :  get_closest_date                       #
    # input : user start date etc...                          #
    # role : get closest date of a given date/date intervalle #
    #*********************************************************#
            
    def get_closest_date(self,date,date_list,since,since_to,default_max,to):

        time_research = None 
        user_date = date
        
       
        date = self.format(date,'format',"%m/%d/%y")
        closest_date = min(date_list, key=lambda t: abs(date - self.format(t,'format',"%m/%d/%y")))

        
        formated_closest_date = self.format(closest_date,'format',"%m/%d/%y")
        formated_date = datetime.datetime.strptime(str(date),"%Y-%m-%d %H:%M:%S")
        

        closest_date_first_occurence = date_list.index(closest_date)
        closest_date_last_occurence = len(date_list) - date_list[::-1].index(closest_date) - 1
        last_history_date_index = len(date_list) - 1
        #if start_day bigger thab current day existing history days, print nothing
        
        if since or since_to:
            #print 'since date action'
            #if asked date bigger than closest day
            if formated_date > formated_closest_date:
                #print 'closest date smaller'
                #if the history contains old dates only -> print nothing
                if closest_date_last_occurence == last_history_date_index :
                    #print 'there is no future date'
                    
                    
                    #it can be start or end
                    if since_to:
                        #start
                        if not to:
                            start_or_end = None
                        #end    
                        else:
                            start_or_end = closest_date_last_occurence
                    else:
                        end = None
                        start = None
                                   
                #if the history contains future dates but far -> print all from next future date
                else: 
                    #print 'there is future date !'
                    next_future_date = closest_date_last_occurence + 1
                    
                    
                    
                    if since_to:
                    
                        if not to:
                            start_or_end = next_future_date
                        else:
                            start_or_end = closest_date_last_occurence
                    else:    
                        end = default_max
                        start = next_future_date
                        
            #if history contain events recent than provided date         
            elif formated_date < formated_closest_date:
                #print 'closest date bigger'      
                #print 'there is future date !'
                
                
                
                if since_to:
                
                    if not to:
                        start_or_end = closest_date_first_occurence
                    else:
                    
                        if closest_date_first_occurence - 1 >= 0:
                            start_or_end = closest_date_first_occurence - 1
                        else:
                            start_or_end = None
                else:    
                    end = default_max
                    start = closest_date_first_occurence
            
            #if asked date exist in history(closest strictly equal ==)    
            else:
                time_research = 'search'
             
                indexes = [i for i,x in enumerate(date_list) if x == closest_date]
                return indexes , time_research 
                
                
        if since_to:
            return start_or_end, time_research   
        else:
            return [start , end], time_research

    #*********************************************************#
    # Function name :  get_closest_time                       #
    # input : user start time etc...                          #
    # role : get closest time of a given time/time intervalle #               
    #*********************************************************#

        
    def get_closest_time(self,time,closest_dates_indexes,time_list,date_list,since,since_to,default_max,to):

        state = True
       
        
        #here we have corresponding times of selected days
        if len(closest_dates_indexes)>1:
            subset = list(itemgetter(*closest_dates_indexes)(time_list))
        else:
            subset = [str(time_list[closest_dates_indexes[0]])]
            
        
        absolute_start = closest_dates_indexes[0]

         
        user_time = self.format(time,'format',"%H:%M:%S")
        closest_time = min(subset, key=lambda t: abs(user_time - self.format(t,'format',"%H:%M:%S")))



        formated_closest_time = self.format(closest_time,'format',"%H:%M:%S")
        formated_user_time = datetime.datetime.strptime(str(user_time),"%Y-%m-%d %H:%M:%S")
        
       

         
        relative_closest_time_first_occurence = subset.index(closest_time)

        
        absolute_closest_time_first_occurence = absolute_start + relative_closest_time_first_occurence
        
        if since or since_to:
        
            
            #there is only more recents events
            if formated_user_time < formated_closest_time :
                #print 'there is no old events'
                #then print from this time ti end
                
                
                if since_to:
                    #start
                    if not to:
                
                        start_or_end = absolute_closest_time_first_occurence
                     
                    else:
                    
                        if absolute_closest_time_first_occurence - 1 >= 0:
                            start_or_end = absolute_closest_time_first_occurence - 1
                        else:
                            start_or_end = None
                            
                else:
                    start = absolute_closest_time_first_occurence
                    end = default_max     
                
            #the closest is smaller
            elif formated_user_time > formated_closest_time :   
                #print 'there is old events'
                #check if there is next time far but bigger or pick the first of next day
                #if in the times of the day there is more recent time     
                if (relative_closest_time_first_occurence + 1) < len(subset):
                    #print 'there is bigger time in your day'
                    
                    
                    if since_to:
                        if not to:
                        
                            start_or_end = absolute_closest_time_first_occurence + 1
                      
                        else:
                            start_or_end = absolute_closest_time_first_occurence          
                    else:
                        start = absolute_closest_time_first_occurence + 1
                        end = default_max
                
                
                 
                #user time bigger but no history after this time on this day
                #so check the next day 
                else:
                    #if there is no next day 
                    if absolute_start + len(subset) >= len(time_list):
                        #print 'there is no next day'
                        
                        
                        if since_to:
                            if not to :
                                start_or_end = None    
                            else:
                        
                                start_or_end = absolute_closest_time_first_occurence
                        else:
                            start = None
                            end = None
                        
                    else:
                  
                        
                        if since_to:
                            if not to :
                                start_or_end =  absolute_start + len(subset)
                            else:
                                start_or_end =  absolute_closest_time_first_occurence
                        else:
                            start = absolute_start + len(subset)
                            end = default_max

            #closest time equal user time
            else:
            
                if since_to:
       
                    start_or_end =  absolute_closest_time_first_occurence
                else:
                    start = absolute_closest_time_first_occurence
                    end = default_max
        
        
        if since :                
            return start,end     
        else :                
            return start_or_end
    
    
    #***************************#        
    # DATA TYPE/FORMAT checking #
    #***************************#
                
    def format(self,date_time,operation,string_format):

     
        try:
            result = datetime.datetime.strptime(date_time,string_format) 
            if operation == 'check':
                return True
            else:
                return result    
        except:

            if operation == 'check':
                return False
            else:                        
                self.custom_print('Error','Invalid values',True)
                 
            
            
    def is_int(self,input):
        try: 
            int(input)
            return True
        except ValueError:
            return False



