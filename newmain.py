#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtSerialPort import QSerialPort
from PySide6.QtCore import QIODeviceBase, Slot, Signal, Qt, QThread, QObject, QEvent, QRunnable, QThreadPool
from PySide6.QtGui import QPalette, QFocusEvent, QKeySequence, QShortcut, QMouseEvent
from PySide6.QtWidgets import (
QMainWindow, QApplication, QWidgetAction, QWidget, QGroupBox, QDockWidget, QGridLayout, QLabel,
QVBoxLayout, QTextEdit, QPlainTextEdit, QPushButton, QDialog, QLineEdit, QComboBox
)
import glob
import serial
import xtralien
import traceback
try:
    from picamera2 import Picamera2, Preview
except Exception as e:
    print(e)

from mainlib import *
from mainlib import sample
importuserlibs()

try:
    import RPi.GPIO as GPIO
except Exception as e:
    print(e)
import sys
sys.path.insert(0,'../UCF-PCMS-SD')
sys.path.append('./scripts')


try:
    app = QApplication(sys.argv)
except:
    app = QApplication.instance()
    



#----------------
# Console Menu
#----------------
"""
somehow implement a ipykernel console as a subthread/multithread or something
or have scripts send data to some variable to update text that is printed to the screen
overall just have some method of showing the outputs of user scripts while they are run
and have a play button here or on the playlist to start user script w/ popup menu that says "are you sure"
"""
"""
#
# Currently Scrapped! Run with spyder console or traditional python3 -m.
#

class SubprocessWorker(QThread):
    output_line = Signal(str)
    finished_signal = Signal(int) #exit code
    
    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        process = subprocess.Popen(
            self.command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        for line in process.stdout:
            self.output_line.emit(line.rstrip())
            
        process.wait()
        self.finished_signal.emit(process.returncode)

#in the worker thread do subprocess.call(['python', 'somescript.py', somescript_arg1, somescript_val1,...]) or use 'pyhton3', f'{script}' and change value in script to change program targeted.
##fix tmrrw; merge subprocess in and out w/ widget to create one thingy
class SubprocessOut(QPlainTextEdit):
    UsrControl = 1
    usrstr = ""
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.worker = None
 
    def run_command(self):
        if self.worker is not None:
            return
        self.worker = SubprocessWorker(
            "python3", f'{something.py}')
        self.worker.output_line.connect(self.on_output_line)
        self.worker.finished_signal.connect(self.on_finished)
        self.worker.start()
        
    def on_output_line(self,text):
        self.appendPlainText(text)
    
    def on_finished(self, exit_code):
        self.appendPlainText(f"--- Process finished  (exit code {exit_code}) ---")
        self.worker = None
    
            
class SubprocessIn(QLineEdit):
    def __init__(self):
        super().__init__()
        self.setText("$  ")
        self.installEventFilter(self)
        

            
        return 
        
    def DoLineIn(self, *args):
        ans = self.text()
        ans = ans.strip("$")
        self.setText("$  ")
        
class SubprocessWidget(QWidget):
    def __init__(self):
        super().__init__()
        grid = QGridLayout()
        self.setLayout(grid)
        subprocin = SubprocessIn()
        grid.addWidget(SubprocessOut(),0,0)
        grid.addWidget(subprocin,1,0)
"""

        
    
#----------------
# Playlist Menu
#----------------
"""
#todo
create a list of entries that can be clicked or dragged on buttons to change their order
list above the playlist has items which can be selected to set their state to checked() and adds them to the playlist
use a .ini file for the whole program to keep track of the order upon exit and reload of the program (along with other vars)
"""
#----------------
# Sample Window
#----------------
"""
#todo

create a window that lets you set the sample name sample.name() from mainlib
has set directory button next to it to create the output directory and initial config file
warning if named .ini is already found

bottom of this central window should house the parameters editing section

either: display of the .ini that is updated after user input
or
list of fields (w/ scrollbar) that can be edited
"""


class WSignals(QObject): #defines signals that can be given off by Worker when completed
    finished = Signal(int) #gets just thread_id
    error = Signal(str)
    result = Signal(object)
    progress = Signal(tuple) #gets thread_id, progress_value

class Worker(QRunnable): #generic QThread runner example

    @Slot()
    def run(self): #VV call function to be ran in parallel in terminal hereVV
        while(True):
            ans = input(">")
            if ans == 'exit':
                break
            try:
                exec(ans)
            except Exception as e:
                print(e)
            


class ThreadEnabledWidget(QGroupBox):
    grid = QGridLayout()
    threadpool = QThreadPool() #must define threadpool for workers pre __init__
    button = QPushButton()
    ding = True
    
    def __init__(self):
        super().__init__()
        self.setLayout(self.grid)
        self.button.setText("><")
        self.grid.addWidget(self.button)
        self.button.clicked.connect(self.withThread)
        
    def withThread(self): #use this method to call workers
        worker = Worker()
        self.threadpool.start(worker)
        
        
