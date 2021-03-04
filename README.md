 # nintendeals
> "nintendeals was a bot, he loved learning and deals on nintendo's eshop." **LetsFunHans** 💬️

[![Version](https://img.shields.io/pypi/v/nintendeals?logo=pypi)](https://pypi.org/project/nintendeals)
[![Quality Gate Status](https://img.shields.io/sonar/alert_status/fedecalendino_nintendeals?logo=sonarcloud&server=https://sonarcloud.io)](https://sonarcloud.io/dashboard?id=fedecalendino_nintendeals)
[![CodeCoverage](https://img.shields.io/sonar/coverage/fedecalendino_nintendeals?logo=sonarcloud&server=https://sonarcloud.io)](https://sonarcloud.io/dashboard?id=fedecalendino_nintendeals)

-----

Named after the my old [reddit bot](https://reddit.com/u/nintendeals), nintendeals is now a library with 
all the scrapers and integrations of nintendo services that I used.


## Terminology

Before getting into any details first we need too get into the same page with a few terms:

### Region

Here we have three regions NA, EU and JP each one corresponding to Nintendo of America (NoA), Nintendo of Europe (NoE)
and Nintendo of Japan (NoJ). Each of these regions have set of countries they are "in charge of":

NoA:
  * Canada
  * Mexico
  * United Stated
  
NoE:
  * Every country in the European Union
  * Australia
  * New Zealand
  * South Africa
  
NoJ:
  * Japan
  
### nsuid

An nsuid is a 14 digit long string which Nintendo uses to identify games on each region. 
Taking Breath of the Wild as an example, we have these 3 nsuids for it (one per region):

```    
  * 70010000000025 (NA)
  * 70010000000023 (EU)
  * 70010000000026 (JP)
```
    
### Product Code

The product code is another type of ID that Nintendo uses, it usually is a 8/9 character long string.
Taking Splatoon 2 as an example, we have these 3 product codes for it (one per region):

```
  * HACPAAB6B (NA)
  * HACPAAB6C (EU)
  *  HACAAB6A (JP)
```

The difference with the nsuid is that the product code has a constant between all regions (`AAB6` in this example), 
and this is what I decided to call [unique_id](https://github.com/fedecalendino/nintendeals/blob/master/nintendeals/commons/classes/games.py#L56) 
and it is what we can you to join a game across all regions.

You can also see this code in the front of your Nintendo Switch [cartridge](https://media.karousell.com/media/photos/products/2019/08/17/splatoon_2_cartridge_only_1566040350_4f38e061_progressive.jpg).

## Services

This library provides three types of services: Info, Listing, Searching and Pricing. Each region has a different 
version of Info, Listing and Searching, but Pricing is the same for all as it only requires a country and an nsuid.

### Listing

Even thought there are different version for each region, they all work in the same way. Given a supported 
platform ([for this library](https://github.com/fedecalendino/nintendeals/blob/master/nintendeals/constants.py#L15))
they will retrieve a list games in the selected region (in the form of an iterator).

```python
from nintendeals import noa

for game in noa.list_switch_games():
    print(game.title, "/", game.nsuid)
```

```text
>> ARMS / 70010000000392
>> Astro Duel Deluxe / 70010000000301
>> Axiom Verge / 70010000000821
>> Azure Striker GUNVOLT: STRIKER PACK / 70010000000645
>> Beach Buggy Racing / 70010000000721
```

```python
from nintendeals import noe

for game in noe.list_switch_games():
    print(game.title, "/", game.nsuid)
```

```text
>> I and Me / 70010000000314
>> In Between / 70010000009184
>> Ghost 1.0 / 70010000001386
>> Resident Evil 0 / 70010000012848
>> 64.0 / 70010000020867
```

### Searching

Built on top of the listing services, these provide a simple way to search for games by title or release_date:

```python
from nintendeals import noa

for game in noa.search_switch_games(query="Zelda"):
    print(game.title, "/", game.nsuid)
```

```text
>> The Legend of Zelda™: Link’s Awakening / 70010000020033
>> The Legend of Zelda™: Link's Awakening: Dreamer Edition / None
>> Cadence of Hyrule: Crypt of the NecroDancer Featuring The Legend of Zelda / 70010000021364
>> The Legend of Zelda™: Breath of the Wild / 70010000000025
```


### Info

Once you have the nsuid of the game that you want, you can call the `game_info` service. And again, each region has their
own version but they all work the same, but keep in mind that you need to use the correct nsuid for each region.
Coming back to the nsuid of Breath of the Wild as an example:

```python
from nintendeals import noa

game = noa.game_info("70010000000025")
print(game.title)
print(game.product_code, game.unique_id)
print(game.release_date)
print(game.players)
print(str(game.rating[0]), game.rating[1])
print(game.eshop.ca_fr)

for feature, value in game.features.items():
    print(" *", str(feature), ":", value)
```

```text
>> The Legend of Zelda™: Breath of the Wild
>> HACPAAAAA AAAA
>> 2017-03-03 00:00:00
>> 1
>> ESRB Everyone 10+
>> https://www.nintendo.com/fr_CA/games/detail/the-legend-of-zelda-breath-of-the-wild-switch
>>  * Demo Available : False
>>  * DLC Available : False
>>  * Nintendo Switch Online Required : True
>>  * Save Data Cloud Supported : True
```

```python
from nintendeals import noe

game = noe.game_info("70010000000023")
print(game.title)
print(game.product_code, game.unique_id)
print(game.release_date)
print(game.players)
print(str(game.rating[0]), game.rating[1])
print(game.eshop.uk_en)

for feature, value in game.features.items():
    print(" *", str(feature), ":", value)
```

```text
>> The Legend of Zelda: Breath of the Wild
>> HACPAAAAA AAAA
>> 2017-03-03 00:00:00
>> 1
>> PEGI 12
>> https://www.nintendo.co.uk/Games/Nintendo-Switch/The-Legend-of-Zelda-Breath-of-the-Wild-1173609.html
>>  * Amiibo Supported : True
>>  * Demo Available : False
>>  * DLC Available : False
>>  * Nintendo Switch Online Required : False
>>  * Save Data Cloud Supported : True
>>  * Voice Chat Supported : False
```

```python
from nintendeals import noj

game = noj.game_info("70010000000026")
print(game.title)
print(game.product_code, game.unique_id)
print(game.release_date)
print(game.players)
print(str(game.rating[0]), game.rating[1])
print(game.eshop.jp_jp)

for feature, value in game.features.items():
    print(" *", str(feature), ":", value)
```

```text
>> ゼルダの伝説　ブレス オブ ザ ワイルド
>> HACAAAAA AAAA
>> 2017-03-03 00:00:00
>> 1
>> CERO B
>> https://store-jp.nintendo.com/list/software/70010000000026.html
>>  * Amiibo Supported : True
>>  * DLC Available : True
>>  * Nintendo Switch Online Required : False
```


### Pricing

Given a country code (using the alpha-2 iso standard) and a game or list of games this service will fetch the current 
pricing of that/those games for that country. Since this service uses nsuids to fetch the price, make sure that the
games that you provide have the regional nsuid that matches the country that you want. For example, only the nsuid for
the American region will be able to fetch you the prices of Canada, Mexico and United Stated but not for Japan or Spain.

```python
from nintendeals import noe
from nintendeals.api import prices

game = noe.game_info("70010000007705")
print(game.title)
print()

price = prices.get_price(game, country="CZ")  # Czech Republic
print(price.currency)
print(price.value)
print(price.sale_discount, "%")
print(price.sale_value)
print(price.sale_start)
print(price.sale_end)

# Alternatively you can do this for the same effect:
price = game.price(country="CZ") 
``` 

```text
Dead Cells

CZK
625.0
80 %
500.0
2020-04-19 22:00:00
2020-05-03 21:59:59
```

To reduce the amount of call to the prices api, you can also use the `get_prices` service that works in a similar way
but it expects a list of games instead of only one:

```python
from nintendeals import noa
from nintendeals.api import prices

botw = noa.game_info("70010000000025")
print(botw.title)
celeste = noa.game_info("70010000006442")
print(celeste.title)

print()

prices = prices.get_prices([botw, celeste], country="US")
for nsuid, price in prices:
    print(nsuid)
    print(price.value)
    print(price.sale_value)
    print()
```

```text
The Legend of Zelda™: Breath of the Wild
Celeste

70010000000025
59.99
None

70010000006442
19.99
4.99
```
