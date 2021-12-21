from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext, CommandHandler, Updater, MessageHandler, Filters,  ConversationHandler
import configparser
import logging


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
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    start2 = CommandHandler("haha", haha)
    dispatcher.add_handler(start2)
    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)


def main():
    print("Starting telegram bot.")
    token = reading_config_file()
    telegram_conf(token)
    adding_handler()


# Here come the telegram functions:
def start(update: Update, context: CallbackContext):
    message = "Hello, this is your personal telegram bot to receive random entries on your MyAnimeList." \
              "\nGitHub: " \
              '[PyAnimeList-Shuffle](https://github.com/Vernoxvernax/PyAnimeList-Shuffle)' \
              '\nTo start shuffling type /shuffle'
    context.bot.send_message(chat_id=update.effective_chat.id, parse_mode="Markdown", text=message)


def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Unknown input. Did you mean /start?")


def shuffle(update: Update, context: CallbackContext):
    """Starts the conversation and asks the user about their gender."""
    message = "Please enter your MyAnimeList username: "
    update.message.reply_text(text=message)
    reply=ReplyKeyboardMarkup(input_field_placeholder="MyAnimeList.net username")


main()

updater.start_polling()

updater.idle()
