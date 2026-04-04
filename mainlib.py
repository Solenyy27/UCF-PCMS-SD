#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys as sys #module for dealing with memory and file stuff
sys.path.insert(0,'../UCF-PCMS-SD')
sys.path.append('./scripts')
import os #module for file pathing
import configparser #module for config files as .ini
import glob
try:
    import RPi.GPIO as GPIO
except Exception as e:
    print(e)

flaglist = [] #create an empty flag list

for file in glob.glob("./scripts/*.py"): #check the TestScripts directory for user scripts
    if file == "./scripts/__init__.py" or file == "./scripts/example.py": #skip the __init__ and example files.
        continue
    namestuff = file.split("/")
    name = namestuff[2].split(".")
    flaglist.append(name[0]) #add the name stripped from full file name to script list
    exec('import scripts.'+name[0]+' as '+name[0]) #import the user script as its own name


#----------------
# Flag holder class
#----------------
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

sample = sample() #initializes sample as a sample class object that can be viewed and edited by all other scripts

#valid yes/no answers... coulda just used .upper but whatever
yes = ['Y','y','yes','Yes']
no = ['N', 'n', 'no', 'No']

#----------------
# Relay Control
#----------------
try:
    relay_pins = [17, 18, 27, 22, 23, 24, 12, 16] #Relay pins listed in order of their use (relays 1,2,3,...)
    relay_states = [GPIO.HIGH, GPIO.HIGH, GPIO.HIGH, GPIO.HIGH, GPIO.HIGH, GPIO.HIGH, GPIO.HIGH, GPIO.HIGH] #corresponding states of each relay
except:
    pass

def relayinit(): #initializes GPIO for relay
    GPIO.setmode(GPIO.BCM) #sets the pin communication mode to BCM (pins addressed by numbers from pinout)
    for pin in relay_pins:
        GPIO.setup(pin, GPIO.OUT) #sets the pins to be outputs
    for i in range(len(relay_pins)):
        GPIO.output(relay_pins[i], relay_states[i]) #outputs signal to designated pin via GPIO.output(pin,state)
    print(relay_states) #prints the current relay states (1 is high, 0 is low); Switches toggled on when set to low

def relaytoggle(relay): #function for toggling relay as numbered 1 through 8
    relaynum = int(relay) - 1 #subtract 1 from user input to account for arrays starting at 0 instead of 1 e.g., 8 is actually array value 7
    relay_states[relaynum] = not relay_states[relaynum] #uses the not function to invert True/False to False/True
    for i in range(len(relay_pins)): #sets pins to designated state
        GPIO.output(relay_pins[i], relay_states[i])
        
def relayreset(): #resets relay to the default position
    for i in range(len(relay_pins)): #sets all relay states to high
        relay_states[i] = GPIO.HIGH
    for i in range(len(relay_pins)): #sends relay states to GPIO for each pin
        GPIO.output(relay_pins[i], relay_states[i])



#----------------
# Scripting Functions
#----------------

def yesno(err=0): #General function for Y/n, recurse for invalid
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
        
def nameprompt(name): #Prompts for new name, recurse for no during confirm
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
        yn = yesno() #yesno to confirm selections
        if yn == 1:
            return
        if yn == 0:
            testprompt(2) #recurse w/ no error to reinput responses
            return

#----------------
# CFG Control
#----------------
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
            print("Permission denied: Unable to create directory.")
        except Exception as e:
            print(f"An error occurred: {e}")
    print(f"Created directory ~/{path}")
    return        
    
def prgmstart(): #Basic greeting logo
    f = open('logo.txt', 'r')
    file_cont = f.read()
    print(file_cont)
    f.close
    
paramdict = {}
def listparams():
    for i in flaglist:
        tstname = eval(i)
        if sample.chkflag(i) == 1 and hasattr(tstname, 'paramlist'):
            for item in tstname.paramlist:
                paramdict[item] = None
            writecfg(i,item,paramdict[item])

def defineparams():
    paramdict = {} #create an empty dictionary to store needed parameters
    for i in flaglist: #define user vlaues
        tstname = eval(i)
        if sample.chkflag(i) == 1 and hasattr(tstname, 'paramlist'): #check for paramlist elements
            for item in tstname.paramlist:
                if item not in paramdict: #if parameter not already recorded in dictionary, have user define value
                    print(f"Please define a value for {item}")
                    ans = input(">")
                    ans = float(ans) #convert to float
                    paramdict[item]=ans #add float vlaue to paramdict
                writecfg(i,item,paramdict[item]) #write user inputted parameters to the config


def testsort():
    for i in flaglist: 
        tstname = eval(i)
        if sample.chkflag(i) == 1:
            order.append(i)
            if hasattr(tstname, 'needlist'): #checks for needlist in each flagged test
                for item in tstname.needlist:
                    try: #try to append to list of the item
                        needs[item].append(i)
                    except KeyError: #if no list exists, create it
                        needs[item] = [i]
            if hasattr(tstname, 'givelist'): #checks for givelist in each flagged test
                for item in tstname.givelist:
                    gives[item] = i #each givelist variable can only be given by one script

    needls = []
    givels = []
    
    for i in list(needs.values()):
        for j in i:
            needls.append(j)
    print(needls)
    for i in list(gives.values()):
        givels.append(i)
    print(givels)
    
    for i in order:
        if i not in needls:
            orderout.append(i)
        else:
            ordermid.append(i)
    for i, tst in enumerate(ordermid):
        try:    
            nxt = ordermid[i+1]
        except:
            pass
# todo clean this up its so bad


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

