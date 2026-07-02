import os
import time
import threading
from dotenv import load_dotenv
import telebot
from telebot import TeleBot, types
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
PROXY_URL = os.getenv('PROXY_URL')
ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID'))

MyBot = TeleBot(BOT_TOKEN)
telebot.apihelper.proxy = {'https': PROXY_URL}

request = {0: '/start', 1: '/art', 2: '/3dmodel', 3: '/website', 4: '/bot', 5: '/other', 6: '/adressto', 7: '/help', 8: '/info'}

temporary_orders = {}
user_states = {}
media_groups_cache = {} 
media_groups_lock = threading.Lock()


#button for usrer
requestBtn1 = types.InlineKeyboardButton('Арт',  callback_data='orderArt')
requestBtn2 = types.InlineKeyboardButton('3d модель',  callback_data='order3D')
requestBtn3 = types.InlineKeyboardButton('Вебсайт',  callback_data='orderWEB')
requestBtn4 = types.InlineKeyboardButton('Бот',  callback_data='orderBOT') 
requestBtn5 = types.InlineKeyboardButton('Реклама',  callback_data='callOther')
requestBtn6 = types.InlineKeyboardButton('Другое',  callback_data='callOther')
exitBtn = types.InlineKeyboardButton('Назад', callback_data='callExitBtn')
yesBtn = types.InlineKeyboardButton('Отправить', callback_data='callYesBtn')
canseledBtn = types.InlineKeyboardButton('Отменить', callback_data='callСanseledBtn')
repeatBtn = types.InlineKeyboardButton('Нет, переделать', callback_data='callRepeatBtn')

#Button for admin
seeBtn = types.InlineKeyboardButton('Посмотреть', callback_data='callSeeBtn')

Btn = {0: exitBtn, 1: requestBtn1, 2: requestBtn2, 3: requestBtn3, 4: requestBtn4, 5: requestBtn5, 6: requestBtn6, 11: seeBtn, 12: menuBtn}

#button group
def get_menu_markup():
    markup = types.InlineKeyboardMarkup()
    markup.row(Btn[1], Btn[2], Btn[3], Btn[4])
    markup.row(Btn[5], Btn[6])
    return markup
def get_order_markup(send_type):
    markup = types.InlineKeyboardMarkup()
    sendBtn = types.InlineKeyboardButton('Написать ...', callback_data=f'send_{send_type}',)
    markup.row(Btn[0], sendBtn)
    return markup

def get_exit_markup():
    markup = types.InlineKeyboardMarkup()
    markup.row(Btn[0])
    return markup

@MyBot.message_handler()
def main(message):
    chat_id = message.chat.id
    if chat_id in user_states and user_states[chat_id].get('state') == 'waiting_for_order':
        handle_order_message(message)
        return
    if not message.text:
        return
    text = message.text.lower()

    if  text == request[0]:
        MyBot.send_message(chat_id, text=welcomeText(message.from_user.first_name), parse_mode='html', reply_markup=get_menu_markup())
    elif text == request[1]:
        MyBot.send_message(chat_id, text=artText, parse_mode='html', reply_markup=get_order_markup('art'))
    elif text == request[5]:
        MyBot.send_message(chat_id, text=otherText, parse_mode='html', reply_markup=get_order_markup('other'))
    elif text in [request[2], request[3], request[4]]:
        MyBot.send_message(chat_id, text=noText, reply_markup=get_exit_markup())
    elif text == request[6]:
        sentMsg = MyBot.send_message(chat_id, "<em><b>ВАЖНО:</b> Если ваши файлы отправляются по отдельности,"
         "вы можете отправить их ссылкой в самом сообщении, если они хранятся где либо, или архивом, иначе до Софии может просто не дойти то," 
         "что было отправлено следующим сообщением.</em>\n<b>Внимание!</b> Следующее ваше сообщение будет отправлено автору."
         "\nПожалуйста, напишите ваш запрос, контактные данные и прикрепите файлы (картинка, архив и пр.) в ОДНОМ сообщении:", parse_mode='html', reply_markup=get_exit_markup())
        user_states[chat_id] = {'state': 'waiting_for_order', 'user_order_id': 'Напрямую'}

    elif text == request[7]:
        MyBot.send_message(chat_id, text=helpText, reply_markup=get_exit_markup())
    elif text == request[8]:
        MyBot.send_message(chat_id, text=infoText, parse_mode='html', reply_markup=get_exit_markup())



@MyBot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id

