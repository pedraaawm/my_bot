import logging
import datetime
import json
import os
import shutil
import re
import asyncio
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ChatType, ParseMode

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

ALL_INQUIRY_PRODUCTS = [
    "🎮 گیفت‌کارت ایکس‌باکس", "🎮 گیفت‌کارت پلی‌استیشن", "🎮 گیفت‌کارت ولورانت",
    "🎮 گیفت‌کارت استیم", "💬 دیسکورد", "🎮 گیفت‌کارت نینتندو",
    "🎮 گیفت‌کارت ریزر گلد", "🎮 گیفت‌کارت رابلاکس", "🎮 گیفت‌کارت فورتنایت",
    "🎬 نتفلیکس", "🎵 اسپاتیفای", "🎁 گیفت‌کارت اسپاتیفای",
    "▶️ یوتیوب پرمیوم", "🎬 دیزنی‌پلاس", "🎁 گیفت‌کارت دیزنی‌پلاس", "🎁 گیفت‌کارت نتفلیکس",
    "🛒 گیفت‌کارت ای‌‌بی (eBay)", "🍎 گیفت‌کارت اپل", "📦 گیفت‌کارت آمازون",
    "🏪 گیفت‌کارت وال‌مارت", "👑 گیفت‌کارت آمازون پرایم", "🛒 گیفت‌کارت بست‌بای",
    "🎨 فیگما (Figma)", "🖌 ادوبی فتوشاپ", "🎨 کنوا پرو (Canva Pro)",
    "🎓 اسکیل‌شر (Skillshare)", "📚 یودمی (Udemy)",
    "🏡 گیفت‌کارت ایربی‌ان‌بی (Airbnb)", "🏨 گیفت‌کارت بوکینگ (Booking.com)",
    "🛍 گیفت‌کارت زالاندو (Zalando)", "👗 گیفت‌کارت ایسوس (ASOS)"
]

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
    "🎁 ۶ ماهه - ۱ کاربره": {"price": 590000},
    "🎁 ۶ ماهه - ۲ کاربره": {"price": 990000}
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

