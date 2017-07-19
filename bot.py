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
    send_command_message(message, "（逃")


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
            bot.send_message(message.chat.id, "请先设置自述")


def check_me_status(user_id):
    db = sqlite3.connect('~/Bot/data/bot_me.db')
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
    db = sqlite3.connect('~/Bot/data/bot_me.db')
    cursor = db.cursor()
    cursor.execute('''INSERT INTO introduction(id, message) VALUES(?,?)''', (user_id, message))
    db.commit()
    db.close()


def update_introduction(user_id, message):
    db = sqlite3.connect('~/Bot/data/bot_me.db')
    cursor = db.cursor()
    cursor.execute('''UPDATE introduction SET message=? WHERE id=? ''', (message, user_id))
    db.commit()
    db.close()


def read_introduction(user_id):
    db = sqlite3.connect('~/Bot/data/bot_me.db')
    cursor = db.cursor()
    cursor.execute('''SELECT message FROM introduction WHERE id=? ''', (user_id,))
    message = cursor.fetchone()[0]
    db.close()
    return message


def create_introduction():
    db = sqlite3.connect('~/Bot/data/bot_me.db')
    cursor = db.cursor()
    if cursor.execute('''SELECT count(*) FROM sqlite_master WHERE type=? AND name=? ''', ("table", "introduction")).fetchone()[0] is 0:
        cursor.execute('''CREATE TABLE introduction(id INTEGER, message TEXT)''')
        db.commit()
    db.close()


bot.polling()
