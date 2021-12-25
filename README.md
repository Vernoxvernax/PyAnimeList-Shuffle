# PyAnimeList-Shuffle

##### Discord: DepriSheep#1841

This projects heavily relies on [Jikan](https://jikan.moe/) (v3), an unofficial MyAnimeList API.

## Telegram Bot:
#### Merry Christmas: https://t.me/pyanimelist_bot
###### Doesn't need any setup on your side, just text `/start`.

## Installation / Usage:
```
$ git clone https://github.com/Vernoxvernax/PyAnimeList-Shuffle.git
$ cd PyAnimeList-Shuffle
$ python -m pip install -r requirements.txt
$ python pyanimelist-shuffle.py
```
###### Python is a requirement.

## The Code:
Jikan provides great detailed json files, featuring all the details you could want.
To fight people, making their own database, using that data, MyAnimeList itself limits it to one request every 4 seconds.
Unfortunately, those json files are also limited to 300 entries, so for bigger lists, one will have to send multiple requests until the end has been found.
The Jikan API also provides only very little possibilities to filter the requests. Due to all this, the script fetches every page and then applies given filters, such as genre, watching status, etc. locally.
Due to recent changes (to my script) it is now possible to cache your _anime_-list locally, if activated.

## To-Do:
* Look into discord bot api
* Max/Min amount of EPs/Chapters
* More detailed output (genre, score, EP count)

## Demonstration:
![](https://i.imgur.com/nP7T9s7.png)
___
You might ask yourself: why not use this great [Spin.moe](https://spin.moe/) app instead?
Well even though it's a lot easier to use, it doesn't support filtering genres and cli so that's why.
___

###### This is my **first** python project, so don't expect anything useful.
