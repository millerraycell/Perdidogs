from pymongo import MongoClient, GEOSPHERE
import datetime

from telegram.ext import CommandHandler, Filters, MessageHandler, Updater 
from telegram.update import Update
from telegram.bot import Bot
from telegram.ext.callbackcontext import CallbackContext

import twitter

from config.settings import TELEGRAM_TOKEN, MONGO_CONNECTION, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET, TWITTER_CONSUMER_TOKEN_KEY, TWITTER_CONSUMER_TOKEN_SECRET

api = twitter.Api(TWITTER_CONSUMER_TOKEN_KEY, TWITTER_CONSUMER_TOKEN_SECRET,TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)

imagens = []

def start(update: Update, context: CallbackContext):
    response_message = "Bem-vindo(a) ao Perdidogs\nPedimos que tire uma foto do animal que encontrou"
    bot: Bot = context.bot

    bot.send_message(
        chat_id = update.effective_chat.id,
        text = response_message,
    )

    bot.send_message(
        chat_id = update.effective_chat.id,
        text = "Anexe imagens do animal\nQuando finalizar de enviar as fotos basta inserir /tweet",
    )

def tweet(update: Update, context: CallbackContext):
    response_message = "Mensagem enviada com sucesso"
    bot: Bot = context.bot

    res = collection.find_one({"user_id":update.message.from_user.id})

    position = "www.google.com/maps/@{},{},21z".format(res["geometry"]["coordinates"][0], res["geometry"]["coordinates"][1])

    print("Animal encontrado {}".format(position))

    api.PostUpdate("Animal encontrado {}".format(position), media=imagens)

    bot.sendMessage(chat_id=update.effective_chat.id,
                    text=response_message)

def photo(update: Update, context: CallbackContext):
    bot: Bot = context.bot

    fileID = update.message.photo[-1].file_id
    imagens.append(bot.get_file(fileID).file_path)
    
def location(update: Update, context: CallbackContext):
    bot: Bot = context.bot

    print("Mensagem nova de", update.message.from_user.first_name, update.message.location.latitude, update.message.location.longitude)
    user_location = {
        "user_id" : update.message.from_user.id,
        "imagens" : imagens,
        "geometry": {
            "type": "Point",
            "coordinates": [update.message.location.latitude, 
                            update.message.location.longitude]
        },
        "date" : datetime.datetime.utcnow()            
    }

    collection.insert_one(user_location)

    bot.send_message(
        chat_id = update.effective_chat.id,
        text = "Localização lida com sucesso"
    )

def unknown(update: Update, context: CallbackContext):
    response_message = "Unknown command " + update.message.text
    bot: Bot = context.bot

    bot.send_message(
        chat_id = update.effective_chat.id,
        text = response_message
    )

def main():
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(
        CommandHandler('start', start)
    )
    dispatcher.add_handler(
        CommandHandler('tweet', tweet)
    )
    dispatcher.add_handler(
        MessageHandler(Filters.location, location)
    )
    dispatcher.add_handler(
        MessageHandler(Filters.photo, photo)
    )
    dispatcher.add_handler(
        MessageHandler(Filters.command, unknown)
    )

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    conn = MongoClient(MONGO_CONNECTION)

    db = conn.perdidogs
    collection = db.animais

    collection.create_index([("geometry", GEOSPHERE)])
    
    print("press CTRL + C to cancel.")
    main()