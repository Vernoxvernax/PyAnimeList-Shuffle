# PyAnimeList-Shuffle

The code is a joke, but it does what I want.

This projects heavily relies on [Jikan](https://jikan.moe/), an unofficial MyAnimeList API.

![](https://github.com/Vernoxvernax/PyAnimeList-Shuffle/blob/main/fdsfds.gif?raw=true)
###### speed up by 1.5, read below why

## Installation / Usage:
`$ git clone REPO`

`$ cd REPO`

`$ pip install -r requirements.txt`

`$ python pyanimelist-shuffle.py`
###### Python needs to be installed.

## The Code:
Jikan provides great detailed json files, featuring all the details you could want.
To fight people, making their own database, using that data, MyAnimeList itself limits it to one request every 4 seconds.
Unfortunately, those json files are also limited to 300 entries, so for bigger lists, one will have to send multiple requests until the end has been found.
The Jikan API also has only very little possibilities to filter the requests. Due to all this, the script fetches every page and then applies given filters, such as genre, watching status, etc. locally. Currently there is no feature to save any requests, but if there is demand for it, I could work on it.

## To-Do:
* Look into Telegram API (this would be sick, holy fuck)
* Cache requests (ask for deletion on script startup or smth.)

___
You might ask yourself: why not use this great [Spin.moe](https://spin.moe/) app instead?
Well even though it's a lot easier to use, it doesn't support filtering genres so that's why.
___

##### This is my **first** python project, so don't expect anything useful.
