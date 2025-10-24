import telebot
import requests
import threading
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# अपना TOKEN और API Keys यहाँ डालो
TOKEN = '8037281015:AAFkJ0Sp0IIRiFcg2ncZi481tppX505jYLE'
FAST2SMS_KEY = 'YOUR_FAST2SMS_API_KEY'  # Optional
bot = telebot.TeleBot(TOKEN)

# Global vars for bombing
bombing_sessions = {}  # {user_id: {'active': True, 'number': str, 'count': int, 'sent': int}}
stop_event = threading.Event()

def send_sms_via_api(number, message):
    """SMS send via Fast2SMS (or fallback)"""
    try:
        if FAST2SMS_KEY != 'YOUR_FAST2SMS_API_KEY':
            url = "https://www.fast2sms.com/dev/bulkV2"
            data = {
                'authorization': FAST2SMS_KEY,
                'sender_id': 'FSTSMS',
                'message': message,
                'language': 'english',
                'route': 'p',
                'numbers': number
            }
            r = requests.post(url, data=data)
            return r.json().get('return', {}).get('message') == 'success'
        else:
            # Dummy mode: Simulate send (no real SMS)
            time.sleep(0.1)  # Simulate delay
            return True
    except:
        return False

def bomb_thread(user_id, number, count, message="Bomb Alert! 😈"):
    """Thread for bombing"""
    session = bombing_sessions[user_id]
    session['sent'] = 0
    for i in range(count):
        if not session['active']:
            break
        if send_sms_via_api(number, message):
            session['sent'] += 1
            bot.send_message(user_id, f"💣 Sent {session['sent']}/{count}")
        time.sleep(1)  # Delay to avoid rate limit
    session['active'] = False
    bot.send_message(user_id, f"✅ Bombing complete: {session['sent']} SMS sent!")

@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💣 Start Bomb", callback_data="bomb_help"))
    markup.add(InlineKeyboardButton("🛑 Stop", callback_data="stop_help"))
    bot.send_message(
        message.chat.id,
        """
🔥 *SMS Bomber Bot* 🔥

⚠️ *Warning*: Use only for fun/testing. Illegal if misused!

Usage: `/bomb 9876543210 10`

👇 Buttons से help लो.
        """,
        parse_mode='Markdown',
        reply_markup=markup
    )

@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.reply_to(message, """
🛠️ *Commands*:

`/bomb <number> <count>` → Bomb SMS (e.g., /bomb 9876543210 5)
/stop → Stop current bombing

*API Setup*: Fast2SMS key add करो for real SMS.
    """, parse_mode='Markdown')

@bot.message_handler(commands=['bomb'])
def start_bomb(message):
    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "❌ Usage: `/bomb 9876543210 10`", parse_mode='Markdown')
            return
        number = parts[1]
        count = int(parts[2])
        if not number.isdigit() or len(number) != 10:
            bot.reply_to(message, "❌ Invalid number: 10 digits only.")
            return
        if count > 50:  # Limit to prevent abuse
            bot.reply_to(message, "❌ Max 50 SMS. Don't abuse!")
            return
        
        user_id = message.from_user.id
        if user_id in bombing_sessions and bombing_sessions[user_id]['active']:
            bot.reply_to(message, "⚠️ Already bombing! Use /stop first.")
            return
        
        bombing_sessions[user_id] = {'active': True, 'number': number, 'count': count}
        bot.reply_to(message, f"🚀 Starting bomb on {number} x{count}...")
        
        thread = threading.Thread(target=bomb_thread, args=(user_id, number, count))
        thread.start()
    except ValueError:
        bot.reply_to(message, "❌ Invalid count: Use number.")

@bot.message_handler(commands=['stop'])
def stop_bomb(message):
    user_id = message.from_user.id
    if user_id in bombing_sessions:
        bombing_sessions[user_id]['active'] = False
        bot.reply_to(message, f"🛑 Stopped bombing on {bombing_sessions[user_id]['number']}")
    else:
        bot.reply_to(message, "ℹ️ No active bombing.")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "bomb_help":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "💣 `/bomb 9876543210 10` — Send 10 SMS to number.", parse_mode='Markdown')
    elif call.data == "stop_help":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "🛑 `/stop` — Halt the bomb.", parse_mode='Markdown')

# Run Bot
print("🤖 SMS Bomber Bot running... (Use ethically!)")
bot.infinity_polling()
