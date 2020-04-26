"""
Make an image gallery from html
"""
import os

imagedir="/home/pi/Desktop/Images"
outgallery="/var/www/html/index.html"

f = open(outgallery,'w')

htmlstring = '<!DOCTYPE html> <html> <body> <h2>Daily plots</h2>'

for filename in sorted(os.listdir(imagedir)):
    	if filename.endswith(".png"):
            htmlstring += '<img src="'
            htmlstring +=filename
            htmlstring += ' "width="2000" >'
            os.rename(os.path.join(imagedir,filename),os.path.join(os.path.dirname(outgallery),filename))
            
htmlstring += "</body> </html>"

f.write(htmlstring)
f.close()
