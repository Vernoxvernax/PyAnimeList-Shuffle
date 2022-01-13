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
from telegram import Update, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, \
                     ParseMode
import telegram.utils.helpers
from telegram.ext import CallbackContext, CommandHandler, Updater, \
                         MessageHandler, Filters, ConversationHandler, \
                         CallbackQueryHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

USERNAME, LISTTYPE, MEDIATYPE, USERSTATUS, RELEASESTATUS, GENRE, CACHE, SCORE, MIN = range(9)


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
                CallbackQueryHandler(release_status_end, pattern='^(No|Currently Airing|Currently Publishing|Finished'
                                                                 '|Not yet Aired|Not yet Published)$')
            ],
            SCORE: [
                CallbackQueryHandler(score_end, pattern='^[0-9]+$')
            ],
            MIN: [
                CallbackQueryHandler(min_end, pattern='^(Yes|No)$'),
                MessageHandler(Filters.regex('^[0-9]+$'), min_end)
            ],
            GENRE: [
                MessageHandler(Filters.regex('^([0-9]+|[0-9]+\s[0-9]+)$'), cache_check)
            ],
            CACHE: [
                CallbackQueryHandler(cache_input, pattern='^(No|Yes)$')
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
    global username, username_input
    username_input = update.message.text
    username = username_input.lower()
    illegal_check = re.compile("[@_!#$%^&*()<>?/|}{~:]")
    if not (illegal_check.search(username) is None):
        update.message.reply_text("You username has illegal characters, please try again.")
        return USERNAME
    else:
        # update.message.reply_text("Username set to: {}".format(update.message.text))
        update.message.reply_text("Username set to: {}".format(username_input))
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
                InlineKeyboardButton("Currently Airing", callback_data="Currently Airing")
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
                InlineKeyboardButton("Currently Publishing", callback_data="Currently Publishing")
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
    if release_status == "Finished":
        if listtype == "Anime":
            release_status = "Finished Airing"
        else:
            release_status = "Finished"
    if release_status == "Not yet Aired":
        release_status = "Not yet aired"
    if release_status == "Not yet Published":
        release_status = "Not yet published"
    score_reply = [
        [
            InlineKeyboardButton("10", callback_data="10"),
            InlineKeyboardButton("9", callback_data="9"),
            InlineKeyboardButton("8", callback_data="8")
        ],
        [
            InlineKeyboardButton("7", callback_data="7"),
            InlineKeyboardButton("6", callback_data="6"),
            InlineKeyboardButton("5", callback_data="5")
        ],
        [
            InlineKeyboardButton("4", callback_data="4"),
            InlineKeyboardButton("3", callback_data="3"),
            InlineKeyboardButton("2", callback_data="2")
        ],
        [
            InlineKeyboardButton("1", callback_data="1"),
            InlineKeyboardButton("No", callback_data="0")
        ]
    ]
    message = "Do you want to filter after YOUR score?:"
    score_kb = InlineKeyboardMarkup(score_reply, one_time_keyboard=True)
    update.callback_query.message.edit_text(message, reply_markup=score_kb)
    return SCORE


def score_end(update: Update, context: CallbackContext):
    global score, counter
    counter = 0
    score = update.callback_query.data
    question_reply = [
        [
            InlineKeyboardButton("Yes", callback_data="Yes"),
            InlineKeyboardButton("No", callback_data="No")
        ]
    ]
    question_kb = InlineKeyboardMarkup(question_reply)
    if listtype == "Anime":
        temp_score_help = "episodes"
    else:
        temp_score_help = "chapters & volumes"
    message = "Do you want to set min/max amount of {}?\n" \
              "You can skip individual parts by sending 0.".format(temp_score_help)
    update.callback_query.message.edit_text(message, reply_markup=question_kb)
    return MIN


def min_end(update: Update, context: CallbackContext):
    global counter, maximum, minimum
    genre_reply = "```\n" \
                  "> 0 -> don't do anything" \
                  "\n> 1 -> results with [1]" \
                  "\n> 0 32 -> results without [32]" \
                  "\n> 1 2 -> results w/ [1] excl. [2]\n" \
                  "\n.Genres.           .Themes." \
                  "\nAction (1)        |Cars (23)" \
                  "\nAdventure (2)     |Demons (24)" \
                  "\nAvant Garde (3)   |Game (25)" \
                  "\nAward Winning (4) |Harem (26)" \
                  "\nBoys Love (5)     |Historical (27)" \
                  "\nComedy (6)        |Martial Arts (28)" \
                  "\nDrama (7)         |Mecha (29)" \
                  "\nFantasy (8)       |Military (30)" \
                  "\nGirls Love (9)    |Music (31)" \
                  "\nGourmet (10)      |Parody (32)" \
                  "\nHorror (11)       |Police (33)" \
                  "\nMystery (12)      |Psychological (34)" \
                  "\nRomance (13)      |Samurai (35)" \
                  "\nSci-Fi (14)       |School (36)" \
                  "\nSlice of Life (15)|Space (37)" \
                  "\nSports (16)       |Super Power (38)" \
                  "\nSupernatural (17) |Vampire (39)" \
                  "\nSuspense (18)     |" \
                  "\nWork Life (19)    |.Demographics." \
                  "\n                  |Josei (40)" \
                  "\n.Explicit Genres. |Kids (41)" \
                  "\nEcchi (20)        |Seinen (42)" \
                  "\nErotica (21)      |Shoujo (43)" \
                  "\nHentai (22)       |Shounen (44)```"
    # genre_message = "Prioritizing/Avoiding genres?:\n{}".format(genre_reply)
    genre_message = "Prioritizing/Avoiding genres?:"
    if listtype == "Manga":
        genre_message = "Prioritizing/Avoiding genres?:" \
                        "```\n.Manga exclusive tags." \
                        "\nDoujinshi (45)\nGender Bender (46)```"
        # genre_reply = genre_reply + "``` \n\n.Manga exclusive tags." \
        #                             "\nDoujinshi (45)\nGender Bender (46)```"
    if counter == 0:
        try:
            min_answer = update.callback_query.data
        except:
            min_answer = update.message.text
    else:
        min_answer = update.message.text
    counter_check_a = [1, 3, 69, 71]
    counter_check_b = [2, 4, 70, 72]
    if counter == 0 or counter == 69:
        minimum = []
        maximum = []
    if min_answer == "No":
        maximum = minimum = [0, 0]
        update.callback_query.message.edit_text(genre_message, parse_mode="Markdown")
        update.callback_query.message.reply_photo("https://i.imgur.com/Kqb1dk3.jpg")
        return GENRE
    elif counter in counter_check_a:
        minimum.append(min_answer)
    elif counter in counter_check_b:
        maximum.append(min_answer)
    counter = counter + 1
    if counter == 3 and listtype == "Anime" or counter == 71 and listtype == "Anime":
        if int(minimum[0]) > int(maximum[0]) != 0:
            message = "It seems like you accidentally swapped the min and max values. " \
                      "Make sure minimum is smaller than maximum. :)\n" \
                      "Please specify the minimum amount of episodes:"
            update.message.reply_text(message, parse_mode="Markdown")
            counter = 69
            return MIN
        update.message.reply_text(genre_message, parse_mode="Markdown")
        return GENRE
    elif counter == 5 and listtype == "Manga" or counter == 73 and listtype == "Manga":
        if int(minimum[0]) > int(maximum[0]) != 0 or int(minimum[1]) > int(maximum[1]) != 0:
            message = "It seems like you accidentally swapped the min and max values. " \
                      "Make sure minimum is smaller than maximum. :)\n" \
                      "Please specify the minimum amount of chapters:"
            update.message.reply_text(message, parse_mode="Markdown")
            counter = 69
            return MIN
        update.message.reply_text(genre_message, parse_mode="Markdown")
        return GENRE
    if listtype == "Anime":
        temp_score_help = "episodes"
    else:
        if counter < 3:
            temp_score_help = "chapters"
        else:
            temp_score_help = "volumes"
    if counter == 1 or counter == 3:
        message = "Specify how many {} your {} should at least have. (minimum):".\
            format(temp_score_help, listtype_short)
    else:
        message = "Specify the maximum amount of {}:". \
            format(temp_score_help, listtype_short)
    if counter == 1:
        update.callback_query.message.edit_text(message)
    else:
        update.message.reply_text(message)
    ReplyKeyboardRemove()
    return MIN


def cache_check(update: Update, context: CallbackContext):
    global cache_exists, user_genre, using_cache, callbackhandler, queue_msg, genre_exclusion_bool
    user_genre = update.message.text
    genre_exclusion_bool = False
    if " " in user_genre:
        user_genre = user_genre.split()
        genre_exclusion_bool = True
    if os.path.isfile(r"./cache/{}-{}-p1.json".format(username, listtype_long)):
        question_reply = [
            [
                InlineKeyboardButton("Yes", callback_data="Yes"),
                InlineKeyboardButton("No", callback_data="No")
            ]
        ]
        question_kb = InlineKeyboardMarkup(question_reply)
        update.message.reply_text("[INF] Cache found for {}.\nDo you want to use it?".format(username_input),
                                  reply_markup=question_kb)
        cache_exists = True
        return CACHE
    else:
        update.message.reply_text("[INF] No cache found for {}.".format(username_input))
        using_cache = "No"
        cache_exists = False
        message = "[INF] Joining queue."
        update.message.reply_text(message)
        callbackhandler = False
        thread = threading.Thread(target=request_thread, args=(update, context))
        thread.start()
        thread.join()
        return ConversationHandler.END


def cache_input(update: Update, context: CallbackContext):
    global using_cache, callbackhandler
    callbackhandler = True
    using_cache = update.callback_query.data
    message = "[INF] Joining queue."
    if using_cache == "No":
        update.callback_query.message.edit_text(message)
    thread = threading.Thread(target=request_thread, args=(update, context))
    thread.start()
    thread.join()
    return ConversationHandler.END


def request_thread(update: Update, context: CallbackContext):
    def genre_s(query, mtype, c_page, shuffle_title, shuffle_url, status, media_type, minimum, maximum, score):
        item_list = []
        if m_type == "animelist":
            if query != "n":
                if genre_exclusion_bool:
                    def genre_exc_func(item):
                        genre_positive = False
                        genre_negative = False
                        for query in json_body["data"][item][mtype]["genres"]:
                            query = json_body["data"][item][mtype]["genres"].index(query)
                            a_genre = json_body["data"][item][mtype]["genres"][query]["mal_id"]
                            if genre[0] == a_genre:
                                genre_positive = True
                            if genre[1] == a_genre:
                                genre_negative = True
                        for query in json_body["data"][item][mtype]["demographics"]:
                            query = json_body["data"][item][mtype]["demographics"].index(query)
                            a_genre = json_body["data"][item][mtype]["demographics"][query]["mal_id"]
                            if genre[0] == a_genre:
                                genre_positive = True
                            if genre[1] == a_genre:
                                genre_negative = True
                        return genre_positive, genre_negative
                    for eitem in json_body["data"]:
                        item = json_body["data"].index(eitem)
                        genre_positive, genre_negative = genre_exc_func(item)
                        if genre_positive and not genre_negative:
                            item_list.append(eitem)
                        elif genre[0] == -1 and not genre_negative:
                            item_list.append(eitem)
                else:
                    for eitem in json_body["data"]:
                        item = json_body["data"].index(eitem)
                        for query in json_body["data"][item][mtype]["genres"]:
                            query = json_body["data"][item][mtype]["genres"].index(query)
                            a_genre = json_body["data"][item][mtype]["genres"][query]["mal_id"]
                            if genre == a_genre:
                                item_list.append(eitem)
                        for query in json_body["data"][item][mtype]["demographics"]:
                            query = json_body["data"][item][mtype]["demographics"].index(query)
                            a_genre = json_body["data"][item][mtype]["demographics"][query]["mal_id"]
                            if genre == a_genre:
                                item_list.append(eitem)
            else:
                for eitem in json_body["data"]:
                    item_list.append(eitem)
            if pref != "n":
                pref_list = []
                for pref_check in item_list:
                    pref_index = item_list.index(pref_check)
                    if item_list[pref_index][mtype]["status"] == pref:
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
                    if item_list[media_type_index][mtype]["type"] == media_type:
                        media_list.append(media_type_check)
                item_list = media_list.copy()
            if score != 0:
                score_list = []
                for score_check in item_list:
                    score_index = item_list.index(score_check)
                    if item_list[score_index]["score"] == score:
                        score_list.append(score_check)
                item_list = score_list.copy()
            if int(minimum[0]) != 0:
                mini_list = []
                for mini_check in item_list:
                    mini_index = item_list.index(mini_check)
                    if item_list[mini_index][mtype]["episodes"] >= int(minimum[0]):
                        mini_list.append(mini_check)
                item_list = mini_list.copy()
            if int(maximum[0]) != 0:
                max_list = []
                for max_check in item_list:
                    max_index = item_list.index(max_check)
                    if item_list[max_index][mtype]["episodes"] <= int(maximum[0]):
                        max_list.append(max_check)
                item_list = max_list.copy()
            if not item_list:
                print("[INF] Content of page {} did not meet your filters.".format(c_page))
                return shuffle_title, shuffle_url
            for item in item_list:
                item_index = item_list.index(item)
                shuffle_title.append(item_list[item_index][mtype]['title'])
                shuffle_url.append(item_list[item_index][mtype]['url'])
            return shuffle_title, shuffle_url
        elif m_type == "mangalist":
            if query != "n":
                if genre_exclusion_bool:
                    def genre_exc_func(item):
                        genre_positive = False
                        genre_negative = False
                        for query in json_body["data"][item][mtype]["genres"]:
                            query = json_body["data"][item][mtype]["genres"].index(query)
                            a_genre = json_body["data"][item][mtype]["genres"][query]["mal_id"]
                            if genre[0] == a_genre:
                                genre_positive = True
                            if genre[1] == a_genre:
                                genre_negative = True
                        for query in json_body["data"][item][mtype]["demographics"]:
                            query = json_body["data"][item][mtype]["demographics"].index(query)
                            a_genre = json_body["data"][item][mtype]["demographics"][query]["mal_id"]
                            if genre[0] == a_genre:
                                genre_positive = True
                            if genre[1] == a_genre:
                                genre_negative = True
                        return genre_positive, genre_negative
                    for eitem in json_body["data"]:
                        item = json_body["data"].index(eitem)
                        genre_positive, genre_negative = genre_exc_func(item)
                        if genre_positive and not genre_negative:
                            item_list.append(eitem)
                        elif genre[0] == -1 and not genre_negative:
                            item_list.append(eitem)
                else:
                    for eitem in json_body["data"]:
                        item = json_body["data"].index(eitem)
                        for query in json_body["data"][item][mtype]["genres"]:
                            query = json_body["data"][item][mtype]["genres"].index(query)
                            a_genre = json_body["data"][item][mtype]["genres"][query]["mal_id"]
                            if genre == a_genre:
                                item_list.append(eitem)
                        for query in json_body["data"][item][mtype]["demographics"]:
                            query = json_body["data"][item][mtype]["demographics"].index(query)
                            a_genre = json_body["data"][item][mtype]["demographics"][query]["mal_id"]
                            if genre == a_genre:
                                item_list.append(eitem)
            else:
                for eitem in json_body["data"]:
                    item_list.append(eitem)
            if pref != "n":
                pref_list = []
                for pref_check in item_list:
                    pref_index = item_list.index(pref_check)
                    if item_list[pref_index][mtype]["status"] == pref:
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
                    if item_list[media_type_index][mtype]["type"] == media_type:
                        media_list.append(media_type_check)
                item_list = media_list.copy()
            if score != 0:
                score_list = []
                for score_check in item_list:
                    score_index = item_list.index(score_check)
                    if item_list[score_index]["score"] == score:
                        score_list.append(score_check)
                item_list = score_list.copy()
            if int(minimum[0]) != 0:
                mini_list = []
                for mini_check in item_list:
                    mini_index = item_list.index(mini_check)
                    if item_list[mini_index][mtype]["chapters"] >= int(minimum[0]):
                        mini_list.append(mini_check)
                item_list = mini_list.copy()
            if int(minimum[1]) != 0:
                mini_list = []
                for mini_check in item_list:
                    mini_index = item_list.index(mini_check)
                    if item_list[mini_index][mtype]["volumes"] >= int(minimum[1]):
                        mini_list.append(mini_check)
                item_list = mini_list.copy()
            if int(maximum[0]) != 0:
                max_list = []
                for max_check in item_list:
                    max_index = item_list.index(max_check)
                    if item_list[max_index][mtype]["chapters"] <= int(maximum[0]):
                        max_list.append(max_check)
                item_list = max_list.copy()
            if int(maximum[1]) != 0:
                max_list = []
                for max_check in item_list:
                    max_index = item_list.index(max_check)
                    if item_list[max_index][mtype]["volumes"] <= int(maximum[1]):
                        max_list.append(max_check)
                item_list = max_list.copy()
            if not item_list:
                print("[INF] Content of page {} did not meet your filters.".format(c_page))
                return shuffle_title, shuffle_url
            for item in item_list:
                item_index = item_list.index(item)
                shuffle_title.append(item_list[item_index][mtype]['title'])
                shuffle_url.append(item_list[item_index][mtype]['url'])
            return shuffle_title, shuffle_url
    # defining variables and assigning values
    genre = user_genre
    pref = release_status
    m_type = listtype_long
    type_short = listtype_short
    global score, minimum, maximum, genre_exclusion_bool
    score = int(score)
    minimum = list(map(int, minimum))
    maximum = list(map(int, maximum))
    if type_short == "anime":
        m_status_a = ["None", "Watching", "Completed", "On-Hold", "Dropped", "Plan to Watch"]
    else:
        m_status_a = ["None", "Reading", "Completed", "On-Hold", "Dropped", "Plan to Read"]
    m_status_b = ["0", "1", "2", "3", "4", "6"]
    if userstatus == "None":
        m_status = "n"
    elif userstatus in m_status_a:
        m_status = m_status_b[m_status_a.index(userstatus)]
    if pref == "No":
        pref = "n"
    if m_type == "mangalist":
        ch_genre_a = [0] * 47
        ch_genre_b = [1, 2, 5, 46, 28, 4, 8, 10, 26, 47, 14, 7, 22, 24, 36, 30, 37, 45, 48, 9, 49, 12, 3,
                      6, 11, 35, 13, 17, 18, 38, 19, 20, 39, 40, 21, 23, 29, 31, 32, 42, 15, 41, 25, 27, 43, 44]
    else:
        ch_genre_a = [0] * 44
        ch_genre_b = [1, 2, 5, 46, 28, 4, 8, 10, 26, 47, 14, 7, 22, 24, 36, 30, 37, 41, 48, 9, 49, 12, 3,
                      6, 11, 35, 13, 17, 18, 38, 19, 20, 39, 40, 21, 23, 29, 31, 32, 43, 15, 42, 25, 27]
    for x in range(0, len(ch_genre_a)):
        ch_genre_a[x] = x
    if genre == "0" or genre == [0, 0]:
        genre = str("n")
    if genre_exclusion_bool:
        genre[0] = int(genre[0]) - 1
        if genre[0] != -1:
            genre[0] = ch_genre_b[ch_genre_a.index(int(genre[0]))]
        genre[1] = int(genre[1]) - 1
        if genre[1] != -1:
            genre[1] = ch_genre_b[ch_genre_a.index(int(genre[1]))]
    else:
        genre = int(genre) - 1
        genre = ch_genre_b[ch_genre_a.index(int(genre))]
    media_type = mediatype
    if media_type == "TV-Show":
        media_type = "TV"
    if media_type == "All":
        media_type = ""
    message = "[INF] Loading..."
    if not callbackhandler:
        update.message.reply_text(message)
    else:
        update.callback_query.message.edit_text(message)
    if using_cache == "Yes" and os.path.isfile(r"./cache/{}-{}-p1.json".format(username, m_type)):
        with open("./cache/{}-{}-p1.json".format(username, m_type)) as json_file:
            json_body = json.load(json_file)
        req_status = False
        sleeeping = 0
    elif using_cache == "No":
        req_status = True
        sleeeping = 1
    else:
        return stop
    error_count = 0
    c_url = str("https://api.jikan.moe/v4/users/{}/{}".format(username, m_type))
    while req_status:
        try:
            if error_count >= 9:
                print("More than 10 failed attempts, please debug and fix yo shit.")
                return
            request = requests.get(c_url, timeout=10)
        except:
            print("API didn't respond. Trying again in 2 seconds...")
            time.sleep(2)
        else:
            with open("./cache/{}-{}-p1.json".format(username, m_type), "w+") as json_file:
                json_file.write(request.text)
            if '"anime"' in request.text:
                json_body = json.loads(request.text)
                req_status = False
            elif '"manga"' in request.text:
                json_body = json.loads(request.text)
                req_status = False
            elif '"status":' in request.text and '"report_url":"' not in request.text:
                json_body = json.loads(request.text)
                req_status = False
            elif request.text == '{"data":[]}':
                json_body = ""
                req_status = False
            else:
                json_body = ""
                error_count = error_count + 1
    length = len(str(json_body))
    shuffle_title = []
    shuffle_url = []
    c_page = 1
    erroring = True
    if using_cache == "No":
        if length < 14:
            message = "The acquired site does not have any content."
        elif '"status":400,' in request.text:
            message = "Invalid Request. Maybe that username doesn't exist?"
        elif '"status":404,' in request.text:
            message = "This anime/manga list does not exist."
        elif '"status":429,' in request.text:
            message = "You are sending too many requests."
        elif "BadResponseException" in request.text:
            message = "Something broke :("
        elif using_cache == "No":
            erroring = False
            message = "[INF] Page 1 successfully retrieved."
        if not callbackhandler:
            update.message.reply_text(message)
        else:
            update.callback_query.message.edit_text(message)
        if erroring:
            return
    shuffle_title, shuffle_url = genre_s(genre, type_short, c_page, shuffle_title, shuffle_url,
                                         m_status, media_type, minimum, maximum, score)
    c_page = c_page + 1
    error_count = 0
    while length > 150:
        if using_cache == "Yes" and os.path.isfile(r"./cache/{}-{}-p{}.json".format(username, m_type, c_page)):
            try:
                with open("./cache/{}-{}-p{}.json".format(username, m_type, c_page)) as json_file:
                    json_body = json.load(json_file)
            except:
                json_body = ""
            req_status = False
        else:
            req_status = True
        time.sleep(sleeeping)
        print("Loading page:", c_page)
        n_url = str("https://api.jikan.moe/v4/users/{}/{}?page={}".format(username, m_type, c_page))
        while req_status:
            try:
                if error_count >= 9:
                    print("More than 10 failed attempts, please debug and fix yo shit.")
                    return
                request = requests.get(n_url, timeout=10)
            except:
                print("API didn't respond. Trying again in 2 seconds...")
                time.sleep(2)
            else:
                with open("./cache/{}-{}-p{}.json".format(username, m_type, c_page), "w+") as json_file:
                    json_file.write(request.text)
                if '"anime"' in request.text:
                    json_body = json.loads(request.text)
                    req_status = False
                elif '"manga"' in request.text:
                    json_body = json.loads(request.text)
                    req_status = False
                elif '"status":' in request.text:
                    json_body = json.loads(request.text)
                    req_status = False
                elif request.text == '{"data":[]}':
                    json_body = ""
                    req_status = False
                else:
                    json_body = ""
                    error_count = error_count + 1
        erroring = True
        if using_cache == "No":
            if '"status":400,' in request.text:
                message = "Invalid Request. Maybe that username doesn't exist?"
            elif '"status":404,' in request.text:
                message = "This anime/manga list does not exist."
            elif '"status":429,' in request.text:
                message = "You are sending too many requests."
            elif "BadResponseException" in request.text:
                message = "Something broke :("
            elif using_cache == "No":
                erroring = False
                message = "[INF] Page {} successfully retrieved.".format(c_page)
            if not callbackhandler:
                update.message.reply_text(message)
            else:
                update.callback_query.message.edit_text(message)
            if erroring:
                return
        if not json_body == "":
            shuffle_title, shuffle_url = genre_s(genre, type_short, c_page, shuffle_title, shuffle_url,
                                                 m_status, media_type, minimum, maximum, score)
        c_page = c_page + 1
        error_count = 0
        length = len(str(json_body))
    if len(shuffle_title) == 0:
        message = "     Nothing out of your list matches configured search requirements."
        if not callbackhandler:
            update.message.reply_text(message)
        else:
            update.callback_query.message.edit_text(message)
        return stop
    else:
        rnd_pick = shuffle_title[random.randrange(len(shuffle_title))]
    if len(shuffle_title) == 1:
        message = "Only one match has been found:"\
                  "\n     [{} \- MyAnimeList\.net]({})".\
            format(telegram.utils.helpers.escape_markdown(rnd_pick, version=2),
                   telegram.utils.helpers.escape_markdown(shuffle_url[shuffle_title.index(rnd_pick)]), version=2)
    elif len(shuffle_title) > 1:
        message = "Out of: {} titles, the following was picked:" \
                  "\n     [{} \- MyAnimeList\.net]({})"\
            .format(len(shuffle_title), telegram.utils.helpers.escape_markdown(rnd_pick, version=2),
                    telegram.utils.helpers.escape_markdown(shuffle_url[shuffle_title.index(rnd_pick)]), version=2)
    print(message)
    if not callbackhandler:
        update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN_V2)
    else:
        update.callback_query.message.edit_text(message, parse_mode=ParseMode.MARKDOWN_V2)
    return stop


if __name__ == '__main__':
    main()

updater.start_polling()

updater.idle()
