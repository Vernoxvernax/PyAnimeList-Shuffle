import json         # json files from jikan api
import random       # choose between the items in your list
import time         # wait 6 seconds inbetween every request
import requests     # to get anything http related from the internet
from requests.exceptions import Timeout  # to handle timeouts more efficiently
import os.path      # to check for cache files
import configparser   # handling config files


def op():
    global username, cache_check
    # This function clearly checks what the user wants to do when executing the script.

    # Checking if the config file and cache folder is existent.
    if os.path.exists("pyanimelist.conf"):
        config = configparser.ConfigParser()
        config.read("pyanimelist.conf")
        cache_config = config["cache"]
        username = cache_config["default_username"]
        cache_check = cache_config["enabled"]
        if not os.path.exists("pylist-cache"):
            os.makedirs("pylist-cache")
    elif not os.path.exists("pyanimelist.conf"):
        username = ""
        cache_check = ""
    print("Please choose what to do:"
          "\n[1] MyAnimeList SHUFFLE"
          "\n[2] Open the settings (caching, default username)"
          "\n[E] Exit.")
    answer_op = False
    while not answer_op:
        menu_navigation = input(": ")
        if menu_navigation in "12Ee":
            answer_op = True
        else:
            print("Input invalid!\nPlease try again.")
    if menu_navigation == "1":
        requesting()
    elif menu_navigation == "2":
        settings()
        print("")
        op()
    elif menu_navigation in "Ee":
        return


def settings():
    # Should be pretty clear. This function builds the config file, but
    # can also edit it, if chosen.

    # nested function with "ask_" basically just validate user-input.
    def ask_caching():
        answer_settings = False
        while not answer_settings:
            caching_enabled = input(": ")
            if caching_enabled in "YNyn":
                answer_settings = True
            else:
                print("Input invalid!\nPlease try again.")
        if caching_enabled in "Yy":
            return "true"
        else:
            return "false"

    def ask_default_username():
        answer_settings = False
        while not answer_settings:
            username = input(": ")
            if " " not in username:
                answer_settings = True
            else:
                print("Username incorrect! (spaces?)\nPlease try again.")
        return username
    # check if the config file is _not_ existent, so a new one can be created, or not.
    if not os.path.exists("pyanimelist.conf"):
        print("\nNo config file found."
              "\n[C] create pyanimelist.conf\n[E] exit to menu")
        answer_settings = False
        while not answer_settings:
            config_file_question = input(": ")
            if config_file_question in "CcEe":
                answer_settings = True
            else:
                print("Input invalid!\nPlease try again.")
        if config_file_question and config_file_question in "Cc":
            print("\nDo you want to enable caching by default? (recommended)"
                  "\nInformation on cache can be found here: "
                  "https://github.com/Vernoxvernax/PyAnimeList-Shuffle/blob/main/Caching.md"
                  "\n[Y]es / [N]o")
            caching_enabled = ask_caching()
            print("\nWhat should be the default MyAnimeList username?"
                  "\n- Enter nothing, if not preferred.")
            username = ask_default_username()
            # writing input to the local file
            with open("pyanimelist.conf", "a+") as config:
                config.write("[cache]\nenabled = {}\ndefault_username = {}".format(caching_enabled, username))
        else:
            return
    # If the config is existent, ask what the user wants to change, if anything at all.
    else:
        print("\n[INF] Configuration file found.\n\nWhich settings do you want to change?")
        config = configparser.ConfigParser()
        config.read("pyanimelist.conf")
        cache_config = config["cache"]
        if cache_config["enabled"] == "false":
            cache_enabled = "disabled"
        else:
            cache_enabled = "enabled"
        username = cache_config["default_username"]
        print("[1] cache = {}\n[2] default_username = {}\n[N]one".format(cache_enabled, username))
        answer_settings = False
        while not answer_settings:
            config_change = input(": ")
            if config_change in "12Nn":
                answer_settings = True
            else:
                print("\nInput invalid!\nPlease try again.")
        if config_change == "1":
            print("\nDo you want to enable caching by default? (recommended)"
                  "\nInformation on cache can be found here: "
                  "https://github.com/Vernoxvernax/PyAnimeList-Shuffle/blob/main/Caching.md"
                  "\n[Y]es / [N]o")
            cache_enabled = ask_caching()
            config.set('cache', 'enabled', cache_enabled)
            with open("pyanimelist.conf", "w") as config_file:
                config.write(config_file)
            if cache_config["enabled"] == "false":
                cache_enabled = "disabled"
            else:
                cache_enabled = "enabled"
            print("\n[INF] The cache has been {}.\n".format(cache_enabled))
            return
        elif config_change == "2":
            print("What should be the default MyAnimeList username?"
                  "\n- Enter nothing, if not preferred.")
            username = ask_default_username()
            config.set('cache', 'default_username', username)
            with open("pyanimelist.conf", "w") as config_file:
                config.write(config_file)
            if username == "":
                print("\n[INF] The default username has been disabled.\n")
            else:
                print("\n[INF] The default username has been set to: {}.\n".format(username))
            return
        else:
            return


