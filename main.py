import keep_alive
import os
import telebot
import sqlite3

conn = sqlite3.connect('test.db')
conn.execute('''CREATE TABLE IF NOT EXISTS REMINDERS
         (ID INTEGER PRIMARY KEY AUTOINCREMENT  NOT NULL,
         NAME           TEXT     NOT NULL,
         MESSAGE        TEXT     NOT NULL);''')
conn.close()

def showtable():
  conn = sqlite3.connect('test.db')
  cursor = conn.execute("SELECT NAME, MESSAGE from REMINDERS")
  print("current db now:")
  for row in cursor:
    print("NAME = " + row[0])
    print("MESSAGE = " + row[1])
  conn.close()

API_KEY = os.environ['API_KEY']
bot = telebot.TeleBot(API_KEY)

@bot.message_handler(commands=['help'])
def help(message):
  bot.send_message(message.chat.id, "use /add (your reminder) to add a reminder")
  bot.send_message(message.chat.id, "use /view to view all your current reminders")
  bot.send_message(message.chat.id, "use /del (number) to remove a reminder *Note: number is the index of your reminder")

@bot.message_handler(commands=['start'])
def start(message):
  bot.send_message(message.chat.id, "Hello " + str(message.chat.first_name) + "! This is a simple bot to help you keep track of your reminders! (Created by: Ivan Lim)")
  bot.send_message(message.chat.id, "Use /help to learn how to use this simple reminder bot!")

@bot.message_handler(commands=['view'])
def view(message):
  name = str(message.chat.first_name)
  conn = sqlite3.connect('test.db')
  cursor = conn.execute("SELECT MESSAGE from REMINDERS where NAME=(?)", (name,)).fetchall()
  if len(cursor) == 0:
    bot.send_message(message.chat.id, "You have no reminders at the moment :)")
  else:
    bot.send_message(message.chat.id, "CURRENT REMINDERS:")
    counter = 1
    for row in cursor:
      bot.send_message(message.chat.id, str(counter) + ". " + ''.join(row))
      counter+=1;
  conn.close()

def add_reminder(message):
  request = message.text[1:4]
  if request.lower() == "add":
    return True
  else:
    return False

@bot.message_handler(func=add_reminder)
def update_db(message):
  reminder = message.text[5:]
  if len(reminder.strip()) > 0:
    name = str(message.chat.first_name)
    conn = sqlite3.connect('test.db')
    conn.execute("INSERT INTO REMINDERS (NAME, MESSAGE) \
        VALUES (?, ?)", (name, reminder,));
    conn.commit()
    conn.close()
    bot.send_message(message.chat.id, "Reminder added: " + reminder)
  else:
    bot.send_message(message.chat.id, "Why would you want a reminder for nothing?")

def del_reminder(message):
  request = message.text[1:4]
  if request.lower() == "del":
    return True
  else:
    return False

@bot.message_handler(func=del_reminder)
def del_from_db(message):
  name = str(message.chat.first_name)
  conn = sqlite3.connect('test.db')
  cursor = conn.execute("SELECT MESSAGE from REMINDERS where NAME=(?)", (name,)).fetchall()
  if message.text[5:].isdigit():
      if int(message.text[5:]) > 0 and int(message.text[5:]) <= len(cursor):
        count = int(message.text[5:])
        reminder = ''.join(cursor[count-1])
        conn.execute("DELETE FROM REMINDERS WHERE NAME=(?) AND MESSAGE=(?)", (name, reminder,));
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, "Reminder deleted: " + reminder)
      else:
        bot.send_message(message.chat.id, "Please enter an index that is provided in the /view list")
  else:
    bot.send_message(message.chat.id, "Please enter the index of the reminder(the index is the number to the left of your specific reminder in the /view list)")

keep_alive.keep_alive()
bot.polling()