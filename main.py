import telebot
import json
import os
import time
from flask import Flask
from threading import Thread

# --- CONFIGURATION ---
API_TOKEN = '8052478407:AAHgn5heLnCixh1PUXG-8sSiL8brigtO5fM'  
ADMIN_ID = 6130849132 

# 📢 Links
CH_ID = '@onlineincome_x' 
CH_LINK = 'https://t.me/onlineincome_x'
GP_ID = '@moneymakersboys'
GP_LINK = 'https://t.me/moneymakersboys'

bot = telebot.TeleBot(API_TOKEN)
app = Flask('')

# --- DATABASE ---
def load_data():
    if not os.path.exists('users.json'): return {}
    try:
        with open('users.json', 'r') as f: return json.load(f)
    except: return {}

def save_data(data):
    with open('users.json', 'w') as f: json.dump(data, f, indent=4)

# --- UPTIME SERVER ---
@app.route('/')
def home(): return "<h1>Bot is Running 24/7 on Render</h1>"

def run(): app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- DOUBLE JOIN CHECK ---
def check_join(user_id):
    try:
        ch_member = bot.get_chat_member(CH_ID, user_id)
        gp_member = bot.get_chat_member(GP_ID, user_id)
        status = ['member', 'administrator', 'creator']
        return ch_member.status in status and gp_member.status in status
    except: return False

# --- START & REFER SYSTEM ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.chat.id)
    data = load_data()
    
    if uid not in data:
        referrer = None
        if len(message.text.split()) > 1:
            referrer = message.text.split()[1]
        
        data[uid] = {'bal': 0, 'last_ad': 0, 'last_bonus': 0, 'referred_by': referrer}
        
        if referrer and referrer in data and referrer != uid:
            data[referrer]['bal'] += 10 
            try:
                bot.send_message(referrer, f"🎊 **New Referral!**\nAapko milte hain **10 Rs**
