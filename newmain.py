#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtSerialPort import QSerialPort
from PySide6.QtCore import QIODeviceBase, Slot, Signal, Qt, QThread, QObject, QEvent
from PySide6.QtGui import QPalette, QFocusEvent, QKeySequence, QShortcut
from PySide6.QtWidgets import (
QMainWindow, QApplication, QWidgetAction, QWidget, QGroupBox, QDockWidget, QGridLayout, QLabel,
QVBoxLayout, QTextEdit, QPlainTextEdit, QPushButton, QDialog, QLineEdit
)
import glob
import serial
import xtralien
import subprocess
try:
    from picamera2 import Picamera2, Preview
except Exception as e:
    print(e)

from mainlib import *
importuserlibs()

try:
    import RPi.GPIO as GPIO
except Exception as e:
    print(e)
import sys

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
            "python3")
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
        
    def eventFilter(self, target, event):
        if event.type() == QEvent.KeyRelease:
            if event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
                self.DoLineIn()
            
        return super().eventFilter(target, event)
        
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
        refreshbutton.clicked.connect(self.refreshtrigger) #when button is clicked, the refreshtrigger function is done
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
                
        if self.smustatus == 0: #color and text for responselabels is changed based on detection
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
class CameraWidget(QWidget):
    def __init__(self, parent=None):
        super(CameraWidget, self).__init__(parent)

        self.camera = picamera2.Picamera2()
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

    def update_frame(self):
        image = self.camera.capture_image()
        image = image.convert("RGBA")
        data = image.tobytes("raw", "RGBA")
        qim = ImageQt(image)
        pix = PyQt5.QtGui.QPixmap.fromImage(qim)
        self.label.setPixmap(pix)

class CameraGroup(QGroupBox):
    def __init__(self, parent=None):
        super().__init__()
        grid = QGridLayout()
        self.setLayout(grid)
        self.setTitle("Camera Preview")
        self.setAlignment(QtCore.Qt.AlignCenter)
        try:
            grid.addWidget(CameraWidget(),1,0)
        except Exception as e:
            Error = QLabel(f"Error! \n {e}")
            Error.setStyleSheet("color: red;")
            Error.setAlignment(QtCore.Qt.AlignCenter)
            grid.addWidget(Error, 1,0)

class GroupBox(QGroupBox):
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
        centralwidget = GroupBox() #create a widget of class groupbox
        rightwidget = GroupBox()
        
        
        
        grid.addWidget(StatusWidget(),0,0)
        grid.addWidget(CameraGroup(),1,0)
        grid.addWidget(SubprocessWidget(),1,2)
        grid.addWidget(GroupBox(),1,1)
        grid.addWidget(rightwidget,0,2)
        grid.addWidget(centralwidget, 0,1,2,1) #add the widget to the grid in row 0 column 1
        
        
    
class MainWindow(QMainWindow): #Define the class for the window
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PCMS Control Panel")
        self.setGeometry(0, 0, 960, 540) #set x and y coords followed by window width and height
        self.setCentralWidget(MainWidget())
        self.show()
        


#----------------
# MAIN
#----------------
window = MainWindow()
window.show()
app.exec()
sys.exit()




