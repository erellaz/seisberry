"""
This is a Python 3 program for the Seisberry, running in server mode.
This program is stripped down and optimized to run on light hardware, like the Raspberry.
Raspian is 32 bits limitting a numpy array to 2G, past this limit we run into a memory error.
This program runs automatically daily (scheduled in crontab) to process the 
daily production from the 3 components seismometer and generate: 
    -dayplot for display on the seisberry Apache server. 
    -miniseed for upload to IRIS

Usage:
    Daily rawdata in: /media/pi/xxxx/2020-04-01
    Daily miniseed in : /media/pi/yyyy/miniseed
     
    Update the user/station valiables at the beginning of this script.
    Run
    If the program is killed by the OS, check: /var/log/kern.log

Date: 2020-04-23

For tutorial visit:
    https://www.erellaz.com

Original idea from: 
https://github.com/will127534/RaspberryPi-seismograph
https://will-123456.blogspot.com/2019/04/diy-seismograph.html
"""
#______________________________________________________________________________
import numpy as np
from datetime import datetime,timedelta
import os
from obspy.core import Trace,Stream,UTCDateTime
from obspy.core.event import read_events
import requests
import sys

#______________________________________________________________________________
# User adjustable variables - a normal user only needs to edit this block 
# to have the program run anywhere around the globe.

File_date = datetime.now()- timedelta(days=1)
datadir=r"/media/pi/92ED-675B"

#Optional, if you plan to output traces as SEGY or miniseed
miniseeddir=r"/media/pi/PAUL/miniseed"

# Plot dir
plotdir=r"/home/pi/Desktop/Images"

# Url to download the official seismic events from - used to label your plots
# Quakeml is the defacto official format for seismic event
url = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_week.quakeml'

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

decimation=5

# Your latitude and longitude in decimal degrees, West or South are negative
# Example Houston is stationlat=29.0 stationlon=-95.0
stationlat=29.0
stationlon=-95.0
# box search: half size in decimal degrees (to filter catalog events close to you)
box=10.0

# Magnitude of the world-wide biggest events to be shown on plot
bigeventsmag=5.5

# How big do you want your plots?
size = (210*10,210*10)
#______________________________________________________________________________
#         DO NOT MODIFY BELOW, UNLESS YOU KNOW WHAT YOU ARE DOING
#______________________________________________________________________________
# default is component 1
comp=1
# however if the component is passed as argument to the program, we update the component
arguments = len(sys.argv)
if(len(sys.argv)>1):
    try:
        comp=int(sys.argv[1])
        print("Updating component to ",comp)
    except:
        pass
        
# Sanity check on the component
if(comp not in [1,2,3]):
    print("Bad component passed as argument. Comp needs to be 1, 2 or 3. Defaulting to 1")
    comp=1


# Make the process date from the data directory
File_date = os.path.basename(datadir)
print("Processing:",File_date," Component:",comp)

#______________________________________________________________________________
# For seismic event metadata, the de-facto standard is QuakeML (an xml document structure)
# set up a seach box:
minlat=stationlat-box
maxlat=stationlat+box
minlon=stationlon-box
maxlon=stationlon+box

# Load catalog from the web:
print("Events of the week downloaded from:\n",url+"\n UTC Time (Zulu) and filter for location.")
Thisweek_quakeml=requests.get(url).content
cat = read_events(Thisweek_quakeml)
# everything local
cat_local = cat.filter("latitude > " + str(minlat), "latitude < " + str(maxlat), "longitude > " + str(minlon), "longitude < " + str(maxlon))
# and everything world-wide with a magnitude > 5.5
cat_strong=cat.filter("magnitude >= "+ str(bigeventsmag)) 
# concatenate the local events with the strong events to make our label catalog
cat_all=cat_local
cat_all.extend(cat_strong)
#print(catall)
print(cat_all.__str__(print_all=True))

#______________________________________________________________________________
# Let's start by "locking" the files we will be workin on.
# Since the processing of the 3 components are run in succession due to hardware
# limits, we have to ensure they are run on the same set of underlying files.
if(comp==1):
    for filename in sorted(os.listdir(datadir)):
        if filename.endswith(".txt"):
            try:
                os.rename(os.path.join(datadir, filename),os.path.join(datadir, filename+".process"))
            except:
                pass

#______________________________________________________________________________
#Reading the raw  data

starttime=datetime.now()
print("Loading form raw data:")
data=np.empty((0,),float)
for filename in sorted(os.listdir(datadir)):
    if filename.endswith(".process"):
        filename_date = filename
        #print(filename,data.shape)#,data2.shape)
        try:
            data2 = np.genfromtxt(os.path.join(datadir, filename), delimiter=',',invalid_raise='false')
        except:
            print("Error reading:",filename)
        # decimation by xX factor to save memory for 32 bit systems, add acts as antialias
        #print(filename,data.shape,data2.shape)
        try:
            data3=np.add.reduceat(data2, np.arange(0,data2.shape[0],decimation))
            print(filename,data.shape,data2.shape,"decimated to:",data3.shape)
            if(UTCDateTime(data2[0][0])<starttime):
                starttime=UTCDateTime(data3[0][0])
            data = np.append(data,data3[:,comp],axis=0)
            del data2, data3
        except:
            print("Exception adding data from: ",filename)
        # After the 3rd component is done, rename the files as .done
        try:
            if(comp==3):
                os.rename(os.path.join(datadir, filename),os.path.join(datadir, filename+".done"))
        except:
            pass
#______________________________________________________________________________
# Updating variables from what we just learnt from reading the data
length=data.shape[0]
# Update the Obspy structure for plots, from the data read
print("Updating trace stats...")
statsx.update({'npts': length})
statsx.update({'sampling_rate': int(sampling_rate/decimation)})
statsx.update({'starttime': starttime})

#______________________________________________________________________________
# Generate the dayplot and write to miniSeed format, for each component
print("Generating trace...")
statsx.update({'channel': 'BH'+str(comp)})
Xt = Trace(data=data[:], header=statsx)
#Xt.filter('lowpass', freq=50, corners=2, zerophase=True)
del data
stream = Stream(traces=[Xt])
del Xt

# Plot output
print("Generating plot...")
outfile=os.path.join(plotdir,filename_date[0:8]+'-dayplotFilter'+str(comp)+'.png')
stream.plot(type='dayplot',outfile=outfile,size=size,events=cat_all)

print("Miniseed writing...")
outminiseed=os.path.join(miniseeddir,filename_date[0:8]+"-comp"+str(comp)+'.mseed')
stream.write(outminiseed,format='MSEED')
