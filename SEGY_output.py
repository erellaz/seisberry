"""
This is a Python program to output to Segy format the raw data from the Seisberry.

Usage: Put your files to be converted in a directory:
    D:\Seisberry\2020-04-01
    
    Update the variables at the beginning of this script.
    Run

Date: 2020-04-23

For tutorial visit:
    https://www.erellaz.com

Original idea from: 
https://github.com/will127534/RaspberryPi-seismograph
https://will-123456.blogspot.com/2019/04/diy-seismograph.html
"""
#______________________________________________________________________________
import numpy as np
#mport sys
import os
from obspy.core import Trace,Stream,UTCDateTime

# For SEGY output only
from obspy.core import AttribDict

from obspy.io.segy.segy import SEGYBinaryFileHeader
#from obspy.io.segy.segy import SEGYTraceHeader
#from obspy.io.segy.core import _read_segy
#______________________________________________________________________________
# User adjustable variables - a normal user only needs to edit this block 
# to have the program run anywhere around the globe.

# Directory where your raw files are stored, straight from the seisberry:
datadir=r"D:\Seisberry\ToSEGY"

#Directory to output SEGY
segydir=r"D:\Seisberry\SEGY"

#Dictionary in Obspy stats format to document your station, is updated later in the code 
#For channel naming see: http://www.fdsn.org/pdf/SEEDManual_V2.4_Appendix-A.pdf
#BH= broad band, High gain seismometer, 1 2 3 othogonal components 
statsx= {'network': 'USA', 
	'station': 'SeisBerry', 
	'location': 'Houston', 
	'channel': 'BH', 
	'mseed' : {'dataquality' : 'D'}, 
	}

#Sampling rate from the seisberry, in samples per second
sampling_rate =750 #0.0013ms sample interval
sampleinterval=0.001
#______________________________________________________________________________
#         DO NOT MODIFY BELOW, UNLESS YOU KNOW WHAT YOU ARE DOING
#______________________________________________________________________________
#______________________________________________________________________________
#Either read and prepare all the raw data (first run), or just load from a numpy array (rerun)
print("Loading form raw data:")
data=np.empty((0,5),float)
for filename in sorted(os.listdir(datadir)):
	if filename.endswith(".txt"):
		filename_date = filename
		print(filename,data.shape)#,data2.shape)
		data2 = np.genfromtxt(os.path.join(datadir, filename), delimiter=',',invalid_raise='false')
		data = np.append(data,data2,axis=0)


#______________________________________________________________________________
# Data statistics for QC and further use
starttime = UTCDateTime(data[0][0])
length=data.shape[0]

# segy is limitted to 32767 samples
if (length>32767):
    print("Warning, trace too long for SEGY output:",length," samples is too much. Cutting to the first 32767 samples")
    length=32767
    

# Update the Obspy structure for plots, from the data read
statsx.update({'npts': length})
statsx.update({'sampling_rate': sampling_rate})
statsx.update({'starttime': starttime})


#______________________________________________________________________________
# Generate the SEGYs
for i in range(1,4):
    statsx.update({'channel': 'BH'+str(i)})
    statsx = AttribDict()
    statsx.textual_file_header = 'SEISBERRY SEGY, SINGLE TRACE COMPONENT'+str(i)
    statsx.binary_file_header = SEGYBinaryFileHeader()
    statsx.binary_file_header.trace_sorting_code = 5
    statsx.delta = sampleinterval
    data = np.require(data, dtype=np.float32) #handle format conversion
    Xt = Trace(data=data[0:length,i], header=statsx) # cut the trace, add headers
    
    #Xt_filt = Xt.copy()
    #Xt_filt.filter('lowpass', freq=50, corners=2, zerophase=True)
    stream = Stream(traces=[Xt])
    #stream = Stream(traces=[Xt_filt])
    
    # SEGY writing, limited to 32767 samples
    outsegy=os.path.join(segydir,filename_date[0:8]+"-comp"+str(i)+'.sgy')

    print("Stream object before writing...")
    print(stream)
    stream.write(outsegy,format='SEGY')
