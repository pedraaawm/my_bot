import logging
import datetime
import os
import re
import random
import string
import asyncio
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ChatType, ParseMode
from motor.motor_asyncio import AsyncIOMotorClient

# ------------------- تنظیمات اولیه -------------------
TOKEN = os.getenv("BOT_TOKEN", "8909439742:AAG6wlEx6ZiGWzYSS83aDHhYQm07_N6HBRk")
ADMIN_USERNAME = 'eror5511'
ADMIN_ID = 8846204367

CHANNEL_LINK = "https://t.me/Eror_connection"
GROUP_LINK = "https://t.me/Eror_connection_group"

# تنظیمات دیتابیس MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://pedraaawm_db_user:QJzZfOPM7cQRaVAd@cluster0.wul6ohg.mongodb.net/?appName=Cluster0")
mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client["shop_bot_db"]

users_col = db["users"]
point_logs_col = db["point_logs"]
settings_col = db["settings"]

CARD_NUMBER = "6219861967850321"
CARD_HOLDER = "کریمپور"

USDT_RATE = 235000   
TON_RATE = 350000   
TRX_RATE = 80000    

USDT_ADDRESS = "0xFbC56f4732B0af076efc2a09368BD5A908ae72F2"
TON_ADDRESS = "UQDU-b3ZUxwMZFfzyas_D79yOPjXmBPv2qHwQno2Pr0HpgWD"
TRX_ADDRESS = "TCS8KjycnvC6LYDLmfnK73t3MTvy6w9dDt"

# ------------------- داده‌های کاتالوگ و قیمت‌ها -------------------
AI_SERVICES = {
    "🤖 چت‌‌جی‌‌پی‌تی (ChatGPT)": {"name": "چت‌جی‌پی‌تی (ChatGPT)", "price": 2776000},
    "🧠 کلاد (Claude)": {"name": "کلاد (Claude)", "price": 6418000},
    "🚀 گراک (Grok)": {"name": "گراک (Grok)", "price": 2548000},
    "💻 کرسر (Cursor)": {"name": "کرسر (Cursor)", "price": 5558000},
    "✨ جمنای (Gemini)": {"name": "جمنای (Gemini)", "price": 2270000},
    "🔍 پرپلکسیتی (Perplexity)": {"name": "پرپلکسیتی (Perplexity)", "price": 3408000},
    "🎨 میدجرنی (Midjourney)": {"name": "میدجرنی (Midjourney)", "price": 3155000},
    "📝 گرمرلی (Grammarly)": {"name": "گرمرلی (Grammarly)", "price": 2826000}
}

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
    "🛒 گیفت‌کارت ای‌‌بی (eBay)", "🍎 گیفت‌کارت اپل", "📦 گیفت‌کارت آمازون",
    "🏪 گیفت‌کارت وال‌مارت", "👑 گیفت‌کارت آمازون پرایم", "🛒 گیفت‌کارت بست‌بای"
]

DESIGN_TOOLS = ["🎨 فیگما (Figma)", "🖌 ادوبی فتوشاپ", "🎨 کنوا پرو (Canva Pro)"]
EDUCATION_PRODUCTS = ["🎓 اسکیل‌‌شر (Skillshare)", "📚 یودمی (Udemy)"]
TRAVEL_PRODUCTS = ["🏡 گیفت‌کارت ایربی‌ان‌بی (Airbnb)", "🏨 گیفت‌کارت بوکینگ (Booking.com)"]
FASHION_PRODUCTS = ["🛍 گیفت‌کارت زالاندو (Zalando)", "👗 گیفت‌کارت ایسوس (ASOS)"]

ALL_INQUIRY_PRODUCTS = (
    GAMING_PRODUCTS + MOVIE_MUSIC_PRODUCTS + SHOPPING_GIFT_CARDS + 
    DESIGN_TOOLS + EDUCATION_PRODUCTS + TRAVEL_PRODUCTS + FASHION_PRODUCTS
)

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
    "🎁 ۶ ماهه - ۱ کاربره": {"price": 590000, "desc": "اشتراک ۶ ماهه نامحدود (۱ کاربره)"},
    "🎁 ۶ ماهه - ۲ کاربره": {"price": 990000, "desc": "اشتراک ۶ ماهه نامحدود (۲ کاربره)"}
}

V2RAY_LOCATIONS = ["🇩🇪 آلمان", "🇫🇮 فنلاند", "🇫🇷 فرانسه", "🇺🇸 آمریکا", "🇹🇷 ترکیه", "🇳🇱 هلند"]

V2RAY_PRICES = {
    "🔥 اشتراک ۱۰ گیگ": 140000, "🔥 اشتراک ۲۰ گیگ": 250000,
    "🔥 اشتراک ۳۰ گیگ": 380000, "🔥 اشتراک ۵۰ گیگ": 599000
}

V2RAY_MULTI_PRICES = {
    "⚡️ اشتراک ۳۰ گیگ": 199000, "⚡️ اشتراک ۵۰ گیگ": 299000,
    "⚡️ اشتراک ۷۰ گیگ": 379000, "⚡ اشتراک ۱۵۰ گیگ": 599000
}

TELEGRAM_PREMIUM_PRICES = {
    "🗓 ۳ ماهه پرمیوم": 1250000, "🗓 ۶ ماهه پرمیوم": 1850000, "🗓 ۱۲ ماهه پرمیوم": 2950000
}

