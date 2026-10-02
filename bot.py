import logging
import datetime
import json
import os
import shutil
import re
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes
)

# ------------------- تنظیمات اولیه -------------------
TOKEN = "8909439742:AAF0a-ZR0OG-p5YbHq0_Eh6cucO8_xrAWQU"
ADMIN_USERNAME = 'eror5511'
ADMIN_ID = 8846204367

CARD_NUMBER = "6219861967850321"
CARD_HOLDER = "کریمپور"

USDT_RATE = 235000   
TON_RATE = 350000   
TRX_RATE = 80000    

USDT_ADDRESS = "0xFbC56f4732B0af076efc2a09368BD5A908ae72F2"
TON_ADDRESS = "UQDU-b3ZUxwMZFfzyas_D79yOPjXmBPv2qHwQno2Pr0HpgWD"
TRX_ADDRESS = "TCS8KjycnvC6LYDLmfnK73t3MTvy6w9dDt"

# لیست و قیمت‌های هوش مصنوعی
AI_SERVICES = {
    "🤖 چت‌جی‌‌پی‌تی (ChatGPT)": {"name": "چت‌جی‌پی‌تی (ChatGPT)", "price": 2776000},
    "🧠 کلاد (Claude)": {"name": "کلاد (Claude)", "price": 6418000},
    "🚀 گراک (Grok)": {"name": "گراک (Grok)", "price": 2548000},
    "💻 کرسر (Cursor)": {"name": "کرسر (Cursor)", "price": 5558000},
    "✨ جمنای (Gemini)": {"name": "جمنای (Gemini)", "price": 2270000},
    "🔍 پرپلکسیتی (Perplexity)": {"name": "پرپلکسیتی (Perplexity)", "price": 3408000},
    "🎨 میدجرنی (Midjourney)": {"name": "میدجرنی (Midjourney)", "price": 3155000},
    "📝 گرمرلی (Grammarly)": {"name": "گرمرلی (Grammarly)", "price": 2826000}
}

# لیست محصولات مختلف
GAMING_PRODUCTS = [
    "🎮 گیفت‌کارت ایکس‌باکس", "🎮 گیفت‌کارت پلی‌استیشن", "🎮 گیفت‌کارت ولورانت",
    "🎮 گیفت‌کارت استیم", "💬 دیسکورد", "🎮 گیفت‌کارت نینتندو",
    "🎮 گیفت‌کارت ریزر گلد", "🎮 گیفت‌کارت رابلاکس", "🎮 گیفت‌کارت فورتنایت"
]

MOVIE_MUSIC_PRODUCTS = [
    "🎬 نتفلیکس", "🎵 اسپاتیفای", "🎁 گیفت‌کارت اسپاتیفای",
    "▶️ یوتیوب پرمیوم", "🎬 دیزنی‌پلاس", "🎁 گیفت‌کارت دیزنی‌پلاس", "🎁 گیفت‌کارت نتفلیکس"
]

SHOPPING_GIFT_CARDS = [
    "🛒 گیفت‌کارت ای‌بی (eBay)", "🍎 گیفت‌کارت اپل", "📦 گیفت‌کارت آمازون",
    "🏪 گیفت‌کارت وال‌مارت", "👑 گیفت‌کارت آمازون پرایم", "🛒 گیفت‌کارت بست‌بای"
]

DESIGN_TOOLS = ["🎨 فیگما (Figma)", "🖌 ادوبی فتوشاپ", "🎨 کنوا پرو (Canva Pro)"]
EDUCATION_PRODUCTS = ["🎓 اسکیل‌شر (Skillshare)", "📚 یودمی (Udemy)"]
TRAVEL_PRODUCTS = ["🏡 گیفت‌کارت ایربی‌ان‌بی (Airbnb)", "🏨 گیفت‌کارت بوکینگ (Booking.com)"]
FASHION_PRODUCTS = ["🛍 گیفت‌کارت زالاندو (Zalando)", "👗 گیفت‌کارت ایسوس (ASOS)"]

ALL_INQUIRY_PRODUCTS = (
    GAMING_PRODUCTS + MOVIE_MUSIC_PRODUCTS + SHOPPING_GIFT_CARDS + 
    DESIGN_TOOLS + EDUCATION_PRODUCTS + TRAVEL_PRODUCTS + FASHION_PRODUCTS
)

# قیمت‌های ویندسکرایب
WINDSCRIBE_PRICES = {
    "۱ ماهه": {
        "👤 ۱ کاربره": 259000, "👥 ۲ کاربره": 420000, "👥 ۳ کاربره": 639000,
        "👥 ۴ کاربره": 890000, "👥 ۵ کاربره": 999000, "🚀 اکانت فول (۱۵ کاربره)": 1790000
    },
    "۱ ساله": {
        "👤 ۱ کاربره": 1199000, "👥 ۲ کاربره": 1999000, "👥 ۳ کاربره": 2999000,
        "👥 ۴ کاربره": 3850000, "👥 ۵ کاربره": 4400000, "🚀 اکانت فول (۱۵ کاربره)": 8800000
    }
}

SPECIAL_DISCOUNT_PRICES = {
    "🎁 ۶ ماهه - ۱ کاربره": {"price": 590000, "desc": "اشتراک ۶ ماهه نامحدود (۱ کاربره) با تخفیف ویژه"},
    "🎁 ۶ ماهه - ۲ کاربره": {"price": 990000, "desc": "اشتراک ۶ ماهه نامحدود (۲ کاربره) با تخفیف ویژه"}
}

# V2Ray
V2RAY_LOCATIONS = ["🇩🇪 آلمان", "🇫🇮 فنلاند", "🇫🇷 فرانسه", "🇺🇸 آمریکا", "🇹🇷 ترکیه", "🇳🇱 هلند"]

V2RAY_PRICES = {
    "🔥 اشتراک ۱۰ گیگ": 140000,
    "🔥 اشتراک ۲۰ گیگ": 250000,
    "🔥 اشتراک ۳۰ گیگ": 380000,
    "🔥 اشتراک ۵۰ گیگ": 599000
}

V2RAY_MULTI_PRICES = {
    "⚡️ اشتراک ۳۰ گیگ": 199000,
    "⚡️ اشتراک ۵۰ گیگ": 299000,
    "⚡️ اشتراک ۷۰ گیگ": 379000,
    "⚡ اشتراک ۱۵۰ گیگ": 599000
}

TELEGRAM_PREMIUM_PRICES = {
    "🗓 ۳ ماهه پرمیوم": 1250000,
    "🗓 ۶ ماهه پرمیوم": 1850000,
    "🗓 ۱۲ ماهه پرمیوم": 2950000
}

