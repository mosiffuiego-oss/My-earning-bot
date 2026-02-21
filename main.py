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
def home(): 
    return "<b>Bot Status:</b> Online and Running on Render!"

def run(): 
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- DATABASE MANAGEMENT ---
def load_data():
    if not os.path.exists('users.json'): 
        return {}
    try:
        with open('users.json', 'r') as f: 
            return json.load(f)
    except Exception as e:
        print(f"Error loading data: {e}")
        return {}

def save_data(data):
    try:
        with open('users.json', 'w') as f: 
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving data: {e}")

# --- START COMMAND ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.chat.id)
    first_name = message.from_user.first_name
    data = load_data()
    
    if uid not in data:
        # REFER SYSTEM (20 RS PER REFER)
        ref_by = message.text.split()[1] if len(message.text.split()) > 1 else None
        data[uid] = {
            'bal': 0, 
            'invited': 0, 
            'last_ad': 0, 
            'last_bonus': 0,
            'joined_at': time.ctime()
        }
        
        if ref_by and ref_by in data and ref_by != uid:
            data[ref_by]['bal'] += 20  # SET TO 20 RS
            data[ref_by]['invited'] += 1
            bot.send_message(ref_by, f"🔔 <b>New Referral!</b>\nCongratulations, you earned <b>20 Rs</b>.", parse_mode="html")
        
        save_data(data)
        bot.send_message(ADMIN_ID, f"🆕 New User Joined: {first_name} ({uid})")

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("💰 Balance", "🔗 Invite")
    markup.add("📺 Watch Ad", "🎁 Daily Bonus")
    markup.add("🏧 Withdraw")
    
    welcome_text = (
        f"👋 Hello {first_name}!\n\n"
        f"Welcome to <b>MoneyTarbo Earning Bot</b>\n\n"
        f"🚀 <b>Invite:</b> 20 Rs\n"
        f"🎁 <b>Daily Bonus:</b> 5 Rs\n"
        f"🏧 <b>Withdraw:</b> 250 Rs\n\n"
        f"Click on the buttons below to start earning!"
    )
    bot.send_message(uid, welcome_text, reply_markup=markup, parse_mode="html")

# --- MAIN BUTTON LOGIC ---
@bot.message_handler(func=lambda m: True)
def handle_text(message):
    uid = str(message.chat.id)
    data = load_data()
    
    if uid not in data:
        data[uid] = {'bal': 0, 'invited': 0, 'last_ad': 0, 'last_bonus': 0}

    if message.text == "💰 Balance":
        bal = data[uid].get('bal', 0)
        inv = data[uid].get('invited', 0)
        bot.send_message(uid, f"📊 <b>Your Account Details:</b>\n\n💳 Balance: <b>{bal} Rs</b>\n👥 Total Invites: <b>{inv} Users</b>", parse_mode="html")

    elif message.text == "🔗 Invite":
        bot_username = bot.get_me().username
        ref_link = f"https://t.me/{bot_username}?start={uid}"
        invite_msg = (
            f"🎁 <b>Invite & Earn System</b>\n\n"
            f"Share your referral link with friends. When they join, you get <b>20 Rs</b> instantly!\n\n"
            f"🔗 <b>Your Link:</b>\n{ref_link}"
        )
        bot.send_message(uid, invite_msg, parse_mode="html")

    elif message.text == "📺 Watch Ad":
        now = time.time()
        last_ad = data[uid].get('last_ad', 0)
        if now - last_ad > 60: # 1 Minute cooldown
            data[uid]['bal'] += 2
            data[uid]['last_ad'] = now
            save_data(data)
            bot.send_message(uid, "✅ <b>Ad Watched!</b>\nYou earned <b>2 Rs</b>. Come back after 1 minute for more.", parse_mode="html")
        else:
            wait_time = int(60 - (now - last_ad))
            bot.send_message(uid, f"⏳ <b>Wait!</b>\nPlease wait <b>{wait_time} seconds</b> before watching another ad.", parse_mode="html")

    elif message.text == "🎁 Daily Bonus":
        now = time.time()
        last_bonus = data[uid].get('last_bonus', 0)
        if now - last_bonus > 86400: # 24 Hours
            data[uid]['bal'] += 5
            data[uid]['last_bonus'] = now
            save_data(data)
