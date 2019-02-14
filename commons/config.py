import os

from commons.keys import ALIAS
from commons.keys import API
from commons.keys import AU
from commons.keys import CA
from commons.keys import CURRENCY
from commons.keys import CURRENCY_CODE
from commons.keys import DETAILS
from commons.keys import DIGITS
from commons.keys import EU
from commons.keys import FLAG
from commons.keys import GB
from commons.keys import ID
from commons.keys import JP
from commons.keys import MX
from commons.keys import N3DS
from commons.keys import NA
from commons.keys import NAME
from commons.keys import REGION
from commons.keys import RU
from commons.keys import SUBREDDITS
from commons.keys import SWITCH
from commons.keys import US
from commons.keys import WEBSITES
from commons.settings import USER_SUBREDDIT

PRICE_API = 'https://api.ec.nintendo.com/v1/price?country={country}&lang=en&ids={ids}'


SYSTEMS = {
    SWITCH: {
        NAME: 'Nintendo Switch',
        SUBREDDITS: [USER_SUBREDDIT] + os.environ.get('SWITCH_SUBREDDITS', 'uaab').split('|'),
        ALIAS: {
            NA: 'switch',
            EU: 'Nintendo Switch',
            JP: 'switch',
        },
    },

    N3DS: {
        NAME: 'Nintendo 3DS',
        SUBREDDITS: [USER_SUBREDDIT] + os.environ.get('3DS_SUBREDDITS', 'uaab').split('|'),
        ALIAS: {
            NA: '3ds',
            EU: '3DS',
            JP: '3ds'
        },
    },
}

REGIONS = {
    NA: {
        ID: NA,
        NAME: 'North America',
        API: 'https://www.nintendo.com/json/content/get/filter/game'
             '?system={system}&limit={limit}&offset={offset}&sort=title&direction=asc{additional}'
    },

    EU: {
        ID: EU,
        NAME: 'Europe & Friends',
        API: 'https://search.nintendo-europe.com/en/select'
             '?q=*&start={start}&rows={limit}&wt=json&sort=title asc&fq=type:GAME AND system_names_txt:"{system}"'
    },

    JP: {
        ID: JP,
        NAME: 'Japan',
        API: 'https://www.nintendo.co.jp/{system}/software/data/eshopinfo.js',
        DETAILS: {
            SWITCH: 'https://ec.nintendo.com/JP/ja/titles/{}',
            N3DS: 'https://www.nintendo.co.jp/titles/{}'
        }
    }
}

COUNTRIES = {
    US: {
        ID: US,
        NAME: 'United States of America',
        WEBSITES: 'https://www.nintendo.com/games/detail/{}',
        FLAG: '🇺🇸',
        REGION: NA,
        DIGITS: 5,
        CURRENCY: '$',
        CURRENCY_CODE: 'USD'
    },

    CA: {
        ID: CA,
        NAME: 'Canada',
        WEBSITES: 'https://www.nintendo.com/en_CA/games/detail/{}',
        FLAG: '🇨🇦',
        REGION: NA,
        DIGITS: 5,
        CURRENCY: '$',
        CURRENCY_CODE: 'CAD'
    },

    MX: {
        ID: 'MX',
        NAME: 'Mexico',
        FLAG: '🇲🇽',
        REGION: NA,
        DIGITS: 7,
        CURRENCY: '$',
        CURRENCY_CODE: 'MXN'
    },

    EU: {
        ID: EU,
        NAME: 'European Union',
        WEBSITES: 'https://www.nintendo.es/Juegos/{}',
        FLAG: '🇪🇺',
        REGION: EU,
        DIGITS: 5,
        CURRENCY: '€',
        CURRENCY_CODE: 'EUR'
    },

    GB: {
        ID: GB,
        NAME: 'Great Britain',
        WEBSITES: 'https://www.nintendo.co.uk/{}',
        FLAG: '🇬🇧',
        REGION: EU,
        DIGITS: 5,
        CURRENCY: '£',
        CURRENCY_CODE: 'GBP'
    },

    RU: {
        ID: RU,
        NAME: 'Russia',
        WEBSITES: 'https://www.nintendo.ru/-/{}',
        FLAG: '🇷🇺',
        REGION: EU,
        DIGITS: 7,
        CURRENCY: '₽',
        CURRENCY_CODE: 'RUB'
    },

    AU: {
        ID: AU,
        NAME: 'Australia',
        FLAG: '🇦🇺',
        REGION: EU,
        DIGITS: 5,
        CURRENCY: '$',
        CURRENCY_CODE: 'AUD'
    },

    JP: {
        ID: JP,
        NAME: 'Japan',
        WEBSITES: 'https://ec.nintendo.com/JP/ja/titles/{}',
        FLAG: '🇯🇵',
        REGION: JP,
        DIGITS: 7,
        CURRENCY: '¥',
        CURRENCY_CODE: 'JPY'
    }
}
