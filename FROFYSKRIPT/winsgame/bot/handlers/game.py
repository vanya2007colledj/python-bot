from aiogram.types import Message, ChatType
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram import Dispatcher
from aiogram.utils.deep_linking import decode_payload, get_start_link

from settings import keywords, coefs
from settings.constants import knb
from bot.utils import func, text, game_process
from bot.utils.cryptopay import get_balance, crypto
import asyncio, config, main, random
from bot import keyboards

#ОСТОРОЖНО ВНИЗУ ГАВНОКОД ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
async def getter(msg_query: Message):
    """Пиздец"""
    if msg_query.chat.id == config.CHANNEL_BROKER: #проверка чтобы сообщение было в канале посреднике
        if msg_query.entities: #проверяем на наличие entities
            amount = float(msg_query.text.split("отправил(а)")[1].split()[0].replace(',', "")) #получаем сумму ставки
            name = msg_query.text.split("отправил(а)")[0] #получаем имя чела
            if msg_query.entities[0].user: #проверяем есть ли ссылка на чела
                user = msg_query.entities[0].user
                username = f"@{user.username}" if user.username else user.full_name
                name = user.full_name #снова получаем имя более надежным способом
                msg_text = msg_query.text.removeprefix(name) #удаляем имя из сообщения от греха подальше
                user_id = int(user.id)
                asset =  msg_text.split("отправил(а)")[1].split()[1]
                amount = float(msg_text.split("отправил(а)")[1].split()[0].replace(',', "")) #получаем сумму ставки надежным образом
                if user_id not in main.db.get_bannned(): #провека чтобы чел не был в бане
                    if "💬 " in msg_query.text: #проверяме на наличие комента
                        coef = 0
                        if "da;dladla;da;" in name.lower(): #увеличваем кэф если у чела в нике tonbet
                            coef += 0.05
                        old_comment = msg_query.text.split("💬 ")[1]
                        comment = old_comment.lower()
                        comment = comment.replace('ё', 'е') 
                        await asyncio.sleep(4)
                        await main.bot.send_message(config.MAIN_CHANNEL, "[✅] Ваша ставка принята в работу!")
                        message = await main.bot.send_message(config.MAIN_CHANNEL, text.get_stake(amount, asset, comment, name), 'html')
                        gp = game_process.GameProcess(amount, asset, coef, user_id, username)
                        if not main.db.users_exists(user_id):
                            main.db.add_user(user_id)
                            main.db.set_active(user_id, 0)
                        main.db.edit_total(user_id, 1)
                        amount_for_moneyback = amount if asset == "USDT" else amount * 2.8
                        main.db.edit_moneyback(user_id, amount_for_moneyback*config.MONEYBACK)
                        if func.contains(keywords.DICE, comment):
                            new_com = func.remove_prefixes(keywords.DICE, comment)
                            if new_com.isdigit() and new_com != "456" and new_com != "123" and new_com != "321" and new_com != "654" and new_com != "246" and new_com != "135":
                                    coef += coefs.DICE_NUMBER
                                    n = int(new_com)
                                    if 0 < n < 7:
                                       await gp.dice_procces(message, 'number', n)
                                    else:
                                        await func.invalid_syntax(message, amount, asset, user_id, username, name)
                            elif func.equals(keywords.EVEN, new_com):
                                await gp.dice_procces(message, 'even')
                            elif func.equals(keywords.ODD, new_com):
                                await gp.dice_procces(message, 'odd')
                            elif func.equals(keywords.MORE, new_com):
                                await gp.dice_procces(message, 'more')
                            elif func.equals(keywords.LESS, new_com):
                                await gp.dice_procces(message, 'less')
                            elif "дуэль " in new_com:
     
                                num = new_com.split()[1]
                                if num.isdigit():
                                    num = int(num)
                                    if 0 < num < 3:
                                        await gp.duel_number_process(message, num)
                                    else:
                                        await func.invalid_syntax(message, amount, asset, user_id, username, name)
                                else:
                                    await func.invalid_syntax(message, amount, asset, user_id, username, name)
                            elif new_com == "дуэль":
                                await gp.duel_proccess(message)
                            else:
                                await func.invalid_syntax(message, amount, asset, user_id, username, name)
                        elif func.contains(keywords.DARTS, comment):
                            new_com = func.remove_prefixes(keywords.DARTS, comment)
                            if func.equals(keywords.RED, new_com):
                                await gp.darts_procces(message, 'r')
                            elif func.equals(keywords.WHITE, new_com):
                                await gp.darts_procces(message, 'w')
                            elif func.equals(keywords.CENTER, new_com):
                                await gp.darts_procces(message)
                            elif func.equals(keywords.MISS, new_com):
                                await gp.darts_procces(message, 'miss')
                            elif "дуэль " in new_com:
                                coef += coefs.DUEL
                                num = new_com.split()[1]
                                if num.isdigit():
                                    num = int(num)
                                    if 0 < num < 3:
                                        await gp.duel_number_process(message, num, '🎯', ['первого дротика', 'второго дротика'])
                            elif new_com == "дуэль":
                                await gp.duel_proccess(message, '🎯', ['первого дротика', 'второго дротика'], ['lose.jpg', 'win.jpg'])
                            else:
                                await func.invalid_syntax(message, amount, asset, user_id, username, name)
                        elif func.contains(keywords.BASKET, comment):
                                new_com = func.remove_prefixes(keywords.BASKET, comment)
                                if func.equals(keywords.GOAL, new_com):
                                    await gp.basketball_process(message)
                                elif func.equals(keywords.MISS, new_com):
                                    await gp.basketball_process(message, 'miss')
                                else:
                                    await func.invalid_syntax(message, amount, asset, user_id, username, name)
                        elif func.contains(keywords.FOOTBALL, comment):
                            new_com = func.remove_prefixes(keywords.FOOTBALL, comment)
                            if func.equals(keywords.GOAL, new_com):
                                await gp.footaball_process(message)
                            elif func.equals(keywords.MISS, new_com):
                                await gp.footaball_process(message, 'miss')
                            else:
                                await func.invalid_syntax(message, amount, asset, user_id, username, name)
                        elif func.contains(keywords.BOWLING, comment):
                            new_com = func.remove_prefixes(keywords.BOWLING, comment)
                            if new_com.isdigit():
                                stake = int(new_com)
                                if -1 < stake < 7:
                                    await gp.bowling_process(message, stake)
                            elif func.equals(keywords.STRIKE, new_com):
                                await gp.bowling_process(message, 0)
                            else:
                                await func.invalid_syntax(message, amount, asset, user_id, username, name)
                        elif "мины " in comment:
                            if not main.db.user_played_mines(user_id):
                                new_com = comment
                                new_com = new_com.removeprefix("мины ")
                                if new_com.isdigit():
                                    n = int(int(new_com))
                                    if 25 > n > 2:
                                        c = 0
                                        coef += 1
                                        await message.reply(f"*⚡Выберете любой слот*\n*Клеток открыто:* 0\n*Коэффицент:* 1X\n*Выигрыш:* {round(amount * coef, 2)}  {asset}", 'markdown', reply_markup=keyboards.functional.create_mine_keyboards(n, user_id, amount, asset, username))
                                    else:
                                        await func.invalid_syntax(message, amount, asset, user_id, username, name)
                                else:
                                    await func.invalid_syntax(message, amount, asset, user_id, username, name)
                            else:
                                if amount < dict(await get_balance())[asset]:
                                    if amount < 1:
                                        check = await crypto.create_check(asset, amount - amount * 0.1)
                                        main.db.add_check(user_id, check.check_id)
                                        msag = await message.reply("<b>❗Вы ещё не завершили предыдущую игру</b>\n\n<blockquote><b>Нажмите на кнопку ниже, чтобы вернуть деньги c комиссией 10%!</b></blockquote>", 'html', reply_markup=keyboards.functional.create_url_button(await get_start_link(user_id, True), "Вернуть💸"))
                                    else:
                                        await crypto.transfer(user_id, asset, amount - amount * 0.1, text.rnd_id())
                                        msag = await message.reply("<b>❗Вы ещё не завершили предыдущую игру</b>\n\n<blockquote><b>Деньги возвращены на ваш баланс c комиссией 10%!</b></blockquote>", 'html')
                                else:
                                    msag = await message.reply("*❗Вы ещё не завершили предыдущую игру*\n\n<blockquote>Напишите администрации для возвращения средств!</blockquote>", 'markdown')
                                await asyncio.sleep(20)
                                await msag.delete()
                        else:
                            if func.equals(keywords.EVEN, comment):
                                await gp.dice_procces(message, 'even')
                            elif func.equals(keywords.ODD, comment):
                                await gp.dice_procces(message, 'odd')
                            elif func.equals(keywords.RED, comment):
                                await gp.darts_procces(message, 'r')
                            elif func.equals(keywords.WHITE, comment):
                                await gp.darts_procces(message, 'w')
                            elif func.equals(keywords.DARTS, comment) or func.equals(keywords.CENTER, comment):
                                await gp.darts_procces(message)
                            elif func.equals(keywords.BASKET, comment):
                                await gp.basketball_process(message)
                            elif func.equals(keywords.FOOTBALL, comment):
                                await gp.footaball_process(message)
                            elif func.equals(keywords.BOWLING, comment) or func.equals(keywords.STRIKE, comment):
                                await gp.bowling_process(message, 0)
                            elif func.equals(keywords.SLOTS, comment):
                                msg = await message.answer_dice('🎰')
                                v = msg.dice.value
                                await asyncio.sleep(6)
                                if v == 64:
                                    await func.winner(message, amount, asset, coefs.SLOTS_777 + coef, user_id, username, "Победа! Вы выбили три в ряд!", type="cas") #777
                                elif v == 1 or v==22:
                                    await func.winner(message, amount, asset, coefs.SLOTS_GRAPE + coef, user_id,  username, "Победа! Вы выбили три в ряд!", type="cas") #bar and grape
                                elif v == 43:
                                    await func.winner(message, amount, asset, coefs.SLOTS_LEMON + coef, user_id, username, "Победа! Вы выбили три в ряд!", type="cas")
                                else:
                                    await func.looser(message, "Проигрыш! Вы не выбили три в ряд!", type = "cas")
                            elif comment in ["камень", "ножницы", "бумага"]:
                                await gp.knb_procces(message, comment)
                            else:
                                await func.invalid_syntax(message, amount, asset, user_id, username, name)
                    else:
                        #если нет комента
                        message = await main.bot.send_message(config.MAIN_CHANNEL, text.get_stake(amount, asset, '❌', name), 'html')
                        await func.invalid_syntax(message, amount, asset, user_id, username, name)
                        await asyncio.sleep(20)
                        await message.delete()
                else:
                    #если бан
                    await main.bot.send_message(config.LOG_CHANNEL, f"Забанненый {username}({user_id}) отправил {amount} {asset}")
            else:
                #если нет ссылки на акк
                await main.bot.send_message(config.LOG_CHANNEL, f"Не удалось распознать пользователя с именем {name}! Его ставка {amount} {asset}")
                masage = await main.bot.send_message(config.MAIN_CHANNEL, f"❗Мы не смогли опознать человека с именем <b>{name}</b>! Пиши в лс админам\n\n⚠️Проблема возможно возникла из-за ваших настроек приватности!", "html")
                await asyncio.sleep(20)
                await masage.delete()

def register_handlers(dp: Dispatcher):
    dp.register_channel_post_handler(getter, ChatTypeFilter(ChatType.CHANNEL), text_contains="отправил(а)")
