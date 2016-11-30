#!/usr/bin/env python


#*********************** libraries importation  ************************#

#standard libraries
import os 
import sys

def installation_error():
    error_message = """The required packages for the GUI are not available
               In this case, you need the following packages
               1) tkinter and PIL
               To install a package type : pip install name_of_the_package"""

    return error_message

try:
    # for Python2
    import Tkinter as tk  ## notice capitalized T in Tkinter 
except ImportError:
    # for Python3
    try:
        import tkinter as tk ## notice lowercase 't' in tkinter here
    except ImportError:
        raise ImportError(installation_error())

from ScrolledText import *
from tkFileDialog import *
import tkMessageBox

try:
    from PIL import Image, ImageTk
except:
    #the problem is that when we source the bash script init_fcc_stack.sh
    #it modifies the python path and PIL module can no longer be imported
    #so try to re-add lost paths to python path    

    PIL_MODULE_LOCATION = '/usr/lib64/python2.6/site-packages'
    
    if not PIL_MODULE_LOCATION in sys.path:
        sys.path.append(PIL_MODULE_LOCATION)
    
    try:
        from PIL import Image, ImageTk
    except ImportError:
        raise ImportError(installation_error())


#user libraries
import fcc_batch as batch





#constants
Police = 12
LARGE_FONT= ("Verdana", Police)
window_width = 500
window_height = 500
BGlabel=False 
chosen_software=""
popup_log = None
popup_output = None
popup_error = None
main = None

#********************************* Functions Definition  ************************************#


#***********************************#
# Function name : launchGUI         #
# input : none                      #
# role : launch the GUI which       # 
# will 'catch' the configuration    #
# for the submission                #
#***********************************#


def launchGUI(my_file_sys):

    launchGUI.my_file_sys = my_file_sys
    
    main = Submission()
    main.title("FCC SUBMIT")
    #main.main.iconphoto(True,ImageTk.PhotoImage(file=os.path.join(sys.path[0],"fcc.png")))
    #main.iconbitmap('@fcc.xbm')
    main.mainloop()


#***********************************#
# Function name : run               #
# input : class instance and        #
# the fcc software                  #
# role : parse gui textwidgets,save #
# the executable and other options  #    
# in a configuration dictionnary    #
# and send it to                    #
# the final submission "level"      #
#***********************************#

def run(self):
    

    chosen_batch = launchGUI.my_file_sys.get_batch()


    specification = {}
    specification['batch'] = chosen_batch


    fcc_output_file = self.ofile_txt.get()
    
    batch_original_arguments = self.batch_args_txt.get()
    
    stdout = self.stdout_txt.get()
    stderr = self.stderr_txt.get()
    log = self.log_txt.get()

    files = list(self.files_listbox.get(0, tk.END))
    fcc_input_files =  '' if not files else files



    fcc_executable = self.exec_txt.get()
    fcc_conf_file=self.conf_txt.get()
    fcc_output_file=self.ofile_txt.get()
    

    #**************************************************MINIMUM REQUIREMENTS CHECKING*******************************************************#

    if fcc_executable =='' or fcc_conf_file == '':
        message = "Please, provide at least the path of your executable and a configuration file"
        display_error_message('Error',message)
        return      

    #**************************************************MINIMUM REQUIREMENTS CHECKING*******************************************************#


    try:
        tempNOR = self.NOR_txt.get()
        NOR = int(tempNOR) if tempNOR != '' else ''
     
        tempNOE = self.NOE_txt.get()
        NOE = int(tempNOE) if tempNOE != '' else ''
    
        

        specification['fcc_executable'] = fcc_executable
        specification['fcc_conf_file'] = fcc_conf_file
        specification['fcc_input_files'] = fcc_input_files
        specification['number_of_runs'] = NOR
        specification['number_of_events'] = NOE
        specification['fcc_output_file'] = fcc_output_file
        specification['batch_original_arguments'] = batch_original_arguments
        specification['stdout'] = stdout
        specification['stderr'] = stderr
        specification['log'] = log


    
        #submit configuration
        batch.submit_bash(launchGUI.my_file_sys,specification)

    except ValueError:
        message = "Please enter a valid number"
        display_error_message('Error',message)


#*******************************************#
# Function name : show                      #
# input : folder results                    #
# role : print stdout,stderr,log in a popup #
#*******************************************#

