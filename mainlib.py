#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys as sys #module for dealing with memory and file stuff
sys.path.insert(0,'../UCF-PCMS-SD')
sys.path.append('./TestScripts')
import os #module for file pathing
import configparser #module for config files as .ini
import time
import glob


flaglist = [] #create an empty flag list

for file in glob.glob("./TestScripts/*.py"): #check the TestScripts directory for user scripts
    if file == "./TestScripts/__init__.py" or file == "./TestScripts/example.py": #skip the __init__ and example files.
        continue
    namestuff = file.split("/")
    name = namestuff[2].split(".")
    flaglist.append(name[0]) #add the name stripped from full file name to script list
    exec('import TestScripts.'+name[0]+' as '+name[0]) #import the user script as its own name

            
##########################################################
class sample: #define the class "sample" to hold data about where and what the sample has/will do
    #flag value of 0 = not set, 1 = set to be done, 2 = completed successfully, 3 = completed unsuccessfully

    def __init__(self): #initialize the class with list of a list of flags from flaglist with a default value of 0
        self.flags = []
        for i in flaglist:
            self.flags.append([i,0])
            
    def setflag(self,flag,val): #function for setting individual flag values
        for j in self.flags:
            if j[0] == flag:
                j[1] = val
                return
            else:
                continue
        print(f"Error: No flag matching name {flag} was found.")
        
    def chkflag(self,flag): #function for checking individual flag values
        for j in self.flags:
            if j[0] == flag:
                return j[1]
            else:
                continue
        print(f"Error: No flag matching name {flag} was found.")
    
    def clearflags(self): #separate from __init__ bc i'm unsure of if that would break anything lol
        self.flags = []
        for i in flaglist:
            self.flags.append([i,0])
    
    def flagsum(self): #return the sum of what all flags are set to
        amnt = 0
        for i in self.flags:
            amnt += i[1]
        return amnt
            
    sname = str() #name of sample
    cfgpath = str() #config location for sample
##########################################################

sample = sample() #initializes sample as a sample class object that can be viewed and edited by all other scripts

#valid yes/no answers... coulda just used .upper but whatever
yes = ['Y','y','yes','Yes']
no = ['N', 'n', 'no', 'No']

def yesno(*err): #General function for Y/n, recurse for invalid
    if err == 1:
        ans = str()
        print("Invalid Input")
    ans = input('[Y/n]>')
    if ans in yes:
        return(1)
    if ans in no:
        return(0)
    else:
        return yesno(1)
        
def nameprompt(): #Prompts for new name, recurse for no during confirm
    print("Please input a new sample name:")
    name = input(">")
    if name == sample.sname:
        print("Name already in use. Continue anyways? (this will overwrite any data taken)")
        ans = yesno(0)
        if ans == 1:
            sample.sname = name
            print(f"Files will be stored as \"{sample.sname}_Testname.filetype\".")
            return
        if ans == 0:
            nameprompt()
            return
    print("Confirm sample name?")
    ans = yesno(0)
    if ans == 1:
        sample.sname = name
        print(f"Files will be stored as \"{sample.sname}_Testname.filetype\".")
        return
    if ans == 0:
        nameprompt()
        return
    
def testprompt(e=0): #prompts user for test to run
    sample.clearflags()
    valid = 0
    amnt = 0
    lst = str()
    chk = str()
    
    if e == 1: #recurse statement for invalid input
        print("Invalid Input, Please Try Again")
    if e == 0: #default statement
        print("Please select the test to be performed:")
    if e == 2: #recurse statement for discard input
        print("Discarding inputs, please select again.")
    
    print("Valid inputs:",end="")
    for i in sample.flags:
        print(f"{i[0]} ",end="")
    print("(separate inputs by space)")
    
    ans = input(">")
    lst = ans.split() #split answer by spaces, set flags based on input
    
    for chk in lst: #for each part of user input check string
        chk = chk.upper() #convert string to upper case to make sure things can match
        for i in sample.flags: #check for if an input matches the flags set in sample class
            if chk == i[0].upper():
                print(f"Selection: {i[0]}")
                i[1] = 1
                valid = 1
                amnt = amnt + 1
    
    if amnt == 0:
        print("No tests have been selected, confirming selection(s) will exit the program.")
        
    if valid == 0: #recurse if no valid string found
        testprompt(1)
        return

    for flag in flaglist: #after tests have been selected, check for testlist selections
        tstname = eval(flag)
        if sample.chkflag(flag) == 1 and hasattr(tstname, 'testlist'):
            for i in tstname.testlist:
                sample.setflag(i,1) #set the flags for each individual test in flag.testlist to 1
            if hasattr(tstname, 'run') == False:
                sample.setflag(flag, 0) #set the flag for the script to false if file containing testlist has no test

    if valid == 1: # if a valid selection was chosen, confirm
        print("Confirm Selection(s)?")
        yn = yesno(0) #yesno to confirm selections
        if yn == 1:
            return
        if yn == 0:
            testprompt(2) #recurse w/ no error to reinput responses
            return

def initcfg(): #initializes cfg file by blanking the ini file associated with sample.cfgpath
    config = configparser.ConfigParser()
    with open(sample.cfgpath,'w') as configfile:
        config.write(configfile)
    
def writecfg(section, var, val): #write config data to .ini file
    val = str(val)
    config = configparser.ConfigParser()
    config.read(sample.cfgpath)
    try: #attempt to add section, if it already exists (returns exception), pass to next
        config.add_section(section)
    except:
        pass
    config.set(section,var,val)
    with open(sample.cfgpath,'w') as configfile: #write data into config
        config.write(configfile)
    
def readcfg(section, var): #read config data from .ini file and returns sample, must be converted to desired form from str.
    config = configparser.ConfigParser()
    config.read(sample.cfgpath)
    return config[section][var]

def mkdir(path): #creates directory if it does not exist
    if not(os.path.exists(path) and os.path.isdir(path)):
        try:
            os.makedirs(path)
        except PermissionError:
            print(f"Permission denied: Unable to create directory.")
        except Exception as e:
            print(f"An error occurred: {e}")
    print(f"Created directory ~/{path}")
    return        
    
def prgmstart(): #Basic greeting logo
    f = open('logo.txt', 'r')
    file_cont = f.read()
    print(file_cont)
    f.close

def defineparams():
    paramdict = {} #create an empty dictionary to store needed parameters
    for test in flaglist: #define user vlaues
        tstname = eval(test)
        if sample.chkflag(test) == 1 and hasattr(tstname, 'paramlist'): #check for paramlist elements
            for item in tstname.paramlist:
                if item not in paramdict: #if parameter not already recorded in dictionary, have user define value
                    print(f"Please define a value for {item}")
                    ans = input(">")
                    ans = float(ans) #convert to float
                    paramdict[item]=ans #add float vlaue to paramdict
                writecfg(test,item,paramdict[item]) #write user inputted parameters to the config

def paramprompt(e=0):
    skp = 0
    if e == 1:
        print("Something went wrong")
        print(f"Debug: skipto {skp}")
    
def exitprompt(e=0):
    if e == 1:
        Print("Something Went Wrong")
    print("Would you like to test another sample?")
    ans = yesno(0)
    if ans == 1:
        return 0
    if ans == 0:
        return 1

