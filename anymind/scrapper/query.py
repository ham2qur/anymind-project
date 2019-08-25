
import logging

logger = logging.getLogger(__name__)

HEADER = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; x64; fr; rv:1.9.2.13) Gecko/20101203 Firebird/3.6.13'}

INIT_URL = 'https://twitter.com/search?f=tweets&vertical=default&q={q}&l={lang}'
RELOAD_URL = 'https://twitter.com/i/search/timeline?f=tweets&vertical=' \
             'default&include_available_features=1&include_entities=1&' \
             'reset_error_state=false&src=typd&max_position={pos}&q={q}&l={lang}'
INIT_URL_USER = 'https://twitter.com/{u}'
RELOAD_URL_USER = 'https://twitter.com/i/profiles/show/{u}/timeline/tweets?' \
                  'include_available_features=1&include_entities=1&' \
                  'max_position={pos}&reset_error_state=false'
PROXY_URL = 'https://free-proxy-list.net/'


def get_query_url(query, lang, pos, from_user = False):
    if from_user:
        if pos is None:
            return INIT_URL_USER.format(u=query)
        else:
            return RELOAD_URL_USER.format(u=query, pos=pos)
    if pos is None:
        return INIT_URL.format(q=query, lang=lang)
    else:
        return RELOAD_URL.format(q=query, pos=pos, lang=lang)



def query_single_page(query, lang, pos, retry=50, from_user=False, timeout=60):
    """
    Returns tweets from the given URL.
    :param query: The query parameter of the query url
    :param lang: The language parameter of the query url
    :param pos: The query url parameter that determines where to start looking
    :param retry: Number of retries if something goes wrong.
    :return: The list of tweets, the pos argument for getting the next page.
    """
    url = get_query_url(query, lang, pos, from_user)
    logger.info('Scraping tweets from {}'.format(url))

    try:
        proxy = next(proxy_pool)
        logger.info('Using proxy {}'.format(proxy))
        response = requests.get(url, headers=HEADER, proxies={"http": proxy})
        if pos is None:  # html response
            html = response.text or ''
            json_resp = None
        else:
            html = ''
            try:
                json_resp = json.loads(response.text)
                html = json_resp['items_html'] or ''
            except ValueError as e:
                logger.exception('Failed to parse JSON "{}" while requesting "{}"'.format(e, url))

        tweets = list(Tweet.from_html(html))

        if not tweets:
            try:
                if json_resp:
                    pos = json_resp['min_position']
                    has_more_items = json_resp['has_more_items']
                    if not has_more_items:
                        logger.info("Twitter returned : 'has_more_items' ")
                        return [], None
                else:
                    pos = None
            except:
                pass
            if retry > 0:
                logger.info('Retrying... (Attempts left: {})'.format(retry))
                return query_single_page(query, lang, pos, retry - 1, from_user)
            else:
                return [], pos

        if json_resp:
            return tweets, urllib.parse.quote(json_resp['min_position'])
        if from_user:
            return tweets, tweets[-1].tweet_id
        return tweets, "TWEET-{}-{}".format(tweets[-1].tweet_id, tweets[0].tweet_id)

    except requests.exceptions.HTTPError as e:
        logger.exception('HTTPError {} while requesting "{}"'.format(
            e, url))
    except requests.exceptions.ConnectionError as e:
        logger.exception('ConnectionError {} while requesting "{}"'.format(
            e, url))
    except requests.exceptions.Timeout as e:
        logger.exception('TimeOut {} while requesting "{}"'.format(
            e, url))
    except json.decoder.JSONDecodeError as e:
        logger.exception('Failed to parse JSON "{}" while requesting "{}".'.format(
            e, url))

    if retry > 0:
        logger.info('Retrying... (Attempts left: {})'.format(retry))
        return query_single_page(query, lang, pos, retry - 1)

    logger.error('Giving up.')
    return [], None