#!/usr/bin/python
import re
import urllib
from PIL import Image
import cStringIO
import boto
from boto.s3.key import Key
s3_conn = boto.connect_s3()
bucket = s3_conn.get_bucket("apod-twitter")
key = Key(bucket, "apod.png")

baseurl = "http://apod.nasa.gov/apod/"
indexurl = baseurl + "astropix.html"
regex = r'a href="(image.*)"'
# PNG is zlib compressed and the maximum possible compresson ratio is
# 1032:1, fuck that shit. Lets assume no compression.
# ((800**2*12)/8/1024/1024) anything less than 800 is below 800kb
imgsize = 800, 800


def get_apod_image():
    apodpage = urllib.urlopen(indexurl).read()  # grab the mainpage
    apod_url = re.search(regex, apodpage).group(1)  # find image url
    imgfile = urllib.urlopen(baseurl + apod_url)  # open the image file
    # parse it into memory (cStringIO is faster than StringIO)
    imgstr = cStringIO.StringIO(imgfile.read())
    img = Image.open(imgstr)
    img.convert("RGB")
    img.thumbnail(imgsize, Image.ANTIALIAS)
    imgstr = cStringIO.StringIO()
    img.save(imgstr, "PNG")
    key.set_contents_from_file(imgstr)

if __name__ == '__main__':
    get_apod_image()
