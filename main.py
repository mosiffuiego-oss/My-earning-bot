import telebot
import json
import os
import time
from flask import Flask
from threading import Thread

# --- CONFIGURATION ---
API_TOKEN = '8052478407:AAHgn5heLnCixh1PUXG-8sSiL8brigtO5fM' 
ADMIN_ID = 6130849132

# Aapke Links
CHANNEL_ID = -1001905966650
GROUP_ID = -1003430728423
CHANNEL_LINK = 'https://t.me/onlineincome_x'
GROUP_LINK = 'https://t.me/moneymakersboys'

bot = telebot.TeleBot(API_TOKEN)
app = Flask('')

@app.route('/')
def home(): return "Bot is Online with Auto-Accept!"

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

# --- AUTO ACCEPT JOIN REQUEST ---
@bot.chat_join_request_handler()
def accept_request(message):
    try:
        bot.approve_chat_join_request(message.chat.id, message.from_user.id)
        bot.send_message(message.from_user.id, "✅ Your request to join the group has been accepted!")
    except Exception as e:
        print(f"Error accepting request: {e}")

# --- FORCE JOIN CHECK ---
def is_joined(user_id):
    try:
        # Channel check
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        if status not in ['member', 'administrator', 'creator']:
            return False
        return True
    except:
        return False

# --- START COMMAND ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.chat.id)
    data = load_data()
    
    if not is_joined(uid):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK))
        markup.add(telebot.types.InlineKeyboardButton("👥 Join Group", url=GROUP_LINK))
        markup.add(telebot.types.InlineKeyboardButton("✅ Check Joined", callback_data="check_join"))
        bot.send_message(uid, "❌ <b>Access Denied!</b>\n\nYou must join our Channel and Group to use this bot.", parse_mode="html", reply_markup=markup)
        return

    if uid not in data:
        ref_by = message.text.split()[1] if len(message.text.split()) > 1 else None
        data[uid] = {'bal': 0, 'invited': 0, 'last_ad': 0, 'last_bonus': 0}
        if ref_by and ref_by in data and ref_by != uid:
            data[ref_by]['bal'] += 20
            data[ref_by]['invited'] += 1
            bot.send_message(ref_by, "🔔 New Referral! You earned 20 Rs.")
        save_data(data)

    main_menu = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    main_menu.add("💰 Balance", "🔗 Invite")
    main_menu.add("📺 Watch Ad", "🎁 Daily Bonus")
    main_menu.add("🏧 Withdraw")
    bot.send_message(uid, f"👋 Welcome back! Earn 20 Rs per invite.", reply_markup=main_menu)

# --- CALLBACK FOR JOIN CHECK ---
@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def check_callback(call):
    if is_joined(call.message.chat.id):
        bot.answer_callback_query(call.id, "✅ Success!")
        start(call.message)
    else:
        bot.answer_callback_query(call.id, "❌ Join first!", show_alert=True)

# --- BUTTON HANDLING ---
@bot.message_handler(func=lambda m: True)
def handle_text(message):
    uid = str(message.chat.id)
    if not is_joined(uid):
        bot.send_message(uid, "❌ Join our channel first!")
        return
    
    data = load_data()
    if message.text == "💰 Balance":
        bot.send_message(uid, f"💳 Balance: {data[uid]['bal']} Rs")
    elif message.text == "🔗 Invite":
        bot_user = bot.get_me().username
        bot.
