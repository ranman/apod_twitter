# Copyright 2012 Joseph R. Hunt
# All rights reserved.

# Bugs:
# - fails if APOD html changes
# - too many dependencies

import re
import urllib
from PIL import Image
import cStringIO
import sys
from requests_oauthlib import OAuth1Session

baseurl = "http://apod.nasa.gov/apod/"
indexurl = baseurl + "astropix.html"
regex = r'a href="(image.*)"'
imgsize = 800, 800  # ((800**2*12)/8/1024/1024) anything less than 800 is below 800kb
twitterurl = "https://api.twitter.com/1.1/"
twitter = OAuth1Session(
    '',
    client_secret="",
    resource_owner_key="",
    resource_owner_secret=""
)


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
        print("Unexpected Error:\n{0}".format(sys.exc_info()[0]))
        raise
    finally:
        #close things here
        imgfile.close()
        imgstr.close()


def update_twitter():
    try:
        image = open('apod.png', 'rb')
        response = twitter.post(
            ''.join(
                [twitterurl, 'account/update_profile_background_image.json']),
            params={'tile': True, 'use': True},
            files={'image': ('apod.png', image)}
            )
        return response
    except:
        print("Unexpected Error:\n{0}".format(sys.exc_info()[0]))
        raise


if __name__ == '__main__':
    get_apod_image()
    print(update_twitter())
