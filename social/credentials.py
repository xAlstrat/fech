import twitter

from fech.settings.base import INSTAGRAM_USER, INSTAGRAM_PWD, TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_TOKEN_KEY, TWITTER_TOKEN_SECRET

from social.InstagramAPI import InstagramAPI


def get_instagram_api():
    return InstagramAPI(INSTAGRAM_USER, INSTAGRAM_PWD)


def get_twitter_api():
    return twitter.Api(consumer_key=TWITTER_CONSUMER_KEY,
                      consumer_secret=TWITTER_CONSUMER_SECRET,
                      access_token_key=TWITTER_TOKEN_KEY,
                      access_token_secret=TWITTER_TOKEN_SECRET)