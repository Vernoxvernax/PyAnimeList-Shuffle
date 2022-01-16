### Changelog:

#### Commit [ea68cde](https://github.com/Vernoxvernax/PyAnimeList-Shuffle/commit/ea68cde3ec09f6d08a1d798fe0692f39f5603ed8): (Telegram-bot)
* fixed stupid mistake: genre filter can now be avoided again

#### Commit [f8260ea](https://github.com/Vernoxvernax/PyAnimeList-Shuffle/commit/f8260ead64081282890f0761053993e9aaa762a4): (Telegram-bot)
* new feature: excluding/blacklisting genres (two integers separated by a space)
* printing genres/demographics/themes as an image for screens with smaller width
  * image is smaller than 92kb in size; imgur used as cdn
* fixed error handling (including printing errors)
* removed unused comments and variables

#### Commit [f57504a](https://github.com/Vernoxvernax/PyAnimeList-Shuffle/commit/f57504a5159ef615e507b36732670d545b1872a8) and [a8c1128](https://github.com/Vernoxvernax/PyAnimeList-Shuffle/commit/a8c1128e3b1ee53d86b72216b382bd16b26b60d0): (Telegram-bot)
* Fixed typo which resulted in unsuccessful spins when filtering anime episode amounts
* Slightly improved error handling on failed requests
* Increased request-timeout to 10 seconds, since v4 takes a little longer to answer.
* Removed a debug print function

#### Commit [0ae9606](https://github.com/Vernoxvernax/PyAnimeList-Shuffle/commit/0ae960603b2f1ed102023acb38e7d94cf1ee246b) and (`73696e5`,`38d174c`,`e8ebd6f`,`de1874d`): (Telegram-bot and Script)
* Update to Jikan v4.
* Requests are now a lot faster since we are allowed to send 60 requests/s instead of only 30.
* Bugs are currently everywhere (jikan) so problems may occur.
* Fixed bug where the last cache entry lead to a sleep time of 4 seconds.

#### Commit [e4860b1](https://github.com/Vernoxvernax/PyAnimeList-Shuffle/commit/e4860b1e539b80a4611b4e81c730103ae83b1249): (Telegram-Bot)
* Cache is now built on case-insensitive files. (no more "username.json" and "Username.json" files at the same time)
* General improvements and removal of unused comments
###### Until someone finds this repo and does not report me within seconds: I have decided to distance myself from version numbers and will start addressing changes in the changelog here by github's commit sha.

#### v1.0.1:
* Added filtering feature for both the script and telegram bot:
  - Rating/score from the user (!not the community!, as additional data would've to be fetched, for every single entry on your list = impossible).
  - Minimum and maximum amount of (episodes | chapters | volumes).
* removed unused comments
* general fixes
###### When using the bot, please make sure to wait for answers and don't spam!