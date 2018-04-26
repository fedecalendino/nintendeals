# Standard
import os

# Statics
from app.commons.keys import *


MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/nintendo')

VERSION = "v2.5"

REDDIT_USERNAME = os.environ.get("REDDIT_USERNAME")
REDDIT_PASSWORD = os.environ.get("REDDIT_PASSWORD")
REDDIT_CLIENTID = os.environ.get("REDDIT_CLIENTID")
REDDIT_CLIENTSECRET = os.environ.get("REDDIT_CLIENTSECRET")
REDDIT_USERAGENT = os.environ.get("REDDIT_USERAGENT")

EMOJI_NEW = '✨'
EMOJI_EXP_TOMORROW = '❕'
EMOJI_EXP_TODAY = '❗'
EMOJI_MAX_DISCOUNT = '🔥'
EMOJI_METACRITIC = 'Ⓜ️'
EMOJI_USER = '👤'

N3DS_ = '3DS'
SWITCH_ = 'Switch'

SYSTEMS = {
    SWITCH_: {
        name_: 'Nintendo Switch',
        subreddit_: os.environ.get('SWITCH_SUBREDDIT', 'test'),
        frequency_: int(os.environ.get('SWITCH_POST_TIME_FRAME', '2')),
        system_: {
            NA_: 'switch',
            EU_: 'Nintendo Switch'
        }
    }, N3DS_: {
        name_: 'Nintendo 3DS',
        subreddit_: os.environ.get('3DS_SUBREDDIT', 'test'),
        frequency_: int(os.environ.get('3DS_POST_TIME_FRAME', '2')),
        system_: {
            NA_: '3ds',
            EU_: 'Nintendo 3ds'
        }
    }
}

UPDATE_FREQUENCY = int(os.environ.get('UPDATE_TIME_FRAME', 6 * 60 * 60))

PRICE_API = 'https://api.ec.nintendo.com/v1/price?country={country}&lang=en&ids={id}'

REGIONS = {
    NA_: {
        key_: NA_,
        name_: 'North America',
        api_: 'https://www.nintendo.com/json/content/get/filter/game?system={system}&limit={limit}&offset={offset}&sort=title&direction=asc&sale=true',
        countries_: {
            US_: {
                key_: US_,
                name_: 'United States of America',
                websites_: 'https://www.nintendo.com/games/detail/{}',
                flag_: '🇺🇸'
            },
            CA_: {
                key_: CA_,
                name_: 'Canada',
                websites_: 'https://www.nintendo.com/en_CA/games/detail/{}',
                flag_: '🇨🇦'
            },
            MX_: {
                key_: 'MX',
                name_: 'Mexico',
                flag_: '🇲🇽'
            }
        }
    },
    EU_: {
        key_: EU_,
        name_: 'Europe & Friends',
        api_: 'https://search.nintendo-europe.com/en/select?q=*&start={start}&wt=json&sort=title asc&fq=type:GAME AND price_has_discount_b:"true" AND system_names_txt:"{system}"',
        countries_: {
            EU_: {
                key_: ES_,
                name_: 'European Union',
                websites_: 'https://www.nintendo.es/Juegos/{}',
                flag_: '🇪🇺'
            },
            GB_: {
                key_: GB_,
                name_: 'Great Britain',
                websites_: 'https://www.nintendo.co.uk/{}',
                flag_: '🇬🇧'
            },
            AU_: {
                key_: AU_,
                name_: 'Australia',
                flag_: '🇦🇺'
            },
#            RU_: {
#                key_: RU_,
#                name_: 'Russia',
#                websites_: 'https://nintendo.ru/{}',
#                flag_: '🇷🇺'
#            },
            ZA_: {
                key_: ZA_,
                name_: 'South Africa',
                websites_: 'https://www.nintendo.co.za/Games/{}',
                flag_: '🇿🇦'
            },
            CH_: {
                key_: CH_,
                name_: 'Switzerland',
                websites_: 'https://www.nintendo.ch/de/Games/{}',
                flag_: '🇨🇭'
            }
        }
    }
}
