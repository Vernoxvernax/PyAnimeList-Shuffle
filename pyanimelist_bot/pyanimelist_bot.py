import configparser         # configuration file
import logging              # logging module
import re                   # regex
import os.path
import time
import json
import requests
from requests import Timeout
import random
import threading            # to handle multiple requests at the same time
from telegram import Update, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, Updater, \
                         MessageHandler, Filters, ConversationHandler, \
                         CallbackQueryHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

USERNAME, LISTTYPE, MEDIATYPE, USERSTATUS, RELEASESTATUS, GENRE, CACHE = range(7)


def reading_config_file():
    # config for parsing api token:
    # ----------------------------- telegram.conf
    # [config]
    # TOKEN = <token>
    # -----------------------------
    config_file = configparser.ConfigParser()
    config_file.read("telegram.conf")
    config = config_file["config"]
    token = config["TOKEN"]
    return token


def telegram_conf(token):
    global dispatcher, updater
    # Configuring the updater and dispatcher
    updater = Updater(token=token, use_context=True)
    if updater == "":
        print("Error. Updater not defined.")
        exit()
    dispatcher = updater.dispatcher


def adding_handler():
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    # Shuffle question and answer processing
    # shuffle_handler = CommandHandler("shuffle", shuffle)
    # dispatcher.add_handler(shuffle_handler)
    # shuffle_processing_handler = MessageHandler(Filters.text, shuffle_processing)
    # dispatcher.add_handler(shuffle_processing_handler)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('shuffle', shuffle)],
        states={
            USERNAME: [
                MessageHandler(Filters.text, username_end)
            ],
            LISTTYPE: [
                CallbackQueryHandler(listtype_end, pattern='^(Anime|Manga)$')
            ],
            MEDIATYPE: [
                CallbackQueryHandler(mediatype_end, pattern='^(All|TV-Show|OVA|Movie|Special|ONA|Music|Manga|'
                                                            'One-Shot|Doujinshi|Novel|Light Novel|Manhwa|Manhua)$'),
            ],
            USERSTATUS: [
                CallbackQueryHandler(userstatus_end, pattern='^(None|Watching|Completed|On-Hold|Dropped|Plan to Watch|'
                                                             'Plan to Read|Reading)$')
            ],
            RELEASESTATUS: [
                CallbackQueryHandler(release_status_end, pattern='^(No|Airing|Publishing|Finished'
                                                                 '|Not yet Aired|Not yet Published)$')
            ],
            GENRE: [
                MessageHandler(Filters.regex('^[0-9]+$'), cache_check)
            ],
            CACHE: [
                CallbackQueryHandler(processing, pattern='^(No|Yes)$')
            ]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    dispatcher.add_handler(conv_handler)
    # Unknown input
    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)


def main():
    print("Starting telegram bot.")
    token = reading_config_file()
    telegram_conf(token)
    adding_handler()


# Here come the telegram functions:
def stop(update: Update, context: CallbackContext) -> None:
    print("conv ended")
    return ConversationHandler.END


def start(update: Update, context: CallbackContext) -> None:
    message = "Hello, this is your personal telegram bot to get random entries from your MyAnimeList." \
              "\nGitHub: " \
              '[PyAnimeList-Shuffle](https://github.com/Vernoxvernax/PyAnimeList-Shuffle)' \
              '\nTo start shuffling type: /shuffle.'
    context.bot.send_message(chat_id=update.effective_chat.id, parse_mode="Markdown", text=message)


def unknown(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id, text="Unknown command. Maybe try /start?")


def shuffle(update: Update, context: CallbackContext) -> None:
    print("User just initiated shuffle.")
    message = "Please enter your MyAnimeList username:"
    update.message.reply_text(text=message)
    # print(update.message.text)
    # reply=ReplyKeyboardMarkup(input_field_placeholder="MyAnimeList.net username")
    return USERNAME


