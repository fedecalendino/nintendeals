# Standard
import os

# Statics
from app.commons.keys import *


MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/nintendo')

VERSION = "v0.6"

REDDIT_USERNAME = os.environ.get("REDDIT_USERNAME")
REDDIT_PASSWORD = os.environ.get("REDDIT_PASSWORD")
REDDIT_CLIENTID = os.environ.get("REDDIT_CLIENTID")
REDDIT_CLIENTSECRET = os.environ.get("REDDIT_CLIENTSECRET")
REDDIT_USERAGENT = os.environ.get("REDDIT_USERAGENT")

EMOJI_NEW = '✨'
EMOJI_EXP_TOMORROW = '❗'
EMOJI_EXP_TODAY = '‼️'

N3DS = '3ds'
SWITCH = 'switch'

SYSTEMS = {
    SWITCH: {
        name_: 'Nintendo Switch',
        subreddit_: os.environ.get('SWITCH_SUBREDDIT', 'test'),
        frequency_: int(os.environ.get('SWITCH_POST_TIME_FRAME', '2'))
    }, N3DS: {
        name_: 'Nintendo 3DS',
        subreddit_: os.environ.get('3DS_SUBREDDIT', 'test'),
        frequency_: int(os.environ.get('3DS_POST_TIME_FRAME', '2'))
    }
}

UPDATE_FREQUENCY = int(os.environ.get('UPDATE_TIME_FRAME', 6 * 60 * 60))


REGIONS = {
    NA_: {
        key_: NA_,
        name_: 'North America',
        api_: {
            list_api_: 'https://www.nintendo.com/json/content/get/filter/game?system={}&sort=title&direction=asc&limit={}&offset={}{}',
            price_api_: 'https://api.ec.nintendo.com/v1/price?country={}&lang=en&ids={}'
        },
        countries_: {
            US_: {
                key_: US_,
                name_: 'United Stated of America',
                currency_: 'USD',
                flag_: '🇺🇸',
                website_: 'https://www.nintendo.com/games/detail/{}'
            },
            CA_: {
                key_: CA_,
                name_: 'Canada',
                currency_: 'CAD',
                flag_: '🇨🇦',
                website_: 'https://www.nintendo.com/en_CA/games/detail/{}'
            },
            MX_: {
                key_: 'MX',
                name_: 'Mexico',
                currency_: 'MXN',
                flag_: '🇲🇽',
                website_: ''
            }
        }
    }
}

