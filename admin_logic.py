import os; import time; import threading
from dotenv import load_dotenv
import telebot; from telebot import TeleBot, types

BOT_TOKEN = os.getenv('BOT_TOKEN')
PROXY_URL = os.getenv('PROXY_URL')
ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID'))

MyBot = TeleBot(BOT_TOKEN)
telebot.apihelper.proxy = {'https': PROXY_URL}

menuBtn = types.InlineKeyboardButton('Меню', callback_data='callMenu')
orderListBtn = types.InlineKeyboardButton('Запросы', callback_data='callOrder')
artListBtn = types.InlineKeyboardButton('Арт', callback_data='callArt')
refuseBtn = types.InlineKeyboardButton('Отказ', callback_data='')
# requestBtn4 = types.InlineKeyboardButton('3д', callback_data='')
# requestBtn5 = types.InlineKeyboardButton('Боты', callback_data='')
# requestBtn6 = types.InlineKeyboardButton('Сайты', callback_data='')
Btn = {0: menuBtn, 1: orderListBtn, 2:artListBtn, 3:refuseBtn}

@MyBot.message_handler()
def main(message):
    chat_id = message.chat.id
    # if text == '/start'