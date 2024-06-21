from aiogram.utils.deep_linking import decode_payload, get_start_link
from aiogram.types import Message

import main as m
import config
from bot.utils.cryptopay import get_balance, crypto
from bot.utils import text
from bot import keyboards
import base64, datetime, asyncio, main

def check_button_back(buttons) -> bool:
    for keyboard in buttons:
        for button in keyboard:
            if button.text == "Забрать":
                return False
    return True
   
def check_winning(id, buttons) -> bool:
    for keyboard in buttons:
        for button in keyboard:
            if button.callback_data != "finish" and "stop_" not in button.callback_data:
                i = int(button.callback_data.split('_')[2])
                if i not in m.db.get_bad_mines(id) and i != -1:
                    return False
    return True

def remaining_slots(buttons: list, id: int) -> int:
    i = 0
    for keyboard in buttons:
        for button in keyboard:
            if "stop_" not in button.callback_data:
                if button.callback_data != "ready_empty_-1" and int(button.callback_data.split('_')[2]) not in m.db.get_bad_mines(id):
                    i = i + 1
    return i

def contains(l, item) -> bool:
    for el in l:
        if el + " " in item:
            return True
    return False

def equals(l, item) -> bool:
    for el in l:
        if el==item:
            return True
    return False

def remove_prefixes(l: list, item: str):
    for el in l:
        item = item.removeprefix(el + " ")
    return item

async def get_price_mine(message: Message, amount, asset, coef, user_id, username):
    if amount*coef < dict(await get_balance())[asset]:
        if amount*coef > 1:
            await crypto.transfer(user_id, asset, amount * coef, text.rnd_id())
            await message.edit_text(f"<b>Победа! На баланс победителя была зачислена сумма в размере {round(amount * coef, 3)} {asset}</b>" + "\n\n"+ text.links, 'html',
                                     keyboards.functional.create_url_button(config.CHECK_URL, "Сделать Ставку"), disable_web_page_preview=True)
        else:
            check = await crypto.create_check(asset, amount * coef)
            m.db.add_check(user_id, check.check_id)
            await message.edit_text(f"<b>Победа! Победитель выиграл {round(amount * coef, 3)} {asset}! Заберите выигрыш по кнопке ниже!</b>" + "\n\n"+ text.links, 'html',
                                reply_markup=keyboards.functional.create_double_button(await get_start_link(user_id, True), "Забрать Выигрыш"), 
                                disable_web_page_preview=True)
    else:
        await m.bot.send_message(config.LOG_CHANNEL, f"{username} ({user_id}) выиграл {round(amount * coef, 3)} {asset}. ЗАДОЛЖЕННОСТЬ!")
        await message.edit_text(f"<b>Победа! Сумма в размере {amount} {asset}! будет зачислена администрацией вручную.</b>" + "\n\n"+ text.links, 'html', 
                                reply_markup=keyboards.functional.create_url_button(config.CHECK_URL, "Сделать Ставку"), disable_web_page_preview=True)
        
async def winner(message: Message, amount, asset, coef, user_id, username, a_text, photo = "win.jpg", type = 'def'):
        photo = "imgs\\" + photo
        if amount*coef < dict(await get_balance())[asset]:
            if amount*coef > 1:
                await crypto.transfer(user_id, asset, amount * coef, text.rnd_id())
                await message.reply_photo(open(photo, 'rb'),text.get_win_text(round(amount * coef, 3), asset, type, a_text), 'html', reply_markup=keyboards.functional.create_url_button(config.CHECK_URL, "Сделать Ставку"))
            else:
                check = await crypto.create_check(asset, amount * coef)
                m.db.add_check(user_id, check.check_id)
                await message.reply_photo(open(photo, 'rb'),text.get_win_text(round(amount * coef, 3), asset, type, a_text, is_less_dol = True), 'html',
                                 reply_markup=keyboards.functional.create_double_button(await get_start_link(user_id, True), "Забрать Выигрыш"))
        else:
            await m.bot.send_message(config.LOG_CHANNEL, f"{username} ({user_id}) выиграл {round(amount * coef, 3)} {asset}. ЗАДОЛЖЕННОСТЬ!")
            await message.reply_photo(open(photo, 'rb'),text.get_win_text(round(amount * coef, 3), asset, type, a_text, is_less=True), 'html', reply_markup=keyboards.functional.create_url_button(config.CHECK_URL, "Сделать Ставку"))

async def looser(message: Message, a_text, photo = "lose.jpg", type = "def"):
    photo = "imgs\\" + photo
    await message.reply_photo(open(photo, 'rb'), text.get_lose_text(a_text, type), 'html', reply_markup=keyboards.functional.create_url_button(config.CHECK_URL, "Сделать Ставку"))

async def invalid_syntax(message: Message, amount, asset, user_id, username, name):
    end_amount = amount - amount * 0.1
    main.db.edit_total(user_id, -1)
    main.db.edit_moneyback(user_id, -(amount*config.MONEYBACK))
    if end_amount < dict(await get_balance())[asset]:
        if end_amount > 1:
                await crypto.transfer(user_id, asset, end_amount, text.rnd_id())
                msg = await message.reply(text.get_invalid_text(name), 'html', disable_notification=True)
        else:
            check = await crypto.create_check(asset, end_amount)
            m.db.add_check(user_id, check.check_id)
            msg = await message.reply(text.get_invalid_text(name, 'button'), 'html', reply_markup=keyboards.functional.create_url_button(await get_start_link(user_id, True), "Вернуть💸"), disable_notification=True)
    else:       
        await m.bot.send_message(config.LOG_CHANNEL, f"❗{username} ({user_id}) ошибся в синтаксесе. {round(end_amount, 3)} {asset.upper()}. ЗАДОЛЖЕННОСТЬ!")
        msg = await message.reply(text.get_invalid_text(name, 'admin'), 'html', disable_notification=True)