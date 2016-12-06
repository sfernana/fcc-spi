#!/usr/bin/env python


#*********************** libraries importation  ************************#

#standard libraries
import os 
import sys



try:
    # for Python2
    import Tkinter as tk  # Tkinter begins with a capitalized T 
except ImportError:
    # for Python3
    try:
        import tkinter as tk # tkinter begins with a lowercased t
    except ImportError:
        raise ImportError(installation_error())

from ScrolledText import *
from tkFileDialog import *
import tkMessageBox

try:
    from PIL import Image, ImageTk
except:
    #when we source the bash script init_fcc_stack.sh
    #it modifies the python path and PIL module can no longer be imported
    #so try to re-add lost PIL paths to python path    

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
window_height = 550 

#********************************* Functions Definition  ************************************#

#********************************************#
# Function name : installation_error         #
# input : none                               #
# role : return error message installation   # 
# when libraries are missing                 #
#********************************************#

def installation_error():
    error_message = """The required packages for the GUI are not available
               In this case, you need the following packages
               1) tkinter and PIL
               To install a package type : pip install name_of_the_package"""

    return error_message
    
    
#***********************************#
# Function name : launchGUI         #
# input : none                      #
# role : launch the GUI which       # 
# will 'catch' the specification    #
# for the submission                #
#***********************************#


def launchGUI(my_file_sys):

    #to obtain my_file_sys variable scope from another function
    launchGUI.my_file_sys = my_file_sys
    
    main = Submission()
    
    #to obtain main variable scope from another function
    launchGUI.main = main 
    
    main.title("FCC SUBMIT")
    main.mainloop()


#**********************************************#
# Function name : run                          #
# input : class instance                       #       
# role : parse gui textwidgets, save           #
# the executable and other options             #    
# in a specification dictionnary               #
# and send it to                               #
# the final submission "level" : fcc_batch     #
#**********************************************#

def run(self):
    

    chosen_batch = launchGUI.my_file_sys.chosen_batch


    specification = {}
    specification['batch'] = chosen_batch


    fcc_output_file = self.ofile_txt.get()
    
    batch_original_arguments = self.batch_args_txt.get()
    
    stdout = self.stdout_txt.get()
    stderr = self.stderr_txt.get()
    log = self.log_txt.get()
    outdir = self.outdir_txt.get()

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
        NOR = str(int(tempNOR)) if tempNOR != '' else ''
     
        tempNOE = self.NOE_txt.get()
        NOE = str(int(tempNOE)) if tempNOE != '' else ''
    
        

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
        specification['outdir'] = outdir

    
        #submit configuration
        batch.submit_bash(launchGUI.my_file_sys,specification)

    except ValueError:
        message = "Please enter a valid number"
        display_error_message('Error',message)


#*************************************#
# Function name : initialize_popup    #
# input : folder type                 #
# role : look for stdout,stderr,log   #
# and initializes corresponding popup #
#*************************************#

def initialize_popup(self,who):


    result_folder, batch_folder, stdout_folder, error_folder , log_folder, outdir_folder = launchGUI.my_file_sys.get_workspace()
  

    if who == 'log':

        show_popup(log_folder,'.log',self.log_scrolltext,self.popup_log)

    elif who == 'output':
        show_popup(stdout_folder,'.out',self.output_scrolltext,self.popup_output)
  
    elif who == 'error':
        
        show_popup(error_folder,'.err',self.error_scrolltext,self.popup_error)

    elif who == 'history':
        
        since = self.from_txt.get().split(' ') if '' != self.from_txt.get() else ''
        to = self.to_txt.get().split(' ') if '' != self.to_txt.get() else ''
      
        if since != '':
            since += to
        else:
            since = to
               
        show_popup(None,since,self.history_scrolltext, self.popup_history)
        
#****************************************#
# Function name : show_popup             #
# input : popup type                     #
# role : display stdout,stderr,log popup #
#****************************************#