def username_end(update: Update, context: CallbackContext) -> None:
    global username
    username = update.message.text
    illegal_check = re.compile("[@_!#$%^&*()<>?/|}{~:]")
    if not (illegal_check.search(username) is None):
        update.message.reply_text("You username has illegal characters, please try again.")
        return USERNAME
    else:
        update.message.reply_text("Username set to: {}".format(update.message.text))
    # update.message.reply_text("Username set to: {}".format(username))
    message = "Please choose the type of list you want to shuffle:"
    listtype_reply = [
        [
            InlineKeyboardButton("Anime", callback_data="Anime"),
            InlineKeyboardButton("Manga", callback_data="Manga")
        ]
    ]
    listtype_kb = InlineKeyboardMarkup(listtype_reply)
    update.message.reply_text(message, reply_markup=listtype_kb)
    return LISTTYPE


def listtype_end(update: Update, context: CallbackContext) -> None:
    global listtype, listtype_long, listtype_short
    listtype = update.callback_query.data
    # print(update.callback_query.data)
    if listtype == "Anime":
        word = "anime"
        listtype_long = "animelist"
        listtype_short = "anime"
        mediatype_reply = [
            [
                InlineKeyboardButton("All", callback_data="All")
            ],
            [
                InlineKeyboardButton("TV-Show", callback_data="TV-Show"),
                InlineKeyboardButton("OVA", callback_data="OVA"),
                InlineKeyboardButton("Movie", callback_data="Movie")
            ],
            [
                InlineKeyboardButton("Special", callback_data="Special"),
                InlineKeyboardButton("ONA", callback_data="ONA"),
                InlineKeyboardButton("Music", callback_data="Music")

            ]
        ]
    else:
        word = "manga"
        listtype_long = "mangalist"
        listtype_short = "manga"
        mediatype_reply = [
            [
                InlineKeyboardButton("All", callback_data="All"),
                InlineKeyboardButton("Manga", callback_data="Manga")
            ],
            [
                InlineKeyboardButton("One-Shot", callback_data="One-Shot"),
                InlineKeyboardButton("Doujinshi", callback_data="Doujinshi"),
                InlineKeyboardButton("Novel", callback_data="Novel")
            ],
            [
                InlineKeyboardButton("Light Novel", callback_data="Light Novel"),
                InlineKeyboardButton("Manhwa", callback_data="Manhwa"),
                InlineKeyboardButton("Manhua", callback_data="Manhua")
            ]
        ]
    message = "Please choose the type of {}:".format(word)
    mediatype_kb = InlineKeyboardMarkup(mediatype_reply)
    update.callback_query.message.edit_text(message, reply_markup=mediatype_kb)
    return MEDIATYPE


def mediatype_end(update: Update, context: CallbackContext) -> None:
    global mediatype
    mediatype = update.callback_query.data
    if listtype == "Anime":
        userstatus_reply = [
            [
                InlineKeyboardButton("None", callback_data="None"),
                InlineKeyboardButton("Watching", callback_data="Watching"),
                InlineKeyboardButton("Completed", callback_data="Completed")
            ],
            [
                InlineKeyboardButton("On-Hold", callback_data="On-Hold"),
                InlineKeyboardButton("Dropped", callback_data="Dropped"),
                InlineKeyboardButton("Plan to Watch", callback_data="Plan to Watch"),
            ]
        ]
    else:
        userstatus_reply = [
            [
                InlineKeyboardButton("None", callback_data="None"),
                InlineKeyboardButton("Reading", callback_data="Reading"),
                InlineKeyboardButton("Completed", callback_data="Completed")
            ],
            [
                InlineKeyboardButton("On-Hold", callback_data="On-Hold"),
                InlineKeyboardButton("Dropped", callback_data="Dropped"),
                InlineKeyboardButton("Plan to Read", callback_data="Plan to Read"),
            ]
        ]
    message = "Please pick one these watching statuses:"
    userstatus_kb = InlineKeyboardMarkup(userstatus_reply, one_time_keyboard=True)
    update.callback_query.message.edit_text(message, reply_markup=userstatus_kb)
    return USERSTATUS


