#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtSerialPort import QSerialPort
from PySide6.QtCore import QIODeviceBase, Slot, Signal, Qt, QThread, QObject, QEvent, QRunnable, QThreadPool, QMimeData, Qt
from PySide6.QtGui import QPalette, QFocusEvent, QKeySequence, QShortcut, QMouseEvent, QIcon, QDrag, QPixmap
from PySide6.QtWidgets import (
QMainWindow, QApplication, QWidgetAction, QWidget, QGroupBox, QDockWidget, QGridLayout, QLabel,
QVBoxLayout, QTextEdit, QPlainTextEdit, QPushButton, QDialog, QLineEdit, QComboBox, QCheckBox, QToolButton,
QHBoxLayout, QListWidget, QInputDialog
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

for file in glob.glob("./scripts/*.py"): #check the TestScripts directory for user scripts
    if file == "./scripts/__init__.py" or file == "./scripts/example.py": #skip the __init__ and example files.
        continue
    namestuff = file.split("/")
    name = namestuff[2].split(".")
    exec('import scripts.'+name[0]+' as '+name[0]) #import the user script as its own name


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
# Command Threading Objects
#----------------
class Breadboard(QRunnable): #"breadboard" script that allows for user command exec and exiting after user tinkering
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
                
class RunScripts(QRunnable): #script that attempts to run all currently queued tests in order
    @Slot()
    def run(self):
        if scriptorder == None or scriptorder == [""]: #check to make sure scriptorder has been set
            print("No Scripts Have Been Selected!")
            return
        
        for i in scriptorder:
            tstname = i+'.run()'
            try:
                exec(tstname)
            except Exception as e:
                print(e)

#----------------
# Console Menu
#----------------
"""
#
# Currently Scrapped! Run with DE console or with spyder console for separated window.
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
scriptorder = [] #creates a variable to mirror the positions of scripts to be ran

class PlaylistPanel(QGroupBox): #creates the overall groupbox
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        layout = QGridLayout(self)
        self.setLayout(layout)
        
        self.scriptlist = QListWidget() #creates a QListWidget to hold the available user scripts
        for item in flaglist:
            self.scriptlist.addItem(item)
        
        # set the layout for all needed widgets
        self.list_widget = QListWidget(self)
        
        scripttitle = QLabel("Available Scripts")
        scripttitle.setAlignment(QtCore.Qt.AlignCenter)
        scripttitle.setMargin(0)
        scripttitle.setMinimumHeight(0)
        
        scriptorder = QLabel("Script Order (Top to Bottom)")
        scriptorder.setAlignment(QtCore.Qt.AlignCenter)
        scriptorder.setMargin(0)
        scriptorder.setMinimumHeight(0)
        
        layout.addWidget(scripttitle,0,0)
        layout.addWidget(scriptorder,0,2)
        layout.addWidget(self.scriptlist,1,0,4,1)
        layout.addWidget(QLabel(">"), 1,1,4,1)
        layout.addWidget(self.list_widget, 1, 2, 4, 1)

        # create buttons
        add_button = QPushButton('Add')
        add_button.clicked.connect(self.add)

        insert_button = QPushButton('Insert')
        insert_button.clicked.connect(self.insert)

        remove_button = QPushButton('Remove')
        remove_button.clicked.connect(self.remove)

        clear_button = QPushButton('Clear')
        clear_button.clicked.connect(self.clear)

        layout.addWidget(add_button, 1, 3)
        layout.addWidget(insert_button, 2, 3)
        layout.addWidget(remove_button, 3, 3)
        layout.addWidget(clear_button, 4, 3)

    def add(self): #each function changes list_widget and then mirrors the change to scriptorder
        item = self.scriptlist.currentItem().text()
        self.list_widget.addItem(item)
        scriptorder.append(item)

    def insert(self):
            current_row = self.list_widget.currentRow()
            item = self.scriptlist.currentItem().text()
            self.list_widget.insertItem(current_row+1,item)
            scriptorder.insert(current_row+1, item)

    def remove(self):
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            current_item = self.list_widget.takeItem(current_row)
            del current_item
            del scriptorder[current_row]

    def clear(self):
        self.list_widget.clear()
        scriptorder.clear()

class StartStopPanel(QWidget): 
    #defines icons for the buttons
    startico = QIcon("StartIcon.png")
    stopico = QIcon("StopIcon.png")
    breadico = QIcon("BreadboardIcon.png")
    threadstate = 0 #defines a var used to hold info about the currently used QRunnable
    threadpool = QThreadPool() #defines threadpool to hold runnable objects started within the widget
    def __init__(self):
        super().__init__() #set the layout and buttons
        grid = QGridLayout()
        self.setLayout(grid)
        start = QToolButton()
        stop = QToolButton()
        bread = QToolButton()
        start.setIcon(self.startico)
        stop.setIcon(self.stopico)
        bread.setIcon(self.breadico)
        start.setIconSize(QtCore.QSize(35,35))
        stop.setIconSize(QtCore.QSize(35,35))
        bread.setIconSize(QtCore.QSize(35,35))
        grid.addWidget(start,0,0)
        grid.addWidget(stop,1,0)
        grid.addWidget(bread,2,0)
        start.clicked.connect(self.StartButton)
        stop.clicked.connect(self.StopButton)
        bread.clicked.connect(self.BreadboardButton)

        
    def StopButton(self):
        self.threadpool.clear()
        
    def BreadboardButton(self): #use this method to call workers
        self.getstate()
        if self.threadstate == 0:
            worker = Breadboard()
            self.threadpool.start(worker)
            self.threadstate = 1
        
    def StartButton(self): #TODO, make it so this doesn't work if a name and makedir hasn't been set yet and if params haven't been fully defined
        self.getstate()
        if self.threadstate == 0:
            worker = RunScripts()
            self.threadpool.start(worker)
    
    def getstate(self):
        if self.threadpool.activeThreadCount() > 0:
            print("A Script is Currently Running, Please Wait or Hit Stop to Execute New Console Inputs.")
            self.threadstate = 1
        else:
        #use this https://www.pythonguis.com/faq/how-to-start-stop-or-pause-running-threads/ to contorl start and stop.
            self.threadstate = 0

class Playlist(QWidget):
    def __init__(self):
        super().__init__()
        grid = QGridLayout()
        self.setLayout(grid)
        grid.addWidget(PlaylistPanel(),0,0)
        grid.addWidget(StartStopPanel(),0,1)

#----------------
# Sample Window
#----------------

class EditableBox(QWidget): #box to hold the editable class widgets in SampleFiles (defines the grid layout)
    grid = QGridLayout()
    def __init__(self):
        super().__init__()
        self.setLayout(self.grid)
        

class SampleFiles(QWidget):
    grid = QGridLayout() #creates the layout for this widget
    snamein = QLineEdit() #creates field for user to input sample name
    flocinfo = QLineEdit() #creates field for file location info to be read into
    editablebox = EditableBox() #creates the box to hold the checkbox and label
    editable = QCheckBox() #creates a checkbox that can be clicked to override the file location
    button = QToolButton() #creates a button that can be used instead of the enter key
    flocstr = "..." #holds the string that corresponds to the namepath
    usredit = 0 #holds the state of user editability
    SaveIcon = QIcon()
    
    def __init__(self):
        super().__init__()
        self.setLayout(self.grid)
        self.installEventFilter(self) #installs an event filter to catch enter keypresses and use them to activate setfileloc function
        sampnamebox = QLabel("Sample Name")
        sampnamebox.setAlignment(QtCore.Qt.AlignLeft)
        self.grid.addWidget(sampnamebox,0,0)
        filenamebox = QLabel("Output Folder Path")
        sampnamebox.setAlignment(QtCore.Qt.AlignLeft)
        self.grid.addWidget(filenamebox,1,0)
        self.snamein.setAlignment(QtCore.Qt.AlignVCenter)
        self.snamein.setPlaceholderText("Enter a Sample Name")
        self.grid.addWidget(self.snamein, 0,1)
        self.SaveIcon.addFile('SaveIcon.png')
        self.button.setIcon(self.SaveIcon)
        self.button.clicked.connect(self.setfileloc)
        self.grid.addWidget(self.button, 0,2)
        self.flocinfo.setAlignment(QtCore.Qt.AlignVCenter)
        self.flocinfo.setText(self.flocstr) #sets the text of flocinfo to be the namepath string
        self.flocinfo.setReadOnly(True)
        self.grid.addWidget(self.flocinfo,1,1)
        self.editablebox.grid.addWidget(QLabel("Override"),0,0)
        self.editablebox.grid.addWidget(self.editable, 0,1)
        self.grid.addWidget(self.editablebox,1,2)
        self.editable.checkStateChanged.connect(self.editcheck) #connects the checkbox to the editcheck function
        
    def setfileloc(self):
        sample.sname = self.snamein.text() #sets the sample class field sname to be the user input
        if self.snamein.text() == "":
            return
        if self.usredit == 0: #if user override for filepath is not used,
            namepath = "output/"+sample.sname+"/" #default namepath is output / samplename / 
            self.flocstr = namepath #uses mainlib var namepath to set self.flocstr
            sample.cfgpath = namepath+sample.sname+'_config.ini' #sets sample config path
            mkdir(namepath) #uses mainlib function to set make directory if needed
            initcfg() #uses mainlib function to initialize config file
        if self.usredit == 1: #if user override is enabled
            self.flocstr = self.flocinfo.text() #uses user text to set flocstr
            namepath = self.flocstr #sets namepath from user input
            sample.cfgpath = self.flocstr +sample.sname+'_config.ini' #sets sample path to be the sample name in the user defined directory
            mkdir(namepath)
            initcfg()
        self.flocinfo.setText(self.flocstr)
            
    def editcheck(self): #sets the flag for user edit override and the corresponding ability to use the textedit property of the file location box
        if self.editable.isChecked() == True:
            self.flocinfo.setReadOnly(False)
            self.usredit = 1
        else:
            self.flocinfo.setReadOnly(True)
            self.usredit = 0
        
    def eventFilter(self, target, event):
        if event.type() == QEvent.KeyRelease:
            if event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
                self.setfileloc()
        return super().eventFilter(target, event)
    
class SampleParams(QWidget): #todo later; get params from files and then generate a list of QTextFields and corresponding QLabels for them to be edited with
# add a refresh button so that they can be generated again from the currently imported list of user things
    
    def __init__(self):
        super().__init__()
        grid = QGridLayout()
        listparams()
        

class SampleWidget(QGroupBox): #overall box for the sample definiton widgets
    def __init__(self):
        super().__init__()
        grid = QGridLayout()
        self.setLayout(grid)
        grid.addWidget(SampleFiles(),0,0)
        grid.addWidget(SampleParams(),1,0)
        
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
        crgrid.addWidget(Playlist(),1,0)
        grid.addWidget(centralrightContainer,0,1,2,2)
        
debugmode = 0

class MainWindow(QMainWindow): #Define the class for the window
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("PCMS Control Panel") #sets window title
        self.setStyleSheet("""
            background-color: #262626;
            """)
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




