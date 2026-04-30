from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def admin_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📢 Kanal qo'shish"), KeyboardButton(text="🗑 Kanalni o'chirish")],
            [KeyboardButton(text="🏆 Referral boshqaruv"), KeyboardButton(text="📨 Ommaviy post")],
            [KeyboardButton(text="📊 Monitoring")],
        ],
        resize_keyboard=True
    )

def referral_manage_keyboard(has_active: bool):
    buttons = [
        [InlineKeyboardButton(text="➕ Yangi loyiha", callback_data="new_project")],
    ]
    if has_active:
        buttons.append([InlineKeyboardButton(text="⏹ Loyihani tugatish", callback_data="end_project")])
        buttons.append([InlineKeyboardButton(text="📊 Joriy statistika", callback_data="project_stats")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def auto_link_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha", callback_data="auto_yes"),
            InlineKeyboardButton(text="❌ Yo'q", callback_data="auto_no"),
        ]
    ])

def confirm_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm_project"),
            InlineKeyboardButton(text="❌ Bekor", callback_data="cancel_project"),
        ]
    ])

def channels_list_keyboard(channels: list):
    buttons = []
    for ch in channels:
        buttons.append([InlineKeyboardButton(
            text=f"❌ {ch['channel_name']}",
            callback_data=f"delch_{ch['id']}"
        )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