def show_popup(folder,extension,scrolltext,popup):

    #display history, the function already read the file in the default folder
    if None == folder:
        #extension becomes : args from to
        file_content = launchGUI.my_file_sys.display_history(extension,True)
    else:
    #try to look log,output,error in respective folders
        job_id = launchGUI.my_file_sys.current_job_id

        file_content = launchGUI.my_file_sys.read_from_file(folder + '/job.' + job_id + extension)
    
    if False is not file_content :

        what = file_content

        actual_content = scrolltext.get(1.0, tk.END)

        #delete content of last submission if there exist
        if actual_content != '' : scrolltext.delete(1.0, tk.END)

        #insert content of file in text widget
        scrolltext.insert(tk.END,what)
    

        #show it
        popup.update()
        popup.deiconify()
        #put on the front
        popup.lift()
        #put focus on it
        popup.focus_force()





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

    program_label = tk.Label(popup, text='FCC SUBMIT v1.0 by FCC group',font=LARGE_FONT)
    program_label.place(x=80,y=10)

    image_filename = 'fcc.png'    

    if os.path.isfile(image_filename):

        img = ImageTk.PhotoImage(Image.open(image_filename))
        panel = tk.Label(popup, image = img)

        panel.place(x=80,y=60)

    informations = """

SOFTWARE INFORMATIONS     
                               
                   Property of CERN               
                               
EP-SFT Group (Experimental Physics - SoFTware)             
                               
Simplified Submission Script for using Batchs systems       
at CERN.                           
                               
FCC group can use it to run jobs on LXBatch.       
                               
This script provides a simple interface for the submission 
of jobs on HtCondor or LSF Batch :                        
                               
-> A simple way to submit a job :                   
  ie. python fcc_submit.py --gui               
                               
                               
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

        
        specification = launchGUI.my_file_sys.import_specification(filename)

        if False is not specification :
    
            [chosen_batch, fcc_executable, fcc_conf_file ,fcc_output_file, NOR , NOE , fcc_input_files ,batch_original_arguments, stdout, stderr, log, outdir]  =  specification
            
            
    
            self.exec_txt.set(fcc_executable)
            self.conf_txt.set(fcc_conf_file)
            self.ofile_txt.set(fcc_output_file)
            self.NOR_txt.set(NOR)
            self.NOE_txt.set(NOE)
            self.batch_args_txt.set(batch_original_arguments)
            self.stdout_txt.set(stdout)    
            self.stderr_txt.set(stderr)
            self.log_txt.set(log)
            self.outdir_txt.set(outdir)


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

    chosen_batch = launchGUI.my_file_sys.chosen_batch

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
        outdir = self.outdir_txt.get()

        files = list(self.files_listbox.get(0, tk.END))
        fcc_input_files =  '' if not files else ' '.join(files)
        

        specification_values = [chosen_batch, fcc_executable, fcc_conf_file, fcc_output_file, NOR, NOE, fcc_input_files,batch_original_arguments,stdout,stderr,log, outdir]
                
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
        
    #print batch
    
    if batch == 'lsf':
        self.LSF_button.configure(bg = "green")    
        self.HTCondor_button.configure(bg = "grey")
        self.log_view_button.configure(state=tk.DISABLED) 
    else:
        self.LSF_button.configure(bg = "grey")    
        self.HTCondor_button.configure(bg = "green")
        self.log_view_button.configure(state=tk.NORMAL)
    
    launchGUI.my_file_sys.chosen_batch = batch



    



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


        outdir_label = tk.Label(self, text="Output directory")
        outdir_label.place(x=10,y=190,width=200,height=20)

        self.outdir_txt = tk.StringVar()
        outdir_entry = tk.Entry(self,textvariable=self.outdir_txt)
        outdir_entry.place(x=230,y=190,width=200,height=20)

        search_outdir_button = tk.Button(self, text="...",command=lambda: open_dialog_box('dir','set_one',self.outdir_txt))
        search_outdir_button.place(x=430,y=190,width=60,height=20)
        
        
        NOR_label = tk.Label(self, text="Number of Runs")
        NOR_label.place(x=10,y=210,width=200,height=20)


        self.NOR_txt = tk.StringVar()
        NOR_entry = tk.Entry(self,textvariable=self.NOR_txt)
        NOR_entry.place(x=230,y=210,width=200,height=20)

        NOE_label = tk.Label(self, text="Number of Events")
        NOE_label.place(x=10,y=230,width=200,height=20)

        self.NOE_txt = tk.StringVar()
        NOE_entry = tk.Entry(self,textvariable=self.NOE_txt)
        NOE_entry.place(x=230,y=230,width=200,height=20)


        files_label = tk.Label(self, text="Input Files (Default AFS)")
        files_label.place(x=10,y=250,width=250,height=20)

        self.files_listbox = tk.Listbox(self)
        self.files_listbox.place(x=230,y=250,width=200,height=60)


        self.files_listbox.bind('<Double-1>', lambda _: self.delete_list_box_items(self.files_listbox))


        search_afs_files_button = tk.Button(self, text="...",command=lambda: open_dialog_box('file','set_many',self.files_listbox))
        search_afs_files_button.place(x=430,y=250,width=60,height=20)


        eos_file_label = tk.Label(self, text="Input File (other file system)")
        eos_file_label.place(x=10,y=310,width=200,height=20)

        self.eos_file_txt = tk.StringVar()
        eos_file_entry = tk.Entry(self,textvariable=self.eos_file_txt)
        eos_file_entry.place(x=230,y=310,width=200,height=20)


        add_eos_file_button = tk.Button(self, text="add",command=lambda: self.add_to_list_box_items(self.files_listbox,self.eos_file_txt.get()))
        add_eos_file_button.place(x=430,y=310,width=60,height=20)


        batch_args_label = tk.Label(self, text="Batch additionnal arguments")
        batch_args_label.place(x=10,y=340,width=200,height=20)

        self.batch_args_txt = tk.StringVar()
        batch_args_entry = tk.Entry(self,textvariable=self.batch_args_txt)
        batch_args_entry.place(x=230,y=340,width=200,height=20)


        batch_label = tk.Label(self, text="Batch system choice")
        batch_label.place(x=10,y=360,width=200,height=20)


        self.LSF_button = tk.Button(self, text ="LSF", relief=tk.RIDGE,command=lambda: set_gui_batch(self,'lsf'))
        self.LSF_button.place(x=230,y=370,width=70,height=40)

        self.HTCondor_button = tk.Button(self, text ="HTCondor", relief=tk.RIDGE,command=lambda: set_gui_batch(self,'htcondor'))
        self.HTCondor_button.place(x=320,y=370,width=70,height=40)


        self.popup_log = tk.Toplevel()
        self.popup_log.title('LOG')    
        self.popup_log.protocol("WM_DELETE_WINDOW", self.popup_log.withdraw)
        self.popup_log.withdraw()

        self.popup_log.minsize(400,400)


        self.log_scrolltext = ScrolledText(self.popup_log)
        self.log_scrolltext.pack(fill=tk.BOTH,expand=True)


        self.log_view_button = tk.Button(self, text="Log",state=tk.DISABLED,command=lambda: initialize_popup(self,'log'))
        self.log_view_button.place(x=300,y=420,width=60,height=40)


        self.popup_output = tk.Toplevel()
        self.popup_output.title('OUTPUT')    
        self.popup_output.protocol("WM_DELETE_WINDOW", self.popup_output.withdraw)
        self.popup_output.withdraw()

        self.popup_output.minsize(400,400)

        self.output_scrolltext = ScrolledText(self.popup_output)
        self.output_scrolltext.pack(fill=tk.BOTH,expand=True)

        stdout_view_button = tk.Button(self, text="Output",command=lambda: initialize_popup(self,'output'))
        stdout_view_button.place(x=360,y=420,width=60,height=40)

        self.popup_error = tk.Toplevel()
        self.popup_error.title('ERROR')
        self.popup_error.protocol("WM_DELETE_WINDOW", self.popup_error.withdraw)
        self.popup_error.withdraw()

        self.popup_error.minsize(400,400)

        self.error_scrolltext = ScrolledText(self.popup_error)
        self.error_scrolltext.pack(fill=tk.BOTH,expand=True)


        stderr_view_button = tk.Button(self, text="Error",command=lambda: initialize_popup(self,'error'))
        stderr_view_button.place(x=420,y=420,width=60,height=40)    

        run_button = tk.Button(self, text="RUN",command=lambda: run(self))
        run_button.place(x=230,y=420,width=60,height=40)
    
        self.is_history = tk.IntVar()

        display_history_cb = tk.Checkbutton(self, text = "history", onvalue = 1, offvalue = 0, variable = self.is_history, height=5,width = 20,command=lambda: self.change_history_state())
        display_history_cb.place(x=10,y=380)
        
        self.from_label = tk.Label(self, text="from")

        self.from_txt = tk.StringVar()
        self.from_entry = tk.Entry(self,textvariable=self.from_txt)

        self.to_label = tk.Label(self, text="to")

        self.to_txt = tk.StringVar()
        self.to_entry = tk.Entry(self,textvariable=self.to_txt)


        self.popup_history = tk.Toplevel()
        self.popup_history.title('HISTORY')
        self.popup_history.protocol("WM_DELETE_WINDOW", self.popup_history.withdraw)
        self.popup_history.withdraw()

        self.popup_history.minsize(400,400)

        self.history_scrolltext = ScrolledText(self.popup_history)
        self.history_scrolltext.pack(fill=tk.BOTH,expand=True)


        self.history_button = tk.Button(self, text="display",command=lambda: initialize_popup(self,'history'))

        set_gui_batch(self,'htcondor')

    def change_history_state(self):
    
        if not self.is_history.get():

            self.from_label.place_forget()
            self.from_entry.place_forget()
            self.to_label.place_forget()
            self.to_entry.place_forget()
            self.history_button.place_forget()
        else:       

            self.from_label.place(x=10,y=480,width=70,height=20)
            self.from_entry.place(x=80,y=480,width=120,height=20)
            self.to_label.place(x=200,y=480,width=70,height=20)
            self.to_entry.place(x=270,y=480,width=120,height=20)
            self.history_button.place(x=400,y=480,width=60,height=20)

    #delete file on listbox
    def delete_list_box_items(self,listbox): 
        #get selected line index
        selection = listbox.curselection()
        if selection:        
            index = selection[0]
            listbox.delete(index)

    #add file on listbox
    def add_to_list_box_items(self,listbox,item): 
        listbox.insert(tk.END,item)




#if you want to call the script independantly of the CLI
#**************************** MAIN START ************************************#

#user libraries
#import fcc_file_system as filesys
#my_file_sys = filesys.FileSystem()

#we set the current interface type    
#my_file_sys.set_interface('gui')    

#we check fcc environnement 
#my_file_sys.init_fcc_stack()
    
#we launch the gui
#fcc_submit_gui.launchGUI(my_file_sys)

#launchGUI()    

#****************************** MAIN END ************************************#


