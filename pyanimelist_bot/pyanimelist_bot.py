from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, Updater
import configparser
import logging


config_file = configparser.ConfigParser()
config_file.read("telegram.conf")
config = config_file["config"]
TOKEN = config["TOKEN"]

# print(config)
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def start(update: Update, context: CallbackContext):
    message = "Hello, this is your personal telegram bot to receive random entries on your MyAnimeList." \
              "\nGitHub: " \
              '[PyAnimeList-Shuffle](https://github.com/Vernoxvernax/PyAnimeList-Shuffle)'
    context.bot.send_message(chat_id=update.effective_chat.id, parse_mode="Markdown", text=message)


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

updater.start_polling()
