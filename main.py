import telebot
import pymongo
import random
import time
from datetime import datetime
from telebot import types

# --- [CONFIGURED DETAILS] ---
TOKEN = "8052478407:AAHgn5heLnCixh1PUXG-8sSiL8brigtO5fM"
ADMIN_ID = 6130849132
CHANNEL_ID = -1001905966650
GROUP_ID = -1003430728423
CHANNEL_LINK = "https://t.me/onlineincome_x"
GROUP_LINK = "https://t.me/moneymakersboys"

bot = telebot.TeleBot(TOKEN)
client = pymongo.MongoClient("mongodb+srv://mosiffuiego_db_user:9RTLIPCOzi2qPIGr@cluster0.ly0dot0.mongodb.net/?appName=Cluster0")
db = client['MoneyTarDB']
users_col = db['users']
settings_col = db['settings']

# Settings Initialization
if not settings_col.find_one({"id": "bot_config"}):
    settings_col.insert_one({"id": "bot_config", "is_on": True, "back_time": "Soon", "m_msg": "Upgrading Servers"})

# --- 🧠 BOT BRAIN FUNCTIONS ---
def get_config():
    return settings_col.find_one({"id": "bot_config"})

def is_joined(uid):
    try:
        c = bot.get_chat_member(CHANNEL_ID, uid).status
        g = bot.get_chat_member(GROUP_ID, uid).status
        return c in ['member', 'administrator', 'creator'] and g in ['member', 'administrator', 'creator']
    except: return False

def get_user(uid, name="User"):
    uid = str(uid)
    user = users_col.find_one({"uid": uid})
    if not user:
        user = {"uid": uid, "bal": 0.0, "ref": 0, "spins": 0, "name": name, "last_bonus": ""}
        users_col.insert_one(user)
    return user

# --- 🛠️ MAINTENANCE MIDDLEWARE ---
def check_maintenance(message):
    config = get_config()
    if not config['is_on'] and message.from_user.id != ADMIN_ID:
        text = f"🛠️ **BOT UNDER MAINTENANCE** 🛠️\n\nReason: {config['m_msg']}\n⏰ Back Online: `{config['back_time']}`\n\nStay tuned in our channel!"
        img = "https://img.freepik.com/free-vector/maintenance-concept-illustration_114360-381.jpg"
        bot.send_photo(message.chat.id, img, caption=text, parse_mode='Markdown')
        return False
    return True

# --- 🏠 START & MAIN MENU ---
@bot.message_handler(commands=['start'])
def start(message):
    if not check_maintenance(message): return
    uid = message.from_user.id
    
    if not is_joined(uid):
        m = types.InlineKeyboardMarkup()
        m.add(types.InlineKeyboardButton("📢 Channel", url=CHANNEL_LINK), types.InlineKeyboardButton("💬 Group", url=GROUP_LINK))
        m.add(types.InlineKeyboardButton("🔄 Check Join", callback_data="check_join"))
        return bot.send_message(message.chat.id, "❌ **Access Denied!** Join both to continue:", reply_markup=m)

    user = get_user(uid, message.from_user.first_name)
    
    # Referral Logic (1 Refer = 1 Spin)
    args = message.text.split()
    if len(args) > 1 and args[1] != str(uid):
        if not users_col.find_one({"uid": str(uid)}):
            users_col.update_one({"uid": args[1]}, {"$inc": {"spins": 1, "ref": 1}})
            bot.send_message(args[1], "🔔 **New Referral!** You got **1 Spin Ticket**! 🎡")

    hour = datetime.now().hour
    greet = "Good Morning ☀️" if 5<=hour<12 else "Good Afternoon 🌤️" if 12<=hour<17 else "Good Evening 🌆"
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🎡 Lucky Spin", "📅 Daily Bonus")
    markup.row("💰 Wallet", "🏦 Withdraw")
    markup.row("🏆 Leaderboard", "📸 Submit Task")
    markup.row("👥 Refer & Earn", "👨‍💻 Support")
    if uid == ADMIN_ID: markup.row("⚙️ Admin Panel")
    
    bot.send_message(message.chat.id, f"💎 **{greet}, {message.from_user.first_name}!**\n\n💰 Balance: ₹{user['bal']}\n🎡 Spins: {user['spins']}", reply_markup=markup)

# --- 🎡 SPIN LOGIC ---
@bot.message_handler(func=lambda m: m.text == "🎡 Lucky Spin")
def spin(message):
    if not check_maintenance(message): return
    user = get_user(message.from_user.id)
    if user['spins'] < 1:
        return bot.reply_to(message, "❌ No Spins! Refer friends to get spins.")
    
    win = random.choice([0, 0.5, 1, 2, 5, 0, 1, 10])
    users_col.update_one({"uid": str(user['uid'])}, {"$inc": {"spins": -1, "bal": win}})
    bot.send_message(message.chat.id, f"🎡 Spinning... You won **₹{win}**!")

# --- 🏦 WITHDRAW & GST ---
@bot.message_handler(func=lambda m: m.text == "🏦 Withdraw")
def withdraw(message):
    if not check_maintenance(message): return
    user = get_user(message.from_user.id)
    if user['bal'] < 400:
        bot.reply_to(message, f"❌ Min withdrawal ₹400. Needed: ₹{400 - user['bal']}")
    else:
        gst = user['bal'] * 0.28
        bot
