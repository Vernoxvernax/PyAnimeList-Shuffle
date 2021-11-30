import json         # json files from jikan api
import random       # choose between the items in your list
import time         # wait 6 seconds inbetween every request
import requests     # to get anything http related from the internet
from requests.exceptions import Timeout # to handle timeouts more efficiently
import os.path      # to check for cache files


def caching():
    cache_check = os.path.exists("cache")
    if cache_check:
        print("cache found")
    else:
        print("cache not found")
    print("Do you want to enable caching?\n"
          "Further information can be found here: ")
    print("")
    input()


def reading_details():
    # reading_details() is doing what it's named after. Everything else is done in requesting().
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
        z = 0
        return y
    username = str(input("Please enter your MyAnimeList username here: "))
    print("Select from the following list:\n"
          "> AnimeList (1)\n> MangaList (2)")
    x = input_c(['1', "anime", "ANIME", "Anime", "AnimeList", "Animelist", "animelist",
                 "2", "manga", "MANGA", "Manga", "MangaList", "Mangalist", "mangalist"])
    if x in ["1", "anime", "ANIME", "Anime", "AnimeList", "Animelist", "animelist"]:
        m_type = str("animelist")
    elif x in ["2", "manga", "MANGA", "Manga", "MangaList", "Mangalist", "mangalist"]:
        m_type = str("mangalist")
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
    # Above and below are only to display those genres more nicely.

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
    # DON'T CHANGE THESE VALUES ABOVE. MyAnimeList has very weird sorting.
    str_ch_genre_a = ch_genre_a.copy()
    str_ch_genre_a = map(str, str_ch_genre_a)
    genre = input_c(list(str_ch_genre_a))
    if genre == "0":
        genre = str("n")
    elif int(genre) in ch_genre_a:
        genre = int(genre) - 1
        genre = ch_genre_b[ch_genre_a.index(int(genre))]
    return username, m_type, m_status, genre, pref, genre


def requesting():
    # genre_s is passing the json from jikan through the genres and airing/... status.
    # Yes, I tried combining the json files but in the end it just added a few more lines of code.
    def genre_s(query, mtype, c_page, shuffle_title, shuffle_url, status):
        parsed_list = []
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
            if not item_list:
                empty = ""
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
            if not item_list:
                empty = ""
                print("[INF] Content of page {} did not meet your filters.".format(c_page))
                return shuffle_title, shuffle_url
            for item in item_list:
                item_index = item_list.index(item)
                shuffle_title.append(item_list[item_index]['title'])
                shuffle_url.append(item_list[item_index]['url'])
            return shuffle_title, shuffle_url
    # From here on requesting() actually starts. The above are just functions, called later on.
    username, m_type, m_status, genre, pref, genre = reading_details()
    if username == "":
        username, m_type, m_status, genre, pref, genre = reading_details()
    if m_type == "animelist":
        type_short = "anime"
    elif m_type == "mangalist":
        type_short = "manga"
    else:
        print("Error occurred. Please contact the dev.")
    x = 1
    print("\nFetching page:", x)
    # Change below domain, if you are having connection issues.
    c_url = str("https://api.jikan.moe/v3/user/{}/{}".format(username, m_type))
    # try:
    #     request = requests.get(c_url, timeout=6)
    # except Timeout:
    #     print("API didn't respond. Trying again in 4 seconds...")
    #     time.sleep(4)
    #     request = requests.get(c_url, timeout=8)
    req_status = True
    while req_status:
        try:
            request = requests.get(c_url, timeout=6)
        except Timeout:
            print("API didn't respond. Trying again in 4 seconds...")
            time.sleep(4)
        else:
            req_status = False
    json_body = json.loads(request.text)
    length = len(str(json_body))
    shuffle_title = []
    shuffle_url = []
    c_page = 1
    if length < 145:
        print("Your filters don't seem to match any content.")
        return
    elif '"status":400,' in json_body:
        print("That username doesn't exist.")
        return
    elif "BadResponseException" in str(json_body):
        print("The connection to MyAnimeList failed.")
        return
    shuffle_title, shuffle_url = genre_s(genre, type_short, c_page, shuffle_title, shuffle_url, m_status)
    c_page = c_page + 1
    while length > 150:
        time.sleep(6)
        print("Fetching page:", c_page)
        n_url = str("https://api.jikan.moe/v3/user/{}/{}?page={}".format(username, m_type, c_page))
        req_status = True
        while req_status:
            try:
                request = requests.get(n_url, timeout=6)
            except Timeout:
                print("API didn't respond. Trying again in 4 seconds...")
                time.sleep(4)
            else:
                req_status = False
        json_body = json.loads(request.text)
        if "BadResponseException" in str(json_body):
            print("The connection to MyAnimeList failed.")
            return
        shuffle_title, shuffle_url = genre_s(genre, type_short, c_page, shuffle_title, shuffle_url, m_status)
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
    print("This script uses the unofficial Jikan API\n"
          "Please don't send more than 2 requests per second.\n")
    # No, srsly. Their servers time out really easily.
    # Just some stuff for the future:
    # caching()
    requesting()
    print("\npython script finished.")


main()
