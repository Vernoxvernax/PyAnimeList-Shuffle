from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext, CommandHandler, Updater, MessageHandler, Filters,  ConversationHandler
import configparser
import logging
import re


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
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)


def adding_handler():
    # Welcome message
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    # Shuffle question and answer processing
    shuffle_handler = CommandHandler("shuffle", shuffle)
    dispatcher.add_handler(shuffle_handler)
    # Unknown input
    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)


def main():
    print("Starting telegram bot.")
    token = reading_config_file()
    telegram_conf(token)
    adding_handler()


# Here come the telegram functions:
def start(update: Update, context: CallbackContext) -> None:
    message = "Hello, this is your personal telegram bot to receive random entries on your MyAnimeList." \
              "\nGitHub: " \
              '[PyAnimeList-Shuffle](https://github.com/Vernoxvernax/PyAnimeList-Shuffle)' \
              '\nTo start shuffling type: /shuffle.'
    context.bot.send_message(chat_id=update.effective_chat.id, parse_mode="Markdown", text=message)


def unknown(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id, text="Unknown command. Maybe try /start?")


def shuffle(update: Update, context: CallbackContext) -> None:
    """Starts the conversation and asks the user about their gender."""
    message = "Please enter your MyAnimeList username: "
    update.message.reply_text(text=message)
    # print(update.message.text)
    # reply=ReplyKeyboardMarkup(input_field_placeholder="MyAnimeList.net username")
    shuffle_processing_handler = MessageHandler(Filters.text, shuffle_processing)
    dispatcher.add_handler(shuffle_processing_handler)


def shuffle_processing(update: Update, context: CallbackContext) -> None:
    username = update.message.text
    illegal_check = re.compile("[@_!#$%^&*()<>?/\|}{~:]")
    if not (illegal_check.search(username) == None):
        update.message.reply_text("You username has illegal characters, please try again.")
    else:
        update.message.reply_text("You've written {}".format(update.message.text))
        return


if __name__ == '__main__':
    main()

updater.start_polling()

updater.idle()
