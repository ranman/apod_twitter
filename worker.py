#!/usr/bin/python
import os
import requests
from requests_oauthlib import OAuth1
import boto.sqs
from boto.sqs.jsonmessage import JSONMessage
sqs_conn = boto.sqs.connect_to_region("us-east-1")
q = sqs_conn.get_queue("apod_twitter")
errorq = sqs_conn.get_queue("apod_twitter_errors")
q.set_message_class(JSONMessage)
s3_conn = boto.connect_s3()
bucket = s3_conn.get_bucket("apod-twitter")
url = "https://api.twitter.com/1.1/"
endpoint = "account/update_profile_background_image.json"
auth = OAuth1(
    os.getenv("TWITTER_KEY"),
    os.getenv("TWITTER_SECRET")
)
image = bucket.get("apod.png")


def get_messages():
    return q.get_messages(
        num_messages=10,
        visibility_timeout=60*5,
        wait_time_seconds=60*10
    )


def process_a_few_messages():
    messages = get_messages()
    while len(messages) > 0:
        for message in messages:
            update_twitter(message)
        messages = q.get_messages()


def update_twitter(message):
    auth.client.resource_owner_key = unicode(message['key'])
    auth.client.resource_owner_secret = unicode(message['secret'])
    image = open('apod.png', 'rb')  # get this from S3
    response = requests.post(
        url+endpoint,
        params={'tile': True, 'use': True},
        files={'image': ('apod.png', image)},
        auth=auth
    )
    if response.status_code == 200:
        message.delete()
    else:
        errorq.write(message['username'])


if __name__ == '__main__':
    process_a_few_messages()