def reading_details():
    global username
    # reading_details() is doing what it's named after. Input is returned to requesting().

    def input_c(x):
        y = ""
        z = 0
        while y not in x:
            if z == 1:
                print("Input invalid!\nPlease try again.")
                y = input(": ")
            else:
                z = 1
                y = input(": ")
        return y
    if username == "":
        username = str(input("\nPlease enter your MyAnimeList username here: "))
    else:
        print("\nSearching for user: {}.".format(username))
    print("\nSelect the type of list:\n"
          "> AnimeList (1)\n> MangaList (2)")
    x = input_c(["1", "anime", "ANIME", "Anime", "AnimeList", "Animelist", "animelist",
                 "2", "manga", "MANGA", "Manga", "MangaList", "Mangalist", "mangalist"])
    if x in ["1", "anime", "ANIME", "Anime", "AnimeList", "Animelist", "animelist"]:
        m_type = str("animelist")
    elif x in ["2", "manga", "MANGA", "Manga", "MangaList", "Mangalist", "mangalist"]:
        m_type = str("mangalist")
    if m_type == "animelist":
        media_type_input = ["0", "1", "2", "3", "4", "5", "6"]
        media_type_output = ["", "TV", "OVA", "Movie", "Special", "ONA", "Music"]
        print("\nPlease choose the type of anime:\n"
              "> All (0)\n"
              "> TV-Show (1)\n"
              "> OVA (2)\n"
              "> Movie (3)\n"
              "> Special (4)\n"
              "> ONA (5)\n"
              "> Music (6)")
        media_type = input_c(media_type_input)
    elif m_type == "mangalist":
        media_type_input = ["0", "1", "2", "3", "4", "5", "6", "7"]
        media_type_output = ["", "Manga", "Oneshot", "Doujinshi", "Novel", "Light Novel", "Manhwa", "Manhua"]
        print("\nPlease choose the type of manga:\n"
              "> All (0)\n"
              "> Manga (1)\n"
              "> One-Shot (2)\n"
              "> Doujinshi (3)"
              "> Novel (4)\n"
              "> Light Novel (5)\n"
              "> Manhwa (6)\n"
              "> Manhua (7)")
        media_type = input_c(media_type_input)
    media_type = media_type_output[media_type_input.index(media_type)]
    print("\nDo you want one of these filters:\n"
          "> None (0)\n"
          "> Watching/Reading (1)\n"
          "> Completed (2)\n"
          "> On-Hold (3)\n"
          "> Dropped (4)\n"
          "> Plan to Watch/Plan to Read (5)")
    m_status_a = ["1", "2", "3", "4", "5", "6"]
    m_status_b = ["0", "1", "2", "3", "4", "5"]
    m_status = input_c(m_status_b)
    if m_status == "0":
        m_status = "n"
    if m_status in m_status_b:
        m_status = m_status_a[m_status_b.index(m_status)]
    print("\nAny preferences on the status:\n"
          "> None (0)\n"
          "> Airing/Publishing (1)\n"
          "> Finished (2)\n"
          "> Not yet Aired/Not yet Published (3)")
    pref_a = ["n", "1", "2", "3"]
    pref_m = ["n", "1", "2", "3"]
    pref_b = [0] * 4
    for x in range(len(pref_a)):
        pref_b[x] = x
    pref_ = map(str, list(pref_b))
    pref = int(input_c(list(pref_)))
    if pref in pref_b and m_type == "animelist":
        pref = pref_a[pref_b.index(pref)]
    elif pref in pref_b and m_type == "mangalist":
        pref = pref_m[pref_b.index(pref)]
    print("\nWhich of the following genres do you want to prioritize:\n"
          "> None (0)\n")
    left = ["Genres               ",
            "> Action (1)         ",
            "> Adventure (2)      ",
            "> Avant Garde (3)    ",
            "> Award Winning (4)  ",
            "> Boys Love (5)      ",
            "> Comedy (6)         ",
            "> Drama (7)          ",
            "> Fantasy (8)        ",
            "> Girls Love (9)     ",
            "> Gourmet (10)       ",
            "> Horror (11)        ",
            "> Mystery (12)       ",
            "> Romance (13)       ",
            "> Sci-Fi (14)        ",
            "> Slice of Life (15) ",
            "> Sports (16)        ",
            "> Supernatural (17)  ",
            "> Suspense (18)      ",
            "> Work Life (19)     ",
            "Explicit Genres      ",
            "> Ecchi (20)         ",
            "> Erotica (21)       ",
            "> Hentai (22)        "]
    right = ["Themes               ",
             "> Cars (23)          ",
             "> Demons (24)        ",
             "> Game (25)          ",
             "> Harem (26)         ",
             "> Historical (27)    ",
             "> Martial Arts (28)  ",
             "> Mecha (29)         ",
             "> Military (30)      ",
             "> Music (31)         ",
             "> Parody (32)        ",
             "> Police (33)        ",
             "> Psychological (34) ",
             "> Samurai (35)       ",
             "> School (36)        ",
             "> Space (37)         ",
             "> Super Power (38)   ",
             "> Vampire (39)       ",
             "Demographics         ",
             "> Josei (40)         ",
             "> Kids (41)          ",
             "> Seinen (42)        ",
             "> Shoujo (43)        ",
             "> Shounen (44)       "]
    # Above print() and below space() functions are only to display those genres more nicely.

    def space(left):
        left2 = left.copy()
        for x in range(left.index(left[-1]), 1, -1):
            if ">" not in left[x]:
                left2.insert(x, "                     ")
        return left2
    left2 = space(left)
    right2 = space(right)
    for x in range(24):
        output = str(left2[x] + '\t|      ' + right2[x])
        print(output)
    if m_type == "mangalist":
        print("\nManga exclusive tags:\n> Doujinshi (45)\n> Gender Bender (46)")
        ch_genre_a = [0] * 47
        ch_genre_b = [1, 2, 5, 46, 28, 4, 8, 10, 26, 47, 14, 7, 22, 24, 36, 30, 37, 45, 48, 9, 49, 12, 3,
                      6, 11, 35, 13, 17, 18, 38, 19, 20, 39, 40, 21, 23, 29, 31, 32, 42, 15, 41, 25, 27, 43, 44]
    else:
        ch_genre_a = [0] * 44
        ch_genre_b = [1, 2, 5, 46, 28, 4, 8, 10, 26, 47, 14, 7, 22, 24, 36, 30, 37, 41, 48, 9, 49, 12, 3,
                      6, 11, 35, 13, 17, 18, 38, 19, 20, 39, 40, 21, 23, 29, 31, 32, 43, 15, 42, 25, 27]
    for x in range(0, len(ch_genre_a)):
        ch_genre_a[x] = x
    # DON'T CHANGE THESE VALUES ABOVE. MyAnimeList has very weird genre numbering, not following the alphabetic order.
    str_ch_genre_a = ch_genre_a.copy()
    str_ch_genre_a = map(str, str_ch_genre_a)
    genre = input_c(list(str_ch_genre_a))
    if genre == "0":
        genre = str("n")
    elif int(genre) in ch_genre_a:
        genre = int(genre) - 1
        genre = ch_genre_b[ch_genre_a.index(int(genre))]
    return m_type, m_status, genre, pref, genre, media_type