TELEGRAM_STARS_PRICES = {
    "⭐ ۱۰۰ تا استارز": 180000,
    "⭐ ۲۰۰ تا استارز": 350000,
    "⭐ ۵۰۰ تا استارز": 850000,
    "⭐ ۱۰۰۰ تا استارز": 1650000
}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ------------------- دیتابیس JSON -------------------
DATA_FILE = "bot_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return (
                    {int(k): v for k, v in data.get("user_wallets", {}).items()},
                    {int(k): v for k, v in data.get("user_subscriptions", {}).items()},
                    {int(k): v for k, v in data.get("user_history", {}).items()},
                    data.get("point_logs", []),
                    set(data.get("registered_inviters", [])),
                    {int(k): v for k, v in data.get("user_referrals", {}).items()},
                    set(data.get("purchased_referrals", [])),
                    data.get("group_chat_id", None),
                    {int(k): v for k, v in data.get("user_names", {}).items()}
                )
        except Exception as e:
            logging.error(f"خطا در خواندن فایل داده‌ها: {e}")
    return {}, {}, {}, [], set(), {}, set(), None, {}

def save_data():
    data = {
        "user_wallets": user_wallets,
        "user_subscriptions": user_subscriptions,
        "user_history": user_history,
        "point_logs": point_logs,
        "registered_inviters": list(registered_inviters),
        "user_referrals": user_referrals,
        "purchased_referrals": list(purchased_referrals),
        "group_chat_id": group_chat_id,
        "user_names": user_names
    }
    temp_file = "bot_data_temp.json"
    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        shutil.move(temp_file, DATA_FILE)
    except Exception as e:
        logging.error(f"خطا در ذخیره‌سازی داده‌ها: {e}")

(user_wallets, user_subscriptions, user_history, point_logs, 
 registered_inviters, user_referrals, purchased_referrals, group_chat_id, user_names) = load_data()

pending_orders = {}

# ------------------- پشتیبان‌گیری خودکار -------------------
async def send_auto_backup(context: ContextTypes.DEFAULT_TYPE):
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "rb") as f:
                await context.bot.send_document(
                    chat_id=ADMIN_ID,
                    document=f,
                    caption=f"📦 **پشتیبان‌گیری خودکار دیتابیس ربات**\n🗓 تاریخ: {datetime.datetime.now().strftime('%Y/%m/%d - %H:%M')}"
                )
        except Exception as e:
            logging.error(f"خطا در ارسال بک‌آپ خودکار: {e}")

# ------------------- ثبت و فرمت اطلاعات کاربر -------------------
def update_user_info(user):
    if user and not user.is_bot:
        user_names[user.id] = {
            "first_name": user.first_name or "کاربر",
            "username": user.username or ""
        }
        save_data()

def format_user_display(user_id: int) -> str:
    info = user_names.get(user_id, {})
    name = info.get("first_name", f"کاربر {user_id}")
    username = info.get("username", "")
    
    display_name = f"[{name}](tg://user?id={user_id})"
    if username:
        return f"{display_name} (@{username})"
    return f"{display_name} (`{user_id}`)"

def format_points(pts: float) -> str:
    pts = round(pts, 2)
    if pts.is_integer():
        return str(int(pts))
    return f"{pts:.1f}"

