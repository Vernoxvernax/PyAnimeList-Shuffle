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
above-mentioned folder.

___
### Usage:
Upon running the script for the first time,
it will ask you if you want to use caching.
If you decide for it, the following shuffle
will proceed as usual, but save those json
data to `pylist-cache`.

When running the script again, it will see
that folder and ask you if you want to clean
the cache, or not.
