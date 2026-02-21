import telebot
import json
import os
import time
from flask import Flask
from threading import Thread

# --- CONFIGURATION ---
API_TOKEN = '8052478407:AAHgn5heLnCixh1PUXG-8sSiL8brigtO5fM' 
ADMIN_ID = 6130849132

# Aapki Numerical IDs
CHANNEL_ID = -1001905966650 
GROUP_ID = -1003430728423
CHANNEL_LINK = 'https://t.me/onlineincome_x'
GROUP_LINK = 'https://t.me/moneymakersboys'

bot = telebot.TeleBot(API_TOKEN)
app = Flask('')

@app.route('/')
def home(): return "Bot is Online - IDs Fixed"

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

# --- FORCE JOIN CHECK ---
def is_joined(user_id):
    try:
        # Dono jagah check kar rahe hain
        ch = bot.get_chat_member(CHANNEL_ID, user_id).status
        gr = bot.get_chat_member(GROUP_ID, user_id).status
        allowed = ['member', 'administrator', 'creator']
        if ch in allowed and gr in allowed:
            return True
        return False
    except Exception as e:
        print(f"ID Check Error: {e}")
        return False

# --- AUTO ACCEPT REQUESTS ---
@bot.chat_join_request_handler()
def handle_request(request):
    try:
        bot.approve_chat_join_request(request.chat.id, request.from_user.id)
    except: pass

# --- START COMMAND ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.chat.id)
    data = load_data()
    
    if not is_joined(uid):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("📢 Channel", url=CHANNEL_LINK))
        markup.add(telebot.types.InlineKeyboardButton("👥 Group", url=GROUP_LINK))
        markup.add(telebot.types.InlineKeyboardButton("✅ Check Joined", callback_data="verify"))
        bot.send_message(uid, "⚠️ <b>Access Denied!</b>\n\nAapne hamara Channel aur Group join nahi kiya hai.", parse_mode="html", reply_markup=markup)
        return

    if uid not in data:
        ref_by = message.text.split()[1] if len(message.text.split()) > 1 else None
        data[uid] = {'bal': 0, 'invited': 0}
        if ref_by and ref_by in data and ref_by != uid:
            data[ref_by]['bal'] += 20
            data[ref_by]['invited'] += 1
            bot.send_message(ref_by, "🔔 New Referral! You earned 20 Rs.")
        save_data(data)
    
    main_menu = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    main_menu.add("💰 Balance", "🔗 Invite")
    main_menu.add("🏧 Withdraw")
    bot.send_message(uid, "✅ Welcome! Account is now active.", reply_markup=main_menu)

@bot.callback_query_handler(func=lambda call: call.data == "verify")
def verify(call):
    if is_joined(call.message.chat.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start(call.message)
    else:
        bot.answer_callback_query(call.id, "❌ Join First!", show_alert=True)

if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)
