# Imports
from pymongo import MongoClient, GEOSPHERE
import datetime

from telegram.ext import CommandHandler, Filters, MessageHandler, Updater 
from telegram.update import Update
from telegram.bot import Bot
from telegram.ext.callbackcontext import CallbackContext

import twitter

from config.settings import TELEGRAM_TOKEN, MONGO_CONNECTION, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET, TWITTER_CONSUMER_TOKEN_KEY, TWITTER_CONSUMER_TOKEN_SECRET

api = twitter.Api(TWITTER_CONSUMER_TOKEN_KEY, TWITTER_CONSUMER_TOKEN_SECRET,TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)

#Database Connetion
conn = MongoClient(MONGO_CONNECTION)

db = conn.perdidogs
collection = db.animais

collection.create_index([("geometry", GEOSPHERE)])

#Telegram bot start
updater = Updater(token=TELEGRAM_TOKEN, use_context=True)

def start(update: Update, context: CallbackContext):
    bot: Bot = context.bot

    bot.send_message(
        chat_id = update.effective_chat.id,
        text = "Bem-vindo(a) ao Perdidogs\nO Bot oficial de publicação de animais perdidos",
    )

    bot.send_message(
        chat_id = update.effective_chat.id,
        text = "O nosso sistema funciona através do compartilhamento das fotos e da localização dos animais perdidos",
    )

    bot.send_message(
        chat_id = update.effective_chat.id,
        text = "Os procedimentos para a publicação do animal são os seguintes:",
    )

    bot.send_message(
        chat_id = update.effective_chat.id,
        text = "Primeiramente necessitamos que você compartilhe a sua localização do seu dispositivo, para servir como base para a localização dos animais",
    )

    bot.send_message(
        chat_id = update.effective_chat.id,
        text = "Para qualquer dúvida sobre o uso da localização insira /help_localization",
    )

    bot.send_message(
        chat_id = update.effective_chat.id,
        text = "Após enviar a sua localização, aparecerá uma mensagem de confirmação\nAgora só encaminhar as fotos do animal",
    )

    bot.send_message(
        chat_id = update.effective_chat.id,
        text = "Depois de enviar as fotos do animal, só inserir /post e as fotos do animal serão publicadas em nosso site e no twitter @Perdidogs1",
    )

def post(update: Update, context: CallbackContext):
    response_message = "Mensagem enviada com sucesso"
    bot: Bot = context.bot

    collection.update_one({"chat_id": update.message.chat_id, "posted": False}, {"$set":{"posted" : True}})
    res = collection.find_one({"chat_id":update.message.chat_id})

    imagens = [i for i in res["imagens"]]

    position = "www.google.com/maps/@{},{},21z".format(res["geometry"]["coordinates"][0], res["geometry"]["coordinates"][1])

    api.PostUpdate("Animal encontrado {}".format(position), media=imagens)

    bot.sendMessage(
        chat_id=update.message.chat_id,
        text=response_message
    )
    updater.start_polling()

    
def photo(update: Update, context: CallbackContext):
    bot: Bot = context.bot

    if collection.find_one({"chat_id": update.message.chat_id}) == None:
        bot.send_message(
            chat_id = update.effective_chat.id,
            text = "Envie a sua localização para fazer a busca"
        )

    else:
        fileID = update.message.photo[-1].file_id

        collection.update_one({"chat_id": update.message.chat_id, "posted": False}, { "$push": {
                    "imagens" : bot.get_file(fileID).file_path,
                }
            }
        )
    
def location(update: Update, context: CallbackContext):
    bot: Bot = context.bot

    animal_post = {
        "chat_id" : update.message.chat_id,
        "geometry": {
            "type": "Point",
            "coordinates": [update.message.location.latitude, 
                            update.message.location.longitude]
        },
        "imagens": [],
        "date" : datetime.datetime.utcnow(), 
        "posted": False           
    }

    collection.insert_one(animal_post)

    bot.send_message(
        chat_id = update.effective_chat.id,
        text = "Localização lida com sucesso"
    )

def show_animals_close_by(update: Update, context: CallbackContext):
    bot: Bot = context.bot

    if collection.find_one({"chat_id": update.message.chat_id}) == None:
        bot.send_message(
            chat_id = update.effective_chat.id,
            text = "Envie a sua localização para fazer a busca"
        )

    else:
        data = collection.aggregate([{"$geoNear":{
            "near" : {
                "type":"Point",
                "coordinates":[update.message.location.latitude,
                                update.message.location.longitude]
            },
            "distanceField":"dist.calculated",
            "maxDistance": 5000,
            "spherical": True
        }}])

        # TODO: Sempre retornar os 3 primeiros animais, enviar mais depois 

        for animal in data:
            print(animal)

def flush(update: Update, context: CallbackContext):
    collection.delete_one({"chat_id": update.message.chat_id})

def unknown(update: Update, context: CallbackContext):
    response_message = "Unknown command " + update.message.text
    bot: Bot = context.bot

    bot.send_message(
        chat_id = update.effective_chat.id,
        text = response_message
    )

def main():
    dispatcher = updater.dispatcher

    dispatcher.add_handler(
        CommandHandler('start', start)
    )
    dispatcher.add_handler(
        CommandHandler('post', post)
    )
    dispatcher.add_handler(
        CommandHandler('flush', flush)
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
    main()