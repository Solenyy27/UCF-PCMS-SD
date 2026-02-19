#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import time

paramlist = ['length', 'width', 'height']

def ping(): #debug tool to ensure connection with the script is possible.
    print("ping successful")
    
def run(mode=0):
    from mainlib import yesno
    from mainlib import writecfg
    writecfg('TEST','test',0)
    if mode == 1:
        print("Doing Something")
        time.sleep(1)
        print("Continuing to Next Item")
        time.sleep(1)
        print("All Good?")
        if yesno() == 1:
            print("Returning Successful Test")
            return 2
        else: 
            print("Returning Unsuccessful Test")
            return 3
    
        
    


