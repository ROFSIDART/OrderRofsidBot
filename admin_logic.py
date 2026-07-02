import os; import time; import threading
from dotenv import load_dotenv
import telebot; from telebot import TeleBot, types
import ru_text

BOT_TOKEN = os.getenv('BOT_TOKEN')
PROXY_URL = os.getenv('PROXY_URL')
ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID'))

MyBot = TeleBot(BOT_TOKEN)
telebot.apihelper.proxy = {'https': PROXY_URL}

requestBtn1 = types.InlineKeyboardButton('Запросы', callback_data='callOrder')
requestBtn2 = types.InlineKeyboardButton('Меню', callback_data='callMenu')
requestBtn3 = types.InlineKeyboardButton('Арт', callback_data='callArt')
# requestBtn4 = types.InlineKeyboardButton('3д', callback_data='')
# requestBtn5 = types.InlineKeyboardButton('Боты', callback_data='')
# requestBtn6 = types.InlineKeyboardButton('Сайты', callback_data='')
Btn = {}
#Чтото не так. мб заменить на кнопки внизу в меню?