def userstatus_end(update: Update, context: CallbackContext) -> None:
    global userstatus
    userstatus = update.callback_query.data
    if listtype == "Anime":
        release_status_reply = [
            [
                InlineKeyboardButton("No", callback_data="No"),
                InlineKeyboardButton("Airing", callback_data="Airing")
            ],
            [
                InlineKeyboardButton("Finished", callback_data="Finished"),
                InlineKeyboardButton("Not yet Aired", callback_data="Not yet Aired")
            ]
        ]
    else:
        release_status_reply = [
            [
                InlineKeyboardButton("No", callback_data="No"),
                InlineKeyboardButton("Publishing", callback_data="Publishing")
            ],
            [
                InlineKeyboardButton("Finished", callback_data="Finished"),
                InlineKeyboardButton("Not yet Published", callback_data="Not yet Published")
            ]
        ]
    message = "Any preference on the status?:"
    release_status_kb = InlineKeyboardMarkup(release_status_reply, one_time_keyboard=True)
    update.callback_query.message.edit_text(message, reply_markup=release_status_kb)
    return RELEASESTATUS


def release_status_end(update: Update, context: CallbackContext) -> None:
    global release_status
    release_status = update.callback_query.data
    ReplyKeyboardRemove()
    if listtype == "Anime":
        genre_reply = "```\n" \
                      "Genres                 Themes" \
                      "\n> Action (1)           | > Cars (23)" \
                      "\n> Adventure (2)        | > Demons (24)" \
                      "\n> Avant Garde (3)      | > Game (25)" \
                      "\n> Award Winning (4)    | > Harem (26)" \
                      "\n> Boys Love (5)        | > Historical (27)" \
                      "\n> Comedy (6)           | > Martial Arts (28)" \
                      "\n> Drama (7)            | > Mecha (29)" \
                      "\n> Fantasy (8)          | > Military (30)" \
                      "\n> Girls Love (9)       | > Music (31)" \
                      "\n> Gourmet (10)         | > Parody (32)" \
                      "\n> Horror (11)          | > Police (33)" \
                      "\n> Mystery (12)         | > Psychological (34)" \
                      "\n> Romance (13)         | > Samurai (35)" \
                      "\n> Sci-Fi (14)          | > School (36)" \
                      "\n> Slice of Life (15)   | > Space (37)" \
                      "\n> Sports (16)          | > Super Power (38)" \
                      "\n> Supernatural (17)    | > Vampire (39)" \
                      "\n> Suspense (18)        | > Demographics (40)" \
                      "\n> Work Life (19)       | > Josei" \
                      "\nExplicit Genres        | > Kids (41)" \
                      "\n> Ecchi (20)           | > Seinen (42)" \
                      "\n> Erotica (21)         | > Shoujo (43)" \
                      "\n> Hentai (22)          | > Shounen (44)" \
                      "\n\nNo genre (0)```"
    else:
        genre_reply = "```\n" \
                      "Genres                 Themes" \
                      "\n> Action (1)         | > Cars (23)" \
                      "\n> Adventure (2)      | > Demons (24)" \
                      "\n> Avant Garde (3)    | > Game (25)" \
                      "\n> Award Winning (4)  | > Harem (26)" \
                      "\n> Boys Love (5)      | > Historical (27)" \
                      "\n> Comedy (6)         | > Martial Arts (28)" \
                      "\n> Drama (7)          | > Mecha (29)" \
                      "\n> Fantasy (8)        | > Military (30)" \
                      "\n> Girls Love (9)     | > Music (31)" \
                      "\n> Gourmet (10)       | > Parody (32)" \
                      "\n> Horror (11)        | > Police (33)" \
                      "\n> Mystery (12)       | > Psychological (34)" \
                      "\n> Romance (13)       | > Samurai (35)" \
                      "\n> Sci-Fi (14)        | > School (36)" \
                      "\n> Slice of Life (15) | > Space (37)" \
                      "\n> Sports (16)        | > Super Power (38)" \
                      "\n> Supernatural (17)  | > Vampire (39)" \
                      "\n> Suspense (18)      | > Demographics (40)" \
                      "\n> Work Life (19)     | > Josei" \
                      "\nExplicit Genres      | > Kids (41)" \
                      "\n> Ecchi (20)         | > Seinen (42)" \
                      "\n> Erotica (21)       | > Shoujo (43)" \
                      "\n> Hentai (22)        | > Shounen (44)" \
                      "\nManga exclusive tags:" \
                      "\n> Doujinshi (45)     | > Gender Bender (46)" \
                      "\n\nNo genre (0)```"
    message = "Which of the following genres do you want to prioritize?:\n{}".format(genre_reply)
    update.callback_query.message.edit_text(message, parse_mode="Markdown")
    return GENRE