class filedropdown(QComboBox):
    itemlist = ["..."]
    itemcontents = []
    ran = 0
    namepathcontents = ""
    
    def __init__(self):
        super().__init__()
        for i in self.itemlist:
            self.addItem(i)
        self.ran = len(self.itemlist)
        #todo: get window cfg file for recently used paths to import into itemlist
        
    # def itemrefresh(self):
    #     for i in range(len(self.itemlist)):
    #         if self.itemlist[i] == "...":
    #             self.itemlist[i] = self.namepathcontents
    #         if self.namepathcontents not in self.itemlist:
    #             self.itemlist.append(self.namepathcontents)
            
    #     for i in self.itemlist:
    #         if i in self.itemrefresh()
        
    #     if len(self.itemlist) > self.ran:
    #         self.ran = len(self.itemlist)
    #         print("ding")
  #todo: fix asap
#just use glob.glob for this
#use the setfileloc function's mkdir to call this function
#then make this function scan glob.glob ./output for any changes
#add all current output folders to the list
#set the active item to be the one that matches the current output for namepath


class SampleFiles(QWidget):
    grid = QGridLayout()
    snamein = QLineEdit()
    fileloc = filedropdown()
    def __init__(self):
        super().__init__()
        self.setLayout(self.grid)
        self.installEventFilter(self)
        sampnamebox = QLabel("Sample Name")
        sampnamebox.setAlignment(QtCore.Qt.AlignLeft)
        self.grid.addWidget(sampnamebox,0,0)
        filenamebox = QLabel("File Location")
        sampnamebox.setAlignment(QtCore.Qt.AlignLeft)
        self.grid.addWidget(filenamebox,1,0)
        
        
  
        self.snamein.setAlignment(QtCore.Qt.AlignCenter)
        self.snamein.setPlaceholderText("Enter a Sample Name")
        self.grid.addWidget(self.snamein, 0,2)
        
        
        self.grid.addWidget(self.fileloc, 1,2)
        
    def setfileloc(self):
        sample.sname = self.snamein.text()
        namepath = "output/"+sample.sname+"/"
        self.fileloc.namepathcontents = namepath
        sample.cfgpath = namepath+sample.sname+'_config.ini' 
        mkdir(namepath)
        initcfg()
        self.fileloc.itemrefresh()
        
    #on save button or enter in QWidget:
        #do mkdir(namepath)
        #set sample.cfgpath
        #do cfginit()
        
        
    def eventFilter(self, target, event):
        if event.type() == QEvent.KeyRelease:
            if event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
                self.setfileloc()
        return super().eventFilter(target, event)
    



class SampleWidget(QGroupBox):
    def __init__(self):
        super().__init__()
        grid = QGridLayout()
        self.setLayout(grid)
        self.installEventFilter(self)
        grid.addWidget(SampleFiles(),0,0)

    
    def eventTrigger(self):
        not self.show() #change
        
    

    


#----------------
# Status Window
#----------------
class StatusWidget(QGroupBox): #create a group box element for the status notifications
    smustatus = 0 #define vars to track status of SMU and solar sim
    solstatus = 0
    grid = QGridLayout() #define grid layout to be used within the groupbox
    statlabels = (QLabel("SMU:"), QLabel("Solar Simulator:"), QLabel("Relay:")) #set lists of labels
    responselabels = (QLabel("..."),QLabel("..."),QLabel("..."))
    def __init__(self):
        super().__init__()
        self.setTitle("Connection Status") #set the title of the groupbox
        self.setAlignment(QtCore.Qt.AlignCenter) #set alignment of groupbox
        self.setLayout(self.grid) #set layout to be gridlayout
        for i in range(len(self.statlabels)):
            self.statlabels[i].setAlignment(QtCore.Qt.AlignRight) #sets the alignment of each element in statlabels
            self.grid.addWidget(self.statlabels[i],i,0) #adds each statlabel to an individual row
            self.responselabels[i].setStyleSheet("color: yellow;") #configures responselabels to be yellow
            self.responselabels[i].setAlignment(QtCore.Qt.AlignHCenter) 
            self.grid.addWidget(self.responselabels[i],i,1) #adds each response label to the next column
            self.rows = i #records the number of rows iterated through
        refreshbutton = QPushButton("Refresh Devices")
        refreshbutton.clicked.connect(self.refreshtrigger) #uses the Qt.Signal package to .connect() with the button and trigger the function refreshtrigger on click
        self.grid.addWidget(refreshbutton, self.rows+1,0, 1,2) #adds a button below the last created row
        self.refreshtrigger() #calls refreshtrigger once to get initial states of each item
        
    def refreshtrigger(self): #on refreshtrigger, check for SMU and sol and set status
        for device in glob.glob('/dev/serial/by-id/*'): #go through the serial folder
            if 'Source_Measure_Unit' in device: #connnect to devices with matching string contents in their name
                smu = xtralien.Device(device) #connects smu using xtralien
                self.smustatus = 1 #sets smu status to indicate that an SMU has been detected
                print(f'connection established with smu in {device}')
            if 'Solar-Sim' in device:
                sol = serial.Serial(device) #uses serial library to connect to solar sim in the same fashion
                self.solstatus = 1
                print(f'connection established with solar sim in {device}')
                sspower(0) #sets the solar sim power level to zero to turn off the lighting
                
        if self.smustatus == 0: #color and text for response labels is changed based on detection
            self.responselabels[0].setText("No Connection")
            self.responselabels[0].setStyleSheet("color: red;")
        elif self.smustatus == 1:
            self.responselabels[0].setText("Connected")
            self.responselabels[0].setStyleSheet("color: green;")
        if self.solstatus == 0:
            self.responselabels[1].setText("No Connection")
            self.responselabels[1].setStyleSheet("color: red;")
        elif self.solstatus == 1:
            self.responselabels[1].setText("Connected")
            self.responselabels[1].setStyleSheet("color: green;")
        try:
            relayinit()
            self.responselabels[2].setText("Connected")
            self.responselabels[2].setStyleSheet("color: green;")
        except:
            self.responselabels[2].setText("No Connection")
            self.responselabels[2].setStyleSheet("color: red;")

