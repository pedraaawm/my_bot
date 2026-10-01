import asyncio
import logging
import os
import random
import string
from aiogram import Bot, Dispatcher, F
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.filters import Command
from aiogram.types import Message
from pymongo import MongoClient

# ------------------- تنظیمات اولیه -------------------
API_TOKEN = "8909439742:AAGLea9vDRXufHxbCXIZ8n7yGY2SmQVE0L8"
ADMIN_ID = 8846204367  # آیدی عددی ادمین

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# اتصال به دیتابیس ابری MongoDB Atlas با اطلاعات شما
MONGO_URL = "mongodb+srv://Pedraaawm_db_user:QJzZfOPM7cQRaVAd@cluster0.wul6ohg.mongodb.net/?appName=Cluster0"
client = MongoClient(MONGO_URL)
db = client["my_bot_database"]
wallets_collection = db["wallets"]  # ذخیره موجودی کیف پول‌ها
discounts_collection = db["discounts"]  # ذخیره کدهای تخفیف


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
  """تبدیل اعداد فارسی و عربی به انگلیسی"""
  translation_table = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
  return text.translate(translation_table)


def clean_input(text: str) -> str:
  """حذف کاما، تومان، ریال، درصد و فضاهای خالی"""
  text = fa_to_en_num(text)
  for term in [",", "تومان", "ریال", "%", "درصد"]:
    text = text.replace(term, "")
  return text.strip()


def generate_discount_code(percent: int) -> str:
  """تولید کد تخفیف انحصاری"""
  chars = string.ascii_uppercase + string.digits
  return f"OFF{percent}-" + "".join(random.choices(chars, k=6))


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
        "❌ **روش صحیح هدیه تومانی:**\n"
        "روی پیام کاربر ریپلای کنید:\n"
        "`gift 50000` یا `/gift 50,000 تومان`",
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


# ------------------- ۲. ارسال کد تخفیف انحصاری به پی‌وی (code / /code) -------------------
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
        "❌ **روش صحیح کد تخفیف:**\n"
        "روی پیام کاربر ریپلای کنید:\n"
        "`code 20%` یا `/code 20 درصد`",
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
        text=(
            f"⚠️ کاربر {user_link} هنوز ربات را استارت نکرده است! لطفاً ابتدا"
            " ربات را در پی‌وی استارت کند تا کد ارسال شود."
        ),
        reply_to_message_id=message.reply_to_message.message_id,
        parse_mode="Markdown",
    )


# ------------------- ۳. بررسی موجودی کیف پول -------------------
@dp.message(Command("balance"))
@dp.message(F.text.in_(["موجودی", "کیف پول", "balance", "/balance"]))
async def handle_check_balance(message: Message):
  user_id = message.from_user.id
  balance = get_wallet(user_id)
  await message.reply(
      f"💳 **موجودی کیف پول شما:**\n\n💰 **{balance:,} تومان**",
      parse_mode="Markdown",
  )


# ------------------- اجرای ربات -------------------
async def main():
  logging.basicConfig(level=logging.INFO)
  print("🤖 ربات متصل به دیتابیس ابری MongoDB آماده به کار است...")
  await dp.start_polling(bot)


if __name__ == "__main__":
  asyncio.run(main())
