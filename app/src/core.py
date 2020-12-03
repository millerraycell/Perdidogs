from pymongo import MongoClient, GEOSPHERE

from telegram import InlineQueryResultLocation, ReplyKeyboardMarkup
from telegram.keyboardbutton import KeyboardButton
from telegram.ext import InlineQueryHandler, CommandHandler, Filters, MessageHandler, Updater 
from telegram.update import Update
from telegram.bot import Bot
from telegram.ext.callbackcontext import CallbackContext

import twitter

from config.settings import TELEGRAM_TOKEN, MONGO_CONNECTION, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET, TWITTER_CONSUMER_TOKEN_KEY, TWITTER_CONSUMER_TOKEN_SECRET

api = twitter.Api(TWITTER_CONSUMER_TOKEN_KEY, TWITTER_CONSUMER_TOKEN_SECRET,TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)

testes = []

def start(update: Update, context: CallbackContext):
    response_message = "Bem-vindo(a) ao Perdidogs\nPedimos que tire uma foto do animal que encontrou"
    bot: Bot = context.bot

    bot.send_message(
        chat_id = update.effective_chat.id,
        text = response_message,
    )

    bot.send_message(
        chat_id = update.effective_chat.id,
        text = "Anexe imagens do animal",
    )

def tweet(update: Update, context: CallbackContext):
    response_message = "Mensagem enviada com sucesso"
    bot: Bot = context.bot

    status = api.PostUpdate('Testeeee', testes)
    print(status)

    bot.sendMessage(chat_id=update.effective_chat.id,
                    text=response_message)

def photo(update: Update, context: CallbackContext):
    bot: Bot = context.bot

    fileID = update.message.photo[-1].file_id
    testes.append(bot.get_file(fileID).file_path)
    
def location(update: Update, context: CallbackContext):
    bot: Bot = context.bot

    if update.edited_message:
        print("Mensagem atualizada de", update.edited_message.from_user.first_name, update.edited_message.location.longitude, update.edited_message.location.latitude)
        user_location = {
            'user_id':   update.edited_message.from_user.id,
            'user_name': update.edited_message.from_user.first_name,
            "geometry": {
                "type": "Point",
                "coordinates": [update.edited_message.location.latitude, 
                                update.edited_message.location.longitude]
            }
            
        }

        collection.replace_one(
            {"user_id": update.message.from_user.id}, 
            user_location, 
            upsert= True
        )
    else:
        print("Mensagem nova de", update.message.from_user.first_name, update.message.location.latitude, update.message.location.longitude)
        user_location = {
            'user_id':   update.message.from_user.id,
            'user_name': update.message.from_user.first_name,
            "geometry": {
                "type": "Point",
                "coordinates": [update.message.location.latitude, 
                                update.message.location.longitude]
            }
            
        }

        position = "google.com/maps/@{},{},21z".format(update.message.location.latitude, update.message.location.longitude)

        local = api.PostUpdate("Testandooo {}".format(position))

        print(local)

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

    db = conn.geobot
    collection = db.clientes

    collection.create_index([("geometry", GEOSPHERE)])

    print("press CTRL + C to cancel.")
    main()