def cache_check(update: Update, context: CallbackContext):
    global cache_exists, user_genre, using_cache
    user_genre = update.message.text
    if os.path.isfile(r"./cache/{}-{}-p1.json".format(username, listtype_long)):
        question_reply = [
            [
                InlineKeyboardButton("Yes", callback_data="Yes"),
                InlineKeyboardButton("No", callback_data="No")
            ]
        ]
        question_kb = InlineKeyboardMarkup(question_reply)
        update.message.reply_text("[INF] Cache found for {}.\nDo you want to use it?".format(username),
                                  reply_markup=question_kb)
        return CACHE
    else:
        update.message.reply_text("[INF] No cache found for {}.".format(username))
        using_cache = "No"
        message = "[INF] Joined queue."
        try:
            update.message.reply_text(message)
        except:
            update.callback_query.message.edit_text(message)
        thread = threading.Thread(target=request_thread, args=(update, context))
        thread.start()
        thread.join()
        return stop


def custom_message(update: Update, context: CallbackContext, x, y):
    if y == "a":
        update.callback_query.message.edit_text(x)
    else:
        update.message.reply_text(x)
    return


def processing(update: Update, context: CallbackContext):
    global using_cache
    using_cache = update.callback_query.data
    message = "[INF] Joined queue."
    try:
        update.message.reply_text(message)
    except:
        update.callback_query.message.edit_text(message)
    thread = threading.Thread(target=request_thread, args=(update, context))
    thread.start()
    thread.join()
    return ConversationHandler.END
    # request_thread(update, context)


# def requesting(update: Update, context: CallbackContext):
#     if using_cache == "No":
#         message = "Not using cache"
#     elif using_cache == "Yes":
#         message = "Using cache"
#     else:
#         message = "doing stuff, not the right kind"
#     custom_message(update, context, message)
#     thread = threading.Thread(target=request_thread)
#     thread.start()
#     thread.join()
#     return ConversationHandler.END


