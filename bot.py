import asyncio
import logging
import os
import random
import string
from aiogram import Bot, Dispatcher, F
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.filters import Command
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup
from pymongo import MongoClient

# ------------------- تنظیمات اولیه -------------------
API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8846204367  # آیدی عددی ادمین

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# اتصال به دیتابیس ابری MongoDB Atlas
MONGO_URL = os.getenv(
    "MONGO_URI",
    "mongodb+srv://Pedraaawm_db_user:QJzZfOPM7cQRaVAd@cluster0.wul6ohg.mongodb.net/?appName=Cluster0",
)
client = MongoClient(MONGO_URL)
db = client["my_bot_database"]
wallets_collection = db["wallets"]  # ذخیره موجودی کیف پول‌ها
discounts_collection = db["discounts"]  # ذخیره کدهای تخفیف

# ------------------- کیبوردها و منوها (کامل و به‌روز) -------------------
main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="راهنمای کسب درآمد 📋"),
            KeyboardButton(text="ثبت معرفی‌کننده 🔗"),
        ],
        [
            KeyboardButton(text="معرفی کانال و گروه 📢"),
            KeyboardButton(text="امتیازات من ⭐"),
        ],
        [
            KeyboardButton(text="جدول برترین‌ها 🏆"),
            KeyboardButton(text="منوی اصلی 🏠"),
        ],
    ],
    resize_keyboard=True,
)


# ------------------- توابع کمکی (دیتابیس ابری) -------------------
def get_wallet(user_id: int) -> int:
  user_data = wallets_collection.find_one({"user_id": user_id})
  return user_data["balance"] if user_data else 0


def update_wallet(user_id: int, amount: int):
  current = get_wallet(user_id)
  new_balance = current + amount
  wallets_collection.update_one(
      {"user_id": user_id}, {"$set": {"balance": new_balance}}, upsert=True
  )
  return new_balance


def add_discount_to_db(user_id: int, code: str, percent: int):
  discounts_collection.insert_one(
      {"user_id": user_id, "code": code, "percent": percent}
  )


def fa_to_en_num(text: str) -> str:
  translation_table = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
  return text.translate(translation_table)


def clean_input(text: str) -> str:
  text = fa_to_en_num(text)
  for term in [",", "تومان", "ریال", "%", "درصد"]:
    text = text.replace(term, "")
  return text.strip()


def generate_discount_code(percent: int) -> str:
  chars = string.ascii_uppercase + string.digits
  return f"OFF{percent}-" + "".join(random.choices(chars, k=6))


# ------------------- هندلر دستور استارت و پیام خوش‌آمدگویی -------------------
@dp.message(Command("start"))
@dp.message(F.text.in_(["منوی اصلی 🏠", "/menu"]))
async def cmd_start(message: Message):
  welcome_text = (
      "سلام! 👋 خوش آمدید.\n\n"
      "🤖 به ربات جامع ما خوش آمدید. از طریق دکمه‌های زیر می‌توانید به بخش‌های"
      " مختلف دسترسی داشته باشید و از امکانات ربات استفاده کنید 👇"
  )
  await message.reply(
      welcome_text, reply_markup=main_menu_keyboard, parse_mode="Markdown"
  )


# ------------------- ۱. هدیه تومانی مستقیم در گروه (gift / /gift) -------------------
@dp.message(
    F.text.func(
        lambda t: t
        and (t.lower().startswith("gift") or t.lower().startswith("/gift"))
    )
)
async def handle_cash_gift(message: Message):
  if message.from_user.id != ADMIN_ID:
    return

  if not message.reply_to_message:
    await message.reply(
        "❌ لطفاً این دستور را روی پیام کاربر مورد نظر **ریپلای** کنید!",
        parse_mode="Markdown",
    )
    return

  cleaned_text = clean_input(message.text)
  parts = cleaned_text.split()

  if len(parts) < 2 or not parts[1].isdigit():
    await message.reply(
        "❌ **روش صحیح هدیه تومانی:**\nروی پیام کاربر ریپلای کنید:\n`gift"
        " 50000`",
        parse_mode="Markdown",
    )
    return

  amount = int(parts[1])
  target_user = message.reply_to_message.from_user

  if target_user.is_bot:
    await message.reply(
        "❌ نمی‌توانید به ربات هدیه بدهید!", parse_mode="Markdown"
    )
    return

  new_balance = update_wallet(target_user.id, amount)
  user_link = f"[{target_user.first_name}](tg://user?id={target_user.id})"

  await message.chat.send_message(
      text=(
          f"🎁 **هدیه نقدی برای کاربر ثبت شد!**\n\n"
          f"مبلغ **{amount:,} تومان** به کیف پول {user_link} اضافه شد. 🎉\n"
          f"💰 موجودی جدید: **{new_balance:,} تومان**"
      ),
      reply_to_message_id=message.reply_to_message.message_id,
      parse_mode="Markdown",
  )