def show(self,who):


    result_folder, batch_folder, output_folder, error_folder , log_folder = launchGUI.my_file_sys.get_workspace()

    job_id = launchGUI.my_file_sys.get_last_job_id()    

    if who == 'log':


        file_content = launchGUI.my_file_sys.read_from_file(output_folder + '/job.' + job_id + '.log')

        if False != file_content :

            what = file_content


            actual_content = self.log_scrolltext.get(1.0, tk.END)

            if actual_content != '' : self.log_scrolltext.delete(1.0, tk.END)

            self.log_scrolltext.insert(tk.END,what)
        
        

            #show it
            #self.popup_log.update()
            self.popup_log.deiconify()
            #put on the front
            self.popup_log.lift()
            #put focus on it
            self.popup_log.focus_force()


    elif who == 'output':

        file_content = launchGUI.my_file_sys.read_from_file(output_folder + '/job.' + job_id + '.out')

        if False != file_content :

            what = file_content

            

            actual_content = self.output_scrolltext.get(1.0, tk.END)

            if actual_content != '' : self.output_scrolltext.delete(1.0, tk.END)

            self.output_scrolltext.insert(tk.END,what)
        
        

            #show it
            self.popup_log.update()
            self.popup_output.deiconify()
            #put on the front
            self.popup_output.lift()
            #put focus on it
            self.popup_output.focus_force()

    elif who == 'error':
        
        file_content = launchGUI.my_file_sys.read_from_file(output_folder + '/job.' + job_id + '.err')

        if False != file_content :

            what = file_content

        

            actual_content = self.error_scrolltext.get(1.0, tk.END)

            if actual_content != '' : self.error_scrolltext.delete(1.0, tk.END)

            self.error_scrolltext.insert(tk.END,what)
        

            #show it
            self.popup_log.update()
            self.popup_error.deiconify()
            #put on the front
            self.popup_error.lift()
            #put focus on it
            self.popup_error.focus_force()


    
    
    #main.wait_window(popup)


#*************************************************#
# Function name : display_error_message           #
# input : message                                 #
# role : display short message on gui ok window   #
#*************************************************#

def display_error_message(message_type,message):
    tkMessageBox.showinfo(message_type, message)


#*******************************************#
# Function name : display_question          #
# input : message                           #
# role : display long message on gui window #     
# with eventually long response             #
#*******************************************#

def display_question(question,answer_type):
    if answer_type == 'long':
        popup = tk.Toplevel()

        popup.minsize(400,100)
        popup.maxsize(400,100)

        question_label = tk.Label(popup, text=question, height=0, width=100)
        question_label.place(x=10,y=10,width=300,height=20)

        path_txt = tk.StringVar()
        path_entry = tk.Entry(popup,textvariable=path_txt)
        path_entry.place(x=10,y=30,width=300,height=20)    

        search_path_button = tk.Button(popup, text="...",command=lambda: open_dialog_box('dir','set_one',path_txt))
        search_path_button.place(x=320,y=30,width=60,height=20)

        ok_button = tk.Button(popup, text="OK",command=lambda: popup.destroy())
        ok_button.place(x=200,y=50,width=60,height=40)

        popup.focus_force()
        
        launchGUI.main.wait_window(popup)

        result = path_txt.get()        
    else:
        result = tkMessageBox.askquestion("Installation", question , icon='warning')
    return result


#***********************************************#
# Function name : display_about                 #
# input : none                                  #
# role : display informations about application #
#***********************************************#

def display_about():

    popup = tk.Toplevel()

    popup.minsize(450,600)
    popup.maxsize(450,600)

    program_label = tk.Label(popup, text='FCC SUBMIT v1.0 by FCC',font=LARGE_FONT)
    program_label.place(x=80,y=10)

    image_filename = 'fcc.png'    

    if os.path.isfile(image_filename):

        img = ImageTk.PhotoImage(Image.open(image_filename))
        panel = tk.Label(popup, image = img)

        panel.place(x=80,y=60)

    informations = """

SOFTWARE INFORMATIONS     
                               
                   Property of CERN               
                               
EP-SFT Group (Experimental physics - Software)             
                               
Simplified Submission Script for using Batchs systems       
at CERN.                           
                               
FCC group can use it to run jobs on LXBatch.       
                               
This script provides a simple interface for the submission 
of jobs on HtCondor or LSF Batch and it offers more        
fonctionnalities wich are :                        
                               
-> An usual way to submit a job :                   
  ie. fcc-submit --gui               
                               
-> An abstract management of job spliting           
                               
For more information, please contact us                   
at fcc-experiments-sw-devATSPAMNOTcern.ch            
                                   

"""

    informations_label = tk.Label(popup, text=informations)
    informations_label.place(x=10,y=170)


    ok_button = tk.Button(popup, text="OK",command=lambda: popup.destroy())
    ok_button.place(x=200,y=550,width=60,height=40)

    popup.focus_force()
    
    launchGUI.main.wait_window(popup)
    

