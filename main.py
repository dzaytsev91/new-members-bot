import os
import sqlite3
from datetime import datetime, timedelta
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

import telebot


bot = telebot.TeleBot(os.getenv("BOT_TOKEN"), skip_pending=True)
bot.set_my_commands(
    [
        telebot.types.BotCommand("/stat", "show messages statistic"),
    ]
)

conn = sqlite3.connect("katty.db", check_same_thread=False)
conn.execute(
    "CREATE TABLE IF NOT EXISTS user_messages (user_id int, username string, text string, message_id int, created_at timestamp);"
)

matplotlib.use("agg")
matplotlib.rc("figure", figsize=(20, 5))


def decl(number: int, titles: list):
    cases = [2, 0, 1, 1, 1, 2]
    if 4 < number % 100 < 20:
        idx = 2
    elif number % 10 < 5:
        idx = cases[number % 10]
    else:
        idx = cases[5]

    return titles[idx]


@bot.message_handler(commands=["stat"])
def get_statistic(message):
    seven_days_ago = datetime.now() - timedelta(days=14)
    query = "select date(created_at), count(*) from user_messages WHERE created_at > ? group by date(created_at) order by date(created_at);"
    rows = conn.execute(query, (seven_days_ago,)).fetchall()
    date_time = []
    data = []
    for row in rows:
        date_time.append(row[0])
        data.append(row[1])

    date_time = pd.to_datetime(date_time)
    df = pd.DataFrame()
    df["value"] = data
    df = df.set_index(date_time)
    plt.plot(df, **{"marker": "o"})
    plt.gcf().autofmt_xdate()
    plt.title("Messages count")
    plt.grid()
    plt.savefig("test.png", dpi=300)
    plt.close()
    with open("test.png", "rb") as f:
        content = f.read()
    return bot.send_photo(
        message.chat.id,
        message_thread_id=message.message_thread_id,
        photo=content,
    )


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


@bot.message_handler(
    content_types=[
        "text",
    ]
)
def handle_message(message):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO user_messages (user_id, username, text, message_id, created_at) VALUES(?, ?, ?, ?, ?) ON CONFLICT DO NOTHING",
        (
            message.from_user.id,
            message.from_user.username,
            message.text,
            message.id,
            datetime.now(),
        ),
    )
    conn.commit()


def main():
    bot.infinity_polling(allowed_updates=telebot.util.update_types)


if __name__ == "__main__":
    main()
