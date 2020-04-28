"""
This is a Python 3 program to look at the daily output of a 3 components 
seismometer, like the seisberry.

Usage: Put your daily production in a directory like:
    D:\Seisberry\2020-04-01 
    The base name of the path needs to be the date, 
    in the format: 2020-04-18 or 2020_04_19 
    
    Update the user/station valiables at the beginning of this script.
    Run

Date: 2020-04-19

For tutorial visit:
    https://www.erellaz.com

Original idea from: 
https://github.com/will127534/RaspberryPi-seismograph
https://will-123456.blogspot.com/2019/04/diy-seismograph.html
"""
#______________________________________________________________________________
import numpy as np
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
import os
from obspy.core import Trace,Stream,UTCDateTime
from obspy.core.event import read_events
import requests

#______________________________________________________________________________
# User adjustable variables - a normal user only needs to edit this block 
# to have the program run anywhere around the globe.

# Rerun =1: normal mode, attempt to quickload data from a previous run first, 
# if the numpy array from a previous run cannot be detected, then load from raw 
# data (much slower) instead.
# rerun =1 force loading from raw file regardless of presence numpy array. 
rerun=1 #this value should remain at 1 for optimum behaviour in 99% of the cases

# Directory where your raw files are stored, straight from the seisberry:
# Important: The base name needs to be the date, in the format: 2020-04-18 or 2020_04_18
# 2 Options: 

File_date = datetime.now()- timedelta(days=1)
# Either manual if you want to reprocess past data
datadir=r"D:\Seisberry\2020-04-24"
# or automatic, for today's data:
#datadir=os.path.join(r"D:\Seisberry",File_date.strftime("%Y-%m-%d"))

# File extension of the files conatianing the raw data. Example, your raw files 
# are named:20200425_040500.txt.done
raw_ext=".done"

#Optional, if you plan to output traces as SEGY or miniseed
miniseeddir=r"D:\Seisberry\miniseed"
#segydir=r"D:\Seisberry\SEGY"

# Plot dir
plotdir=r"D:\Dropbox\RaspberryPi\dayPlots"

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
# Make the process date from the data directory
File_date = os.path.basename(datadir)
print("Processing:",File_date)

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
#Either read and prepare all the raw data (first run), or just load from a numpy array (rerun)
npfilename=os.path.join(datadir,File_date+".npy")
if (rerun!=0): #try to load data from numpy array
    rerun=0 # but assume it will fail
    print("Attempt to loading form precomputed data:",npfilename)
    for filename in sorted(os.listdir(datadir)):
        if filename.endswith(".npy"):
            data=np.load(npfilename)
            rerun=1 # It worked, we can skip loading from raw


if (rerun==0):
    #Reading the data, in a robist way, as some files will be badely formed.
    print("Loading form raw data:")
    data=np.empty((0,5),float)
    for filename in sorted(os.listdir(datadir)):
        if filename.endswith(raw_ext):
            filename_date = filename
            print(filename,data.shape)#,data2.shape)
            try:
                data2 = np.genfromtxt(os.path.join(datadir, filename), delimiter=',',invalid_raise='false')
                try:
                    data = np.append(data,data2,axis=0)
                except:
                    print("File ",filename,"was read but np.append failed, possible column mismatch or empty file. Skipping.")
                    try:
                        print(data2)
                    except:
                        print("Cannot print numpy array of: ",filename)
            except:
                print("File ",filename,"caused a read exception. Skipping.")
    
    #Saving the concatenated file to disk
    print("Saving computed data as:",npfilename)
    np.save(npfilename,data)



#______________________________________________________________________________
# Updating variables from what we just learnt from reading the data
starttime = UTCDateTime(data[0][0])
length=data.shape[0]
# Update the Obspy structure for plots, from the data read
statsx.update({'npts': length})
statsx.update({'sampling_rate': sampling_rate})
statsx.update({'starttime': starttime})

#______________________________________________________________________________
# Optional: data statistics for QC, only used for the print out 
print("Start Time for Graph",starttime.strftime("%Y_%m_%d %H:%M:%S"))
print("Data length:",length,"Sampling Interval:",sampling_rate)
truesampling=data[:,4].mean()/1000000.0
stddev=data[:,4].std()/1000000.0
print("SI:",truesampling,"Standard deviation:",stddev,"Sampling",int(1000/truesampling),"Hz")
for i in range(1,4):
    mt=data[:,i].mean()
    stdt=data[:,i].std()
    maxt=data[:,i].max()
    mint=data[:,i].min()
    print("Component:",i,"DC component (Mean):",mt,"Standard deviation:",stdt,"Max:",maxt,"Min:",mint)
    

#______________________________________________________________________________
# Generate the dayplot and write to miniSeed format, for each component
for i in range(1,4):
    statsx.update({'channel': 'BH'+str(i)})
    Xt = Trace(data=data[:,i], header=statsx)
    Xt_filt = Xt.copy()
    Xt_filt.filter('lowpass', freq=50, corners=2, zerophase=True)
    stream = Stream(traces=[Xt_filt])
    outfile=os.path.join(plotdir,filename_date[0:8]+'-dayplotFilter'+str(i)+'.png')
    stream.plot(type='dayplot',outfile=outfile,size=size,events=cat_all)
    stream = Stream(traces=[Xt])
    # Plot output
    outfile=os.path.join(plotdir,filename_date[0:8]+'-dayplot'+str(i)+'.png')
    stream.plot(type='dayplot',outfile=outfile,size=size,events=cat_all)
    # Miniseed writing
    outminiseed=os.path.join(miniseeddir,filename_date[0:8]+"-comp"+str(i)+'.mseed')
    stream.write(outminiseed,format='MSEED')

#______________________________________________________________________________
# Optional: QC the sampling, histogram of the jitter
_ = plt.hist(data[:,4]/1000000, bins=np.arange(1.3,1.375,0.0005))  # arguments are passed to np.histogram
plt.title("Histogram of the sample rate stability over the time period")
outfile=os.path.join(plotdir,filename_date[0:8]+'-Histogram_sample_rate.png')
plt.savefig(outfile)

