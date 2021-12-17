# Caching
This feature can save you a lot of time.
Instead of fetching every single page of your
anime/manga list on each shuffle, it will save those
files to you hard disk.

Of course this also means, changes on MyAnimeList.net
will not affect this cache and will lead to 
outdated information displayed.
___
### How:

Next to `pyanimelist-shuffle.py` a new folder
will be created named: `pylist-cache`.

After the script has fetched your list, it
will then save it like this: 
`username-animelist-p1.json` in the
cache folder.

___
### Usage:
If enabled in the settings, anime and manga-lists
will be saved to `pylist-cache`, after being requested from jikan.
