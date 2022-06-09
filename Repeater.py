import telebot
import config

bot = telebot.TeleBot(config.TOKEN)

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "Рад вас видеть, располагайтесь, {0.first_name}!\nЯ - <b>{1.first_name}</b>, бот, созданный для тестов")

@bot.message_handler(content_types=['text'])
def repeater(message):
    bot.send_message(message.chat.id, message.text)


# RUN
bot.polling(none_stop=True)