def request_thread(update: Update, context: CallbackContext):
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
    # defining variables and assigning values
    genre = user_genre
    pref = release_status
    m_type = listtype_long
    type_short = listtype_short
    if type_short == "anime":
        m_status_a = ["None", "Watching", "Completed", "On-Hold", "Dropped", "Plan to Watch"]
    else:
        m_status_a = ["None", "Reading", "Completed", "On-Hold", "Dropped", "Plan to Read"]
    m_status_b = ["0", "1", "2", "3", "4", "6"]
    if userstatus == "None":
        m_status = "n"
    elif userstatus in m_status_a:
        m_status = m_status_b[m_status_a.index(userstatus)]
    pref_a = ["n", "1", "2", "3"]
    if m_type == "animelist":
        pref_b = ["No", "Airing", "Finished", "Not yet Aired"]
        pref = pref_a[pref_b.index(pref)]
    elif m_type == "mangalist":
        pref_b = ["No", "Publishing", "Finished", "Not yet Published"]
        pref = pref_a[pref_b.index(pref)]
    if m_type == "mangalist":
        ch_genre_a = [0] * 47
        ch_genre_b = [1, 2, 5, 46, 28, 4, 8, 10, 26, 47, 14, 7, 22, 24, 36, 30, 37, 45, 48, 9, 49, 12, 3,
                      6, 11, 35, 13, 17, 18, 38, 19, 20, 39, 40, 21, 23, 29, 31, 32, 42, 15, 41, 25, 27, 43, 44]
    else:
        ch_genre_a = [0] * 44
        ch_genre_b = [1, 2, 5, 46, 28, 4, 8, 10, 26, 47, 14, 7, 22, 24, 36, 30, 37, 41, 48, 9, 49, 12, 3,
                      6, 11, 35, 13, 17, 18, 38, 19, 20, 39, 40, 21, 23, 29, 31, 32, 43, 15, 42, 25, 27]
    if genre == "0":
        genre = str("n")
    elif int(genre) in ch_genre_a:
        genre = int(genre) - 1
        genre = ch_genre_b[ch_genre_a.index(int(genre))]
    media_type = mediatype
    if media_type == "All":
        media_type = ""
    message = "[INF] Shuffling..."
    try:
        update.message.reply_text(message)
    except:
        update.callback_query.message.edit_text(message)
    if using_cache == "Yes" and os.path.isfile(r"./cache/{}-{}-p1.json".format(username, m_type)):
        with open("./cache/{}-{}-p1.json".format(username, m_type)) as json_file:
            json_body = json.load(json_file)
        req_status = False
        sleeeping = 0
    elif using_cache == "No":
        req_status = True
        sleeeping = 5
    else:
        return stop
    c_url = str("https://api.jikan.moe/v3/user/{}/{}".format(username, m_type))
    while req_status:
        try:
            request = requests.get(c_url, timeout=6)
        except Timeout:
            print("API didn't respond. Trying again in 4 seconds...")
            time.sleep(4)
        else:
            with open("./cache/{}-{}-p1.json".format(username, m_type), "w+") as json_file:
                json_file.write(request.text)
            json_body = json.loads(request.text)
            req_status = False
    length = len(str(json_body))
    shuffle_title = []
    shuffle_url = []
    c_page = 1
    if length < 145:
        print("The list doesn't seem to have content.")
        return
    elif '"status":400,' in json_body:
        print("That username doesn't exist.")
        return
    elif "BadResponseException" in str(json_body):
        print("Jikan failed to connect to MyAnimeList. MyAnimeList may be down, unavailable or refuses to connect.")
        return
    shuffle_title, shuffle_url = genre_s(genre, type_short, c_page, shuffle_title, shuffle_url, m_status, media_type)
    c_page = c_page + 1
    while length > 150:
        if using_cache == "Yes" and os.path.isfile(r"./cache/{}-{}-p{}.json".format(username, m_type, c_page)):
            try:
                with open("./cache/{}-{}-p{}.json".format(username, m_type, c_page)) as json_file:
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
                with open("./cache/{}-{}-p{}.json".format(username, m_type, c_page), "w+") as json_file:
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
    if len(shuffle_title) == 0:
        message = "     Nothing out of your list matches configured search requirements!"
        try:
            update.message.reply_text(message, parse_mode="Markdown")
        except:
            update.callback_query.message.edit_text(message, parse_mode="Markdown")
        return stop
    rnd_pick = shuffle_title[random.randrange(len(shuffle_title))]
    if len(shuffle_title) == 1:
        message = "Only one match has been found:"\
                  "\n     {}" \
                  "\n     {}".format(rnd_pick, shuffle_url[shuffle_title.index(rnd_pick)])
    elif len(shuffle_title) > 1:
        message = "Out of: {} titles, the following was picked:" \
                  "\n     {}" \
                  "\n     {}".format(len(shuffle_title), rnd_pick, shuffle_url[shuffle_title.index(rnd_pick)])
    try:
        update.message.reply_text(text=message, parse_mode="Markdown")
    except:
        update.callback_query.message.edit_text(message, parse_mode="Markdown")
    return stop


if __name__ == '__main__':
    main()

updater.start_polling()

updater.idle()