# ------------------- ۲. ارسال کد تخفیف انحصاری به پی‌وی -------------------
@dp.message(
    F.text.func(
        lambda t: t
        and (t.lower().startswith("code") or t.lower().startswith("/code"))
    )
)
async def handle_send_discount_code(message: Message):
  if message.from_user.id != ADMIN_ID:
    return

  if not message.reply_to_message:
    await message.reply(
        "❌ لطفاً این دستور را روی پیام کاربر مورد نظر **ریپلای** کنید!",
        parse_mode="Markdown",
    )
    return

  cleaned_text = clean_input(message.text)
  parts = cleaned_text.split()

  if len(parts) < 2 or not parts[1].isdigit():
    await message.reply(
        "❌ **روش صحیح کد تخفیف:**\nروی پیام کاربر ریپلای کنید:\n`code 20%`",
        parse_mode="Markdown",
    )
    return

  percent = int(parts[1])
  target_user = message.reply_to_message.from_user

  if target_user.is_bot:
    await message.reply(
        "❌ نمی‌توان برای ربات کد ارسال کرد!", parse_mode="Markdown"
    )
    return

  discount_code = generate_discount_code(percent)

  try:
    await bot.send_message(
        chat_id=target_user.id,
        text=(
            f"🎉 **کد تخفیف اختصاصی برای شما!**\n\n"
            f"شما یک کد تخفیف **{percent}% درصدی** دریافت کردید. 🎁\n\n"
            f"🔑 **کد انحصاری شما:**\n`{discount_code}`"
        ),
        parse_mode="Markdown",
    )

    add_discount_to_db(target_user.id, discount_code, percent)
    user_link = f"[{target_user.first_name}](tg://user?id={target_user.id})"
    await message.chat.send_message(
        text=(
            f"✅ کد تخفیف **{percent}%** انحصاری برای کاربر {user_link} در"
            " **پی‌وی (PV)** ارسال شد! 📩"
        ),
        reply_to_message_id=message.reply_to_message.message_id,
        parse_mode="Markdown",
    )

  except (TelegramForbiddenError, TelegramBadRequest):
    user_link = f"[{target_user.first_name}](tg://user?id={target_user.id})"
    await message.chat.send_message(
        text=f"⚠️ کاربر {user_link} هنوز ربات را استارت نکرده است!",
        reply_to_message_id=message.reply_to_message.message_id,
        parse_mode="Markdown",
    )


# ------------------- ۳. بررسی موجودی کیف پول -------------------
@dp.message(Command("balance"))
@dp.message(
    F.text.in_(
        ["موجودی", "کیف پول", "balance", "/balance", "امتیازات من ⭐"]
    )
)
async def handle_check_balance(message: Message):
  user_id = message.from_user.id
  balance = get_wallet(user_id)
  await message.reply(
      f"💳 **موجودی کیف پول شما:**\n\n💰 **{balance:,} تومان**",
      parse_mode="Markdown",
  )


# ------------------- ۴. سایر دکمه‌های منو -------------------
@dp.message(F.text == "راهنمای کسب درآمد 📋")
async def menu_guide(message: Message):
  await message.reply(
      "📋 **راهنمای کسب درآمد:**\n\nبا دعوت دوستان خود به ربات می‌توانید پاداش"
      " دریافت کنید.",
      parse_mode="Markdown",
  )


@dp.message(F.text == "ثبت معرفی‌کننده 🔗")
async def menu_referral(message: Message):
  await message.reply(
      "🔗 لطفاً لینک یا آیدی معرفی‌کننده خود را بفرستید.",
      parse_mode="Markdown",
  )


@dp.message(F.text == "معرفی کانال و گروه 📢")
async def menu_channels(message: Message):
  await message.reply(
      "📢 **کانال‌ها و گروه‌های رسمی ما:**\n\nبرای اطلاع از آخرین اخبار و تخفیف‌ها"
      " حتماً در کانال ما عضو شوید:\n👉 [@YourChannelID](https://t.me/your_channel)",
      parse_mode="Markdown",
      disable_web_page_preview=True,
  )


@dp.message(F.text == "جدول برترین‌ها 🏆")
async def menu_leaderboard(message: Message):
  await message.reply(
      "🏆 **جدول برترین‌ها:**\n\nبه زودی کاربران برتر اینجا نمایش داده می‌شوند.",
      parse_mode="Markdown",
  )


# ------------------- اجرای ربات -------------------
async def main():
  logging.basicConfig(level=logging.INFO)
  print("🤖 ربات متصل به دیتابیس ابری MongoDB آماده به کار است...")
  await dp.start_polling(bot)


if __name__ == "__main__":
  asyncio.run(main())
