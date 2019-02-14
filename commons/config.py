import os

from commons.keys import ALIAS
from commons.keys import API
from commons.keys import CUT
from commons.keys import CURRENCY
from commons.keys import CURRENCY_CODE
from commons.keys import DETAILS
from commons.keys import DIGITS
from commons.keys import FLAG
from commons.keys import N3DS
from commons.keys import NAME
from commons.keys import REGION
from commons.keys import SUBREDDITS
from commons.keys import SWITCH
from commons.keys import TAG
from commons.keys import WEBSITE
from commons.keys import AU
from commons.keys import CA
from commons.keys import CH
from commons.keys import CZ
from commons.keys import EU
from commons.keys import GB
from commons.keys import ID
from commons.keys import JP
from commons.keys import MX
from commons.keys import NA
from commons.keys import NZ
from commons.keys import PL
from commons.keys import RU
from commons.keys import SE
from commons.keys import US
from commons.keys import ZA
from commons.settings import USER_SUBREDDIT

PRICE_API = 'https://api.ec.nintendo.com/v1/price?country={country}&lang=en&ids={ids}'


SWITCH_SUBREDDITS = os.environ.get('SWITCH_SUBREDDITS').split('|') if os.environ.get('SWITCH_SUBREDDITS') else []
N3DS_SUBREDDITS = os.environ.get('3DS_SUBREDDITS').split('|') if os.environ.get('3DS_SUBREDDITS') else []

SYSTEMS = {
    SWITCH: {
        ID: SWITCH,
        NAME: 'Nintendo Switch',
        TAG: 'NX',
        CUT: -5,
        SUBREDDITS: [USER_SUBREDDIT] + SWITCH_SUBREDDITS,
        ALIAS: {
            NA: 'switch',
            EU: 'Nintendo Switch',
            JP: 'switch',
        },
    },

    N3DS: {
        ID: N3DS,
        NAME: 'Nintendo 3DS',
        TAG: '3DS',
        CUT: -4,
        SUBREDDITS: [USER_SUBREDDIT] + N3DS_SUBREDDITS,
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
        NAME: 'Europe',
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
    CA: {
        ID: CA,
        NAME: 'Canada',
        WEBSITE: 'https://www.nintendo.com/en_CA/games/detail/{}',
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
    US: {
        ID: US,
        NAME: 'United States of America',
        WEBSITE: 'https://www.nintendo.com/games/detail/{}',
        FLAG: '🇺🇸',
        REGION: NA,
        DIGITS: 5,
        CURRENCY: '$',
        CURRENCY_CODE: 'USD'
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
    CH: {
        ID: CH,
        NAME: 'Switzerland',
        WEBSITE: 'https://www.nintendo.ch/de/Spiele/{}',
        FLAG: '🇨🇭',
        REGION: EU,
        DIGITS: 5,
        CURRENCY: '₣',
        CURRENCY_CODE: 'CHF'
    },
    CZ: {
        ID: CZ,
        NAME: 'Czech Republic',
        FLAG: '🇨🇿',
        REGION: EU,
        DIGITS: 7,
        CURRENCY: 'Kč',
        CURRENCY_CODE: 'CZK'
    },
    EU: {
        ID: EU,
        NAME: 'European Union',
        WEBSITE: 'https://www.nintendo.es/Juegos/{}',
        FLAG: '🇪🇺',
        REGION: EU,
        DIGITS: 5,
        CURRENCY: '€',
        CURRENCY_CODE: 'EUR'
    },
    GB: {
        ID: GB,
        NAME: 'Great Britain',
        WEBSITE: 'https://www.nintendo.co.uk/{}',
        FLAG: '🇬🇧',
        REGION: EU,
        DIGITS: 5,
        CURRENCY: '£',
        CURRENCY_CODE: 'GBP'
    },
    NZ: {
        ID: NZ,
        NAME: 'New Zealand',
        FLAG: '🇳🇿',
        REGION: EU,
        DIGITS: 5,
        CURRENCY: '$',
        CURRENCY_CODE: 'NZD'
    },
    PL: {
        ID: PL,
        NAME: 'Poland',
        FLAG: '🇵🇱',
        REGION: EU,
        DIGITS: 6,
        CURRENCY: 'zł',
        CURRENCY_CODE: 'PLN'
    },
    RU: {
        ID: RU,
        NAME: 'Russia',
        WEBSITE: 'https://www.nintendo.ru/-/{}',
        FLAG: '🇷🇺',
        REGION: EU,
        DIGITS: 7,
        CURRENCY: '₽',
        CURRENCY_CODE: 'RUB'
    },
    SE: {
        ID: SE,
        NAME: 'Sweden',
        FLAG: '🇸🇪',
        REGION: EU,
        DIGITS: 7,
        CURRENCY: 'kr',
        CURRENCY_CODE: 'SEK'
    },
    ZA: {
        ID: ZA,
        NAME: 'South Africa',
        WEBSITE: 'https://www.nintendo.co.za/Games/{}',
        FLAG: '🇿🇦',
        REGION: EU,
        DIGITS: 7,
        CURRENCY: 'R',
        CURRENCY_CODE: 'ZAR'
    },

    JP: {
        ID: JP,
        NAME: 'Japan',
        WEBSITE: 'https://ec.nintendo.com/JP/ja/titles/{}',
        FLAG: '🇯🇵',
        REGION: JP,
        DIGITS: 7,
        CURRENCY: '¥',
        CURRENCY_CODE: 'JPY'
    },
}