# ------------------- سیستم امتیازات -------------------
def add_user_points(user_id: int, points: float, p_type: str):
    if points > 0:
        point_logs.append({
            "user_id": user_id,
            "points": points,
            "type": p_type,
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        save_data()

def get_total_user_points(user_id: int) -> float:
    return sum(log['points'] for log in point_logs if log['user_id'] == user_id)

def get_user_daily_rank(user_id: int) -> int:
    now = datetime.datetime.now()
    user_sums = {}
    for log in point_logs:
        log_time = datetime.datetime.strptime(log['time'], "%Y-%m-%d %H:%M:%S")
        if (now - log_time).total_seconds() <= 86400:
            uid = log['user_id']
            user_sums[uid] = user_sums.get(uid, 0.0) + log['points']
            
    sorted_users = sorted(user_sums.items(), key=lambda x: x[1], reverse=True)
    for rank, (u_id, pts) in enumerate(sorted_users, 1):
        if u_id == user_id:
            return rank
    return len(sorted_users) + 1

def check_and_reward_referral_purchase(buyer_id: int):
    if buyer_id in user_referrals and buyer_id not in purchased_referrals:
        inviter_id = user_referrals[buyer_id]
        add_user_points(inviter_id, 5.0, 'invite')
        purchased_referrals.add(buyer_id)
        save_data()
        return inviter_id
    return None

def generate_leaderboard(filter_type: str) -> str:
    now = datetime.datetime.now()
    user_sums = {}

    for log in point_logs:
        uid = log['user_id']
        pts = log['points']
        log_time = datetime.datetime.strptime(log['time'], "%Y-%m-%d %H:%M:%S")
        l_type = log['type']

        if filter_type == 'daily' and (now - log_time).total_seconds() > 86400:
            continue
        elif filter_type == 'weekly' and (now - log_time).days > 7:
            continue
        elif filter_type == 'invite' and l_type != 'invite':
            continue
        elif filter_type == 'answer' and l_type != 'answer':
            continue

        user_sums[uid] = user_sums.get(uid, 0.0) + pts

    sorted_users = sorted(user_sums.items(), key=lambda x: x[1], reverse=True)[:10]

    titles = {
        'overall': '📊 **جدول برترین‌های کلی (کل تاریخ)**',
        'weekly': '📅 **جدول برترین‌های هفتگی (۷ روز اخیر)**',
        'daily': '☀️ **جدول برترین‌های روزانه (۲۴ ساعت اخیر)**',
        'invite': '👥 **برترین‌های دعوت‌کننده (رفرال)**',
        'answer': '💡 **برترین‌های راهنمایی و پاسخ‌دهی**'
    }

    if not sorted_users:
        return f"{titles.get(filter_type, '🏆 جدول برترین‌ها')}\n\n❌ هنوز امتیازی در این بخش ثبت نشده است."

    res = f"{titles.get(filter_type, '🏆 جدول برترین‌ها')}\n\n"
    for idx, (u_id, p) in enumerate(sorted_users, 1):
        medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
        user_str = format_user_display(u_id)
        res += f"{medal} {user_str} 👈 **{format_points(p)} امتیاز**\n"
    
    return res

# ------------------- کیبوردهای منوها -------------------
def get_main_menu():
    keyboard = [
        [KeyboardButton("⚡️ خرید فیلترشکن"), KeyboardButton("🤖 خرید اشتراک هوش مصنوعی")],
        [KeyboardButton("⭐️ خدمات تلگرام و استارز"), KeyboardButton("🛍 سایر محصولات")],
        [KeyboardButton("💰 کسب درآمد و امتیاز"), KeyboardButton("👤 حساب و کیف پول")],
        [KeyboardButton("🎧 پشتیبانی و راهنما")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_ai_menu():
    keyboard = [
        [KeyboardButton("🤖 چت‌‌جی‌پی‌تی (ChatGPT)"), KeyboardButton("🧠 کلاد (Claude)")],
        [KeyboardButton("🚀 گراک (Grok)"), KeyboardButton("💻 کرسر (Cursor)")],
        [KeyboardButton("✨ جمنای (Gemini)"), KeyboardButton("🔍 پرپلکسیتی (Perplexity)")],
        [KeyboardButton("🎨 میدجرنی (Midjourney)"), KeyboardButton("📝 گرمرلی (Grammarly)")],
        [KeyboardButton("🔙 بازگشت به منوی اصلی")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_telegram_menu():
    keyboard = [
        [KeyboardButton("⭐ خرید اشتراک پرمیوم تلگرام"), KeyboardButton("🌟 خرید استارز تلگرام")],
        [KeyboardButton("🔙 بازگشت به منوی اصلی")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_telegram_premium_menu():
    keyboard = [
        [KeyboardButton("🗓 ۳ ماهه پرمیوم"), KeyboardButton("🗓 ۶ ماهه پرمیوم")],
        [KeyboardButton("🗓 ۱۲ ماهه پرمیوم")],
        [KeyboardButton("🔙 بازگشت به خدمات تلگرام")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_telegram_stars_menu():
    keyboard = [
        [KeyboardButton("⭐ ۱۰۰ تا استارز"), KeyboardButton("⭐ ۲۰۰ تا استارز")],
        [KeyboardButton("⭐ ۵۰۰ تا استارز"), KeyboardButton("⭐ ۱۰۰۰ تا استارز")],
        [KeyboardButton("🔙 بازگشت به خدمات تلگرام")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_other_products_menu():
    keyboard = [
        [KeyboardButton("🎮 بازی و گیمینگ"), KeyboardButton("🎬 فیلم و موسیقی")],
        [KeyboardButton("💳 گیفت‌کارت خرید آنلاین"), KeyboardButton("🛠 ابزارهای تخصصی و طراحی")],
        [KeyboardButton("🎓 آموزشی و کورس‌ها"), KeyboardButton("✈️️ گردشگری، سفر و اقامت")],
        [KeyboardButton("👗 مد و پوشاک")],
        [KeyboardButton("🔙 بازگشت به منوی اصلی")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_gaming_menu():
    keyboard = [
        [KeyboardButton("🎮 گیفت‌‌کارت ایکس‌باکس"), KeyboardButton("🎮 گیفت‌کارت پلی‌استیشن")],
        [KeyboardButton("🎮 گیفت‌کارت ولورانت"), KeyboardButton("🎮 گیفت‌کارت استیم")],
        [KeyboardButton("💬 دیسکورد"), KeyboardButton("🎮 گیفت‌کارت نینتندو")],
        [KeyboardButton("🎮 گیفت‌کارت ریزر گلد"), KeyboardButton("🎮 گیفت‌کارت رابلاکس")],
        [KeyboardButton("🎮 گیفت‌کارت فورتنایت")],
        [KeyboardButton("🔙 بازگشت به سایر محصولات")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_movie_music_menu():
    keyboard = [
        [KeyboardButton("🎬 نتفلیکس"), KeyboardButton("🎵 اسپاتیفای")],
        [KeyboardButton("🎁 گیفت‌کارت اسپاتیفای"), KeyboardButton("▶️ یوتیوب پرمیوم")],
        [KeyboardButton("🎬 دیزنی‌پلاس"), KeyboardButton("🎁 گیفت‌کارت دیزنی‌پلاس")],
        [KeyboardButton("🎁 گیفت‌کارت نتفلیکس")],
        [KeyboardButton("🔙 بازگشت به سایر محصولات")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_shopping_cards_menu():
    keyboard = [
        [KeyboardButton("🛒 گیفت‌کارت ای‌بی (eBay)"), KeyboardButton("🍎 گیفت‌کارت اپل")],
        [KeyboardButton("📦 گیفت‌کارت آمازون"), KeyboardButton("🏪 گیفت‌کارت وال‌مارت")],
        [KeyboardButton("👑 گیفت‌کارت آمازون پرایم"), KeyboardButton("🛒 گیفت‌کارت بست‌بای")],
        [KeyboardButton("🔙 بازگشت به سایر محصولات")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_design_tools_menu():
    keyboard = [
        [KeyboardButton("🎨 فیگما (Figma)"), KeyboardButton("🖌 ادوبی فتوشاپ")],
        [KeyboardButton("🎨 کنوا پرو (Canva Pro)")],
        [KeyboardButton("🔙 بازگشت به سایر محصولات")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_education_menu():
    keyboard = [
        [KeyboardButton("🎓 اسکیل‌شر (Skillshare)"), KeyboardButton("📚 یودمی (Udemy)")],
        [KeyboardButton("🔙 بازگشت به سایر محصولات")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_travel_menu():
    keyboard = [
        [KeyboardButton("🏡 گیفت‌کارت ایربی‌ان‌بی (Airbnb)"), KeyboardButton("🏨 گیفت‌کارت بوکینگ (Booking.com)")],
        [KeyboardButton("🔙 بازگشت به سایر محصولات")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_fashion_menu():
    keyboard = [
        [KeyboardButton("🛍 گیفت‌کارت زالاندو (Zalando)"), KeyboardButton("👗 گیفت‌کارت ایسوس (ASOS)")],
        [KeyboardButton("🔙 بازگشت به سایر محصولات")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_earn_money_menu():
    keyboard = [
        [KeyboardButton("🔗 ثبت معرفی‌کننده"), KeyboardButton("📋 راهنمای کسب درآمد")],
        [KeyboardButton("🏆 جدول برترین‌ها"), KeyboardButton("⭐️ امتیازات من")],
        [KeyboardButton("🔙 بازگشت به منوی اصلی")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_leaderboard_menu():
    keyboard = [
        [KeyboardButton("📊 جدول کلی"), KeyboardButton("📅 جدول هفتگی")],
        [KeyboardButton("☀️ جدول روزانه"), KeyboardButton("👥 برترین‌های دعوت")],
        [KeyboardButton("💡 برترین‌های راهنمایی"), KeyboardButton("🔙 بازگشت به کسب درآمد")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_account_menu():
    keyboard = [
        [KeyboardButton("💳 شارژ کیف پول"), KeyboardButton("⏳ اشتراک‌های فعال")],
        [KeyboardButton("📦 سوابق خرید"), KeyboardButton("🎁 کد تخفیف")],
        [KeyboardButton("🔙 بازگشت به منوی اصلی")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_vpn_menu():
    keyboard = [
        [KeyboardButton("🌀 اکانت ویندسکرایب نامحدود")],
        [KeyboardButton("🌐 اشتراک V2Ray حجمی آی‌پی ثابت")],
        [KeyboardButton("🔙 بازگشت به منوی اصلی")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_v2ray_type_menu():
    keyboard = [
        [KeyboardButton("⭐ اشتراک‌های تک لوکیشن VIP آی‌پی ثابت برای کارهای تخصصی")],
        [KeyboardButton("💡 اشتراک‌های مولتی لوکیشن اقتصادی ارور کانکشن")],
        [KeyboardButton("🔙 بازگشت به انتخاب فیلترشکن")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_v2ray_locations_menu():
    keyboard = [
        [KeyboardButton("🇩🇪 آلمان"), KeyboardButton("🇫🇮 فنلاند")],
        [KeyboardButton("🇫🇷 فرانسه"), KeyboardButton("🇺🇸 آمریکا")],
        [KeyboardButton("🇹🇷 ترکیه"), KeyboardButton("🇳🇱 هلند")],
        [KeyboardButton("🔙 بازگشت به نوع V2Ray")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_v2ray_plans_menu():
    keyboard = []
    for plan, price in V2RAY_PRICES.items():
        keyboard.append([KeyboardButton(f"{plan} - {price:,} تومان")])
    keyboard.append([KeyboardButton("🔙 بازگشت به انتخاب لوکیشن")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_v2ray_multi_plans_menu():
    keyboard = []
    for plan, price in V2RAY_MULTI_PRICES.items():
        keyboard.append([KeyboardButton(f"{plan} - {price:,} تومان")])
    keyboard.append([KeyboardButton("🔙 بازگشت به نوع V2Ray")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_windscribe_duration_menu():
    keyboard = [
        [KeyboardButton("🗓 اشتراک ۱ ماهه"), KeyboardButton("🗓 اشتراک ۱ ساله")],
        [KeyboardButton("🔥 تخفیف‌های روز و اکانت‌های ویژه")],
        [KeyboardButton("🔙 بازگشت به انتخاب فیلترشکن")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_user_count_menu(duration="۱ ماهه"):
    prices = WINDSCRIBE_PRICES.get(duration, {})
    p1, p2 = prices.get("👤 ۱ کاربره", 0), prices.get("👥 ۲ کاربره", 0)
    p3, p4 = prices.get("👥 ۳ کاربره", 0), prices.get("👥 ۴ کاربره", 0)
    p5, p15 = prices.get("👥 ۵ کاربره", 0), prices.get("🚀 اکانت فول (۱۵ کاربره)", 0)

    keyboard = [
        [KeyboardButton(f"👤 ۱ کاربره - {p1:,} تومان"), KeyboardButton(f"👥 ۲ کاربره - {p2:,} تومان")],
        [KeyboardButton(f"👥 ۳ کاربره - {p3:,} تومان"), KeyboardButton(f"👥 ۴ کاربره - {p4:,} تومان")],
        [KeyboardButton(f"👥 ۵ کاربره - {p5:,} تومان"), KeyboardButton(f"🚀 اکانت فول (۱۵ کاربره) - {p15:,} تومان")],
        [KeyboardButton("🔙 بازگشت به انتخاب مدت")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_discount_menu():
    keyboard = []
    for name, info in SPECIAL_DISCOUNT_PRICES.items():
        keyboard.append([KeyboardButton(f"{name} - {info['price']:,} تومان")])
    keyboard.append([KeyboardButton("🔙 بازگشت به انتخاب مدت")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def build_payment_keyboard(price: int, user_balance: int):
    inline_keyboard = []
    if user_balance >= price:
        inline_keyboard.append([InlineKeyboardButton("💰 پرداخت کامل از کیف پول", callback_data=f"pay_from_wallet:{price}")])
    elif user_balance > 0:
        rem = price - user_balance
        inline_keyboard.append([InlineKeyboardButton(f"💳 کارت به کارت ({rem:,} تومان)", callback_data=f"buy_card:{rem}:{user_balance}")])
        inline_keyboard.append([InlineKeyboardButton(f"🌐 پرداخت ارزی ({rem:,} تومان)", callback_data=f"buy_crypto:{rem}:{user_balance}")])
    else:
        inline_keyboard.append([InlineKeyboardButton("💳 پرداخت کارت به کارت", callback_data=f"buy_card:{price}:0")])
        inline_keyboard.append([InlineKeyboardButton("🌐 پرداخت ارزی (تتر)", callback_data=f"buy_crypto:{price}:0")])
    
    inline_keyboard.append([InlineKeyboardButton("🎟 اعمال کد تخفیف", callback_data=f"apply_discount:{price}")])
    return InlineKeyboardMarkup(inline_keyboard)

# ------------------- دستور /start -------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    update_user_info(user)
    context.user_data.clear()
    text = f"سلام {user.first_name} عزیز! 👋\nبه فروشگاه خوش آمدید.\n\nلطفاً از منوی زیر انتخاب کنید:"
    await update.message.reply_text(text, reply_markup=get_main_menu())

# ------------------- پردازش کالبک‌ها -------------------
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user = query.from_user
    update_user_info(user)
    
    user_id = user.id
    username = user.username or ""

    if data.startswith("confirm_invite:"):
        _, new_user_id, target_username_or_id = data.split(":")
        new_user_id = int(new_user_id)

        is_target = False
        if target_username_or_id.isdigit() and int(target_username_or_id) == user_id:
            is_target = True
        elif username.lower() == target_username_or_id.lower():
            is_target = True

        if not is_target:
            await query.answer("❌ این دکمه فقط برای شخص دعوت‌کننده است!", show_alert=True)
            return

        add_user_points(user_id, 5.0, 'invite')
        registered_inviters.add(new_user_id)
        user_referrals[new_user_id] = user_id
        save_data()

        await query.answer("🎉 تایید شد! ۵ امتیاز هدیه به حساب شما اضافه شد.", show_alert=True)
        try: await query.message.delete()
        except Exception: pass
        return

    await query.answer()

    if data.startswith("buy_card:"):
        parts = data.split(":")
        pay_amount, wallet_deduct = int(parts[1]), int(parts[2]) if len(parts) > 2 else 0
        context.user_data['state'] = 'WAITING_FOR_PRODUCT_RECEIPT'
        context.user_data['pay_method'] = f"کارت به کارت ({pay_amount:,} تومان)"
        context.user_data['wallet_deduct'] = wallet_deduct

        text = f"💳 **پرداخت سفارش**\n\n📦 **سفارش:** {context.user_data.get('pending_order')}\n💰 **قابل واریز:** {pay_amount:,} تومان\n📌 **شماره کارت:**\n`{CARD_NUMBER}`\n👤 **به نام:** {CARD_HOLDER}\n\n📸 تصویر فیش را ارسال کنید."
        await query.message.reply_text(text, parse_mode="Markdown")

    elif data.startswith("buy_crypto:"):
        parts = data.split(":")
        pay_amount = int(parts[1])
        usdt_val = round(pay_amount / USDT_RATE, 2)
        text = (
            f"🌐 **پرداخت ارزی (تتر / TRC20 یا BEP20)**\n\n"
            f"💰 **مبلغ تومان:** {pay_amount:,} تومان\n"
            f"💵 **معادل تتر:** ~{usdt_val} USDT\n\n"
            f"📌 **آدرس ولت تتر:**\n`{USDT_ADDRESS}`\n\n"
            f"📸 پس از واریز، تصویر رسید یا TxID را ارسال فرمایید."
        )
        context.user_data['state'] = 'WAITING_FOR_PRODUCT_RECEIPT'
        await query.message.reply_text(text, parse_mode="Markdown")

    elif data.startswith("pay_from_wallet:"):
        price = int(data.split(":")[1])
        user_balance = user_wallets.get(user_id, 0)
        selected_plan = context.user_data.get('pending_order', 'اشتراک')

        if user_balance < price:
            await query.message.reply_text("❌ موجودی کیف پول کافی نیست!")
        else:
            user_wallets[user_id] -= price
            save_data()
            
            inviter_id = check_and_reward_referral_purchase(user_id)
            if inviter_id:
                try: await context.bot.send_message(chat_id=inviter_id, text="🎉 **خبر خوب!** دوست شما اولین خرید خود را انجام داد و **۵ امتیاز هدیه دیگر** به حساب شما اضافه شد!")
                except Exception: pass

            admin_keyboard = [[InlineKeyboardButton("📦 ارسال اکانت برای کاربر", callback_data=f"send_account_to:{user_id}")]]
            await query.message.reply_text(f"✅ **پرداخت با موفقیت انجام شد!**\n\n🛍 سفارش: {selected_plan}\n💰 کسر شده: {price:,} تومان\n💳 موجودی: {user_wallets[user_id]:,} تومان\n\n⏳ کانفیگ/اکانت شما به زودی ارسال می‌شود.", parse_mode="Markdown")
            try: await context.bot.send_message(chat_id=ADMIN_ID, text=f"🚨 **سفارش جدید (از کیف پول)!**\n\n👤 کاربر: {user.first_name}\n🆔 آیدی: `{user_id}`\n📦 سفارش: {selected_plan}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(admin_keyboard))
            except Exception: pass

    elif data.startswith("send_account_to:"):
        parts = data.split(":")
        target_uid = int(parts[1])
        context.user_data['admin_state'] = 'WAITING_FOR_ACCOUNT_DATA'
        context.user_data['target_user_id'] = target_uid
        await query.message.reply_text(f"✏️ **لطفاً اطلاعات اکانت/کانفیگ را ارسال کنید:**\n👤 آیدی کاربر: `{target_uid}`", parse_mode="Markdown")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_state = context.user_data.get('state')
    user = update.effective_user
    update_user_info(user)
    
    photo_file_id = update.message.photo[-1].file_id if update.message.photo else (update.message.document.file_id if update.message.document else None)

    if photo_file_id and user_state == 'WAITING_FOR_PRODUCT_RECEIPT':
        order_details = context.user_data.get('pending_order', 'اکانت سفارشی')
        wallet_deduct = context.user_data.get('wallet_deduct', 0)
        admin_keyboard = [[InlineKeyboardButton("✅ ارسال اکانت", callback_data=f"send_account_to:{user.id}:{wallet_deduct}"), InlineKeyboardButton("❌ رد", callback_data=f"admin_reject:{user.id}")]]
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=photo_file_id, caption=f"🛍 **سفارش جدید**\n👤 {user.first_name}\n🆔 `{user.id}`\n📦 {order_details}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(admin_keyboard))
        context.user_data['state'] = None
        await update.message.reply_text("✅ رسید ارسال شد. سفارش شما به زودی توسط پشتیبانی پردازش و ارسال می‌شود.")

# ------------------- مدیریت پیام‌های متنی (هسته اصلی) -------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global group_chat_id
    msg = update.message
    text = (msg.text or "").strip()
    user = update.effective_user
    chat_type = update.effective_chat.type

    if user and not user.is_bot:
        update_user_info(user)

    # ------------------ مدیریت فعالیت گروه ------------------
    if chat_type in ['group', 'supergroup']:
        if group_chat_id != msg.chat_id:
            group_chat_id = msg.chat_id
            save_data()

        if msg.reply_to_message and not msg.reply_to_message.from_user.is_bot:
            if text in ['+', '+1', 'امتیاز', 'مفید بود']:
                questioner = user
                answerer = msg.reply_to_message.from_user
                update_user_info(answerer)
                
                if questioner.id != answerer.id:
                    add_user_points(answerer.id, 1.0, 'answer')
                    
                    total_pts = get_total_user_points(answerer.id)
                    daily_rank = get_user_daily_rank(answerer.id)
                    answerer_link = f"[{answerer.first_name}](tg://user?id={answerer.id})"
                    
                    group_announcement = (
                        f"🌱 {answerer_link} عزیز، پاسخ شما مفید تشخیص داده شد!\n"
                        f"➕ **۱+ امتیاز دریافت کردید**\n"
                        f"📊 مجموع امتیازات: **{format_points(total_pts)}** | 🏆 رتبه امروز در گروه: **{daily_rank}**"
                    )
                    
                    try:
                        await msg.reply_text(group_announcement, parse_mode="Markdown")
                    except Exception:
                        pass
                
                try:
                    await msg.delete()
                except Exception:
                    pass
                return

        if not user.is_bot:
            add_user_points(user.id, 0.1, 'chat')
        return

    # ------------------ پیوی ربات: پاسخ ادمین ------------------
    if user.id == ADMIN_ID and context.user_data.get('admin_state') == 'WAITING_FOR_ACCOUNT_DATA':
        target_uid = context.user_data.get('target_user_id')
        try:
            await context.bot.send_message(chat_id=target_uid, text=f"🎉 **سفارش شما تحویل داده شد:**\n\n{text}\n\nبا تشکر از خرید شما!", parse_mode="Markdown")
            order_info = pending_orders.get(target_uid, {"item": "اشتراک سفارشی", "price": 0})
            
            user_subscriptions.setdefault(target_uid, []).append({"name": order_info["item"], "expire": "فعال", "details": text})
            user_history.setdefault(target_uid, []).append({"item": order_info["item"], "price": order_info["price"], "date": datetime.datetime.now().strftime("%Y/%m/%d - %H:%M")})
            save_data()

            inviter_id = check_and_reward_referral_purchase(target_uid)
            if inviter_id:
                try: await context.bot.send_message(chat_id=inviter_id, text="🎉 **خبر خوب!** دوست شما اولین خرید خود را انجام داد و **۵ امتیاز هدیه دیگر** به حساب شما اضافه شد!")
                except Exception: pass

            await msg.reply_text("✅ اطلاعات برای کاربر ارسال و در سوابق خریدش ذخیره شد.")
        except Exception as e:
            await msg.reply_text(f"❌ خطا: {e}")
        context.user_data['admin_state'] = None
        return

    # ------------------ پیوی ربات: ورودی معرفی‌کننده ------------------
    if context.user_data.get('state') == 'WAITING_FOR_INVITER_INPUT':
        inviter_input = text.replace('@', '')
        context.user_data['state'] = None

        if not group_chat_id:
            await msg.reply_text("❌ گروه پیدا نشد! لطفاً ابتدا مطمئن شوید ربات در گروه ادمین است.")
            return

        keyboard = [[
            InlineKeyboardButton("✅ بله، من دعوت کردم (+۵ امتیاز)", callback_data=f"confirm_invite:{user.id}:{inviter_input}")
        ]]
        
        try:
            await context.bot.send_message(
                chat_id=group_chat_id,
                text=(
                    f"📢 **تایید دعوت‌کننده:**\n"
                    f"کاربر [{user.first_name}](tg://user?id={user.id}) اعلام کرده که توسط @{inviter_input} به گروه دعوت شده است.\n\n"
                    f"آیا تایید می‌کنید؟"
                ),
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            await msg.reply_text("✅ درخواست تایید برای معرفی‌کننده در گروه ارسال شد!")
        except Exception as e:
            await msg.reply_text(f"❌ خطایی در ارسال پیام به گروه رخ داد: {e}")
        return

    # ------------------ منوهای اصلی و فرعی ------------------
    if text == "🔙 بازگشت به منوی اصلی":
        await msg.reply_text("🏠 **منوی اصلی:**", reply_markup=get_main_menu())

    elif text == "🛍 سایر محصولات":
        await msg.reply_text("🛍 **سایر محصولات و خدمات:**\nلطفاً دسته‌بندی مورد نظر خود را انتخاب کنید:", reply_markup=get_other_products_menu())
        
    elif text == "🎮 بازی و گیمینگ":
        await msg.reply_text("🎮 **بخش بازی و گیمینگ (گیفت‌کارت‌ها)**\n\nلطفاً محصول مورد نظر خود را انتخاب کنید:", reply_markup=get_gaming_menu())

    elif text == "🎬 فیلم و موسیقی":
        await msg.reply_text("🎬 **بخش فیلم و موسیقی**\n\nلطفاً اشتراک یا سرویس مورد نظر خود را انتخاب کنید:", reply_markup=get_movie_music_menu())

    elif text == "💳 گیفت‌کارت خرید آنلاین":
        await msg.reply_text("💳 **گیفت‌کارت و فروشگاه‌های آنلاین**\n\nلطفاً سرویس مورد نظر خود را انتخاب کنید:", reply_markup=get_shopping_cards_menu())

    elif text == "🛠 ابزارهای تخصصی و طراحی":
        await msg.reply_text("🛠 **ابزارهای تخصصی و طراحی**\n\nلطفاً سرویس مورد نظر خود را انتخاب کنید:", reply_markup=get_design_tools_menu())

    elif text == "🎓 آموزشی و کورس‌ها":
        await msg.reply_text("🎓 **آموزشی و کورس‌ها**\n\nلطفاً سرویس مورد نظر خود را انتخاب کنید:", reply_markup=get_education_menu())

    elif text == "✈️ گردشگری، سفر و اقامت":
        await msg.reply_text("✈️ **گردشگری، سفر و اقامت**\n\nلطفاً سرویس مورد نظر خود را انتخاب کنید:", reply_markup=get_travel_menu())

    elif text == "👗 مد و پوشاک":
        await msg.reply_text("👗 **مد و پوشاک**\n\nلطفاً سرویس مورد نظر خود را انتخاب کنید:", reply_markup=get_fashion_menu())

    elif text == "🔙 بازگشت به سایر محصولات":
        await msg.reply_text("🛍 **سایر محصولات و خدمات:**\nلطفاً دسته‌بندی مورد نظر خود را انتخاب کنید:", reply_markup=get_other_products_menu())

    elif text in ALL_INQUIRY_PRODUCTS:
        caption_text = (
            f"🛍 **{text}**\n\n"
            f"به دلیل نوسانات قیمت ارز و دلار و برای اینکه بتونیم این سفارش رو دقیق‌تر، با سرعت بیشتر و بهترین کیفیت روی اکانت شخصی خودتون فعال کنیم، لطفاً جهت استعلام قیمت روز و ثبت سفارش به آیدی ادمین پیام دهید:\n\n"
            f"👉 @{ADMIN_USERNAME}"
        )
        inline_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 پیام به ادمین جهت خرید", url=f"https://t.me/{ADMIN_USERNAME}")]
        ])
        await msg.reply_text(caption_text, parse_mode="Markdown", reply_markup=inline_kb)

    elif text == "🤖 خرید اشتراک هوش مصنوعی":
        await msg.reply_text("🤖 **خرید اشتراک هوش مصنوعی**\n\nلطفاً ابزار هوش مصنوعی مورد نظر خود را انتخاب کنید:", reply_markup=get_ai_menu())

    elif text in AI_SERVICES:
        service_info = AI_SERVICES[text]
        s_name = service_info["name"]
        s_price = service_info["price"]

        caption_text = (
            f"✨ **اشتراک {s_name}**\n\n"
            f"💰 **شروع قیمت‌ها از:** {s_price:,} تومان\n\n"
            f"📌 **توضیحات سفارش:**\n"
            f"به دلیل نوسانات قیمت دلار، نیاز به دریافت اطلاعات تکمیلی شما و جهت بررسی دقیق درخواست برای انتخاب بهترین حالت متناسب با نیازتان، لطفاً جهت مشاوره و ثبت سفارش به ادمین مربوطه مراجعه کنید:\n\n"
            f"👉 @{ADMIN_USERNAME}"
        )
        inline_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 پیام به ادمین جهت ثبت سفارش", url=f"https://t.me/{ADMIN_USERNAME}")]
        ])
        await msg.reply_text(caption_text, parse_mode="Markdown", reply_markup=inline_kb)

    # ------------------ خدمات تلگرام و استارز ------------------
    elif text == "⭐️️ خدمات تلگرام و استارز":
        await msg.reply_text("⭐️ **خدمات تلگرام و استارز**\nلطفاً بخش مورد نظر خود را انتخاب کنید:", reply_markup=get_telegram_menu())

    elif text == "⭐ خرید اشتراک پرمیوم تلگرام":
        await msg.reply_text("⭐ **خرید اشتراک پرمیوم تلگرام**\nلطفاً مدت زمان مورد نظر را انتخاب کنید:", reply_markup=get_telegram_premium_menu())

    elif text in TELEGRAM_PREMIUM_PRICES:
        price = TELEGRAM_PREMIUM_PRICES[text]
        context.user_data['pending_order'] = f"تلگرام پرمیوم ({text})"
        pending_orders[user.id] = {"item": f"تلگرام پرمیوم ({text})", "price": price}
        user_bal = user_wallets.get(user.id, 0)
        await msg.reply_text(f"💎 **سفارش {text}**\n💰 **قیمت:** {price:,} تومان\n💳 **موجودی کیف پول شما:** {user_bal:,} تومان", reply_markup=build_payment_keyboard(price, user_bal), parse_mode="Markdown")

    elif text == "🌟 خرید استارز تلگرام":
        await msg.reply_text("🌟 **خرید استارز تلگرام**\nلطفاً بسته مورد نظر را انتخاب کنید:", reply_markup=get_telegram_stars_menu())

    elif text in TELEGRAM_STARS_PRICES:
        price = TELEGRAM_STARS_PRICES[text]
        context.user_data['pending_order'] = f"استارز تلگرام ({text})"
        pending_orders[user.id] = {"item": f"استارز تلگرام ({text})", "price": price}
        user_bal = user_wallets.get(user.id, 0)
        await msg.reply_text(f"🌟 **سفارش {text}**\n💰 **قیمت:** {price:,} تومان\n💳 **موجودی کیف پول شما:** {user_bal:,} تومان", reply_markup=build_payment_keyboard(price, user_bal), parse_mode="Markdown")

    elif text == "🔙 بازگشت به خدمات تلگرام":
        await msg.reply_text("⭐️ **خدمات تلگرام و استارز**", reply_markup=get_telegram_menu())

    # ------------------ کسب درآمد و امتیاز ------------------
    elif text == "💰 کسب درآمد و امتیاز":
        await msg.reply_text("💰 **کسب درآمد و امتیاز**\nلطفاً یک گزینه را انتخاب کنید:", reply_markup=get_earn_money_menu())

    elif text == "🔗 ثبت معرفی‌کننده":
        context.user_data['state'] = 'WAITING_FOR_INVITER_INPUT'
        await msg.reply_text("✏️ لطفاً آیدی یا نام کاربری تلگرام شخصی که شما را به گروه دعوت کرده وارد کنید (مثال: eror5511):")

    elif text == "📋 راهنمای کسب درآمد":
        guide_text = (
            "📋 **راهنمای کسب درآمد و امتیاز:**\n\n"
            "1️⃣ **چت در گروه:** با ارسال پیام در گروه ادمین، 0.1 امتیاز به ازای هر پیام دریافت می‌کنید.\n"
            "2️⃣ **پاسخ مفید:** اگر پاسخ شما در گروه تایید شود (+1)، 1 امتیاز هدیه می‌گیرید.\n"
            "3️⃣ **دعوت از دوستان:** با ثبت معرفی‌کننده 5 امتیاز هدیه دریافت می‌کنید.\n"
            "4️⃣ **پاداش خرید رفرال:** پس از اولین خرید دوست معرفی شده، 5 امتیاز اضافه می‌گیرید."
        )
        await msg.reply_text(guide_text, parse_mode="Markdown")

    elif text == "🏆 جدول برترین‌ها":
        await msg.reply_text("🏆 **جدول برترین‌ها**\nبازه‌ مورد نظر را انتخاب کنید:", reply_markup=get_leaderboard_menu())

    elif text == "📊 جدول کلی":
        await msg.reply_text(generate_leaderboard('overall'), parse_mode="Markdown")

    elif text == "📅 جدول هفتگی":
        await msg.reply_text(generate_leaderboard('weekly'), parse_mode="Markdown")

    elif text == "☀️ جدول روزانه":
        await msg.reply_text(generate_leaderboard('daily'), parse_mode="Markdown")

    elif text == "👥 برترین‌های دعوت":
        await msg.reply_text(generate_leaderboard('invite'), parse_mode="Markdown")

    elif text == "💡 برترین‌های راهنمایی":
        await msg.reply_text(generate_leaderboard('answer'), parse_mode="Markdown")

    elif text == "⭐️ امتیازات من":
        pts = get_total_user_points(user.id)
        rank = get_user_daily_rank(user.id)
        await msg.reply_text(f"👤 **امتیازات شما:**\n\n⭐ مجموع امتیاز: **{format_points(pts)}**\n🏆 رتبه ۲۴ ساعت اخیر: **{rank}**", parse_mode="Markdown")

    elif text == "🔙 بازگشت به کسب درآمد":
        await msg.reply_text("💰 **کسب درآمد و امتیاز**", reply_markup=get_earn_money_menu())

    # ------------------ حساب و کیف پول ------------------
    elif text == "👤 حساب و کیف پول":
        bal = user_wallets.get(user.id, 0)
        await msg.reply_text(f"👤 **حساب کاربری**\n🆔 شناسه: `{user.id}`\n💰 موجودی کیف پول: **{bal:,} تومان**", reply_markup=get_account_menu(), parse_mode="Markdown")

    elif text == "💳 شارژ کیف پول":
        caption_text = (
            f"💳 **شارژ کیف پول**\n\n"
            f"برای شارژ کیف پول خود، لطفا مبلغ پرداختی را به شماره کارت زیر واریز نموده و فیش را برای پشتیبانی ارسال کنید:\n\n"
            f"📌 **شماره کارت:** `{CARD_NUMBER}`\n👤 **به نام:** {CARD_HOLDER}\n\n"
            f"👉 @{ADMIN_USERNAME}"
        )
        await msg.reply_text(caption_text, parse_mode="Markdown")

    elif text == "⏳ اشتراک‌های فعال":
        subs = user_subscriptions.get(user.id, [])
        if not subs:
            await msg.reply_text("❌ هیچ اشتراک فعالی یافت نشد.")
        else:
            resp = "⏳ **اشتراک‌های فعال شما:**\n\n"
            for s in subs:
                resp += f"🔹 **{s.get('name')}** | وضعیت: {s.get('expire')}\nاطلاعات: `{s.get('details')}`\n\n"
            await msg.reply_text(resp, parse_mode="Markdown")

    elif text == "📦 سوابق خرید":
        hist = user_history.get(user.id, [])
        if not hist:
            await msg.reply_text("❌ سابقه خریدی برای شما ثبت نشده است.")
        else:
            resp = "📦 **سوابق خرید شما:**\n\n"
            for h in hist:
                resp += f"🔸 {h.get('item')} - {h.get('price'):,} تومان ({h.get('date')})\n"
            await msg.reply_text(resp, parse_mode="Markdown")

    elif text == "🎁 کد تخفیف":
        await msg.reply_text("🎟 کد تخفیف خود را هنگام سفارش نهایی وارد کنید.")

    # ------------------ فیلترشکن (V2Ray و ویندسکرایب) ------------------
    elif text == "⚡️ خرید فیلترشکن":
        await msg.reply_text("⚡️ **خرید فیلترشکن**\nنوع سرویس را انتخاب کنید:", reply_markup=get_vpn_menu())

    elif text == "🌀 اکانت ویندسکرایب نامحدود":
        await msg.reply_text("🌀 **اکانت ویندسکرایب نامحدود**\nمدت زمان اشتراک را انتخاب کنید:", reply_markup=get_windscribe_duration_menu())

    elif text in ["🗓 اشتراک ۱ ماهه", "🗓 اشتراک ۱ ساله"]:
        dur = "۱ ماهه" if "۱ ماهه" in text else "۱ ساله"
        context.user_data['windscribe_duration'] = dur
        await msg.reply_text(f"👤 **انتخاب تعداد کاربر ({dur}):**", reply_markup=get_user_count_menu(dur))

    elif text == "🔥 تخفیف‌های روز و اکانت‌های ویژه":
        await msg.reply_text("🔥 **تخفیف‌های ویژه روز:**", reply_markup=get_discount_menu())

    elif text == "🌐 اشتراک V2Ray حجمی آی‌پی ثابت":
        await msg.reply_text("🌐 **اشتراک V2Ray**\nنوع سرویس را انتخاب کنید:", reply_markup=get_v2ray_type_menu())

    elif text == "⭐ اشتراک‌های تک لوکیشن VIP آی‌پی ثابت برای کارهای تخصصی":
        await msg.reply_text("🌐 **انتخاب لوکیشن:**", reply_markup=get_v2ray_locations_menu())

    elif text in V2RAY_LOCATIONS:
        context.user_data['v2ray_location'] = text
        await msg.reply_text(f"📍 لوکیشن انتخاب شده: **{text}**\nحجم مورد نظر را انتخاب کنید:", reply_markup=get_v2ray_plans_menu(), parse_mode="Markdown")

    elif text == "💡 اشتراک‌های مولتی لوکیشن اقتصادی ارور کانکشن":
        await msg.reply_text("⚡️ **اشتراک‌های مولتی لوکیشن:**", reply_markup=get_v2ray_multi_plans_menu())

    elif text == "🔙 بازگشت به انتخاب فیلترشکن":
        await msg.reply_text("⚡️ **خرید فیلترشکن**", reply_markup=get_vpn_menu())

    elif text == "🔙 بازگشت به انتخاب مدت":
        await msg.reply_text("🌀 **اکانت ویندسکرایب نامحدود**", reply_markup=get_windscribe_duration_menu())

    elif text == "🔙 بازگشت به نوع V2Ray":
        await msg.reply_text("🌐 **اشتراک V2Ray**", reply_markup=get_v2ray_type_menu())

    elif text == "🔙 بازگشت به انتخاب لوکیشن":
        await msg.reply_text("🌐 **انتخاب لوکیشن:**", reply_markup=get_v2ray_locations_menu())

    # ------------------ پردازش خریدهای متنی V2Ray و Windscribe ------------------
    elif "تومان" in text and ("کاربره" in text or "اشتراک" in text or "اکانت" in text):
        clean_price = re.sub(r'[^\d]', '', text)
        if clean_price.isdigit():
            price = int(clean_price)
            item_title = text.split("-")[0].strip()
            context.user_data['pending_order'] = item_title
            pending_orders[user.id] = {"item": item_title, "price": price}
            user_bal = user_wallets.get(user.id, 0)
            await msg.reply_text(
                f"🛍 **سفارش:** {item_title}\n💰 **قیمت:** {price:,} تومان\n💳 **موجودی کیف پول شما:** {user_bal:,} تومان",
                reply_markup=build_payment_keyboard(price, user_bal),
                parse_mode="Markdown"
            )

    # ------------------ پشتیبانی و راهنما ------------------
    elif text == "🎧 پشتیبانی و راهنما":
        support_text = (
            f"🎧 **پشتیبانی و راهنمایی**\n\n"
            f"در صورت وجود هرگونه سوال، مشکل در فعال‌سازی یا نیاز به راهنمایی قبل از خرید، می‌توانید با آیدی پشتیبانی در ارتباط باشید:\n\n"
            f"👤 **آیدی ادمین پشتیبانی:** @{ADMIN_USERNAME}\n"
            f"🆔 **شناسه ادمین:** `{ADMIN_ID}`"
        )
        inline_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 ارتباط مستقیم با پشتیبانی", url=f"https://t.me/{ADMIN_USERNAME}")]
        ])
        await msg.reply_text(support_text, parse_mode="Markdown", reply_markup=inline_kb)

    else:
        await msg.reply_text("❌ متوجه دستور نشدم. لطفاً از دکمه‌های منو استفاده کنید.", reply_markup=get_main_menu())

# ------------------- راه اندازی ربات -------------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is running successfully...")
    app.run_polling()

if __name__ == '__main__':
    main()
