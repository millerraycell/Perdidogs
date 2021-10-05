# Imports
from bson import json_util
from pymongo import MongoClient, GEOSPHERE
import datetime

from telegram.ext import CommandHandler, Filters, MessageHandler, Updater, CallbackQueryHandler
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup 
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

post_collection = db.posts

animal_post = {}

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
    bot: Bot = context.bot

    animal_post["posted"] = True
    collection.insert_one(animal_post)

    print(animal_post)

    imagens = [bot.get_file(i).file_path for i in animal_post["images"]]

    position = "www.google.com/maps/@{},{},21z".format(animal_post["geometry"]["coordinates"][0], animal_post["geometry"]["coordinates"][1])

    api.PostUpdate("Animal encontrado {}".format(position), media=imagens)

    animal_post.clear()

    bot.sendMessage(
        chat_id=update.message.chat_id,
        text="Post realizado com sucesso"
    )

    
def photo(update: Update, context: CallbackContext):
    bot: Bot = context.bot

    fileID = update.message.photo[-1].file_id
    print(fileID)

    if "images" not in animal_post.keys():
        animal_post["images"] = [fileID]
    
    else:
        animal_post["images"].append(fileID)

    print(animal_post)

    bot.send_message(
        chat_id = update.effective_chat.id,
        text = "Fotos lidas com sucesso"
    )
    
def location(update: Update, context: CallbackContext):
    bot: Bot = context.bot

    animal_post["chat_id"] = update.message.chat.id
    animal_post["geometry"] = {
        "type": "Point",
        "coordinates": [update.message.location.latitude, 
                            update.message.location.longitude]
    }
    animal_post["date"] = datetime.datetime.utcnow()
    animal_post["posted"] = False

    bot.send_message(
        chat_id = update.effective_chat.id,
        text = "Localização lida com sucesso"
    )

# TODO
def show_animals_close_by(update: Update, context: CallbackContext):
    bot: Bot = context.bot

    if "geometry" not in animal_post.keys():
        bot.send_message(
            chat_id = update.effective_chat.id,
            text= "Envie a sua localização para fazer a busca dos animais"
        )

    else:
        data = collection.aggregate([{"$geoNear":{
            "near" : {
                "type":"Point",
                "coordinates":[animal_post["geometry"]["coordinates"][0],
                            animal_post["geometry"]["coordinates"][1]]
            },
            "distanceField":"dist.calculated",
            "maxDistance": 5000,
            "spherical": True
        }}])

        for animal in data:
            keyboard = [
                [
                    InlineKeyboardButton("Sim", callback_data= json_util.dumps(animal["_id"])),
                    InlineKeyboardButton("Não", callback_data='2'),
                ]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)

            bot.sendPhoto(
                chat_id = update.effective_chat.id,
                photo = animal["images"][0]
            )
            bot.sendMessage(
                chat_id = update.effective_chat.id,
                text = "Você encontrou ese animal?",
                reply_markup = reply_markup
            )

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer

    choice = query.data

    if choice != "2":
        post_collection.insert_one({
            "id_post" : choice,
            "user_id" : update.message.from_user.id
        })


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
        CommandHandler('post', post)
    )
    dispatcher.add_handler(
        CommandHandler('near_animals', show_animals_close_by)
    )

    dispatcher.add_handler(
        CallbackQueryHandler(button)
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