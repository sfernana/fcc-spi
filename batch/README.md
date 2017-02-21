# Getting Started with FCCBATCH


Contents:

  * [FCCBATCH](#fccbatch)
    * [Overview](#overview)
    * [1 - Existing Infrastructure](#1---existing-infrastructure)
      * [a - Cluster](#a---cluster)
      * [b - Batch Management Software](#b---batch-management-software)
    * [2 - FCCBATCH](#2---fccbatch)
      * [a - Objective of this repository](#a---objective-of-this-repository)
      * [b - Script Options](#b---script-options)
    * [3 - Prerequisites](#3---prerequisites)
      * [a - BATCH access](#a---batch-access)
      * [b - Setting up FCC environment](#b---setting-up-fcc-environment)
    * [4 - FCCBATCH Installation](#4---fccbatch-installation)
    * [5 - Example](#5---example)
      * [a - FCCPHYSICS on BATCH from CLI](#a---fccphysics-on-batch-from-cli)
      * [b - FCCPHYSICS on BATCH from GUI](#b---fccphysics-on-batch-from-gui)
    * [6 - Get Back Results](#6---get-back-results)
  



## Overview


## 1 - Existing Infrastructure


### a - Cluster

	
Cern is equiped with a batch computing service consisting of around 120,000 CPU cores. 
A such power is essential to run CERN experiments, tasks such as physics event reconstruction, data analysis and simulation available for all users of the system.

### b - Batch Management Software

Such clusters of computers are managed by workload management platforms acting as **job schedulers** like :

- LSF developped by IBM
- HTCondor developped by Wisconsin's University

CERN has experienced during a while LSF platform and now they are migrating to HTCondor platform.


## 2 - FCCBATCH


### a - Objective of this repository


Before using the BATCH services, you need to fullfill the prerequisites. This repository is a set of python scripts that permit you to submit a job without reading the documentation of any Batch systems.
It aims to offer you an abstraction in submitting jobs to the cluster in the simplest way.
Indeed, we did the work for you in reading documentation of how to use batch services at CERN, but if you feel the need to use a specific Batch platform with your own script, you can begin with this tutorial :

[FccCondor](https://github.com/sfernana/fcc-tutorials/blob/master/FccCondor.md)


At the end of this tutorial, you will be able from your seat to run a job on a machine located somewhere at CERN among 120,000 CPU cores without paying attention about **HOW** it works.
Once the job will finish, in principle the system will get back the results to the submitted working directory. You can switch off your machine, go to home and come back once you feel that the results are available.



### b - Script options


![IMAGE NOT AVAILABLE](https://github.com/sfernana/fcc-spi/tree/master/batch/tutorial_images/help.png "options")


In order to submit a 'valid' job, you have to provide at least :

-	an executable
-	a configuration file

## 3 - Prerequisites


### a - BATCH access



To be authorized to use the BATCH, you need to have access to LXPLUS service which is the interactive logon service to Linux for all CERN users. 

The cluster LXPLUS consists of public machines provided by the IT Department for interactive work.

All machines offer access to the usual public services like (Non-exhaustive list) :

-	AFS home directories
-	Batch systems at CERN (HTCondor, LSF)



### b - Setting up FCC environment



Log in to LXPLUS via ssh from a shell or software such as Putty if you are running windows and execute the following command :

	source /afs/cern.ch/exp/fcc/sw/0.8pre/setup.sh

The script setup.sh available on AFS as on CVMFS contains informations about all softwares used by FCC group and whose the job may need.

FCCBATCH does not really need a pre-checking because the job will run on a worked node on the cluster.

So this step will be already added by FCCBATCH before the execution of the job on the worker node.

FCCBATCH requires to set up environment locally in order to check locally the correctness of the command provided by the user job before sending the job to the batch.
Like that, FCCBATCH ensure to send an "error-less job" in order to avoid the user waiting for a bad job and wasting his time. 


## 4 - FCCBATCH Installation



```

mkdir -p $HOME/FCCBATCH
cd $HOME/FCCBATCH
git clone https://github.com/sfernana/fcc-spi.git
cd fcc-spi/batch


```

## 5 - Example




### a - FCCPHYSICS on BATCH from CLI


In this simple example, we want to run **FCC PHYSICS** on the BATCH from the command line interface.

In this case, the executable and the configuration file are stored in a public AFS folder.

You can also run your own executable and configuration file located in your user space.


```


#submit fcc-physics job on htcondor (you can replace htcondor by lsf)
./fcc_submit.py --batch htcondor --exec fcc-pythia8-generate  --conf "/afs/cern.ch/exp/fcc/sw/0.7/fcc-physics/0.1/x86_64-slc6-gcc49-opt/share/ee_ZH_Zmumu_Hbb.txt"


#check history
#./fcc_submit.py --hist 11/24/16 11:49:27 11/24/16 11:50:30


#for more options
#./fcc_submit.py --help 


```


### b - FCCPHYSICS on BATCH from GUI

And now another way to run **FCC PHYSICS** :


```

#launch gui
./fcc_submit.py --gui


```

It will open a GUI, and you can fill manually the fields of the GUI or import an existing specification file like [fccphysics.spec](https://github.com/sfernana/fcc-spi/blob/master/batch/fccphysics.spec) 
provided on this repository by doing Menu -> Import

Then click **RUN** to submit the job !


![IMAGE NOT AVAILABLE](https://github.com/sfernana/fcc-spi/tree/master/batch/tutorial_images/fcc_gui_fccphysics.png "fccphysics")

Congratulations !!!

You ran FCC softwares on the BATCH.


## 6 - Get Back Results

Results are automatically retrieved in the current working directory from which you submitted your job. 
You can specify the output directory by the **--outdir** options in the CLI or by the field **Output directory** in the GUI.


Now you get familiar with the CERN batchs services, we can go up one level in using the GRID system with this tutorial :

[FCCDIRAC](https://github.com/sfernana/FCCDIRAC)



For any questions or any further informations, please contact us at : fcc-experiments-sw-devATSPAMNOTcern.ch






