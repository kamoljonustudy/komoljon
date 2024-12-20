from aiogram import types, Dispatcher, Bot
from aiogram.filters import Command
import asyncio
import random
import requests
from aiogram.types import KeyboardButton

TOKEN = "8010264669:AAGFjR6axBEzyFsSjv9oWJdKqUHehLboY6M"
bot = Bot(token=TOKEN)
dp = Dispatcher()

user_data = {}

email = "kamoljon817@gmail.com"
password = "4mL0hI0RyPXLkrBPlbNIoFgxdH1pXvvF8LLut7aG"


def get_eskiz_token(email, password):
    url = "https://notify.eskiz.uz/api/auth/login"
    payload = {
        'email': email,
        'password': password
    }
    headers = {}
    response = requests.post(url, data=payload, headers=headers)
    if response.status_code == 200:
        return response.json().get('data', {}).get('token', {})


def send_sms(phone, token):
    url = "https://notify.eskiz.uz/api/message/sms/send"
    payload = {"mobile_phone": phone,
               "message": "Bu Eskiz dan test",
               "from": "4546",
               "callback_url": "http:/0000.uz/test.php"}
    headers = {
        "Authorization": f"Bearer{token}"
    }
    response = requests.post(url, headers=headers, data=payload)
    if response.status_code != 200:
        raise Exception("SMS yuborishda hatolik")


@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data or message.text == "/start":
        await start(message)
    elif 'phone' not in user_data[user_id]:
        await send_code(message)
    elif 'status' not in user_data[user_id]:
        await check_code(message)
    elif 'location' not in user_data[user_id]:
        await save_address(message)
    elif 'kategoriyalar' in user_data[user_id]['keyboard']:
        await show_menu(message)
    elif 'tovarlar' in user_data[user_id]['keyboard']:
        await show_item(message)
    elif 'tanlanga_tovar' in user_data[user_id]['keyboard']:
        await select_item(message)


@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {}
    button = [
        [types.KeyboardButton(text="Share Contact", request_contact=True)]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=button, one_time_keyboard=True, resize_keyboard=True)
    await message.answer(f"Assalomu aleykum! Les Ailes yetkaziv berish xizmatiga xush kelibsiz!\n"
                         f"Iltimos telefon raqamingizni kiriting:", reply_markup=keyboard)
    print(1, user_data)


async def send_code(message: types.Message):
    user_id = message.from_user.id
    if message.contact is not None:
        phone = message.contact.phone_number
    else:
        phone = message.text
    flag = False
    if phone[0:4] == '+998' or phone[0:3] == '998':
        if len(phone) == 13:
            phone = phone[1:]
        if len(phone) == 12:
            phone = phone
        for s in phone:
            if s in '0123456789':
                flag = True
            else:
                flag = False
                break
    if flag == True:
        user_data[user_id]['phone'] = phone
        verification_code = random.randint(1000, 9999)
        user_data[user_id]['verification_code'] = verification_code
        try:
            token = get_eskiz_token(email, password)
            send_sms(phone, token)
            await message.answer(f"Iltimos tasdiqlash raqamini kiriting:{verification_code}")
        except Exception as ex:
            await message.answer(f"{ex}")

    else:
        await message.answer("To'g'ri raqam kiriting")
    print(2, user_data)


async def check_code(message: types.Message):
    user_id = message.from_user.id
    sent_code = message.text
    verification_code = user_data[user_id]["verification_code"]
    if str(verification_code) == sent_code:
        await message.answer("Siz ro'yxatdan o'tdingiz!\n")
        await address(message)
    else:
        await message.answer(f"Noto'g'ri kod. Qaytadan kiriting.")
    print(3, user_data)