#bullon button go
    if callback.data == 'orderArt':
        MyBot.edit_message_text(chat_id=chat_id, message_id=message_id, text=artText, parse_mode='html', reply_markup=get_order_markup('art'))

    elif callback.data in ['callExitBtn', 'callСanseledBtn']:
        if chat_id in temporary_orders and chat_id in user_states: 
            del temporary_orders[chat_id]
            del user_states[chat_id]

        MyBot.edit_message_text(chat_id=chat_id, message_id=message_id, text=welcomeText(callback.from_user.first_name), parse_mode='html', reply_markup=get_menu_markup())

    elif callback.data in ['order3D', 'orderWEB', 'orderBOT']:
        MyBot.edit_message_text(chat_id=chat_id, message_id=message_id, text=noText, reply_markup=get_exit_markup())

    elif callback.data == 'callOther':
        MyBot.edit_message_text(chat_id=chat_id, message_id=message_id, text=otherText, parse_mode='html', reply_markup=get_order_markup('other'))

    elif callback.data == 'callRepeatBtn':
        if chat_id in temporary_orders:
            user_order_id = temporary_orders[chat_id]['user_order_id']
            MyBot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=None)
            sentMsg = MyBot.send_message(chat_id, "Хорошо, давайте переделаем. Напишите ваш запрос заново в ОДНОМ сообщении:")
            user_states[chat_id] = {'state': 'waiting_for_order', 'user_order_id': user_order_id}

    elif callback.data == 'callYesBtn': 
        if chat_id in temporary_orders:
            data = temporary_orders[chat_id]
            admin_message = (
                f"🚨<b>Новый запрос. Тип:</b> {data['user_order_id']}\n"
                f"<b>От:</b> {data['user_name']} ({data['user_username']})\n"
                f"<b>ID пользователя:</b> <code>{data['user_id']}</code>\n\n"
                f"<b>Текст обращения:</b>\n{data['order_text']}"
            )
            MyBot.send_message(ADMIN_CHAT_ID, admin_message, parse_mode='html')

            if data['content_type'] == 'photo':
                MyBot.send_photo(ADMIN_CHAT_ID, photo=data['file_id'], caption=admin_message, parse_mode='html')
            elif data['content_type'] == 'document':
                MyBot.send_document(ADMIN_CHAT_ID, document=data['file_id'], caption=admin_message, parse_mode='html')
            else:
                MyBot.send_message(ADMIN_CHAT_ID, admin_message, parse_mode='html')
                
            MyBot.send_message(chat_id, "🎉 Ваш запрос успешно отправлен! В скором времени София свяжется с вами, чтобы подтвердить запрос...", reply_markup=get_exit_markup())
            del temporary_orders[chat_id]

    elif callback.data.startswith('send_'):
        MyBot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=None)

        sentMsg = MyBot.send_message(chat_id, "<em><b>ВАЖНО:</b> Если ваши файлы отправляются по отдельности,"
         "вы можете отправить их ссылкой если они хранятся где либо, или архивом, иначе до Софии может просто не дойти то," 
         "что было отправлено следующим сообщением.</em>\n<b>Внимание!</b> Следующее ваше сообщение будет отправлено автору."
         "\nПожалуйста, напишите ваш запрос, контактные данные и прикрепите файлы (картинка, архив и пр.) в ОДНОМ сообщении:", parse_mode='html', reply_markup=get_exit_markup())

        order_type = callback.data.split('_')[1]
        user_order_id = '#Арт' if order_type == 'art' else '#Другое'
        user_states[chat_id] = {'state': 'waiting_for_order', 'user_order_id': user_order_id}

def handle_order_message(message):
    chat_id = message.chat.id
    user_order_id = user_states[chat_id]['user_order_id']
    if message.text and message.text.startswith('/'):
        del user_states[chat_id]
        MyBot.send_message(message.chat.id, "❌ Оформление заказа отменено.", reply_markup=get_menu_markup())
        return
def ask_confirmation(message, user_order_id):
    user_text = message.text or message.caption

    
    content_type = message.content_type 
    file_id = None
    order_text = ""

    if content_type == 'text':
        order_text = message.text
    elif content_type == 'photo':
        file_id = message.photo[-1].file_id
        order_text = message.caption or "[Фото без описания]"
    elif content_type == 'document':
        file_id = message.document.file_id
        order_text = message.caption or "[Файл/Архив без описания]"


    temporary_orders[message.chat.id] = {
        'user_order_id': user_order_id,
        "user_name" : message.from_user.first_name,
        "user_username" : f"@{message.from_user.username}" if message.from_user.username else "Нет юзернейма",
        "user_id" : message.from_user.id,
        "order_text" : order_text,
        "content_type": content_type,
        "file_id": file_id
    }
    markup = types.InlineKeyboardMarkup()
    markup.row(canseledBtn, repeatBtn, yesBtn,)
    
    preview_text = (
        f"<b>Проверьте ваш запрос ({user_order_id}):</b>\n\n"
        f"<i>{temporary_orders[message.chat.id]['order_text']}</i>\n\n"
        f"Вы уверены, или хотите переделать?"
    )

    if content_type == 'photo':
        MyBot.send_photo(message.chat.id, photo=file_id, caption=preview_text, reply_markup=markup, parse_mode='html')
    elif content_type == 'document':
        MyBot.send_document(message.chat.id, document=file_id, caption=preview_text, reply_markup=markup, parse_mode='html')
    else:
        MyBot.send_message(message.chat.id, text=preview_text, reply_markup=markup, parse_mode='html')
    
MyBot.polling(none_stop=True)