# ------------------- تنظیمات دیتابیس -------------------
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
        except: pass
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
    with open("bot_data_temp.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    shutil.move("bot_data_temp.json", DATA_FILE)

(user_wallets, user_subscriptions, user_history, point_logs, 
 registered_inviters, user_referrals, purchased_referrals, group_chat_id, user_names) = load_data()

# ------------------- توابع کمکی -------------------
def update_user_info(user):
    if user and not user.is_bot:
        user_names[user.id] = {"first_name": user.first_name or "کاربر", "username": user.username or ""}
        save_data()

def format_points(pts: float) -> str:
    pts = round(pts, 2)
    return str(int(pts)) if pts.is_integer() else f"{pts:.1f}"

def add_user_points(user_id: int, points: float, p_type: str):
    if points > 0:
        point_logs.append({"user_id": user_id, "points": points, "type": p_type, "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
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
        if u_id == user_id: return rank
    return len(sorted_users) + 1

def check_and_reward_referral(buyer_id: int):
    if buyer_id in user_referrals and buyer_id not in purchased_referrals:
        inviter_id = user_referrals[buyer_id]
        add_user_points(inviter_id, 5.0, 'invite')
        purchased_referrals.add(buyer_id)
        save_data()
        return inviter_id
    return None

# ------------------- کیبوردها (مهاجرت به Aiogram) -------------------
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

def get_ai_menu():
    return build_reply_kb([
        ["🤖 چت‌‌جی‌پی‌تی (ChatGPT)", "🧠 کلاد (Claude)"],
        ["🚀 گراک (Grok)", "💻 کرسر (Cursor)"],
        ["✨ جمنای (Gemini)", "🔍 پرپلکسیتی (Perplexity)"],
        ["🎨 میدجرنی (Midjourney)", "📝 گرمرلی (Grammarly)"],
        ["🔙 بازگشت به منوی اصلی"]
    ])

def get_telegram_menu(): return build_reply_kb([["⭐ خرید اشتراک پرمیوم تلگرام", "🌟 خرید استارز تلگرام"], ["🔙 بازگشت به منوی اصلی"]])
def get_telegram_premium_menu(): return build_reply_kb([["🗓 ۳ ماهه پرمیوم", "🗓 ۶ ماهه پرمیوم"], ["🗓 ۱۲ ماهه پرمیوم"], ["🔙 بازگشت به خدمات تلگرام"]])
def get_telegram_stars_menu(): return build_reply_kb([["⭐ ۱۰۰ تا استارز", "⭐ ۲۰۰ تا استارز"], ["⭐ ۵۰۰ تا استارز", "⭐ ۱۰۰۰ تا استارز"], ["🔙 بازگشت به خدمات تلگرام"]])
def get_earn_money_menu(): return build_reply_kb([["🔗 ثبت معرفی‌کننده", "📋 راهنمای کسب درآمد"], ["🏆 جدول برترین‌ها", "⭐️ امتیازات من"], ["🔙 بازگشت به منوی اصلی"]])
def get_account_menu(): return build_reply_kb([["💳 شارژ کیف پول", "⏳ اشتراک‌های فعال"], ["📦 سوابق خرید", "🎁 کد تخفیف"], ["🔙 بازگشت به منوی اصلی"]])
def get_vpn_menu(): return build_reply_kb([["🌀 اکانت ویندسکرایب نامحدود"], ["🌐 اشتراک V2Ray حجمی آی‌‌پی ثابت"], ["🔙 بازگشت به منوی اصلی"]])
def get_v2ray_type_menu(): return build_reply_kb([["⭐ اشتراک‌های تک لوکیشن VIP آی‌پی ثابت برای کارهای تخصصی"], ["💡 اشتراک‌های مولتی لوکیشن اقتصادی ارور کانکشن"], ["🔙 بازگشت به انتخاب فیلترشکن"]])
def get_v2ray_locations_menu(): return build_reply_kb([["🇩🇪 آلمان", "🇫🇮 فنلاند"], ["🇫🇷 فرانسه", "🇺🇸 آمریکا"], ["🇹🇷 ترکیه", "🇳🇱 هلند"], ["🔙 بازگشت به نوع V2Ray"]])
def get_windscribe_duration_menu(): return build_reply_kb([["🗓 اشتراک ۱ ماهه", "🗓 اشتراک ۱ ساله"], ["🔥 تخفیف‌های روز و اکانت‌های ویژه"], ["🔙 بازگشت به انتخاب فیلترشکن"]])

def get_v2ray_plans_menu():
    btns = [[f"{p} - {pr:,} تومان"] for p, pr in V2RAY_PRICES.items()]
    btns.append(["🔙 بازگشت به انتخاب لوکیشن"])
    return build_reply_kb(btns)

def get_v2ray_multi_plans_menu():
    btns = [[f"{p} - {pr:,} تومان"] for p, pr in V2RAY_MULTI_PRICES.items()]
    btns.append(["🔙 بازگشت به نوع V2Ray"])
    return build_reply_kb(btns)

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

# ------------------- سیستم وضعیت‌ها (FSM) -------------------
class BotStates(StatesGroup):
    WAITING_FOR_RECEIPT = State()
    WAITING_FOR_INVITER = State()
    WAITING_FOR_ACCOUNT = State()

router = Router()

# ------------------- دستورات -------------------
@router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    update_user_info(message.from_user)
    await state.clear()
    await message.answer(f"سلام {message.from_user.first_name} عزیز! 👋\nبه فروشگاه خوش آمدید.", reply_markup=get_main_menu())

# ------------------- پردازش کالبک‌ها -------------------
@router.callback_query()
async def handle_callback(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    data = callback.data
    user = callback.from_user
    update_user_info(user)
    
    if data.startswith("confirm_invite:"):
        _, new_user_id, target_username_or_id = data.split(":")
        new_user_id = int(new_user_id)
        
        is_target = False
        if target_username_or_id.isdigit() and int(target_username_or_id) == user.id: is_target = True
        elif (user.username or "").lower() == target_username_or_id.lower(): is_target = True

        if not is_target:
            return await callback.answer("❌ این دکمه فقط برای شخص دعوت‌کننده است!", show_alert=True)

        add_user_points(user.id, 5.0, 'invite')
        registered_inviters.add(new_user_id)
        user_referrals[new_user_id] = user.id
        save_data()
        await callback.answer("🎉 تایید شد! ۵ امتیاز هدیه به حساب شما اضافه شد.", show_alert=True)
        try: await callback.message.delete()
        except: pass

    elif data.startswith("buy_card:"):
        parts = data.split(":")
        pay_amount, wallet_deduct = int(parts[1]), int(parts[2]) if len(parts) > 2 else 0
        state_data = await state.get_data()
        
        await state.set_state(BotStates.WAITING_FOR_RECEIPT)
        await state.update_data(pay_amount=pay_amount, wallet_deduct=wallet_deduct)
        text = f"💳 **پرداخت سفارش**\n\n📦 **سفارش:** {state_data.get('pending_order', 'اشتراک')}\n💰 **قابل واریز:** {pay_amount:,} تومان\n📌 **شماره کارت:**\n`{CARD_NUMBER}`\n\n📸 تصویر فیش را ارسال کنید."
        await callback.message.answer(text, parse_mode=ParseMode.MARKDOWN)
        await callback.answer()

    elif data.startswith("pay_from_wallet:"):
        price = int(data.split(":")[1])
        user_balance = user_wallets.get(user.id, 0)
        state_data = await state.get_data()
        selected_plan = state_data.get('pending_order', 'اشتراک')

        if user_balance < price:
            await callback.answer("❌ موجودی کیف پول کافی نیست!", show_alert=True)
        else:
            user_wallets[user.id] -= price
            save_data()
            inviter_id = check_and_reward_referral(user.id)
            if inviter_id:
                try: await bot.send_message(chat_id=inviter_id, text="🎉 **خبر خوب!** دوست شما خرید کرد و **۵ امتیاز** گرفتی!")
                except: pass

            admin_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📦 ارسال اکانت", callback_data=f"send_acc:{user.id}")]])
            await callback.message.answer(f"✅ **پرداخت با موفقیت انجام شد!**\n\n🛍 سفارش: {selected_plan}\n💰 کسر شده: {price:,} تومان", parse_mode=ParseMode.MARKDOWN)
            try: await bot.send_message(chat_id=ADMIN_ID, text=f"🚨 **سفارش جدید (کیف پول)!**\n👤 {user.first_name}\n🆔 `{user.id}`\n📦 {selected_plan}", reply_markup=admin_kb, parse_mode=ParseMode.MARKDOWN)
            except: pass
        await callback.answer()

    elif data.startswith("send_acc:"):
        target_uid = int(data.split(":")[1])
        await state.set_state(BotStates.WAITING_FOR_ACCOUNT)
        await state.update_data(target_uid=target_uid)
        await callback.message.answer(f"✏️ **لطفاً اطلاعات اکانت را ارسال کنید:**\n👤 آیدی کاربر: `{target_uid}`", parse_mode=ParseMode.MARKDOWN)
        await callback.answer()

# ------------------- دریافت تصاویر / رسید پرداخت -------------------
@router.message(F.photo | F.document)
async def handle_photo(message: types.Message, state: FSMContext, bot: Bot):
    current_state = await state.get_state()
    if current_state == BotStates.WAITING_FOR_RECEIPT.state:
        photo_id = message.photo[-1].file_id if message.photo else message.document.file_id
        state_data = await state.get_data()
        order_details = state_data.get('pending_order', 'اکانت سفارشی')
        wallet_deduct = state_data.get('wallet_deduct', 0)
        
        admin_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ تایید و ارسال", callback_data=f"send_acc:{message.from_user.id}")]
        ])
        await bot.send_photo(chat_id=ADMIN_ID, photo=photo_id, caption=f"🛍 **سفارش جدید**\n👤 {message.from_user.first_name}\n🆔 `{message.from_user.id}`\n📦 {order_details}", reply_markup=admin_kb, parse_mode=ParseMode.MARKDOWN)
        await state.clear()
        await message.answer("✅ رسید ارسال شد. سفارش شما به زودی پردازش می‌شود.")

# ------------------- پردازش پیام‌های متنی -------------------
@router.message(F.text)
async def handle_text(message: types.Message, state: FSMContext, bot: Bot):
    global group_chat_id
    text = message.text.strip()
    user = message.from_user
    chat_type = message.chat.type

    # وضعیت‌های ادمین و معرفی‌کننده
    current_state = await state.get_state()
    if current_state == BotStates.WAITING_FOR_ACCOUNT.state and user.id == ADMIN_ID:
        state_data = await state.get_data()
        target_uid = state_data.get('target_uid')
        try:
            await bot.send_message(chat_id=target_uid, text=f"🎉 **سفارش شما تحویل داده شد:**\n\n{text}\n\nبا تشکر از خرید شما!", parse_mode=ParseMode.MARKDOWN)
            user_subscriptions.setdefault(target_uid, []).append({"name": "سفارش", "expire": "فعال", "details": text})
            save_data()
            await message.answer("✅ اطلاعات برای کاربر ارسال شد.")
        except Exception as e: await message.answer(f"❌ خطا: {e}")
        return await state.clear()

    if current_state == BotStates.WAITING_FOR_INVITER.state:
        if not group_chat_id: return await message.answer("❌ گروه پیدا نشد!")
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ بله، من دعوت کردم (+۵ امتیاز)", callback_data=f"confirm_invite:{user.id}:{text.replace('@', '')}")]])
        await bot.send_message(chat_id=group_chat_id, text=f"📢 **تایید دعوت‌کننده:**\nکاربر [{user.first_name}](tg://user?id={user.id}) اعلام کرده توسط @{text} دعوت شده. تایید می‌کنید؟", reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
        await state.clear()
        return await message.answer("✅ درخواست تایید در گروه ارسال شد!")

    # مدیریت پیام‌های گروه
    if chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        if group_chat_id != message.chat.id:
            group_chat_id = message.chat.id
            save_data()
        if message.reply_to_message and not message.reply_to_message.from_user.is_bot and text in ['+', '+1', 'امتیاز', 'مفید بود']:
            answerer = message.reply_to_message.from_user
            if user.id != answerer.id:
                add_user_points(answerer.id, 1.0, 'answer')
                try: await message.answer(f"🌱 پاسخ مفید تشخیص داده شد!\n➕ **۱+ امتیاز به {answerer.first_name} اضافه شد.**")
                except: pass
        add_user_points(user.id, 0.1, 'chat')
        return

    # منوهای اصلی و ناوبری
    if text == "🔙 بازگشت به منوی اصلی": await message.answer("🏠 **منوی اصلی:**", reply_markup=get_main_menu())
    elif text == "⚡️ خرید فیلترشکن": await message.answer("⚡️ نوع سرویس را انتخاب کنید:", reply_markup=get_vpn_menu())
    elif text == "🤖 خرید اشتراک هوش مصنوعی": await message.answer("🤖 لطفاً ابزار مورد نظر را انتخاب کنید:", reply_markup=get_ai_menu())
    elif text == "⭐️ خدمات تلگرام و استارز": await message.answer("⭐️ لطفاً بخش مورد نظر را انتخاب کنید:", reply_markup=get_telegram_menu())
    elif text == "💰 کسب درآمد و امتیاز": await message.answer("💰 لطفاً یک گزینه انتخاب کنید:", reply_markup=get_earn_money_menu())
    elif text == "👤 حساب و کیف پول": 
        await message.answer(f"👤 **حساب کاربری**\n💰 موجودی: **{user_wallets.get(user.id, 0):,} تومان**", reply_markup=get_account_menu(), parse_mode=ParseMode.MARKDOWN)
    
    # منوهای فرعی V2ray و ویندسکرایب
    elif text == "🌐 اشتراک V2Ray حجمی آی‌پی ثابت": await message.answer("🌐 نوع سرویس:", reply_markup=get_v2ray_type_menu())
    elif text == "⭐ اشتراک‌های تک لوکیشن VIP آی‌پی ثابت برای کارهای تخصصی": await message.answer("📍 انتخاب لوکیشن:", reply_markup=get_v2ray_locations_menu())
    elif text in V2RAY_LOCATIONS: await message.answer(f"📍 لوکیشن: **{text}**\nحجم مورد نظر را انتخاب کنید:", reply_markup=get_v2ray_plans_menu())
    elif text == "💡 اشتراک‌های مولتی لوکیشن اقتصادی ارور کانکشن": await message.answer("⚡️ اشتراک‌های مولتی لوکیشن:", reply_markup=get_v2ray_multi_plans_menu())
    elif text == "🌀 اکانت ویندسکرایب نامحدود": await message.answer("🌀 مدت زمان اشتراک:", reply_markup=get_windscribe_duration_menu())
    elif text in ["🗓 اشتراک ۱ ماهه", "🗓 اشتراک ۱ ساله"]: await message.answer(f"👤 انتخاب تعداد کاربر:", reply_markup=get_user_count_menu("۱ ماهه" if "۱ ماهه" in text else "۱ ساله"))

    # استعلام و ارجاع به پشتیبانی
    elif text == "🎧 پشتیبانی و راهنما" or text in ALL_INQUIRY_PRODUCTS or text in AI_SERVICES:
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="💬 ارتباط با پشتیبانی", url=f"https://t.me/{ADMIN_USERNAME}")]])
        await message.answer(f"🛍 درخواست شما برای **{text}** ثبت اولیه شد.\nبرای تکمیل فرآیند و استعلام قیمت روز به پشتیبانی پیام دهید.", reply_markup=kb, parse_mode=ParseMode.MARKDOWN)

    # تشخیص خرید بر اساس متن قیمت
    elif "تومان" in text and ("کاربره" in text or "اشتراک" in text or "استارز" in text or "پرمیوم" in text):
        clean_price = re.sub(r'[^\d]', '', text)
        if clean_price.isdigit():
            price = int(clean_price)
            item_title = text.split("-")[0].strip()
            await state.update_data(pending_order=item_title)
            user_bal = user_wallets.get(user.id, 0)
            await message.answer(f"🛍 **سفارش:** {item_title}\n💰 **قیمت:** {price:,} تومان\n💳 **موجودی شما:** {user_bal:,} تومان", reply_markup=build_payment_keyboard(price, user_bal), parse_mode=ParseMode.MARKDOWN)

    # دکمه‌های متفرقه
    elif text == "🔗 ثبت معرفی‌کننده":
        await state.set_state(BotStates.WAITING_FOR_INVITER)
        await message.answer("✏️ لطفاً آیدی شخصی که شما را دعوت کرده بفرستید:")
    elif text == "⏳ اشتراک‌های فعال":
        subs = user_subscriptions.get(user.id, [])
        if subs: await message.answer("\n".join([f"🔹 {s['name']} | {s['expire']}\n`{s['details']}`" for s in subs]), parse_mode=ParseMode.MARKDOWN)
        else: await message.answer("❌ اشتراک فعالی ندارید.")

# ------------------- راه‌اندازی ربات -------------------
async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    print("🤖 Bot is running with Aiogram 3...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
