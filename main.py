import telebot
import json
import os
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

# --- DATABASE ---
def load_data():
    if not os.path.exists('users.json'): return {}
    try:
        with open('users.json', 'r') as f: return json.load(f)
    except: return {}

def save_data(data):
    with open('users.json', 'w') as f: json.dump(data, f, indent=4)

# --- COMMANDS ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.chat.id)
    first_name = message.from_user.first_name
    data = load_data()
    
    # Refer System Logic
    if uid not in data:
        ref_by = message.text.split()[1] if len(message.text.split()) > 1 else None
        data[uid] = {'bal': 0, 'invited': 0}
        
        if ref_by and ref_by in data and ref_by != uid:
            data[ref_by]['bal'] += 20  # REFER AMOUNT: 20 RS
            data[ref_by]['invited'] += 1
            bot.send_message(ref_by, f"🔔 New Referral! You earned 20 Rs.")
        
        save_data(data)
    
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("💰 Balance", "🔗 Invite")
    markup.add("📺 Watch Ad", "🎁 Daily Bonus")
    markup.add("🏧 Withdraw")
    bot.send_message(uid, f"Hello {first_name}! Welcome to MoneyTarbo 💰", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    uid = str(message.chat.id)
    data = load_data()
    if uid not in data: data[uid] = {'bal': 0, 'invited': 0}

    if message.text == "💰 Balance":
        bot.send_message(uid, f"💳 Your Balance: {data[uid]['bal']} Rs\n👥 Total Invites: {data[uid]['invited']}")
