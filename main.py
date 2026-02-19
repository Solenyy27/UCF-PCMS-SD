#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from mainlib import *

### Program ###
prgmstart()

while(1==1):
    ### get sample name and sample ###
    nameprompt() #run nameprompt
    namepath = "output/"+sample.sname+"/" #set path for files with matching sample name
    mkdir(namepath) #make directory for sample name
    sample.cfgpath = namepath+sample.sname+'_config.ini' #store config path for use in write/read config
    initcfg() #initializes config file by blanking the ini file associated with the name
    testprompt() #prompt user for which tests they want to run
    defineparams() #prompt user for needed parameters
                
    
    
    #todo general
    '''
    get SMU, Solar sim, and camera devices and set a variable to communicate with them
    '''

    if exitprompt() == 1:
        break
    else:
        continue
sys.exit() #Exit command just in case