# Standard
import os

# Statics
from bot.commons.keys import *

MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/nintendo')

PORT = int(os.environ.get("PORT", 5000))

if PORT == 5000:
    IP = '127.0.0.1'
else:
    IP = '0.0.0.0'


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
EMOJI_PLUS = '➕'
EMOJI_MINUS = '➖'
EMOJI_NINTENDO = ' 🍄'


PRICE_API = 'https://api.ec.nintendo.com/v1/price?country={country}&lang=en&ids={ids}'

WISHLIST_URL = 'https://nintendo-deals.herokuapp.com/wishlist'

SYSTEMS = {
    SWITCH_: {
        name_: 'Nintendo Switch',
        subreddit_: os.environ.get('SWITCH_SUBREDDIT', 'test3|supermarioposters').split('|'),
        system_: {
            NA_: 'switch',
            EU_: 'Nintendo Switch',
            JP_: 'switch',
        }
    },

    N3DS_: {
        name_: 'Nintendo 3DS',
        subreddit_: os.environ.get('3DS_SUBREDDIT', 'test4').split('|'),
        system_: {
            NA_: '3ds',
            EU_: '3DS',
            JP_: '3ds'
        }
    }
}

REGIONS = {
    NA_: {
        key_: NA_,
        name_: 'North America',
        api_: 'https://www.nintendo.com/json/content/get/filter/game?system={system}&limit={limit}&offset={offset}&sort=title&direction=asc{additional}'
    },

    EU_: {
        key_: EU_,
        name_: 'Europe & Friends',
        api_: 'https://search.nintendo-europe.com/en/select?q=*&start={start}&rows={limit}&wt=json&sort=title asc&fq=type:GAME AND system_names_txt:"{system}"'
    },

    JP_: {
        key_: JP_,
        name_: 'Japan',
        api_: 'https://www.nintendo.co.jp/{system}/software/data/eshopinfo.js',
        details_: {
            SWITCH_: 'https://ec.nintendo.com/JP/ja/titles/{}',
            N3DS_: 'https://www.nintendo.co.jp/titles/{}'
        }
    }
}

COUNTRIES = {
    CA_: {
        key_: CA_,
        name_: 'Canada',
        websites_: 'https://www.nintendo.com/en_CA/games/detail/{}',
        flag_: '🇨🇦',
        region_: NA_,
        digits_: 5,
        currency_: '$',
        currency_code_: 'CAD'
    },

    MX_: {
        key_: 'MX',
        name_: 'Mexico',
        flag_: '🇲🇽',
        region_: NA_,
        digits_: 7,
        currency_: '$',
        currency_code_: 'MXN'
    },

    US_: {
        key_: US_,
        name_: 'United States of America',
        websites_: 'https://www.nintendo.com/games/detail/{}',
        flag_: '🇺🇸',
        region_: NA_,
        digits_: 5,
        currency_: '$',
        currency_code_: 'USD'
    },

    AU_: {
        key_: AU_,
        name_: 'Australia',
        flag_: '🇦🇺',
        region_: EU_,
        digits_: 5,
        currency_: '$',
        currency_code_: 'AUD'
    },

    EU_: {
        key_: EU_,
        name_: 'European Union',
        websites_: 'https://www.nintendo.es/Juegos/{}',
        flag_: '🇪🇺',
        region_: EU_,
        digits_: 5,
        currency_: '€',
        currency_code_: 'EUR'
    },

    GB_: {
        key_: GB_,
        name_: 'Great Britain',
        websites_: 'https://www.nintendo.co.uk/{}',
        flag_: '🇬🇧',
        region_: EU_,
        digits_: 5,
        currency_: '£',
        currency_code_: 'GBP'
    },

    RU_: {
        key_: RU_,
        name_: 'Russia',
        websites_: 'https://www.nintendo.ru/-/{}',
        flag_: '🇷🇺',
        region_: EU_,
        digits_: 7,
        currency_: '₽',
        currency_code_: 'RUB'
    },

    JP_: {
        key_: JP_,
        name_: 'Japan',
        websites_: 'https://ec.nintendo.com/JP/ja/titles/{}',
        flag_: '🇯🇵',
        region_: JP_,
        digits_: 7,
        currency_: '¥',
        currency_code_: 'JPY'
    }
}

CMD_ADD = 'add'
CMD_REMOVE = 'remove'
CMD_LIST = 'list'