def requesting():
    global cache_check

    # genre_s is passing the json from jikan through the genres and airing/... status.
    # Yes, I tried combining the json files but in the end it just added a few' more lines of code.
    def genre_s(query, mtype, c_page, shuffle_title, shuffle_url, status, media_type):
        item_list = []
        if m_type == "animelist":
            if query != "n":
                for eitem in json_body[mtype]:
                    item = json_body[mtype].index(eitem)
                    for query in json_body[mtype][item]["genres"]:
                        query = json_body[mtype][item]["genres"].index(query)
                        a_genre = json_body[mtype][item]["genres"][query]["mal_id"]
                        if genre == a_genre:
                            item_list.append(eitem)
                    for query in json_body[mtype][item]["demographics"]:
                        query = json_body[mtype][item]["demographics"].index(query)
                        a_genre = json_body[mtype][item]["demographics"][query]["mal_id"]
                        if genre == a_genre:
                            item_list.append(eitem)
            else:
                for eitem in json_body[mtype]:
                    item_list.append(eitem)
            if pref != "n":
                pref_list = []
                for pref_check in item_list:
                    pref_index = item_list.index(pref_check)
                    if item_list[pref_index]["airing_status"] == int(pref):
                        pref_list.append(pref_check)
                item_list = pref_list.copy()
            if status != "n":
                status_list = []
                for status_check in item_list:
                    status_index = item_list.index(status_check)
                    if item_list[status_index]["watching_status"] == int(status):
                        status_list.append(status_check)
                item_list = status_list.copy()
            if media_type != "":
                media_list = []
                for media_type_check in item_list:
                    media_type_index = item_list.index(media_type_check)
                    if item_list[media_type_index]["type"] == media_type:
                        media_list.append(media_type_check)
                item_list = media_list.copy()
            if not item_list:
                print("[INF] Content of page {} did not meet your filters.".format(c_page))
                return shuffle_title, shuffle_url
            for item in item_list:
                item_index = item_list.index(item)
                shuffle_title.append(item_list[item_index]['title'])
                shuffle_url.append(item_list[item_index]['url'])
            return shuffle_title, shuffle_url
        elif m_type == "mangalist":
            if query != "n":
                for eitem in json_body[mtype]:
                    item = json_body[mtype].index(eitem)
                    for query in json_body[mtype][item]["genres"]:
                        query = json_body[mtype][item]["genres"].index(query)
                        a_genre = json_body[mtype][item]["genres"][query]["mal_id"]
                        if genre == a_genre:
                            item_list.append(eitem)
                    for query in json_body[mtype][item]["demographics"]:
                        query = json_body[mtype][item]["demographics"].index(query)
                        a_genre = json_body[mtype][item]["demographics"][query]["mal_id"]
                        if genre == a_genre:
                            item_list.append(eitem)
            else:
                for eitem in json_body[mtype]:
                    item_list.append(eitem)
            if pref != "n":
                pref_list = []
                for pref_check in item_list:
                    pref_index = item_list.index(pref_check)
                    if item_list[pref_index]["publishing_status"] == int(pref):
                        pref_list.append(pref_check)
                item_list = pref_list.copy()
            if status != "n":
                status_list = []
                for status_check in item_list:
                    status_index = item_list.index(status_check)
                    if item_list[status_index]["reading_status"] == int(status):
                        status_list.append(status_check)
                item_list = status_list.copy()
            if media_type != "":
                media_list = []
                for media_type_check in item_list:
                    media_type_index = item_list.index(media_type_check)
                    if item_list[media_type_index]["type"] == media_type:
                        media_list.append(media_type_check)
                item_list = media_list.copy()
            if not item_list:
                print("[INF] Content of page {} did not meet your filters.".format(c_page))
                return shuffle_title, shuffle_url
            for item in item_list:
                item_index = item_list.index(item)
                shuffle_title.append(item_list[item_index]['title'])
                shuffle_url.append(item_list[item_index]['url'])
            return shuffle_title, shuffle_url
    # From here on requesting() actually starts. The above function is to filter the list later on.
    m_type, m_status, genre, pref, genre, media_type = reading_details()
    if username == "":
        m_type, m_status, genre, pref, genre, media_type = reading_details()
    if m_type == "animelist":
        type_short = "anime"
    elif m_type == "mangalist":
        type_short = "manga"
    else:
        print("Error occurred. Please don't contact the dev.\nHe's busy watching twitch.")
        return()
    x = 1
    if cache_check == "true" and os.path.isfile(r"./pylist-cache/{}-{}-p1.json".format(username, m_type)):
        with open("./pylist-cache/{}-{}-p1.json".format(username, m_type)) as json_file:
            json_body = json.load(json_file)
        req_status = False
        print("\n[INF] Using cache for provided username.")
        sleeeping = 0
    else:
        req_status = True
        sleeeping = 6
        print("")
    print("Loading page:", x)
    # Change below domain, if you are having connection issues.
    c_url = str("https://api.jikan.moe/v3/user/{}/{}".format(username, m_type))
    # try:
    #     request = requests.get(c_url, timeout=6)
    # except Timeout:
    #     print("API didn't respond. Trying again in 4 seconds...")
    #     time.sleep(4)
    #     request = requests.get(c_url, timeout=8)
    while req_status:
        try:
            request = requests.get(c_url, timeout=6)
        except Timeout:
            print("API didn't respond. Trying again in 4 seconds...")
            time.sleep(4)
        else:
            if cache_check == "true" and not os.path.isfile(r"./pylist-cache/{}-{}-p1.json".format(username, m_type)):
                with open("./pylist-cache/{}-{}-p1.json".format(username, m_type), "a+") as json_file:
                    json_file.write(request.text)
            json_body = json.loads(request.text)
            req_status = False
    length = len(str(json_body))
    shuffle_title = []
    shuffle_url = []
    c_page = 1
    if length < 145:
        print("Your list doesn't seem to have content.")
        return
    elif '"status":400,' in json_body:
        print("That username doesn't exist.")
        return
    elif "BadResponseException" in str(json_body):
        print("Jikan failed to connect to MyAnimeList. MyAnimeList may be down, unavailable or refuses to connect.")
        return
    print(genre, type_short, c_page, shuffle_title, shuffle_url, m_status, media_type)
    input()
    shuffle_title, shuffle_url = genre_s(genre, type_short, c_page, shuffle_title, shuffle_url, m_status, media_type)
    c_page = c_page + 1
    while length > 150:
        if cache_check == "true" and os.path.isfile(r"./pylist-cache/{}-{}-p{}.json".format(username, m_type, c_page)):
            try:
                with open("./pylist-cache/{}-{}-p{}.json".format(username, m_type, c_page)) as json_file:
                    json_body = json.load(json_file)
            except:
                json_body = ""
                sleeeping = 6
            req_status = False
        else:
            req_status = True
        time.sleep(sleeeping)
        print("Loading page:", c_page)
        n_url = str("https://api.jikan.moe/v3/user/{}/{}?page={}".format(username, m_type, c_page))
        while req_status:
            try:
                request = requests.get(n_url, timeout=6)
            except Timeout:
                print("API didn't respond. Trying again in 4 seconds...")
                time.sleep(4)
            else:
                if cache_check == "true" and not os.path.isfile(r"./pylist-cache/{}-{}-p{}.json".format(username, m_type, c_page)):
                    with open("./pylist-cache/{}-{}-p{}.json".format(username, m_type, c_page), "a+") as json_file:
                        json_file.write(request.text)
                json_body = json.loads(request.text)
                req_status = False
        if "BadResponseException" in str(json_body):
            print("The connection to MyAnimeList failed.")
            return
        shuffle_title, shuffle_url = genre_s(genre, type_short, c_page, shuffle_title, shuffle_url, m_status, media_type)
        c_url = c_url + n_url
        c_page = c_page + 1
        length = len(str(json_body))
    print("Reached the end of your list.")
    if len(shuffle_title) == 0:
        print("     Nothing out of your list matches configured search requirements!")
        return
    rnd_pick = shuffle_title[random.randrange(len(shuffle_title))]
    if len(shuffle_title) == 1:
        print("\nOnly one match has been found:")
        print("     ", rnd_pick,
              "\n     ", shuffle_url[shuffle_title.index(rnd_pick)])
    else:
        print("\nOut of: {}".format(len(shuffle_title)), "titles, the following was picked:")
        print("     ", rnd_pick,
              "\n     ", shuffle_url[shuffle_title.index(rnd_pick)])


def main():
    # No, srsly. Their servers time out really easily.
    print("This script uses the unofficial Jikan API.\n"
          "Please don't spam requests.\n")
    op()
    print("\nscript finished.")


main()
