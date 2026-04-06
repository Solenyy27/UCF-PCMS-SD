

<div style="text-align:center;">
<h1>UCF Department of Materials Science and Engineering</h1>
<h2>High-Throughput Multimodal Metrology System for Photovoltaic Technologies</h2>
<h3>(C) 2025-2026 Cody Sitkoff</h3>
<br>
<br>
</div>

## 1. Introduction
This project, nicknamed the Photovoltaic Characterization and Metrology System (PCMS) is intended to be used along with Ossilla Solar Simulators and Source Measurement Units along with a Raspberry Pi and compatible camera. The purpose of the project is to consolidate a bunch of commonly measured metrologies for PV cells into one system to both enable fast data acquisition at a low cost and to enable future use of multiple testing systems at the same time (e.g., illuminated TLM, EL during IV curve measurement).  
<br>
This code repository uses **python3** scripts which (in theory) should be usable through a compiler of your choice (or simply through python3 -m ...). It was made using **spyder** to comple and run code, so I would consider that the most stable.
<br>
<br>

## 2. Dependencies and Setup
On a Raspberry Pi, the following packages are needed through either pipx or apt:
```
configparser, PySide6, serial, matplotlib, pandas, numpy
```
The following command should work for getting all packages: <br>
**via pipx**
```
pipx install configparser PySide6 serial matplotlib pandas numpy
```
**via apt**
```
apt install python3-configparser python3-PySide6 python3-serial python3-matplotlib python3-pandas python3-numpy
```

Additionally, the `xtralien` package will be needed, it is only available through pip via the following command:
```
pip install xtralien --break-package-system
```

Finally, `git clone` this project to your device. In theory, the `.desktop` file witin the directory should provide a shortcut the accessing the program if placed in /home/

## 3. Repository Layout and Contents
The file structure should be as follows:  
<pre>
UCF-PCMS-SD
├── mainlib.py  
├── main.py  
├── logo.txt  
├── README.md  
├── icons.png  
├── output  
│       └──<b>Data Output</b>  
└──Scripts  
        ├──<b>User Made Testing Scripts</b>  
        └──example.py  
</pre>

Below is a description of each system component that is provided:

- **mainlib.py** provides functions able to be called within test scripts and within the main.py file.
- **main.py** is responsible for the CUI.
- **logo.txt** provides a CUI graphic at the beginning of the CUI session.
- **icons.png** various icons existing in .png format are located in the main folder, they are used for the GUI
- **README.md** is where you are now! Hi!
- **output** is the location where data will be stored within a folder corresponding to the user-inputted sample name.
- **Scripts** is where user scripts should be placed. Please see **Section 3. User Test Scripts** for more info.

The **main.py** script is what must be run to actually get an interface. It pulls functions from mainlib.py in order to operate in a way that makes the code more understandable and hopefully easy to edit to your liking if you want. Within **mainlib.py**, there is a (somewhat hacky) bit of code near the beginning which is **responsible for importing the user made test scripts from the ./Scripts folder.** It does so by using the `exec()` function to pull together an import command for each .py file in Scripts. I would **highly suggest** not editing the file structure or functions present within mainlib.py. Adding functions should be fine, however.

## 4. User Scripts
### 4.1 The Basics
code to be executed must be ran in a user-defined `run()` function:
```python3
parmlist = ['my','needed','parameters']
def run(mode=0):
    #your code here
    
if __name__ == '__main__': #to make your script usable without GUI while working with the GUI, you can use this function to call run() if the script is executed by itself
    run()

```
In order to run the function, the GUI will call `exec(yourfunction.run())`.  In order to define variables that are needed for the script, the list variable `paramlist` is set and called upon for each individual script (e.g. in the format `myscript.paramlist`).  

## 4.2 Testing Procedure in Practice
To begin with, the user can define a sample name and hit the corresponding save button. This will set the field `sample.sname` and will generate a corresponding config path for the sname_config.ini file that holds test info. After doing so, the user can use the available list of user scripts to define the scripts and order for which they want to run. After defining the scripts and order, the user can hit the refresh button to retrieve the needed parameters from the scripts to be ran. The user can input these parameters and then hit the corresponding save button to generate the parameters into the config. Pressing the play button at this time will begin running the tests in the order the user defined.

The gear button will instead launch a "breadboard" mode, where the user can input strings to be ran via `exec(userstring)`. This is useful for doing things like interacting with the SMU or solar simulator.

### 4.3 Writing Test Scripts
As it is hard to articulate exactly how you should go about doing this, I recommend checking the included ./TestScripts/example.py file. It should be able to act as a boilerplate to create a usable test script. However, here are some tips:

- Importing mainlib functions does not work within the body of test scripts, as doing so would result in circular imports. Instead, you should import specifically needed functions directly within the `run()` function, e.g.:
```python3
def run(mode=0):
    from mainlib import somefunction
    somefunction(value)
```
- If some sort of **data analysis** needs to be done after a test, call the data analysis script when needed. You can use the `mainlib` functions `writecfg()` and `readcfg` to take advantage of the config file for reading parameter values and writing your own results.


## 5. HTML Template Report
Unfortunately, this section has not yet been completed due to time constraints.
