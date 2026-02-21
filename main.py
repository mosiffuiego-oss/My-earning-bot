import telebot
import json
import os
import time
from flask import Flask
from threading import Thread

# --- CONFIGURATION ---
API_TOKEN = '8052478407:AAHgn5heLnCixh1PUXG-8sSiL8brigtO5fM' 
ADMIN_ID = 6130849132

# Aapki IDs
CHANNEL_ID = -1001905966650 
GROUP_ID = -1003430728423
CHANNEL_LINK = 'https://t.me/onlineincome_x'
GROUP_LINK = 'https://t.me/moneymakersboys'

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

# --- JOIN CHECK FUNCTION ---
def is_joined(user_id):
    try:
        ch = bot.get_chat_member(CHANNEL_ID, user_id).status
        gr = bot.get_chat_member(GROUP_ID, user_id).status
        allowed = ['member', 'administrator', 'creator']
        if ch in allowed and gr in allowed:
            return True
        return False
    except:
        return False

# --- START COMMAND ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.chat.id)
    data = load_data()
    
    # 1. Check if user joined
    if not is_joined(uid):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("📢 Channel", url=CHANNEL_LINK))
        markup.add(telebot.types.InlineKeyboardButton("👥 Group", url=GROUP_LINK))
        markup.add(telebot.types.InlineKeyboardButton("✅ Check Joined", callback_data="verify"))
        bot.send_message(uid, "⚠️ <b>Access Denied!</b>\n\nAapne Channel ya Group join nahi kiya hai.", parse_mode="html", reply_markup=markup)
        return

    # 2. Add New User + Refer Logic
    if uid not in data:
        ref_by = message.text.split()[1] if len(message.text.split()) > 1 else None
        data[uid] = {'bal': 0, 'invited': 0, 'last_ad': 0, 'last_bonus': 0}
        
        if ref_by and ref_by in data and ref_by != uid:
            data[ref_by]['bal'] += 20
            data[ref_by]['invited'] += 1
            bot.send_message(ref_by, "🔔 New Referral! You earned 20 Rs.")
        save_data(data)

    # 3. Main Menu (Replit Style)
    main_menu = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    main_menu.add("💰 Balance", "🔗 Invite")
    main_menu.add("📺 Watch Ad", "🎁 Daily Bonus")
    main_menu.add("🏧 Withdraw")
    bot.send_message(uid, "👋 Welcome! Aapka account active hai.\nEarn 20 Rs per invite.", reply_markup=main_menu)

# --- VERIFY CALLBACK ---
@bot.callback_query_handler(func=lambda call: call.data == "verify")
def verify(call):
    if is_joined(call.message.chat.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start(call.message)
    else:
        bot.answer_callback_query(call.id, "❌ Join First!", show_alert=True)

# --- BUTTON LOGIC (REPLIT STYLE) ---
@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    uid = str(message.chat.id)
    
    # Force join check for every button click
    if not is_joined(uid):
        bot.send_message(uid, "❌ Please join our channel and group first!")
        return

    data = load_data()
    if uid not in data: data[uid] = {'bal': 0, 'invited': 0, 'last_ad': 0, 'last_bonus': 0}

    if message.text == "💰 Balance":
        bot.send_message(uid, f"📊 <b>Account Details:</b>\n\n💳 Balance: {data[uid]['bal']} Rs\n👥 Invites: {data[uid]['invited']}", parse_mode="html")

    elif message.text == "🔗 Invite":
        bot_user = bot.get_me().username
        ref_link = f"https://t.me/{bot_user}?start={uid}"
        bot.send_message(uid, f"🎁 <b>Invite & Earn</b>\n\nEarn 20 Rs per refer!\n🔗 Link: {ref_link}", parse_mode="html")

    elif message.text == "📺 Watch Ad":
        now = time.time()
        if now - data[uid].get('last_ad', 0) > 60:
            data[uid]['bal'] += 2
            data[uid]['last_ad'] = now
            save_data(data)
            bot.send_message(uid, "✅ Ad watched! 2 Rs added.")
        else:
            bot.send_message(uid, "⏳ Wait 60 seconds.")

    elif message.text == "🎁 Daily Bonus":
        now = time.time()
        if now - data[uid].get('last_bonus', 0) > 86400:
            data[uid]['bal'] += 5
            data[uid]['last_bonus'] = now
            save_data(data)
            bot.send_message(uid, "🎁 5 Rs Bonus added!")
        else:
            bot.send_message(uid, "❌ Come back tomorrow.")

    elif message.text == "🏧 Withdraw":
        if data[uid]['bal'] >= 250:
            bot.send_message(uid, "📤 Send UPI ID & Amount (Ex: abc@ybl 250):")
        else:
            bot.send_message(uid, f"❌ Min withdraw 250 Rs.\nYour balance: {data[uid]['bal']} Rs")

# --- AUTO ACCEPT ---
@bot.chat_join_request_handler()
def handle_request(request):
    try: bot.approve_chat_join_request(request.chat.id, request.from_user.id)
    except: pass

if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)
