import os

import telebot


bot = telebot.TeleBot(os.getenv("BOT_TOKEN"), skip_pending=True)


@bot.message_handler(content_types=["new_chat_members"])
def hello(message):
    for new_user in message.new_chat_members:
        user_id = new_user.id
        user_name = new_user.first_name
        mention = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
        hello_text = "Пожалуйста напиши рассказ #осебе"
        instruction_message = "Добро пожаловать в чат {}!\n{}".format(
            mention, hello_text
        )
        bot.send_message(
            message.chat.id,
            message_thread_id=message.message_thread_id,
            text=instruction_message,
            parse_mode="Markdown",
        )


def main():
    bot.infinity_polling(allowed_updates=telebot.util.update_types)


if __name__ == "__main__":
    main()
