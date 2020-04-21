### Nintendo of Europe

```python
from nintendeals import noe
from nintendeals.classes.games import Game

game: Game = noe.game_info(nsuid="70010000000023")
print(game.product_code)
print(game.title)
print()
print(game.release_date)
print(", ".join(game.genres))
print(game.players)
print(game.publisher, "/", game.developer)
print()
print(game.demo)
print(game.dlc)
print(game.free_to_play)
print(game.online_play)
print(game.save_data_cloud)
```

```text
>> HACPAAAAA
>> The Legend of Zelda: Breath of the Wild
>> 
>> 2017-03-03 00:00:00
>> Action, Adventure
>> 1
>> Nintendo / Nintendo
>> 
>> False
>> True
>> False
>> False
>> True

```