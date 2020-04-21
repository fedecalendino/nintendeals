### Nintendo of America

```python

from nintendeals import noa
from nintendeals.classes.games import Game

game: Game = noa.game_info(nsuid="70010000000025")
print(game.product_code)
print(game.title)
print(game.slug)
print()
print(game.release_date)
print(", ".join(game.genres))
print(game.players)
print(game.publisher, "/", game.developer)
print()
print(game.demo)
print(game.dlc)
print(game.free_to_play)
print(game.game_vouchers)
print(game.online_play)
print(game.save_data_cloud)
```

```text
>> HACPAAAAA
>> The Legend of Zelda: Breath of the Wild
>> the-legend-of-zelda-breath-of-the-wild-switch
>>
>> 2017-03-03 00:00:00
>> Action, Adventure, Other, Role-Playing
>> 1
>> Nintendo / Nintendo
>>
>> False
>> True
>> False
>> True
>> False
>> True
```