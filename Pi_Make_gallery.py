"""
Make an image gallery from html
"""
import os
from datetime import datetime

imagedir="/home/pi/Desktop/Images"
outgallery="/var/www/html/index.html"

pagetime=datetime.now()
time_to_print=str(pagetime.strftime("%Y-%m-%d"))

#__________________________________________________________________________________________________________
# Move the images to the www directory
for filename in sorted(os.listdir(imagedir)):
    	if filename.endswith(".png"):
            os.rename(os.path.join(imagedir,filename),os.path.join(os.path.dirname(outgallery),filename))
            
#__________________________________________________________________________________________________________
# Build the html pages showcasing the pictures
f = open(outgallery,'w')

htmlstring = '<!DOCTYPE html> <html> <body> <h2>Daily plots, updated on: ' + time_to_print + '</h2>'

for filename in sorted(os.listdir(os.path.dirname(outgallery))):
    	if filename.endswith(".png"):
            htmlstring += '<img src="'
            htmlstring +=filename
            htmlstring += ' "width="2000" >'
            
htmlstring += "</body> </html>"

f.write(htmlstring)
f.close()