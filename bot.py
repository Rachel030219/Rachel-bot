# coding=utf-8

import telebot
import random
import sqlite3

bot = telebot.TeleBot("<TOKEN>")


@bot.message_handler(commands=['start'])
def send_start(message):
    send_command_message(message, "我是人型自走机器人 Rachel ，你就是我的 master 吗？")


@bot.message_handler(commands=['help'])
def send_help(message):
    send_command_message(message, "/me <content> 告诉 Rachel 你的自述\n/whois 回复一条消息，让 Rachel 告诉你 TA 的自述")


@bot.message_handler(commands=['prpr'])
def send_prpr(message):
    if random.random() > 0.7:
        send_command_message(message, "才不让呢（")
    else:
        send_command_message(message, "Permission denied.")


@bot.message_handler(regexp="Rikka", func=lambda message: random.random() > 0.9)
def send_prpr(message):
    bot.send_message(message.chat.id, "prpr Rikka")


@bot.message_handler(commands=['me'])
def send_me(message):
    list_split_by_me = message.text.split("me ")
    if "group" in message.chat.type:
        if "@Rachel_bot " in message.text:
            send_me_message(message, message.from_user.first_name + u" 自述:", message.text.split("@Rachel_bot "))
        else:
            send_me_message(message, message.from_user.first_name + u" 自述:", list_split_by_me)
    else:
        send_me_message(message, message.from_user.first_name + u" 自述:", list_split_by_me)


@bot.message_handler(func=lambda message: True, content_types=['new_chat_members'])
def send_welcome(message):
    if "group" in message.chat.type:
        if message.new_chat_member.username is None or "Rachel_bot" not in message.new_chat_member.username:
            name = message.new_chat_member.first_name
            id = message.new_chat_member.id
            if check_me_status(id):
                bot.reply_to(message, u"你就是自称「" + read_introduction(id) + u"」的 " + name + u" 吗？")
            else:
                bot.reply_to(message, name + u" 是一副新面孔呢，快告诉大家你是谁吧")


@bot.message_handler(commands=['whois'])
def send_query(message):
    if message.reply_to_message is not None:
        user_id = message.reply_to_message.from_user.id
        if check_me_status(user_id):
            bot.send_message(message.chat.id, message.reply_to_message.from_user.first_name + u" 的自述是：" + read_introduction(user_id))
        else:
            bot.send_message(message.chat.id, message.reply_to_message.from_user.first_name + u" 还没有设置自述（")
    else:
        bot.send_message(message.chat.id, u"这条命令正确的食用方法是单独回复一条消息（")


@bot.message_handler(func=lambda message: "group" in message.chat.type, regexp="#OFF_TOPIC")
def send_off_topic(message):
    if message.reply_to_message is not None:
        bot.reply_to(message.reply_to_message, "您所讨论的内容可能已超出本群讨论范围，或者您违反了本群的相关规定。请至其它群组寻求帮助并进行讨论。")
    else:
        bot.send_message(message.chat.id, "您所讨论的内容可能已超出本群讨论范围，或者您违反了本群的相关规定。请至其它群组寻求帮助并进行讨论。")


def send_command_message(message, text):
    if "group" in message.chat.type:
        if "@Rachel_bot" in message.text:
            bot.reply_to(message, text)
    else:
        bot.reply_to(message, text)


def send_me_message(message, prefix, message_list):
    user_id = message.from_user.id
    if message_list is not None and len(message_list) > 1:
        if check_me_status(user_id):
            update_introduction(user_id, message_list[1])
        else:
            insert_introduction(user_id, message_list[1])
        bot.send_message(message.chat.id, prefix + message_list[1])
    else:
        if check_me_status(user_id):
            bot.send_message(message.chat.id, prefix + read_introduction(user_id))
        else:
            bot.send_message(message.chat.id, "请先设置自述（")


def check_me_status(user_id):
    db = sqlite3.connect('/home/rachel/Bot/data/bot_me.db')
    create_introduction()
    cursor = db.cursor()
    cursor.execute('''SELECT id FROM introduction''')

    for row in cursor.fetchall():
        if user_id == row[0]:
            db.close()
            return True
    db.close()
    return False


def insert_introduction(user_id, message):
    db = sqlite3.connect('/home/rachel/Bot/data/bot_me.db')
    cursor = db.cursor()
    cursor.execute('''INSERT INTO introduction(id, message) VALUES(?,?)''', (user_id, message))
    db.commit()
    db.close()


def update_introduction(user_id, message):
    db = sqlite3.connect('/home/rachel/Bot/data/bot_me.db')
    cursor = db.cursor()
    cursor.execute('''UPDATE introduction SET message=? WHERE id=? ''', (message, user_id))
    db.commit()
    db.close()


def read_introduction(user_id):
    db = sqlite3.connect('/home/rachel/Bot/data/bot_me.db')
    cursor = db.cursor()
    cursor.execute('''SELECT message FROM introduction WHERE id=? ''', (user_id,))
    message = cursor.fetchone()[0]
    db.close()
    return message


def create_introduction():
    db = sqlite3.connect('/home/rachel/Bot/data/bot_me.db')
    cursor = db.cursor()
    if cursor.execute('''SELECT count(*) FROM sqlite_master WHERE type=? AND name=? ''', ("table", "introduction")).fetchone()[0] is 0:
        cursor.execute('''CREATE TABLE introduction(id INTEGER, message TEXT)''')
        db.commit()
    db.close()


bot.polling()