#----------------
# Camera Window
#----------------
class CameraWidget(QWidget): #creates the widget that handles the camera
    def __init__(self, parent=None):
        super(CameraWidget, self).__init__(parent)

        self.camera = picamera2.Picamera2() #this may have to be changed later, I am unsure.
        self.camera.sensor_mode = 2  # Choose sensor mode 2 for 640x480 resolution
        self.camera.configure(self.camera.create_preview_configuration(main={"size": (640, 480)}))
        self.camera.start()

        self.label = QLabel()
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(int(1000 / 24))

    def update_frame(self): #updates window frames to enabel video output
        image = self.camera.capture_image()
        image = image.convert("RGBA")
        data = image.tobytes("raw", "RGBA")
        qim = ImageQt(image)
        pix = PyQt5.QtGui.QPixmap.fromImage(qim)
        self.label.setPixmap(pix)

class CameraGroup(QGroupBox): #defines the window area for the camera controls
    def __init__(self, parent=None):
        super().__init__()
        grid = QGridLayout()
        self.setLayout(grid)
        self.setTitle("Camera Preview")
        self.setAlignment(QtCore.Qt.AlignCenter)
        try: #attempt to establish connection with the camera widget
            grid.addWidget(CameraWidget(),1,0) #idk why I define a grid; TODO check later.
        except Exception as e: #if no connection is found, shows an error message from exception instead.
            Error = QLabel(f"Error! \n {e}")
            Error.setStyleSheet("color: red;")
            Error.setAlignment(QtCore.Qt.AlignCenter)
            grid.addWidget(Error, 1,0)

class GroupBox(QGroupBox): #generic groupbox for testing purposes
    def __init__(self):
        super().__init__()
        grid = QGridLayout() #creates a grid for the widget
        self.setLayout(grid) # set the groupbox to use the grid layout
        contents = QLabel("test")
        grid.addWidget(contents,0,0) #add the qlabel to 0,0

    def title(self, Name):
        self.setTitle(str(Name))


#----------------
# Main Window Contents
#----------------
class MainWidget(QWidget): #Define the class for the main area within the main window
    def __init__(self):
        super().__init__()
        grid = QGridLayout() #define class QGridLayout to gridlayout
        self.setLayout(grid) #set the main window to use gridlayout

        
        leftContainer = QWidget() #defines a widget as a container to hold the first column of modules
        leftgrid = QGridLayout() #sets left module grid
        leftContainer.setLayout(leftgrid)
        leftgrid.addWidget(StatusWidget(),0,0) #VV adds left modules on top of one another, I could have used QVbox but I forgor VV
        leftgrid.addWidget(CameraGroup(),1,0)
        grid.addWidget(leftContainer,0,0,2,1) #adds the left container to the main widget
    
        centralrightContainer = QWidget() #defines the container to hold the right widgets, which take up two columns (2/3 the window space of the left container)
        crgrid = QGridLayout()
        centralrightContainer.setLayout(crgrid)
        crgrid.addWidget(SampleWidget(),0,0)
        crgrid.addWidget(GroupBox(),1,0)
        grid.addWidget(centralrightContainer,0,1,2,2)
        
debugmode = 0

class MainWindow(QMainWindow): #Define the class for the window
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("PCMS Control Panel") #sets window title
        self.setFixedSize(960, 540) #set x and y coords followed by window width and height; not resizeable because the program is rudimentary.
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, False)
        self.setWindowFlag(Qt.WindowType.WindowFullscreenButtonHint, False)
        self.args = args
        self.kwargs = kwargs
        self.setCentralWidget(MainWidget()) #sets the contents of the window to be the main widget and its contents
        self.show() #shows all components of QWidgets loaded into the main window
        
  
def run():
    window = MainWindow()
    app.exec()
    

#----------------
# MAIN
#----------------
if __name__ == "__main__":
    run()
sys.exit()