#*************************************#
# Function name : open_dialog_box     #
# input : class objects               #
# role : get paths of executable,     #
# etc... from GUI dialog box          #
#*************************************#

def open_dialog_box(type,what,widget):
    
    if type == 'file':    
        if what == "set_many":
            files = askopenfilenames()  

            for file in list(files):
                widget.insert(tk.END,file)
        elif what == "set_one":
            file = askopenfilename()
            widget.set(file)
        elif what== "get_one":
            return askopenfilename()     
    elif type == 'dir':
        directory = askdirectory()
        widget.set(directory)
            


#***************************************#
# Function name : import_to_gui         #
# input : class instance                #
# role : import specification from file #
# and fill corresponding widgets        #
#***************************************#



def import_to_gui(self):
    

    filename = open_dialog_box('file','get_one','')


    if filename:

        
        specification , status = launchGUI.my_file_sys.import_specification(filename)

        if False != status :
    
            [chosen_batch, fcc_executable, fcc_conf_file ,fcc_output_file, NOR , NOE , fcc_input_files ,batch_original_arguments, stdout, stderr, log]  =  specification
            
            
    
            self.exec_txt.set(fcc_executable)
            self.conf_txt.set(fcc_conf_file)
            self.ofile_txt.set(fcc_output_file)
            self.NOR_txt.set(NOR)
            self.NOE_txt.set(NOE)
            self.batch_args_txt.set(batch_original_arguments)
            self.stdout_txt.set(stdout)    
            self.stderr_txt.set(stderr)
            self.log_txt.set(log)


            set_gui_batch(self,chosen_batch)

            if fcc_input_files != '':
                for file in fcc_input_files:
                    self.files_listbox.insert(tk.END,file) 


#***************************************#
# Function name : save_from_gui         #
# input : class instance                #
# role : get widgets text and save      #
# specification to a file               #
#***************************************#

def save_from_gui(self):

    chosen_batch = launchGUI.my_file_sys.get_batch()

    file = asksaveasfile(mode='w', defaultextension=".spec")

    if file is None: # asksaveasfile return `None` if dialog closed with "cancel".
        return
    else:
        fcc_executable=self.exec_txt.get()
        fcc_conf_file=self.conf_txt.get()
        fcc_output_file=self.ofile_txt.get()
        NOR = self.NOR_txt.get()
        NOE = self.NOE_txt.get()
        batch_original_arguments = self.batch_args_txt.get()
        stdout = self.stdout_txt.get()
        stderr = self.stderr_txt.get()
        log = self.log_txt.get()

        files = list(self.files_listbox.get(0, tk.END))
        fcc_input_files =  '' if not files else ' '.join(files)
        

        specification_values = [chosen_batch, fcc_executable, fcc_conf_file, fcc_output_file, NOR, NOE, fcc_input_files,batch_original_arguments,stdout,stderr,log]
                
        launchGUI.my_file_sys.save_specification(specification_values,file.name)

#***********************************#
# Function name : menubar           #
# input : frame/class instance      #
# role : set a menu on the top of   #
# frame                             #
#***********************************#

def menubar(self, root):
    menubar = tk.Menu(root)

    sub_menu = tk.Menu(menubar)
    sub_menu.add_command(label="Import", command=lambda: import_to_gui(root))
    sub_menu.add_command(label="Save as...", command=lambda: save_from_gui(root))

    menubar.add_cascade(label="Menu", menu=sub_menu)

    sub_help = tk.Menu(menubar)
    sub_help.add_command(label="About", command=lambda: display_about())

    menubar.add_cascade(label="Help", menu=sub_help)

    return menubar


#***********************************#
# Function name : set_gui_batch     #
# input : class objects             #
# role : get selected batch button  #
# and set actual batch              #
#***********************************#

def set_gui_batch(self,batch):
    
        
    print batch
    
    if batch == 'lsf':
        self.LSF_button.configure(bg = "green")    
        self.HTCondor_button.configure(bg = "grey")
        self.log_view_button.configure(state=tk.DISABLED) 
    else:
        self.LSF_button.configure(bg = "grey")    
        self.HTCondor_button.configure(bg = "green")
        self.log_view_button.configure(state=tk.NORMAL)
    
    launchGUI.my_file_sys.set_batch(batch)



    



#**************************************************** Classes Definition - START ************************************************************#


