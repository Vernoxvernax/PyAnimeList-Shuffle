# PyAnimeList-Shuffle

##### Discord: DepriSheep#1841

This projects heavily relies on [Jikan](https://jikan.moe/) (v4), an unofficial MyAnimeList API.

## Jikan User-Lists Removal:

So, the api endpoint we've been using is gone, at least from the public api.
I've set up a selfhosted api endpoint for the telegram bot.
This one will continue to work (faster compaired to the public rest) but I won't be making it public (for obvious reasons).

In the coming days, I'll put out a small guide how to set up your own jikan-rest in case you for some reason cannot live without the cli version of this script.

If you like this project, give me some kind of indication, I'm hardly doing this only for myself.

## Telegram Bot:
#### https://t.me/pyanimelist_bot
###### Doesn't need any setup on your side, just text him/her: `/start`.
###### If something breaks (bc of you), and the bot wasn't fast enough to answer, type `/stop`.

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
* come up with better changelog documentation
* Look into discord bot api

## Demonstration:
![](https://i.imgur.com/nP7T9s7.png)

## Changelog:

**[Changelog.md - GitHub.com](https://github.com/Vernoxvernax/PyAnimeList-Shuffle/blob/main/Changelog.md)**

___
You might ask yourself: why not use this great [Spin.moe](https://spin.moe/) app instead?
Well even though it's a lot easier to use, it doesn't support filtering genres and cli so that's why.
___

###### This is my **first** python project, so don't expect anything useful.
