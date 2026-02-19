#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import time


params = 'length','width','height'

def ping():
    print("ping successful")
    
def runtest(mode=1):
    from mainlib import yesno
    from mainlib import writecfg
    writecfg('TEST','test',0)
    if mode == 1:
        print("Doing Something")
        time.sleep(5)
        print("Continuing to Next Item")
        time.sleep(5)
        print("All Good?")
        if yesno() == 1:
            print("Returning Successful Test")
            return 2
        else: 
            print("Returning Unsuccessful Test")
            return 3
    
        
    


