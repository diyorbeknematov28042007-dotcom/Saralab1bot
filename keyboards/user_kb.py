from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from utils.texts import t

def lang_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
        ]
    ])

def subscribe_keyboard(channels: list, lang: str):
    buttons = []
    for ch in channels:
        buttons.append([InlineKeyboardButton(text=f"📢 {ch['channel_name']}", url=ch['channel_link'])])
    buttons.append([InlineKeyboardButton(text=t(lang, "subscribe_check"), callback_data="check_sub")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def main_keyboard(lang: str):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "btn_friends")), KeyboardButton(text=t(lang, "btn_stats"))]
        ],
        resize_keyboard=True
    )
