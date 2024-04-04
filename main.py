import telebot
from telebot import types
import requests
import io

API_TOKEN = '7149116198:AAGovPsxWSiwMHrPeSKSbhbgoewM4QoeF48'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item_start = types.KeyboardButton("/start")
    markup.add(item_start)
    bot.send_message(message.chat.id, "Пришлите мне ссылку на файл, и я отправлю его вам.", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Проверка типа контента
        content_type = response.headers.get('Content-Type')
        if not content_type or not content_type.startswith('application/'):
            bot.reply_to(message, "Ссылка не ведет к файлу.")
            return
      
        file_name = url.split('/')[-1]
        # Создаем BytesIO объект и устанавливаем его имя
        file_content = io.BytesIO()
        file_content.name = file_name
        for chunk in response.iter_content(chunk_size=8192):
            if chunk: # filter out keep-alive new chunks
                file_content.write(chunk)
        file_content.seek(0)
        
        # Отправляем сообщение со смайликом загрузки
        bot.send_message(message.chat.id, "🔄 Загрузка файла...")
        
        # Отправляем файл
        bot.send_document(chat_id=message.chat.id, document=file_content)
    except requests.exceptions.RequestException as e:
        bot.reply_to(message, f"Ошибка при загрузке файла: {e}")

if __name__ == '__main__':
    bot.polling()
