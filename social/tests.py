from django.test import TestCase

# Create your tests here.
from social.credentials import get_twitter_api


def test_twitter_login():
    api = get_twitter_api()
    print(api.VerifyCredentials())