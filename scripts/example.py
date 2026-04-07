import os #import the OS module to allow access to file management
import sys #module for interaction with the system
os.chdir("../../UCF-PCMS-SD/") #set the working directory to the UCF-PCMS-SD folder
from mainlib import writecfg, readcfg, relayinit, relaytoggle, relayreset #import the mainlib functions and variables

paramlist = ['list','your','needed','parameters','here'] #a list with the name 'paramlist' is checked by the front-end to see what variables the program requires

def run(mode=0): #To allow this to be ran via the PCMS control panel, include a run function. A variable like "mode" can be used to define different conditions for the run function.
    if mode == 0: #here the "mode" variable can be used to define a default mode for the automated GUI call while
        data = readcfg("User Input Parameters",'list') #use the readcfg function to get the contents of the list parameter
        data = float(data) #the contents of the data will be returned as a string by default, so it must be converted to the desired form
        
        ans = input("Provide an input >") #stores a user input string as "ans"
        writecfg("Example","UserInput",ans) #use the writecfg function to write to the user config in the form (section, variable, data).
        
        relayinit() #this function will initialize the relay with the pins in the order listed in the relay_pins variable
        relaytoggle(2,3,4) #this function will toggle on or off the relay using the `not` function. It accepts multiple inputs at a time.
        relayreset() #this function will toggle off all of the relays, you can use it at the end of a script to ensure there are no "hot" pins.
    
    if mode == 1: #a mode of 1 will instead do a different set of inputs.
        print("this was ran as the main file!")
        

if __name__ == '__main__': #this command will run the contents of itself only if this script is ran directly (i.e., not through the front-end)
    run(1) #we can pass the mode as 1 to run a different set of commands when the front-end is not in use, this is especially effective when delegating
           #different sections of the script to its own functions that can be called with ease within both modes 0 and 1.        
    
sys.exit() #this command will ensure the program exits properly if ran by itself
