# Copyright 2012 Joseph R. Hunt
# All rights reserved.

# Bugs:
# - fails if APOD html changes
# - too many dependencies

import re
import urllib
import Image
import cStringIO

baseurl = "http://apod.nasa.gov/apod/"
indexurl = baseurl + "astropix.html"
regex = r'a href="(image.*)"'
imgsize = 800, 800


def get_apod_image():
    try:
        apodpage = urllib.urlopen(indexurl).read()  # grab the mainpage
        apod_url = re.search(regex, apodpage).group(1)  # find image url
        imgfile = urllib.urlopen(baseurl + apod_url)  # open the image file
        imgstr = cStringIO.StringIO(imgfile.read())  # parse it into memory (cStringIO is faster than StringIO)
        img = Image.open(imgstr)
        img.convert("RGB")
        img.thumbnail(imgsize, Image.ANTIALIAS)
        img.save("apod.png", "PNG")
    except:
        # not an image or unreachable link
        print "problem getting image"
    finally:
        #close things here
        apodpage.close()
        imgfile.close()
        img.close()
        imgstr.close()
        print "everything closed"


if __name__ == '__main__':
    get_apod_image()
