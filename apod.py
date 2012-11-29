# Copyright 2012 Joseph R. Hunt
# All rights reserved.

# Bugs:
# - fails if APOD html changes
# - too many dependencies

import re
import urllib
import Image
import cStringIO
import sys
import requests
from oauth_hook import OAuthHook

baseurl = "http://apod.nasa.gov/apod/"
indexurl = baseurl + "astropix.html"
regex = r'a href="(image.*)"'
imgsize = 800, 800
twitterurl = "http://api.twitter.com/1/"
OAuthHook.consumer_key = ''
OAuthHook.consumer_secret = ''
access_token = ''
access_token_secret = ''
oauth_hook = OAuthHook(access_token, access_token_secret, header_auth=True)


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
        print "Unexpected Error:", sys.exc_info()[0]
        raise
    finally:
        #close things here
        imgfile.close()
        imgstr.close()


def update_twitter():
    try:
        client = requests.session(hooks={'pre_request': oauth_hook})
        image = open('apod.png', 'rb')
        response = client.post(
            ''.join([twitterurl, 'account/update_profile_background_image.json']),
            params={'tile': True},
            files={'image': ('apod.png', image)}
            )
        return response
    except:
        print "Unexpected Error:", sys.exec_info()[0]
        raise


if __name__ == '__main__':
    get_apod_image()
    update_twitter()
