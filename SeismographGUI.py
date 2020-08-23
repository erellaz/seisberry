"""
GUI for the seismograph application
"""

import tkinter as tk
from subprocess import check_output
import os
import csv

# Declare global variables
prog_name="ads1256_test"
startup_cmd=r"cd /home/pi/Desktop/DIYSeis/C/ && ./ads1256_test param &"
param_file='/home/pi/Desktop/DIYSeis/C/param'

# find pid of a process from name
def get_pid(name):
    return int(check_output(["pidof","-s",name]))

#_________________________________________________________________
# This function is called whenever the STOP button is pressed
# it looks for all processes called ads1256_test and kill them
def stop_deamon():
    global prog_name
    try:
        # Kill both parent and child process, so do it twice
        pid = str(get_pid(prog_name))
        os.system("kill -9 "+str(pid))
        pid = str(get_pid(prog_name))
        os.system("kill -9 "+str(pid))
        PID.set("Not alive")
    except:
        print("Failed to kill")

#_________________________________________________________________
# This function is called whenever the STATUS button is pressed
# it looks for all processes called ads1256_test and finds PID
def status_deamon():
    global PID, prog_name
    try:
        PID.set(get_pid(prog_name))
        #print("Status called:", PID)
    except:
        #print("Failed to find PID")
        PID.set("Not alive")

#_________________________________________________________________
# This function is called whenever the START button is pressed
# it starts the seismograph deamon
def start_deamon():
    global startup_cmd
    try:    
        os.system(startup_cmd)
        status_deamon()
    except:
        pass
#_________________________________________________________________    
# This function is called whenever the Read Param button is pressed
# it reads the seismograph parameter file
def read_param():
    global AG,NG,SI,OP,param_file
    with open(param_file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=':')
        for row in csv_reader:
            #print("CSV:",row[0],row[1])
            if "AmpGain" in row[0]:
                AG.set(row[1])
            if "NumGain" in row[0]:
                NG.set(row[1])
            if r"SampInt" in row[0]:
                SI.set(row[1])
            if "Path" in row[0]:
                OP.set(row[1])
        #print("Read param called:",AG,NG,SI,OP)

#_________________________________________________________________
# Create the main window
root = tk.Tk()
root.title("Seis")

# Create the main container
frame = tk.Frame(root)

# Lay out the main container, specify that we want it to grow with window size
frame.pack(fill=tk.BOTH, expand=True)

# Allow middle cell of grid to grow when window is resized
frame.columnconfigure(1, weight=1)
frame.rowconfigure(1, weight=1)

# Variables for holding parameter data
AG=tk.DoubleVar()
NG=tk.DoubleVar()
SI=tk.DoubleVar()
OP=tk.DoubleVar()
PID=tk.DoubleVar()

read_param()
status_deamon()
#_________________________________________________________________
# Create widgets
label_AG = tk.Label(frame, text="Amplifier Gain")
label_AGV = tk.Label(frame, textvariable=AG)

label_NG = tk.Label(frame, text="Numeric Gain")
label_NGV = tk.Label(frame, textvariable=NG)

label_SI = tk.Label(frame, text="Sample Interval")
label_SIV = tk.Label(frame, textvariable=SI)

label_OP = tk.Label(frame, text="Output Path")
label_OPV = tk.Label(frame, textvariable=OP)

label_PID = tk.Label(frame, text="PID")
label_PIDV = tk.Label(frame, textvariable=PID)

#_________________________________________________________________
# Create buttons
button_stop = tk.Button(frame, text="Stop", command=stop_deamon)
button_status = tk.Button(frame, text="Status", command=status_deamon)
button_start = tk.Button(frame, text="Start", command=start_deamon)
button_read = tk.Button(frame, text="Param", command=read_param)

# Lay out widgets
label_AG.grid(row=0, column=0, padx=5, pady=5)
label_AGV.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

label_NG.grid(row=1, column=0, padx=5, pady=5)
label_NGV.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

label_SI.grid(row=2, column=0, padx=5, pady=5)
label_SIV.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

label_OP.grid(row=3, column=0, padx=5, pady=5)
label_OPV.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

label_PID.grid(row=4, column=0, padx=5, pady=5)
label_PIDV.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)


button_stop.grid(row=5, column=0, columnspan=1, padx=5, pady=5, sticky=tk.W)
button_start.grid(row=5, column=1, columnspan=1, padx=5, pady=5, sticky=tk.E)
button_status.grid(row=6, column=0, columnspan=1, padx=5, pady=5, sticky=tk.W)
button_read.grid(row=6, column=1, columnspan=1, padx=5, pady=5, sticky=tk.E)

# Place cursor in entry box by default
button_stop.focus()

# Run forever!
root.mainloop()