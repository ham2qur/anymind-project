from django.test import TestCase
from . import TEST_RESPONSE_TEXT, SAMPLE_TWEET
from .views import tweet_parser

class TestCase(TestCase):

    def test_tweet_parser(self):
        limit = 20
        data = tweet_parser(TEST_RESPONSE_TEXT, limit=limit)
        self.assertEqual(limit, len(data))

    def test_tweet_from_soup(self):
        limit = 1
        tweets = tweet_parser(TEST_RESPONSE_TEXT, limit=limit)
        tweet = tweets[0]
        self.assertEqual(SAMPLE_TWEET['tweet_id'], tweet['tweet_id'])
        self.assertEqual(SAMPLE_TWEET['user_id'], tweet['user_id'])

