"""
Clean a directory tree on a regular basis to make disk space.
OS agnostic.
Caution 1: carefuly test before using by commenting out the os.remove command 
on the last line, and let the script print out what it would remove.
Caution 2: be mindful of links.
"""

import os
from datetime import date, timedelta
from time import gmtime
import re
import sys

dir_to_clean="/media/pi/92ED-675B" # the root directory to start cleaning
days_protected=1 #number of days the files are protected from cleaning
extension=".txt" #only delete file with this extension

arguments = len(sys.argv)
if(len(sys.argv)>1):
    try:
        dir_to_clean=str(sys.argv[1])
        extension=str(sys.argv[2])
        print("Directory to clean: ",dir_to_clean)
    except:
        pass

#______________________________________________________________________________

cutoffDate = date.today()-timedelta(days=days_protected)  # does not delete files newer than this (exclusive of the date)

# traverse a directory, and remove files based on age and extension
for root, dirs, files in os.walk(dir_to_clean):
    path = root.split(os.sep)
    print((len(path) - 1) * '---', os.path.basename(root))
    for file in files:
        #print(os.path.join(root, file))
        if gmtime(os.path.getmtime(os.path.join(root, file))) <= cutoffDate.timetuple()and re.search(extension,os.path.basename(file)):
            print("Removing file:",file)
            os.remove(os.path.join(root, file))