import os
from flask import (
    Flask,
    url_for,
    request,
    redirect,
    flash,
    make_response,
    render_template
)
from flask_oauthlib.client import OAuth
from boto.dynamodb2.table import Table
from boto.dynamodb2.items import Item
users = Table(os.getenv("DYNAMO_TABLE", "users"))
application = Flask(__name__)
application.config.update(
    DEBUG=os.getenv("DEBUG", False),
    SECRET_KEY=os.getenv("SECRET_KEY", "dev")
)

oauth = OAuth()
twitter = oauth.remote_app(
    "twitter",
    base_url="https://api.twitter.com/1.1/",
    request_token_url="https://api.twitter.com/oauth/request_token",
    access_token_url="https://api.twitter.com/oauth/access_token",
    authorize_url="https://api.twitter.com/oauth/authenticate",
    consumer_key=os.getenv("TWITTER_KEY"),
    consumer_secret=os.getenv("TWITTER_SECRET")
)


@twitter.tokengetter
def get_twitter_token(token=None):
    username = request.cookies.get('username')
    try:
        user = users.get_item(username, consistent=True)
        return (user['key'], user['secret'])
    except:
        return None


@application.route('/oauth-authorized')
def twitter_auth():
    next_url = request.args.get('next') or url_for('index')
    resp = twitter.authorized_response()
    if resp is None:
        flash(u"problem")
        return redirect(next_url)
    try:
        user = users.get_item(resp['screen_name'], consistent=True)
    except:
        user = Item(users, data={'username': resp['screen_name']})

    user['key'] = resp['oauth_token']
    user['secret'] = resp['oauth_token_secret']
    user.save(overwrite=True)

    resp = make_response(redirect(next_url))
    resp.set_cookie('username', user['username'])
    return resp


@application.route('/')
def index():
    username = request.cookies.get('username')
    return render_template('index.html', username=username)


@application.route('/login')
def login():
    next_url = request.args.get('next') or request.referrer or None
    return twitter.authorize(callback=url_for('twitter_auth', next=next_url))


if __name__ == '__main__':
    application.run()
