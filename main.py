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

# --- DATABASE ---
def load_data():
    if not os.path.exists('users.json'): return {}
    try:
        with open('users.json', 'r') as f: return json.load(f)
    except: return {}

def save_data(data):
    with open('users.json', 'w') as f: json.dump(data, f, indent=4)

# --- START COMMAND ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.chat.id)
    first_name = message.from_user.first_name
    data = load_data()
    
    if uid not in data:
        # REFER LOGIC (20 RS)
        ref_by = message.text.split()[1] if len(message.text.split()) > 1 else None
        data[uid] = {'bal': 0, 'invited': 0, 'last_ad': 0, 'last_bonus': 0}
        
        if ref_by and ref_by in data and ref_by != uid:
            data[ref_by]['bal'] += 20  # SET TO 20 RS
            data[ref_by]['invited'] += 1
            bot.send_message(ref_by, f"🔔 New Referral! You earned 20 Rs.")
        save_data(data)
    
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("💰 Balance", "🔗 Invite")
    markup.add("📺 Watch Ad", "🎁 Daily Bonus")
    markup.add("🏧 Withdraw")
    bot.send_message(uid, f"Welcome {first_name} to MoneyTarbo! 💰\nEarn 20 Rs per invite.", reply_markup=markup)

# --- BUTTON HANDLING ---
@bot.message_handler(func=lambda m: True)
def handle_text(message):
    uid = str(message.chat.id)
    data = load_data()
    if uid not in data: data[uid] = {'bal': 0, 'invited': 0, 'last_ad': 0, 'last_bonus': 0}

    if message.text == "💰 Balance":
        bot.send_message(uid, f"💳 Your Balance: {data[uid]['bal']} Rs\n👥 Total Invites: {data[uid]['invited']}")

    elif message.text == "🔗 Invite":
        ref_link = f"https://t.me/{(bot.get_me()).username}?start={uid}"
        bot.send_message(uid, f"🎁 Share link & earn 20 Rs per refer!\n\nYour Link: {ref_link}")

    elif message.text == "📺 Watch Ad":
        now = time.time()
        if now - data[uid].get('last_ad', 0) > 30: # 30 SEC COOLDOWN
            data[uid]['bal'] += 2
            data[uid]['last_ad'] = now
            save_data(data)
            bot.send_message(uid, "✅ You watched an ad and earned 2 Rs!")
        else:
            bot.send_message(uid, "⏳ Wait 30 seconds for next ad.")

    elif message.text == "🎁 Daily Bonus":
        now = time.time()
        if now - data[uid].get('last_bonus', 0) > 86400: # 24 HOURS
            data[uid]['bal'] += 5
            data[uid]['last_bonus'] = now
            save_data(data)
            bot.send_message(uid, "🎁 Daily Bonus of 5 Rs Added!")
        else:
            bot.send_message(uid, "❌ Come back tomorrow for bonus.")

    elif message.text == "🏧 Withdraw":
        if data[uid]['bal'] >= 250: # SET TO 250 RS
            msg = bot.send_message(uid, "📤 Send your UPI ID & Amount (Ex: abc@ybl 250):")
            bot.register_next_step_handler(msg, process_withdraw)
        else:
            bot.send_message(uid, "❌ Minimum withdrawal is 250 Rs.")

def process_withdraw(message):
    bot.send_message(message.chat.id, "✅ Withdrawal request sent to Admin!")
    bot.send_message(ADMIN_ID, f"🔔 NEW WITHDRAWAL:\nUser: {message.chat.id}\nDetails: {message.text}")

# --- BOT POLLING ---
if __name__ == "__main__":
    keep_alive()
    print("Bot is starting on Render...")
    bot.polling(none_stop=True)