TELEGRAM_STARS_PRICES = {
    "⭐ ۱۰۰ تا استارز": 180000, "⭐ ۲۰۰ تا استارز": 350000,
    "⭐ ۵۰۰ تا استارز": 850000, "⭐ ۱۰۰۰ تا استارز": 1650000
}

logging.basicConfig(level=logging.INFO)

# ------------------- توابع MongoDB -------------------
async def update_user_info(user):
    if user and not user.is_bot:
        await users_col.update_one(
            {"_id": user.id},
            {"$set": {"first_name": user.first_name or "کاربر", "username": user.username or ""}},
            upsert=True
        )

async def get_user_wallet(user_id: int) -> int:
    doc = await users_col.find_one({"_id": user_id}, {"wallet": 1})
    return doc.get("wallet", 0) if doc else 0

async def update_user_wallet(user_id: int, amount: int):
    await users_col.update_one({"_id": user_id}, {"$inc": {"wallet": amount}}, upsert=True)

async def add_user_points(user_id: int, points: float, p_type: str):
    if points > 0:
        await point_logs_col.insert_one({
            "user_id": user_id,
            "points": points,
            "type": p_type,
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

async def get_total_user_points(user_id: int) -> float:
    pipeline = [{"$match": {"user_id": user_id}}, {"$group": {"_id": "$user_id", "total": {"$sum": "$points"}}}]
    res = await point_logs_col.aggregate(pipeline).to_list(length=1)
    return res[0]["total"] if res else 0.0

async def get_user_daily_rank(user_id: int) -> int:
    now = datetime.datetime.now()
    yesterday = (now - datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    pipeline = [
        {"$match": {"time": {"$gte": yesterday}}},
        {"$group": {"_id": "$user_id", "total": {"$sum": "$points"}}},
        {"$sort": {"total": -1}}
    ]
    rank_list = await point_logs_col.aggregate(pipeline).to_list(length=100)
    for rank, item in enumerate(rank_list, 1):
        if item["_id"] == user_id: return rank
    return len(rank_list) + 1

async def check_and_reward_referral(buyer_id: int):
    user_doc = await users_col.find_one({"_id": buyer_id})
    if user_doc and user_doc.get("inviter_id") and not user_doc.get("purchased"):
        inviter_id = user_doc["inviter_id"]
        await add_user_points(inviter_id, 5.0, 'invite')
        await users_col.update_one({"_id": buyer_id}, {"$set": {"purchased": True}})
        return inviter_id
    return None

async def set_group_chat_id(chat_id: int):
    await settings_col.update_one({"_id": "bot_settings"}, {"$set": {"group_chat_id": chat_id}}, upsert=True)

async def get_group_chat_id():
    doc = await settings_col.find_one({"_id": "bot_settings"})
    return doc.get("group_chat_id") if doc else None

async def generate_leaderboard(filter_type: str) -> str:
    now = datetime.datetime.now()
    match_stage = {}
    if filter_type == 'daily':
        match_stage["time"] = {"$gte": (now - datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")}
    elif filter_type == 'weekly':
        match_stage["time"] = {"$gte": (now - datetime.timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")}
    elif filter_type == 'invite':
        match_stage["type"] = 'invite'
    elif filter_type == 'answer':
        match_stage["type"] = 'answer'

    pipeline = []
    if match_stage: pipeline.append({"$match": match_stage})
    pipeline.extend([
        {"$group": {"_id": "$user_id", "total": {"$sum": "$points"}}},
        {"$sort": {"total": -1}},
        {"$limit": 10}
    ])
    
    top_list = await point_logs_col.aggregate(pipeline).to_list(length=10)
    titles = {
        'overall': '📊 **جدول برترین‌های کلی**',
        'weekly': '📅 **جدول برترین‌های هفتگی**',
        'daily': '☀️ **جدول برترین‌های روزانه**',
        'invite': '👥 **برترین‌های دعوت‌کننده**',
        'answer': '💡 **برترین‌های پاسخ‌دهی**'
    }
    if not top_list:
        return f"{titles.get(filter_type, '🏆 جدول برترین‌ها')}\n\n❌ هنوز امتیازی ثبت نشده است."

    res = f"{titles.get(filter_type, '🏆 جدول برترین‌ها')}\n\n"
    for idx, item in enumerate(top_list, 1):
        u_doc = await users_col.find_one({"_id": item["_id"]})
        name = u_doc.get("first_name", "کاربر") if u_doc else f"کاربر {item['_id']}"
        pts = item["total"]
        medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
        res += f"{medal} [{name}](tg://user?id={item['_id']}) 👈 **{pts:.1f} امتیاز**\n"
    return res

# ------------------- ساخت کیبوردهای ریپلای و اینلاین -------------------
def build_reply_kb(buttons):
    kb = [[KeyboardButton(text=btn) for btn in row] for row in buttons]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_main_menu():
    return build_reply_kb([
        ["⚡️ خرید فیلترشکن", "🤖 خرید اشتراک هوش مصنوعی"],
        ["⭐️ خدمات تلگرام و استارز", "🛍 سایر محصولات"],
        ["💰 کسب درآمد و امتیاز", "👤 حساب و کیف پول"],
        ["🎧 پشتیبانی و راهنما"]
    ])

def get_join_channels_inline_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 عضویت در کانال", url=CHANNEL_LINK)],
        [InlineKeyboardButton(text="👥 عضویت در گروه", url=GROUP_LINK)]
    ])

def get_ai_menu():
    return build_reply_kb([
        ["🤖 چت‌‌جی‌پی‌تی (ChatGPT)", "🧠 کلاد (Claude)"],
        ["🚀 گراک (Grok)", "💻 کرسر (Cursor)"],
        ["✨ جمنای (Gemini)", "🔍 پرپلکسیتی (Perplexity)"],
        ["🎨 میدجرنی (Midjourney)", "📝 گرمرلی (Grammarly)"],
        ["🔙 بازگشت به منوی اصلی"]
    ])

def get_telegram_menu():
    return build_reply_kb([["⭐ خرید اشتراک پرمیوم تلگرام", "🌟 خرید استارز تلگرام"], ["🔙 بازگشت به منوی اصلی"]])

def get_telegram_premium_menu():
    return build_reply_kb([["🗓 ۳ ماهه پرمیوم", "🗓 ۶ ماهه پرمیوم"], ["🗓 ۱۲ ماهه پرمیوم"], ["🔙 بازگشت به خدمات تلگرام"]])

def get_telegram_stars_menu():
    return build_reply_kb([["⭐ ۱۰۰ تا استارز", "⭐ ۲۰۰ تا استارز"], ["⭐ ۵۰۰ تا استارز", "⭐ ۱۰۰۰ تا استارز"], ["🔙 بازگشت به خدمات تلگرام"]])

def get_other_products_menu():
    return build_reply_kb([
        ["🎮 بازی و گیمینگ", "🎬 فیلم و موسیقی"],
        ["💳 گیفت‌کارت خرید آنلاین", "🛠 ابزارهای تخصصی و طراحی"],
        ["🎓 آموزشی و کورس‌ها", "✈️ گردشگری، سفر و اقامت"],
        ["👗 مد و پوشاک"],
        ["🔙 بازگشت به منوی اصلی"]
    ])

def get_gaming_menu():
    return build_reply_kb([
        ["🎮 گیفت‌کارت ایکس‌باکس", "🎮 گیفت‌کارت پلی‌استیشن"],
        ["🎮 گیفت‌کارت ولورانت", "🎮 گیفت‌کارت استیم"],
        ["💬 دیسکورد", "🎮 گیفت‌کارت نینتندو"],
        ["🎮 گیفت‌کارت ریزر گلد", "🎮 گیفت‌کارت رابلاکس"],
        ["🎮 گیفت‌کارت فورتنایت"],
        ["🔙 بازگشت به سایر محصولات"]
    ])

def get_movie_music_menu():
    return build_reply_kb([
        ["🎬 نتفلیکس", "🎵 اسپاتیفای"],
        ["🎁 گیفت‌کارت اسپاتیفای", "▶️ یوتیوب پرمیوم"],
        ["🎬 دیزنی‌پلاس", "🎁 گیفت‌کارت دیزنی‌پلاس"],
        ["🎁 گیفت‌کارت نتفلیکس"],
        ["🔙 بازگشت به سایر محصولات"]
    ])

def get_shopping_cards_menu():
    return build_reply_kb([
        ["🛒 گیفت‌کارت ای‌‌بی (eBay)", "🍎 گیفت‌کارت اپل"],
        ["📦 گیفت‌کارت آمازون", "🏪 گیفت‌کارت وال‌مارت"],
        ["👑 گیفت‌کارت آمازون پرایم", "🛒 گیفت‌‌کارت بست‌بای"],
        ["🔙 بازگشت به سایر محصولات"]
    ])

def get_design_tools_menu():
    return build_reply_kb([
        ["🎨 فیگما (Figma)", "🖌 ادوبی فتوشاپ"],
        ["🎨 کنوا پرو (Canva Pro)"],
        ["🔙 بازگشت به سایر محصولات"]
    ])

def get_education_menu():
    return build_reply_kb([
        ["🎓 اسکیل‌شر (Skillshare)", "📚 یودمی (Udemy)"],
        ["🔙 بازگشت به سایر محصولات"]
    ])

def get_travel_menu():
    return build_reply_kb([
        ["🏡 گیفت‌کارت ایربی‌ان‌بی (Airbnb)", "🏨 گیفت‌کارت بوکینگ (Booking.com)"],
        ["🔙 بازگشت به سایر محصولات"]
    ])

def get_fashion_menu():
    return build_reply_kb([
        ["🛍 گیفت‌کارت زالاندو (Zalando)", "👗 گیفت‌‌کارت ایسوس (ASOS)"],
        ["🔙 بازگشت به سایر محصولات"]
    ])

def get_earn_money_menu():
    return build_reply_kb([
        ["🔗 ثبت معرفی‌کننده", "📋 راهنمای کسب درآمد"],
        ["🏆 جدول برترین‌ها", "⭐️ امتیازات من"],
        ["🔙 بازگشت به منوی اصلی"]
    ])

def get_leaderboard_menu():
    return build_reply_kb([
        ["📊 جدول کلی", "📅 جدول هفتگی"],
        ["☀️ جدول روزانه", "👥 برترین‌های دعوت"],
        ["💡 برترین‌های راهنمایی", "🔙 بازگشت به کسب درآمد"]
    ])

def get_account_menu():
    return build_reply_kb([
        ["💳 شارژ کیف پول", "⏳ اشتراک‌های فعال"],
        ["📦 سوابق خرید", "🎁 کد تخفیف"],
        ["🔙 بازگشت به منوی اصلی"]
    ])

def get_vpn_menu():
    return build_reply_kb([
        ["🌀 اکانت ویندسکرایب نامحدود"],
        ["🌐 اشتراک V2Ray حجمی آی‌‌پی ثابت"],
        ["🔙 بازگشت به منوی اصلی"]
    ])

def get_v2ray_type_menu():
    return build_reply_kb([
        ["⭐ اشتراک‌های تک لوکیشن VIP آی‌پی ثابت برای کارهای تخصصی"],
        ["💡 اشتراک‌های مولتی لوکیشن اقتصادی ارور کانکشن"],
        ["🔙 بازگشت به انتخاب فیلترشکن"]
    ])

def get_v2ray_locations_menu():
    return build_reply_kb([
        ["🇩🇪 آلمان", "🇫🇮 فنلاند"],
        ["🇫🇷 فرانسه", "🇺🇸 آمریکا"],
        ["🇹🇷 ترکیه", "🇳🇱 هلند"],
        ["🔙 بازگشت به نوع V2Ray"]
    ])

def get_v2ray_plans_menu():
    btns = [[f"{p} - {pr:,} تومان"] for p, pr in V2RAY_PRICES.items()]
    btns.append(["🔙 بازگشت به انتخاب لوکیشن"])
    return build_reply_kb(btns)

def get_v2ray_multi_plans_menu():
    btns = [[f"{p} - {pr:,} تومان"] for p, pr in V2RAY_MULTI_PRICES.items()]
    btns.append(["🔙 بازگشت به نوع V2Ray"])
    return build_reply_kb(btns)

def get_windscribe_duration_menu():
    return build_reply_kb([
        ["🗓 اشتراک ۱ ماهه", "🗓 اشتراک ۱ ساله"],
        ["🔥 تخفیف‌های روز و اکانت‌های ویژه"],
        ["🔙 بازگشت به انتخاب فیلترشکن"]
    ])

def get_user_count_menu(duration="۱ ماهه"):
    prices = WINDSCRIBE_PRICES.get(duration, {})
    return build_reply_kb([
        [f"👤 ۱ کاربره - {prices.get('👤 ۱ کاربره', 0):,} تومان", f"👥 ۲ کاربره - {prices.get('👥 ۲ کاربره', 0):,} تومان"],
        [f"👥 ۳ کاربره - {prices.get('👥 ۳ کاربره', 0):,} تومان", f"👥 ۴ کاربره - {prices.get('👥 ۴ کاربره', 0):,} تومان"],
        [f"👥 ۵ کاربره - {prices.get('👥 ۵ کاربره', 0):,} تومان", f"🚀 اکانت فول (۱۵ کاربره) - {prices.get('🚀 اکانت فول (۱۵ کاربره)', 0):,} تومان"],
        ["🔙 بازگشت به انتخاب مدت"]
    ])

def build_payment_keyboard(price: int, user_balance: int):
    kb = []
    if user_balance >= price:
        kb.append([InlineKeyboardButton(text="💰 پرداخت کامل از کیف پول", callback_data=f"pay_from_wallet:{price}")])
    elif user_balance > 0:
        rem = price - user_balance
        kb.append([InlineKeyboardButton(text=f"💳 کارت به کارت ({rem:,} تومان)", callback_data=f"buy_card:{rem}:{user_balance}")])
        kb.append([InlineKeyboardButton(text=f"🌐 پرداخت ارزی ({rem:,} تومان)", callback_data=f"buy_crypto:{rem}:{user_balance}")])
    else:
        kb.append([InlineKeyboardButton(text="💳 پرداخت کارت به کارت", callback_data=f"buy_card:{price}:0")])
        kb.append([InlineKeyboardButton(text="🌐 پرداخت ارزی (تتر)", callback_data=f"buy_crypto:{price}:0")])
    kb.append([InlineKeyboardButton(text="🎟 اعمال کد تخفیف", callback_data=f"apply_discount:{price}")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

# ------------------- FSM و روتر Aiogram -------------------
class BotStates(StatesGroup):
    WAITING_FOR_RECEIPT = State()
    WAITING_FOR_INVITER = State()
    WAITING_FOR_ACCOUNT = State()

router = Router()

# ------------------- دستور /start و پیام خوش‌آمدگویی -------------------
@router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await update_user_info(message.from_user)
    await state.clear()
    
    welcome_text = (
        f"سلام {message.from_user.first_name} عزیز! 👋\n\n"
        "🚀 **به ربات ارور کانکشن (Eror_connection) خوش آمدید.**\n\n"
        "📢 **برای کارکرد بهتر و کامل‌تر ربات، لطفاً در کانال و گروه ما عضو شوید:**"
    )
    
    await message.answer(
        welcome_text,
        reply_markup=get_join_channels_inline_kb(),
        parse_mode=ParseMode.MARKDOWN
    )
    
    await message.answer(
        "👇 **از منوی زیر سرویس مورد نظر خود را انتخاب کنید:**",
        reply_markup=get_main_menu()
    )

# ------------------- پردازش کلیک دکمه‌ها -------------------
@router.callback_query()
async def handle_callback(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    data = callback.data
    user = callback.from_user
    await update_user_info(user)
    
    if data.startswith("confirm_invite:"):
        _, new_user_id, target_username_or_id = data.split(":")
        new_user_id = int(new_user_id)
        
        is_target = False
        if target_username_or_id.isdigit() and int(target_username_or_id) == user.id: is_target = True
        elif (user.username or "").lower() == target_username_or_id.lower(): is_target = True

        if not is_target:
            return await callback.answer("❌ این دکمه فقط برای شخص دعوت‌کننده است!", show_alert=True)

        await add_user_points(user.id, 5.0, 'invite')
        await users_col.update_one({"_id": new_user_id}, {"$set": {"inviter_id": user.id}}, upsert=True)
        await callback.answer("🎉 تایید شد! ۵ امتیاز هدیه به حساب شما اضافه شد.", show_alert=True)
        try: await callback.message.delete()
        except: pass

    elif data.startswith("buy_card:"):
        parts = data.split(":")
        pay_amount, wallet_deduct = int(parts[1]), int(parts[2]) if len(parts) > 2 else 0
        state_data = await state.get_data()
        
        await state.set_state(BotStates.WAITING_FOR_RECEIPT)
        await state.update_data(pay_amount=pay_amount, wallet_deduct=wallet_deduct)
        text = f"💳 **پرداخت سفارش**\n\n📦 **سفارش:** {state_data.get('pending_order', 'اشتراک')}\n💰 **قابل واریز:** {pay_amount:,} تومان\n📌 **شماره کارت:**\n`{CARD_NUMBER}`\n👤 **به نام:** {CARD_HOLDER}\n\n📸 تصویر فیش واریزی را ارسال کنید."
        await callback.message.answer(text, parse_mode=ParseMode.MARKDOWN)
        await callback.answer()

    elif data.startswith("buy_crypto:"):
        parts = data.split(":")
        pay_amount = int(parts[1])
        usdt_val = round(pay_amount / USDT_RATE, 2)
        text = (
            f"🌐 **پرداخت ارزی (تتر / TRC20)**\n\n"
            f"💰 **مبلغ:** {pay_amount:,} تومان\n"
            f"💵 **معادل تتر:** ~{usdt_val} USDT\n\n"
            f"📌 **آدرس ولت تتر:**\n`{USDT_ADDRESS}`\n\n"
            f"📸 پس از واریز، تصویر رسید یا TxID را ارسال کنید."
        )
        await state.set_state(BotStates.WAITING_FOR_RECEIPT)
        await callback.message.answer(text, parse_mode=ParseMode.MARKDOWN)
        await callback.answer()

    elif data.startswith("pay_from_wallet:"):
        price = int(data.split(":")[1])
        user_balance = await get_user_wallet(user.id)
        state_data = await state.get_data()
        selected_plan = state_data.get('pending_order', 'اشتراک')

        if user_balance < price:
            await callback.answer("❌ موجودی کیف پول کافی نیست!", show_alert=True)
        else:
            await update_user_wallet(user.id, -price)
            inviter_id = await check_and_reward_referral(user.id)
            if inviter_id:
                try: await bot.send_message(chat_id=inviter_id, text="🎉 **خبر خوب!** دوست شما خریدی انجام داد و **۵ امتیاز دیگر** به حساب شما اضافه شد!")
                except: pass

            admin_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📦 ارسال اکانت برای کاربر", callback_data=f"send_acc:{user.id}")]])
            await callback.message.answer(f"✅ **پرداخت با موفقیت انجام شد!**\n\n🛍 سفارش: {selected_plan}\n💰 کسر شده از کیف پول: {price:,} تومان", parse_mode=ParseMode.MARKDOWN)
            try: await bot.send_message(chat_id=ADMIN_ID, text=f"🚨 **سفارش جدید (پرداخت از کیف پول)!**\n👤 {user.first_name}\n🆔 `{user.id}`\n📦 {selected_plan}", reply_markup=admin_kb, parse_mode=ParseMode.MARKDOWN)
            except: pass
        await callback.answer()

    elif data.startswith("send_acc:"):
        target_uid = int(data.split(":")[1])
        await state.set_state(BotStates.WAITING_FOR_ACCOUNT)
        await state.update_data(target_uid=target_uid)
        await callback.message.answer(f"✏️ **لطفاً اطلاعات اکانت/کانفیگ را ارسال کنید:**\n👤 آیدی کاربر: `{target_uid}`", parse_mode=ParseMode.MARKDOWN)
        await callback.answer()

# ------------------- دریافت عکس فیش -------------------
@router.message(F.photo | F.document)
async def handle_photo(message: types.Message, state: FSMContext, bot: Bot):
    current_state = await state.get_state()
    if current_state == BotStates.WAITING_FOR_RECEIPT.state:
        photo_id = message.photo[-1].file_id if message.photo else message.document.file_id
        state_data = await state.get_data()
        order_details = state_data.get('pending_order', 'اکانت سفارشی')
        
        admin_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ ارسال اکانت", callback_data=f"send_acc:{message.from_user.id}")]
        ])
        await bot.send_photo(chat_id=ADMIN_ID, photo=photo_id, caption=f"🛍 **سفارش جدید**\n👤 {message.from_user.first_name}\n🆔 `{message.from_user.id}`\n📦 {order_details}", reply_markup=admin_kb, parse_mode=ParseMode.MARKDOWN)
        await state.clear()
        await message.answer("✅ رسید واریزی شما ارسال شد. سفارش به زودی توسط پشتیبانی تحویل داده می‌شود.")

# ------------------- پردازش پیام‌های متنی -------------------
@router.message(F.text)
async def handle_text(message: types.Message, state: FSMContext, bot: Bot):
    text = message.text.strip()
    user = message.from_user
    chat_type = message.chat.type

    # دستورات ادمین به صورت ریپلای (gift / code)
    if user.id == ADMIN_ID and message.reply_to_message:
        target_user = message.reply_to_message.from_user
        if text.lower().startswith("gift"):
            clean_cmd = text.replace("gift", "").replace(",", "").strip()
            if clean_cmd.isdigit():
                amount = int(clean_cmd)
                await update_user_wallet(target_user.id, amount)
                await message.reply(f"🎁 مبلغ **{amount:,} تومان** هدیه به کیف پول [{target_user.first_name}](tg://user?id={target_user.id}) اضافه شد!", parse_mode=ParseMode.MARKDOWN)
                try: await bot.send_message(target_user.id, f"🎁 **مبلغ {amount:,} تومان هدیه به کیف پول شما اضافه شد!**", parse_mode=ParseMode.MARKDOWN)
                except: pass
                return

        elif text.lower().startswith("code"):
            clean_cmd = text.replace("code", "").replace("%", "").strip()
            if clean_cmd.isdigit():
                percent = int(clean_cmd)
                code_str = f"OFF{percent}-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
                await users_col.update_one({"_id": target_user.id}, {"$push": {"discounts": {"code": code_str, "percent": percent}}}, upsert=True)
                await message.reply(f"✅ کد تخفیف **{percent}%** ساخته شد و به پی‌وی کاربر ارسال گردید.", parse_mode=ParseMode.MARKDOWN)
                try: await bot.send_message(target_user.id, f"🎉 **کد تخفیف اختصاصی {percent}% شما:**\n`{code_str}`", parse_mode=ParseMode.MARKDOWN)
                except: pass
                return

    # وضعیت ارسال اطلاعات توسط ادمین
    current_state = await state.get_state()
    if current_state == BotStates.WAITING_FOR_ACCOUNT.state and user.id == ADMIN_ID:
        state_data = await state.get_data()
        target_uid = state_data.get('target_uid')
        try:
            await bot.send_message(chat_id=target_uid, text=f"🎉 **سفارش شما تحویل داده شد:**\n\n{text}\n\nبا تشکر از خرید شما!", parse_mode=ParseMode.MARKDOWN)
            await users_col.update_one({"_id": target_uid}, {"$push": {"subscriptions": {"name": "سفارش", "expire": "فعال", "details": text}, "history": {"item": "سفارش", "date": datetime.datetime.now().strftime("%Y/%m/%d - %H:%M")}}}, upsert=True)
            await message.answer("✅ اطلاعات با موفقیت برای کاربر ارسال شد.")
        except Exception as e: await message.answer(f"❌ خطا در ارسال: {e}")
        return await state.clear()

    # وضعیت ورود آیدی معرفی‌کننده
    if current_state == BotStates.WAITING_FOR_INVITER.state:
        g_id = await get_group_chat_id()
        if not g_id: return await message.answer("❌ گروه یافت نشد! ربات را در گروه ادمین قرار دهید.")
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ بله، من دعوت کردم (+۵ امتیاز)", callback_data=f"confirm_invite:{user.id}:{text.replace('@', '')}")]])
        await bot.send_message(chat_id=g_id, text=f"📢 **تایید دعوت‌کننده:**\nکاربر [{user.first_name}](tg://user?id={user.id}) اعلام کرده توسط @{text} دعوت شده. آیا تایید می‌کنید؟", reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
        await state.clear()
        return await message.answer("✅ درخواست تایید برای معرفی‌کننده در گروه ارسال شد!")

    # فعالیت گروه (امتیازدهی)
    if chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        await set_group_chat_id(message.chat.id)
        if message.reply_to_message and not message.reply_to_message.from_user.is_bot and text in ['+', '+1', 'امتیاز', 'مفید بود']:
            answerer = message.reply_to_message.from_user
            if user.id != answerer.id:
                await add_user_points(answerer.id, 1.0, 'answer')
                try: await message.answer(f"🌱 پاسخ مفید تشخیص داده شد!\n➕ **۱+ امتیاز به {answerer.first_name} اضافه شد.**")
                except: pass
        await add_user_points(user.id, 0.1, 'chat')
        return

    # منوهای اصلی و فرعی
    if text in ["🏠 منوی اصلی", "منوی اصلی 🏠", "🔙 بازگشت به منوی اصلی"]:
        await message.answer("🏠 **منوی اصلی:**", reply_markup=get_main_menu(), parse_mode=ParseMode.MARKDOWN)

    elif text == "⚡️ خرید فیلترشکن":
        await message.answer("⚡️ **بخش خرید فیلترشکن:**\nنوع سرویس مورد نظر را انتخاب کنید:", reply_markup=get_vpn_menu())

    elif text == "🤖 خرید اشتراک هوش مصنوعی":
        await message.answer("🤖 **سرویس‌های هوش مصنوعی:**\nلطفاً سرویس مورد نظر را انتخاب کنید:", reply_markup=get_ai_menu())

    elif text == "⭐️ خدمات تلگرام و استارز":
        await message.answer("⭐️ **خدمات تلگرام:**\nلطفاً بخش مورد نظر را انتخاب کنید:", reply_markup=get_telegram_menu())

    elif text == "🛍 سایر محصولات":
        await message.answer("🛍 **سایر محصولات و خدمات:**\nدسته‌بندی مورد نظر را انتخاب کنید:", reply_markup=get_other_products_menu())

    elif text == "🎮 بازی و گیمینگ":
        await message.answer("🎮 **بخش گیفت‌کارت‌های بازی:**", reply_markup=get_gaming_menu())

    elif text == "🎬 فیلم و موسیقی":
        await message.answer("🎬 **بخش فیلم و موسیقی:**", reply_markup=get_movie_music_menu())

    elif text == "💳 گیفت‌کارت خرید آنلاین":
        await message.answer("💳 **گیفت‌کارت‌های خرید آنلاین:**", reply_markup=get_shopping_cards_menu())

    elif text == "🛠 ابزارهای تخصصی و طراحی":
        await message.answer("🛠 **ابزارهای طراحی و تخصصی:**", reply_markup=get_design_tools_menu())

    elif text == "🎓 آموزشی و کورس‌ها":
        await message.answer("🎓 **آموزش و دوره‌ها:**", reply_markup=get_education_menu())

    elif text == "✈️️ گردشگری، سفر و اقامت":
        await message.answer("✈️ **گردشگری و سفر:**", reply_markup=get_travel_menu())

    elif text == "👗 مد و پوشاک":
        await message.answer("👗 **مد و پوشاک:**", reply_markup=get_fashion_menu())

    elif text == "🔙 بازگشت به سایر محصولات":
        await message.answer("🛍 **سایر محصولات:**", reply_markup=get_other_products_menu())

    elif text == "💰 کسب درآمد و امتیاز":
        await message.answer("💰 **بخش کسب درآمد و امتیاز:**", reply_markup=get_earn_money_menu())

    elif text == "📋 راهنمای کسب درآمد":
        guide = (
            "📋 **راهنمای کسب درآمد:**\n\n"
            "1️⃣ ارسال هر پیام در گروه: **0.1 امتیاز**\n"
            "2️⃣ پاسخ مفید (علامت `+`): **1 امتیاز کامل**\n"
            "3️⃣ معرفی دوستان به گروه: **5 امتیاز**\n"
            "4️⃣ اول خرید دوست دعوت شده: **5 امتیاز اضافی**"
        )
        await message.answer(guide, parse_mode=ParseMode.MARKDOWN)

    elif text == "🏆 جدول برترین‌ها":
        await message.answer("🏆 **جدول برترین‌ها:**", reply_markup=get_leaderboard_menu())

    elif text == "📊 جدول کلی": await message.answer(await generate_leaderboard('overall'), parse_mode=ParseMode.MARKDOWN)
    elif text == "📅 جدول هفتگی": await message.answer(await generate_leaderboard('weekly'), parse_mode=ParseMode.MARKDOWN)
    elif text == "☀️ جدول روزانه": await message.answer(await generate_leaderboard('daily'), parse_mode=ParseMode.MARKDOWN)
    elif text == "👥 برترین‌های دعوت": await message.answer(await generate_leaderboard('invite'), parse_mode=ParseMode.MARKDOWN)
    elif text == "💡 برترین‌های راهنمایی": await message.answer(await generate_leaderboard('answer'), parse_mode=ParseMode.MARKDOWN)
    elif text == "🔙 بازگشت به کسب درآمد": await message.answer("💰 **کسب درآمد:**", reply_markup=get_earn_money_menu())

    elif text == "⭐️ امتیازات من":
        pts = await get_total_user_points(user.id)
        rank = await get_user_daily_rank(user.id)
        await message.answer(f"👤 **امتیاز شما:** **{pts:.1f} امتیاز**\n🏆 رتبه ۲۴ ساعت اخیر: **{rank}**", parse_mode=ParseMode.MARKDOWN)

    elif text == "👤 حساب و کیف پول":
        bal = await get_user_wallet(user.id)
        await message.answer(f"👤 **حساب کاربری**\n🆔 شناسه: `{user.id}`\n💰 موجودی کیف پول: **{bal:,} تومان**", reply_markup=get_account_menu(), parse_mode=ParseMode.MARKDOWN)

    elif text == "💳 شارژ کیف پول":
        await message.answer(f"💳 **شارژ کیف پول**\nمبلغ واریزی را به کارت زیر واریز و فیش را برای پشتیبانی فرستید:\n\n📌 `{CARD_NUMBER}`\n👤 **{CARD_HOLDER}**\n\n👉 @{ADMIN_USERNAME}", parse_mode=ParseMode.MARKDOWN)

    elif text == "⏳ اشتراک‌های فعال":
        doc = await users_col.find_one({"_id": user.id}, {"subscriptions": 1})
        subs = doc.get("subscriptions", []) if doc else []
        if subs:
            res = "⏳ **اشتراک‌های فعال:**\n\n"
            for s in subs: res += f"🔹 **{s.get('name')}**\n`{s.get('details')}`\n\n"
            await message.answer(res, parse_mode=ParseMode.MARKDOWN)
        else: await message.answer("❌ هیچ اشتراک فعالی ثبت نشده است.")

    elif text == "📦 سوابق خرید":
        doc = await users_col.find_one({"_id": user.id}, {"history": 1})
        hist = doc.get("history", []) if doc else []
        if hist:
            res = "📦 **سوابق خرید:**\n\n"
            for h in hist: res += f"🔸 {h.get('item')} ({h.get('date')})\n"
            await message.answer(res, parse_mode=ParseMode.MARKDOWN)
        else: await message.answer("❌ سابقه خریدی یافت نشد.")

    elif text == "🎁 کد تخفیف":
        doc = await users_col.find_one({"_id": user.id}, {"discounts": 1})
        discs = doc.get("discounts", []) if doc else []
        if discs:
            res = "🎁 **کدهای تخفیف شما:**\n\n"
            for d in discs: res += f"• `{d.get('code')}` ({d.get('percent')}%)\n"
            await message.answer(res, parse_mode=ParseMode.MARKDOWN)
        else: await message.answer("❌ کد تخفیفی ندارید.")

    elif text == "🌐 اشتراک V2Ray حجمی آی‌‌پی ثابت": await message.answer("🌐 **نوع سرویس V2Ray:**", reply_markup=get_v2ray_type_menu())
    elif text == "⭐ اشتراک‌های تک لوکیشن VIP آی‌پی ثابت برای کارهای تخصصی": await message.answer("📍 **انتخاب لوکیشن:**", reply_markup=get_v2ray_locations_menu())
    elif text in V2RAY_LOCATIONS: await message.answer(f"📍 لوکیشن **{text}** انتخاب شد.\nحجم مورد نظر را انتخاب کنید:", reply_markup=get_v2ray_plans_menu())
    elif text == "💡 اشتراک‌های مولتی لوکیشن اقتصادی ارور کانکشن": await message.answer("⚡️ **اشتراک‌های مولتی لوکیشن:**", reply_markup=get_v2ray_multi_plans_menu())
    elif text == "🌀 اکانت ویندسکرایب نامحدود": await message.answer("🌀 **مدت زمان اشتراک:**", reply_markup=get_windscribe_duration_menu())
    elif text in ["🗓 اشتراک ۱ ماهه", "🗓 اشتراک ۱ ساله"]: await message.answer("👤 **تعداد کاربر:**", reply_markup=get_user_count_menu("۱ ماهه" if "۱ ماهه" in text else "۱ ساله"))
    elif text == "⭐ خرید اشتراک پرمیوم تلگرام": await message.answer("⭐ **مدت پرمیوم:**", reply_markup=get_telegram_premium_menu())
    elif text == "🌟 خرید استارز تلگرام": await message.answer("🌟 **بسته استارز:**", reply_markup=get_telegram_stars_menu())
    elif text == "🔙 بازگشت به انتخاب فیلترشکن": await message.answer("⚡️ **خرید فیلترشکن:**", reply_markup=get_vpn_menu())
    elif text == "🔙 بازگشت به نوع V2Ray": await message.answer("🌐 **نوع V2Ray:**", reply_markup=get_v2ray_type_menu())
    elif text == "🔙 بازگشت به انتخاب لوکیشن": await message.answer("📍 **انتخاب لوکیشن:**", reply_markup=get_v2ray_locations_menu())
    elif text == "🔙 بازگشت به انتخاب مدت": await message.answer("🌀 **مدت زمان:**", reply_markup=get_windscribe_duration_menu())
    elif text == "🔙 بازگشت به خدمات تلگرام": await message.answer("⭐️ **خدمات تلگرام:**", reply_markup=get_telegram_menu())

    elif text == "🎧 پشتیبانی و راهنما" or text in ALL_INQUIRY_PRODUCTS or text in AI_SERVICES:
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="💬 ثبت سفارش و استعلام قیمت در پشتیبانی", url=f"https://t.me/{ADMIN_USERNAME}")]])
        caption_text = (
            f"🛍 **{text}**\n\n"
            f"به دلیل نوسانات قیمت ارز و دلار و برای فعال‌سازی دقیق روی اکانت شخصی شما، لطفاً جهت استعلام قیمت روز و خرید به پشتیبانی پیام دهید:\n\n"
            f"👉 @{ADMIN_USERNAME}"
        )
        await message.answer(caption_text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)

    elif "تومان" in text and ("کاربره" in text or "اشتراک" in text or "استارز" in text or "پرمیوم" in text):
        clean_price = re.sub(r'[^\d]', '', text)
        if clean_price.isdigit():
            price = int(clean_price)
            item_title = text.split("-")[0].strip()
            await state.update_data(pending_order=item_title)
            user_bal = await get_user_wallet(user.id)
            await message.answer(f"🛍 **سفارش:** {item_title}\n💰 **قیمت:** {price:,} تومان\n💳 **موجودی کیف پول شما:** {user_bal:,} تومان", reply_markup=build_payment_keyboard(price, user_bal), parse_mode=ParseMode.MARKDOWN)

    elif text == "🔗 ثبت معرفی‌کننده":
        await state.set_state(BotStates.WAITING_FOR_INVITER)
        await message.answer("✏️ لطفاً آیدی شخصی که شما را به گروه دعوت کرده وارد کنید:")

# ------------------- راه‌اندازی ربات -------------------
async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    print("🤖 Bot connected to MongoDB and running seamlessly with Aiogram 3...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
