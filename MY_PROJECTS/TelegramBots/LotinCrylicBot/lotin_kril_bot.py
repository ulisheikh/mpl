from transliterate import to_cyrillic, to_latin
import telebot

TOKEN = "8046330769:AAGmBYC8ojb_rOkz863Z4nOvVbbo1-6Y2so"
bot = telebot.TeleBot(TOKEN, parse_mode=None)


@bot.message_handler(commands=["start"])
def welcome(message):
    javob = "Assalomu alykum\nMatn kiriting:"
    bot.reply_to(message, javob)


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    msg = message.text
    javob = lambda msg: to_cyrillic(msg) if msg.isascii() else to_latin(msg)
    # if msg.isascii():
    #     msg = to_cyrillic(msg)
    # else:
    #     msg = to_latin(msg)

    bot.reply_to(message, javob(msg))


bot.polling()


# matn = input("Matn kiriting:\n>>> ")
# if matn.isascii():
#     print(to_cyrillic(matn))
# else:
#     print(to_latin(matn))
