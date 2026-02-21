import telebot
import json
import os
import time
from flask import Flask
from threading import Thread

# --- CONFIGURATION ---
API_TOKEN = '8052478407:AAHgn5heLnCixh1PUXG-8sSiL8brigtO5fM'  
ADMIN_ID = 6130849132 

bot = telebot.TeleBot(API_TOKEN)
app = Flask('')

@app.route('/')
def home(): return "Bot is Online"

def run(): app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "✅ Bot is working perfectly on Render!")

if __name__ == "__main__":
    keep_alive()
    print("Bot is starting...")
    bot.polling(none_stop=True)
