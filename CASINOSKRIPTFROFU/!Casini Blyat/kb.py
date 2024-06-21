from config import channel_us
from aiogram.types import ReplyKeyboardRemove,ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

button_s = ReplyKeyboardMarkup(resize_keyboard=True)
button_stat = KeyboardButton('👤 Аккаунт')
button_s.add(button_stat)

subc = InlineKeyboardMarkup(row_width=1)
subc.add(
	InlineKeyboardButton(text='⚡ Подписаться', url=channel_us),
	InlineKeyboardButton(text='✅ Проверить', callback_data='check_sub')
)

button_s2 = InlineKeyboardMarkup(row_width=1)
button_s2.add(
	InlineKeyboardButton(text='📤 Вывести средства', callback_data='vuvesti'),
	InlineKeyboardButton(text='« Назад', callback_data='nazad')
)

but = InlineKeyboardMarkup(row_width=1)
but.add(
	InlineKeyboardButton(text='« Назад', callback_data='nazad')
)

adminpanel = InlineKeyboardMarkup(row_width=2)
adminpanel.add(
	InlineKeyboardButton(text='Параметры', callback_data="popoln")
	)