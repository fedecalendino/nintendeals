### Nintendo of Japan

```python
from nintendeals import noj
from nintendeals.classes.games import Game

game: Game = noj.game_info(nsuid="70010000000026")
print(game.product_code)
print(game.title)
print()
print(game.release_date)
print(", ".join(game.genres))
print(game.players)
print(game.publisher)
print()
print(game.demo)
print(game.dlc)
print(game.free_to_play)
print(game.online_play)
print(game.save_data_cloud)
```

```text
>> HACAAAAA
>> ゼルダの伝説　ブレス オブ ザ ワイルド
>> 
>> 2017-03-03 00:00:00
>> アクション, アドベンチャー
>> 1
>> 任天堂
>> 
>> False
>> True
>> False
>> False
>> True

```