

<div style="text-align:center;">
<h1>UCF Department of Materials Science and Engineering</h1>
<h2>High-Throughput Multimodal Metrology System for Photovoltaic Technologies</h2>
<h3>(C) 2025-2026 Cody Sitkoff</h3>
<br>
<br>
</div>
##1. Introduction  
***
This project, nicknamed the Photovoltaic Characterization and Metrology System (PCMS) is intended to be used along with Ossilla Solar Simulators and Source Measurement Units along with a Raspberry Pi and compatible camera. The purpose of the project is to consolidate a bunch of commonly measured metrologies for PV cells into one system to both enable fast data acquisition at a low cost and to enable future use of multiple testing systems at the same time (e.g., illuminated TLM, EL during IV curve measurement).  
<br>
This code repository uses **python3** scripts which (in theory) should be usable through a compiler of your choice (or simply through python3 -m ...). It was made using **spyder** to comple and run code, so I would consider that the most stable.
<br>
<br>
##2. Repository Layout and Contents  
***
The file structure should be as follows:  
<pre>
UCF-PCMS-SD
├── mainlib.py  
├── main.py  
├── logo.txt  
├── README.md  
├── output  
│       └──<b>Data Output</b>  
├──TestScripts  
│       ├──<b>User Made Testing Scripts</b>  
│       ├──example.py  
│       └──ALL.py  
└──DataScripts  
     └──<b>User Made Data Analysis Scripts</b>
</pre>

Below is a description of each system component that is provided:

- **mainlib.py** provides functions able to be called within test scripts and within the main.py file.
- **main.py** is responsible for the CUI.
- **logo.txt** provides a CUI graphic at the beginning of the CUI session.
- **README.md** is where you are now! Hi!
- **output** is the location where data will be stored within a folder corresponding to the user-inputted sample name.
- **TestScripts** is where user test scripts should be placed. Please see **Section 3. User Test Scripts** for more info.
- **DataScripts** is where any data analysis/transformation tools should be placed. Some are provided by default.


The **main.py** script is what must be run to actually get a CUI interface. It pulls functions from mainlib.py in order to operate in a way that makes the CUI very understandable and hopefully easy to edit to your liking if you want. Within **mainlib.py**, there is a (somewhat hacky) bit of code near the beginning which is **responsible for importing the user made test scripts from the ./TestScripts folder.** It does so by using the `exec()` function to pull together an import command for each .py file in TestScripts. I would **highly suggest** not editing the file structure or functions present within mainlib.py. Adding functions should be fine, however.

##3. User Test Scripts
***
###3.1 Types of User Scripts
There are **two types** of user test scripts: **run** scripts and **list** scripts.

**run** scripts include the following snippet of code:
```python3
def run(mode=0):
    #your code
```
This piece of code is responsible for running the test when called. In order to define variables that are needed for the script, the list variable `paramlist` is set and called upon for each individual script (e.g. in the format `myscript.paramlist`).  
<br>
**list** scripts include the list variable `testlist`, which is used to hold the names of other test scripts. When a `testlist` is detected, choosing to run the test containing the `testlist` will result in the back-end of the CUI attempting to set flags for individual tests on the list to "1" to signify that they are marked for completion.

##3.2 Testing Procedure in Practice
When a test is called, the user will be prompted to input needed parameters. The test will then be ran. If the test completes successfully, it will return a value of "2" which is checked to ensure proper completion. If a test aborts for any reason, a value of "3" is returned. These values are stored within the flag value (`sample.flags`) for the test, which is then checked for any errors before completion of the CUI session.

The ALL test script, which is included by default, simply pulls the name of every script within the TestScripts folder and flags them all to be ran as a result. Use with caution if several user-made testing scripts are present.

Once the CUI session is done, you can test a subsequent sample by returning a "yes" answer when prompted to do so. This will return to the beginning of the while loop within the main.py script, rewriting over internal variables to test another sample. This **will not** overwrite your output data **if** the sample name is changed.

###3.3 Writing Test Scripts
As it is hard to articulate exactly how you should go about doing this, I recommend checking the included ./TestScripts/example.py file. It should be able to act as a boilerplate to create a usable test script. However, here are some tips:

- Importing mainlib functions does not work within the body of test scripts, as doing so would result in circular imports. Instead, you should import specifically needed functions directly within the `run()` function, e.g.:
```python3
def run(mode=0):
    from mainlib import somefunction
    somefunction(value)
```
- If some sort of **data analysis** needs to be done after a test, this will be called from ./DataScripts modules. Hence, **testing scripts should focus on obtaining data and saving it** in a readable format.
- If a script needs data analysis to be done before it can start, for example, to run electroluminescence (EL) using the short circuit current value (I<sub>sc</sub>) obtained from illuminated IV response, then the `needs` list variable can be added to the top of the test script to signify that some data must be obtained before it is ran. A corresponding data script with the list variable `provides` is used to signify that the data script should be ran to obtain a value for the needed metric.
#make sure to do this

##4. User Data Scripts
***
TBD

##5. HTML Template Report