#************************************#
# Class name : Submission            #
# input : tk object                  #
# role : configure frame of GUI      #
#************************************#

class Submission(tk.Tk):

    #************************************#
    # Function name : __init__           #
    # input : arguments                  #
    # role : initialize the frame        #
    # of the GUI                         #        
    #************************************#

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)

        self.minsize(window_width,window_height)
        self.maxsize(window_width,window_height)

        container = tk.Frame(self, width=window_width,height=window_height)

        container.pack(side="top", fill="both", expand = True)

    
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)


        self.frame = JOB(container, self)

        self.frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(JOB)


    #************************************#
    # Function name : show_frame         #
    # input : frame/class instance       #
    # role : display the asked frame     #       
    #************************************#


    def show_frame(self, cont):

        self.frame.tkraise()
    
    
        menudef = menubar(self,self.frame)
        self.configure(menu=menudef)


#***************************************#
# Class name : JOB                      #
# input : tk object                     #
# role : create JOB specification frame #
#***************************************#

class JOB(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        #creation of the widgets

        label = tk.Label(self, text="JOB SPECIFICATION", font=LARGE_FONT)
        label.pack(pady=10,padx=10)


        exec_label = tk.Label(self, text="Executable")
        exec_label.place(x=10,y=50,width=200,height=20)

        self.exec_txt = tk.StringVar()
        exec_entry = tk.Entry(self,textvariable=self.exec_txt)
        exec_entry.place(x=230,y=50,width=200,height=20)

        search_exec_button = tk.Button(self, text="...",command=lambda: open_dialog_box('file','set_one',self.exec_txt))
        search_exec_button.place(x=430,y=50,width=60,height=20)

        conf_label = tk.Label(self, text="Configuration File")
        conf_label.place(x=10,y=80,width=200,height=20)

        self.conf_txt = tk.StringVar()
        conf_entry = tk.Entry(self,textvariable=self.conf_txt)
        conf_entry.place(x=230,y=80,width=200,height=20)

        search_conf_button = tk.Button(self, text="...",command=lambda: open_dialog_box('file','set_one',self.conf_txt))
        search_conf_button.place(x=430,y=80,width=60,height=20)

    
        ofile_label = tk.Label(self, text="Output File")
        ofile_label.place(x=10,y=110,width=200,height=20)

        self.ofile_txt = tk.StringVar()
        ofile_entry = tk.Entry(self,textvariable=self.ofile_txt)
        ofile_entry.place(x=230,y=110,width=200,height=20)

        stdout_label = tk.Label(self, text="Standard output")
        stdout_label.place(x=10,y=130,width=200,height=20)

        self.stdout_txt = tk.StringVar()
        stdout_entry = tk.Entry(self,textvariable=self.stdout_txt)
        stdout_entry.place(x=230,y=130,width=200,height=20)

        search_stdout_button = tk.Button(self, text="...",command=lambda: open_dialog_box('dir','set_one',self.stdout_txt))
        search_stdout_button.place(x=430,y=130,width=60,height=20)

        stderr_label = tk.Label(self, text="Standard error")
        stderr_label.place(x=10,y=150,width=200,height=20)

        self.stderr_txt = tk.StringVar()
        stderr_entry = tk.Entry(self,textvariable=self.stderr_txt)
        stderr_entry.place(x=230,y=150,width=200,height=20)

        search_stderr_button = tk.Button(self, text="...",command=lambda: open_dialog_box('dir','set_one',self.stderr_txt))
        search_stderr_button.place(x=430,y=150,width=60,height=20)


        log_label = tk.Label(self, text="Log")
        log_label.place(x=10,y=170,width=200,height=20)

        self.log_txt = tk.StringVar()
        log_entry = tk.Entry(self,textvariable=self.log_txt)
        log_entry.place(x=230,y=170,width=200,height=20)

        search_log_button = tk.Button(self, text="...",command=lambda: open_dialog_box('dir','set_one',self.log_txt))
        search_log_button.place(x=430,y=170,width=60,height=20)



        NOR_label = tk.Label(self, text="Number of Runs")
        NOR_label.place(x=10,y=190,width=200,height=20)


        self.NOR_txt = tk.StringVar()
        NOR_entry = tk.Entry(self,textvariable=self.NOR_txt)
        NOR_entry.place(x=230,y=190,width=200,height=20)

        NOE_label = tk.Label(self, text="Number of Events")
        NOE_label.place(x=10,y=210,width=200,height=20)

        self.NOE_txt = tk.StringVar()
        NOE_entry = tk.Entry(self,textvariable=self.NOE_txt)
        NOE_entry.place(x=230,y=210,width=200,height=20)


        files_label = tk.Label(self, text="Input Files (Default AFS)")
        files_label.place(x=10,y=250,width=250,height=20)

        self.files_listbox = tk.Listbox(self)
        self.files_listbox.place(x=230,y=250,width=200,height=60)


        self.files_listbox.bind('<Double-1>', lambda _: self.delete_list_box_items(self.files_listbox))


        search_afs_files_button = tk.Button(self, text="...",command=lambda: open_dialog_box('file','set_many',self.files_listbox))
        search_afs_files_button.place(x=430,y=250,width=60,height=20)


        eos_file_label = tk.Label(self, text="Input File (other file system)")
        eos_file_label.place(x=10,y=300,width=200,height=20)

        self.eos_file_txt = tk.StringVar()
        eos_file_entry = tk.Entry(self,textvariable=self.eos_file_txt)
        eos_file_entry.place(x=230,y=300,width=200,height=20)


        add_eos_file_button = tk.Button(self, text="add",command=lambda: self.add_to_list_box_items(self.files_listbox,self.eos_file_txt.get()))
        add_eos_file_button.place(x=430,y=300,width=60,height=20)


        batch_args_label = tk.Label(self, text="Batch additionnal arguments")
        batch_args_label.place(x=10,y=320,width=200,height=20)

        self.batch_args_txt = tk.StringVar()
        batch_args_entry = tk.Entry(self,textvariable=self.batch_args_txt)
        batch_args_entry.place(x=230,y=320,width=200,height=20)


        batch_label = tk.Label(self, text="Batch system choice")
        batch_label.place(x=10,y=350,width=200,height=20)


        self.LSF_button = tk.Button(self, text ="LSF", relief=tk.RIDGE,command=lambda: set_gui_batch(self,'lsf'))
        self.LSF_button.place(x=230,y=350,width=70,height=40)

        self.HTCondor_button = tk.Button(self, text ="HTCondor", relief=tk.RIDGE,command=lambda: set_gui_batch(self,'htcondor'))
        self.HTCondor_button.place(x=320,y=350,width=70,height=40)


        self.popup_log = tk.Toplevel()
        self.popup_log.title('LOG')    
        self.popup_log.protocol("WM_DELETE_WINDOW", self.popup_log.withdraw)
        self.popup_log.withdraw()

        self.popup_log.minsize(400,400)


        self.log_scrolltext = ScrolledText(self.popup_log)
        self.log_scrolltext.pack(fill=tk.BOTH,expand=True)
        self.log_scrolltext.insert(tk.INSERT,'LOG')


        self.log_view_button = tk.Button(self, text="Log",state=tk.DISABLED,command=lambda: show(self,'log'))
        self.log_view_button.place(x=300,y=400,width=60,height=40)


        self.popup_output = tk.Toplevel()
        self.popup_output.title('OUTPUT')    
        self.popup_output.protocol("WM_DELETE_WINDOW", self.popup_output.withdraw)
        self.popup_output.withdraw()

        self.popup_output.minsize(400,400)

        self.output_scrolltext = ScrolledText(self.popup_output)
        self.output_scrolltext.pack(fill=tk.BOTH,expand=True)

        stdout_view_button = tk.Button(self, text="Output",command=lambda: show(self,'output'))
        stdout_view_button.place(x=360,y=400,width=60,height=40)

        self.popup_error = tk.Toplevel()
        self.popup_error.title('ERROR')
        self.popup_error.protocol("WM_DELETE_WINDOW", self.popup_error.withdraw)
        self.popup_error.withdraw()

        self.popup_error.minsize(400,400)

        self.error_scrolltext = ScrolledText(self.popup_error)
        self.error_scrolltext.pack(fill=tk.BOTH,expand=True)


        stderr_view_button = tk.Button(self, text="Error",command=lambda: show(self,'error'))
        stderr_view_button.place(x=420,y=400,width=60,height=40)    

        run_button = tk.Button(self, text="RUN",command=lambda: run(self))
        run_button.place(x=230,y=400,width=60,height=40)


        set_gui_batch(self,'htcondor')


    #delete file on listbox
    def delete_list_box_items(self,listbox): 
         #get selected line index       
        index = listbox.curselection()[0]
        listbox.delete(index)

    #add file on listbox
    def add_to_list_box_items(self,listbox,item): 
        listbox.insert(tk.END,item)




#if you to call the script independantly of the CLI
#**************************** MAIN START ************************************#

#launchGUI()    

#****************************** MAIN END ************************************#


