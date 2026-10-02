import asyncio
import json
import logging
import os
import random
import string
from aiogram import Bot, Dispatcher, F
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.filters import Command
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

# ------------------- تنظیمات اولیه -------------------
API_TOKEN = os.getenv("BOT_TOKEN")  # خواندن توکن از متغیرهای محیطی رایلی
ADMIN_ID = 8846204367  # آیدی عددی ادمین

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

DATA_FILE = "bot_data.json"

user_wallets = {}  # {user_id: amount}
user_discounts = {}  # {user_id: [list of codes]}


# ------------------- توابع کمکی -------------------
def load_data():
  global user_wallets, user_discounts
  if os.path.exists(DATA_FILE):
    try:
      with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        user_wallets = {int(k): v for k, v in data.get("wallets", {}).items()}
        user_discounts = {
            int(k): v for k, v in data.get("discounts", {}).items()
        }
    except Exception as e:
      logging.error(f"خطا در بارگذاری داده‌ها: {e}")


def save_data():
  try:
    data = {"wallets": user_wallets, "discounts": user_discounts}
    with open(DATA_FILE, "w", encoding="utf-8") as f:
      json.dump(data, f, ensure_ascii=False, indent=4)
  except Exception as e:
    logging.error(f"خطا در ذخیره داده‌ها: {e}")


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


# ------------------- کیبورد منوی اصلی -------------------
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


# ------------------- هندلر دستور استارت و منوی اصلی -------------------
@dp.message(Command("start"))
@dp.message(F.text.in_(["منوی اصلی 🏠", "/menu"]))
async def cmd_start(message: Message):
  welcome_text = (
      "سلام! 👋 خوش آمدید.\n\n"
      "🤖 به ربات جامع ما خوش آمدید. از طریق دکمه‌های زیر می‌توانید به بخش‌های"
      " مختلف دسترسی داشته باشید 👇"
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

  user_wallets[target_user.id] = user_wallets.get(target_user.id, 0) + amount
  save_data()

  user_link = f"[{target_user.first_name}](tg://user?id={target_user.id})"

  await message.chat.send_message(
      text=(
          f"🎁 **هدیه نقدی برای کاربر ثبت شد!**\n\n"
          f"مبلغ **{amount:,} تومان** به کیف پول {user_link} اضافه شد. 🎉\n"
          f"💰 موجودی جدید: **{user_wallets[target_user.id]:,} تومان**"
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

    if target_user.id not in user_discounts:
      user_discounts[target_user.id] = []
    user_discounts[target_user.id].append(
        {"code": discount_code, "percent": percent}
    )
    save_data()

    user_link = f"[{target_user.first_name}](tg://user?id={target_user.id})"
    await message.chat.send_message(
        text=(
            f"✅ کد تخفیف **{percent}%** انحصاری برای کاربر {user_link} در"
            " **پی‌‌وی (PV)** ارسال شد! 📩"
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


# ------------------- ۳. بررسی موجودی کیف پول و امتیازات -------------------
@dp.message(Command("balance"))
@dp.message(
    F.text.in_(
        ["موجودی", "کیف پول", "balance", "/balance", "امتیازات من ⭐"]
    )
)
async def handle_check_balance(message: Message):
  user_id = message.from_user.id
  balance = user_wallets.get(user_id, 0)
  await message.reply(
      f"💳 **موجودی کیف پول شما:**\n\n💰 **{balance:,} تومان**",
      parse_mode="Markdown",
  )


# ------------------- ۴. دکمه‌های منوی شیشه‌ای و متنی -------------------
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
      " حتماً در کانال ما عضو شوید.",
      parse_mode="Markdown",
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
  load_data()
  print("🤖 ربات آماده به کار است...")
  await dp.start_polling(bot)


if __name__ == "__main__":
  asyncio.run(main())
