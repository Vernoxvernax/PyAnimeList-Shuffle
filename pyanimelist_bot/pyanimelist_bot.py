import configparser         # configuration file
import logging              # logging module
import re                   # regex
import os.path
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
    # Welcome message
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
    message = "Please enter your MyAnimeList username: "
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
    global listtype, listtype_long
    listtype = update.callback_query.data
    # print(update.callback_query.data)
    if listtype == "Anime":
        word = "anime"
        listtype_long = "animelist"
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
    message = "Please choose the type of {}.".format(word)
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
    message = "Please pick between these different filters."
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
    message = "Any preference on the status?"
    release_status_kb = InlineKeyboardMarkup(release_status_reply, one_time_keyboard=True)
    update.callback_query.message.edit_text(message, reply_markup=release_status_kb)
    return RELEASESTATUS


def release_status_end(update: Update, context: CallbackContext) -> None:
    global release_status
    release_status = update.callback_query.data
    ReplyKeyboardRemove()
    if listtype == "Anime":
        genre_reply = "Genres                 Themes" \
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
                      "\n> Hentai (22)        | > Shounen (44)"
    else:
        genre_reply = "Genres                 Themes" \
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
                      "\n> Doujinshi (45)     | > Gender Bender (46)"
    message = "Which of the following genres do you want to prioritize?\n{}".format(genre_reply)
    update.callback_query.message.edit_text(message)
    return GENRE


# def genre_end(update: Update, context: CallbackContext) -> None:
#     update.message.reply_text("Great thanks. I will be thinking for a little bit now.")
#     cache_check()
#     return ConversationHandler.END


# checking cache
def cache_check(update: Update, context: CallbackContext):
    global cache_exists, genre, using_cache
    genre = update.message.text
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
        requesting()
        return stop


def processing(update: Update, context: CallbackContext):
    global using_cache
    using_cache = update.callback_query.data
    requesting()


def requesting():
    if using_cache == "No":
        print("Not using cache")
    elif using_cache == "Yes":
        print("Using cache")
    else:
        print("doing stuff, not the right kind")
    return ConversationHandler.END


if __name__ == '__main__':
    main()

updater.start_polling()

updater.idle()
