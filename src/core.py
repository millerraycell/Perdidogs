from pymongo import MongoClient, GEOSPHERE

from uuid import uuid4

from telegram import InlineQueryResultLocation, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.keyboardbutton import KeyboardButton
from telegram.ext import InlineQueryHandler, CommandHandler, Filters, MessageHandler, Updater
from telegram.update import Update
from telegram.bot import Bot
from telegram.ext.callbackcontext import CallbackContext


from config.settings import TELEGRAM_TOKEN, MONGO_CONNECTION


def start(update: Update, context: CallbackContext):
    response_message = "Deseja enviar a sua localização?"
    bot: Bot = context.bot

    reply_markup = ReplyKeyboardMarkup([[
        KeyboardButton("Sim", False, True),
        KeyboardButton("Não"),
    ]], resize_keyboard=True, one_time_keyboard=True)

    bot.send_message(
        chat_id = update.effective_chat.id,
        text = response_message,
        reply_markup = reply_markup,
    )

def unknown(update: Update, context: CallbackContext):
    response_message = "Unknown command " + update.message.text
    bot: Bot = context.bot

    bot.send_message(
        chat_id = update.effective_chat.id,
        text = response_message
    )

def my_location (update : Update, context : CallbackContext):
    bot : Bot = context.bot
    
    search = collection.find_one({"user_id": update.message.from_user.id})
    coord = search["geometry"]["coordinates"]
    response_message = f"Última localização: Long: {coord[0]} Lat: {coord[1]}"
    
    bot.sendMessage(chat_id=update.effective_chat.id,
                    text=response_message)

def location(update: Update, context: CallbackContext):
    bot: Bot = context.bot

    if update.edited_message:
        print("Mensagem atualizada de", update.edited_message.from_user.first_name, update.edited_message.location.longitude, update.edited_message.location.latitude)
        user_location = {
            'user_id':   update.edited_message.from_user.id,
            'user_name': update.edited_message.from_user.first_name,
            "geometry": {
                "type": "Point",
                "coordinates": [update.edited_message.location.longitude, 
                                update.edited_message.location.latitude]
            }
            
        }
    else:
        print("Mensagem nova de", update.message.from_user.first_name, update.message.location.longitude, update.message.location.latitude)
        user_location = {
            'user_id':   update.message.from_user.id,
            'user_name': update.message.from_user.first_name,
            "geometry": {
                "type": "Point",
                "coordinates": [update.message.location.longitude, 
                                update.message.location.latitude]
            }
            
        }
    
    collection.replace_one(
        {"user_id": update.message.from_user.id}, 
        user_location, 
        upsert= True
    )

    bot.send_message(
        chat_id = update.effective_chat.id,
        text = "Localização lida com sucesso"
    )

def inlinequery(update: Update, context :CallbackContext):
    result = [
        InlineQueryResultLocation(id= uuid4(),
            latitude= update.inline_query.location.latitude,
            longitude= update.inline_query.location.longitude, title="Location")
    ]

    update.inline_query.answer(result)

def main():
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(
        CommandHandler('start', start)
    )
    dispatcher.add_handler(
        CommandHandler('my_location', my_location)
    )
    dispatcher.add_handler(
        MessageHandler(Filters.location, location)
    )
    dispatcher.add_handler(
        MessageHandler(Filters.command, unknown)
    )
    dispatcher.add_handler(
        InlineQueryHandler(inlinequery)
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