import re

from bs4 import BeautifulSoup
import requests
from django.http import JsonResponse
import logging
_logger = logging.getLogger('__name__')

# Fix header for each request
HEADER = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; x64; fr; rv:1.9.2.13) Gecko/20101203 Firebird/3.6.13'}

# TWEETS_BY_TAGS_URL = "https://twitter.com/search?q=%23{0}"
TWEETS_BY_TAGS_URL = 'https://twitter.com/search?f=tweets&vertical=default&q=%23{0}'
TWEETS_BY_USER_URL = "https://twitter.com/search?f=tweets&vertical=default&q=%40{0}"


def tweet_from_soup(tweet):
    tweet_div = tweet.find('div', 'tweet')
    username = tweet_div["data-screen-name"]
    fullname = tweet_div["data-name"]
    user_id = tweet_div["data-user-id"]
    tweet_id = tweet_div["data-tweet-id"]
    tweet_url = tweet_div["data-permalink-path"]
    timestamp_epochs = int(tweet.find('span', '_timestamp')['data-time'])
    try:
        retweet_id = tweet_div["data-retweet-id"]
        retweeter_username = tweet_div["data-retweeter"]
        retweeter_userid = tweet_div.find('a', "pretty-link js-user-profile-link")["data-user-id"]
        is_retweet = 1
    except:
        retweet_id = ""
        retweeter_username = ""
        retweeter_userid = ""
        is_retweet = 0

    text = tweet.find('p', 'tweet-text').text or ""
    replies = int(tweet.find(
        'span', 'ProfileTweet-action--reply u-hiddenVisually').find(
        'span', 'ProfileTweet-actionCount')['data-tweet-stat-count'] or '0')
    retweets = int(tweet.find(
        'span', 'ProfileTweet-action--retweet u-hiddenVisually').find(
        'span', 'ProfileTweet-actionCount')['data-tweet-stat-count'] or '0')
    likes = int(tweet.find(
        'span', 'ProfileTweet-action--favorite u-hiddenVisually').find(
        'span', 'ProfileTweet-actionCount')['data-tweet-stat-count'] or '0')
    html = str(tweet.find('p', 'tweet-text')) or ""

    tweet = {"username": username,
             "fullname": fullname,
             "user_id": user_id,
             "tweet_id": tweet_id,
             "tweet_url": tweet_url,
             "timestamp_epochs": timestamp_epochs,
             "replies": replies,
             "retweets": retweets,
             "likes": likes,
             "is_retweet": is_retweet,
             "retweeter_username": retweeter_username,
             "retweeter_userid": retweeter_userid,
             "retweet_id": retweet_id,
             "text": text,
             "html": html
             }
    return tweet

def user_tweets_from_soup(tag_prof_header, tag_prof_nav):
    """
    Returns the scraped user data from a twitter user page.
    :param tag_prof_header: captures the left hand part of user info
    :param tag_prof_nav: captures the upper part of user info
    :return: Returns a User object with captured data via beautifulsoup
    """

    user = tag_prof_header.find('a', {'class': 'ProfileHeaderCard-nameLink u-textInheritColor js-nav'})[
        'href'].strip("/")
    full_name = tag_prof_header.find('a', {'class': 'ProfileHeaderCard-nameLink u-textInheritColor js-nav'}).text

    location = tag_prof_header.find('span', {'class': 'ProfileHeaderCard-locationText u-dir'})
    if location is None:
        location = "None"
    else:
        location = location.text.strip()

    blog = tag_prof_header.find('span', {'class': "ProfileHeaderCard-urlText u-dir"})
    if blog is None:
        blog = "None"
    else:
        blog = blog.text.strip()

    date_joined = tag_prof_header.find('div', {'class': "ProfileHeaderCard-joinDate"}).find('span', {
        'class': 'ProfileHeaderCard-joinDateText js-tooltip u-dir'})['title']
    if date_joined is None:
        data_joined = "Unknown"
    else:
        date_joined = date_joined.strip()

    tag_verified = tag_prof_header.find('span', {'class': "ProfileHeaderCard-badges"})
    if tag_verified is not None:
        is_verified = 1

    id = tag_prof_nav.find('div', {'class': 'ProfileNav'})['data-user-id']
    tweets = tag_prof_nav.find('span', {'class': "ProfileNav-value"})['data-count']
    if tweets is None:
        tweets = 0
    else:
        tweets = int(tweets)

    following = tag_prof_nav.find('li', {'class': "ProfileNav-item ProfileNav-item--following"}). \
        find('span', {'class': "ProfileNav-value"})['data-count']
    if following is None:
        following = 0
    else:
        following = int(following)

    followers = tag_prof_nav.find('li', {'class': "ProfileNav-item ProfileNav-item--followers"}). \
        find('span', {'class': "ProfileNav-value"})['data-count']
    if followers is None:
        followers = 0
    else:
        followers = int(followers)

    likes = tag_prof_nav.find('li', {'class': "ProfileNav-item ProfileNav-item--favorites"}). \
        find('span', {'class': "ProfileNav-value"})['data-count']
    if likes is None:
        likes = 0
    else:
        likes = int(likes)

    lists = tag_prof_nav.find('li', {'class': "ProfileNav-item ProfileNav-item--lists"})
    if lists is None:
        lists = 0
    elif lists.find('span', {'class': "ProfileNav-value"}) is None:
        lists = 0
    else:
        lists = lists.find('span', {'class': "ProfileNav-value"}).text
        lists = int(lists)
    return {
        "user": user,
        "full_name": full_name,
        "location": location,
        "blog": blog,
        "date_joined": date_joined,
        "id": id,
        "tweets": tweets,
        "following": following,
        "followers": followers,
        "likes": likes,
        "lists": lists,
        "is_verified": is_verified
    }

def tweet_parser(text, limit):
    # parse tweets from the provide raw html text

    # using LXML due to more accurate in parsing
    soup = BeautifulSoup(text, 'lxml')
    all_tweets = list()

    tweets = soup.find_all('li', 'js-stream-item')
    for tweet in tweets:
        all_tweets.append(tweet_from_soup(tweet))
    _logger.info(all_tweets)
    return all_tweets

def tweets_by_user_parser(text, limit):
    # parse tweets from the provide raw html text

    # using LXML due to more accurate in parsing
    soup = BeautifulSoup(text, 'lxml')
    user_profile_header = soup.find("div", {"class": 'ProfileHeaderCard'})
    user_profile_canopy = soup.find("div", {"class": 'ProfileCanopy-nav'})

    all_tweets = list()
    if user_profile_header and user_profile_canopy:
        all_tweets = user_tweets_from_soup()
    return all_tweets

def tweets_by_hashtag(request, tag):
    limit = request.GET.get('limit')
    html = requests.get(TWEETS_BY_TAGS_URL.format(tag),
                        headers=HEADER)

    return JsonResponse(
        data=tweet_parser(html.text, limit),
        safe=False
    )

def user_tweets(request, user):
    limit = request.GET.get('limit')
    r = requests.get(TWEETS_BY_USER_URL.format(user))
    return JsonResponse(
        data=tweets_by_user_parser(r.text, limit),
        safe=False
    )
