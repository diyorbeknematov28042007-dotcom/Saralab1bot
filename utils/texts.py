TEXTS = {
    "uz": {
        "choose_lang": "🌐 Tilni tanlang / Выберите язык:",
        "welcome": (
            "👋 Xush kelibsiz, {name}!\n\n"
            "Quyidagi bo'limlardan birini tanlang:"
        ),
        "subscribe_required": (
            "📢 Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:\n\n"
            "{channels}\n\n"
            "✅ Obuna bo'lgach, «Tekshirish» tugmasini bosing."
        ),
        "subscribe_check": "✅ Tekshirish",
        "not_subscribed": "❌ Siz hali barcha kanallarga obuna bo'lmadingiz!",
        "subscribed_ok": "✅ Obuna tasdiqlandi! Botga xush kelibsiz!",
        "friends_title": "👥 Do'stlarni taklif qilish",
        "friends_text": (
            "🔗 Sizning referal havolangiz:\n"
            "<code>{link}</code>\n\n"
            "👥 Siz taklif qilganlar: <b>{count}</b> kishi"
        ),
        "stats_title": "📊 Statistika",
        "stats_text": (
            "📊 <b>{project_name}</b> — Reyting:\n\n"
            "{rows}\n\n"
            "👤 Sizning natijangiz: <b>{my_count}</b> ta referal"
        ),
        "no_active_project": "⚠️ Hozircha faol referral loyiha yo'q.",
        "btn_friends": "👥 Do'stlarni taklif qilish",
        "btn_stats": "📊 Statistika",
        "lang_changed": "✅ Til o'zgartirildi!",
        "referred_bonus": "🎉 Siz {name} taklifi orqali qo'shildingiz!",
    },
    "ru": {
        "choose_lang": "🌐 Выберите язык / Tilni tanlang:",
        "welcome": (
            "👋 Добро пожаловать, {name}!\n\n"
            "Выберите один из разделов:"
        ),
        "subscribe_required": (
            "📢 Для использования бота подпишитесь на каналы:\n\n"
            "{channels}\n\n"
            "✅ После подписки нажмите «Проверить»."
        ),
        "subscribe_check": "✅ Проверить",
        "not_subscribed": "❌ Вы ещё не подписаны на все каналы!",
        "subscribed_ok": "✅ Подписка подтверждена! Добро пожаловать!",
        "friends_title": "👥 Пригласить друзей",
        "friends_text": (
            "🔗 Ваша реферальная ссылка:\n"
            "<code>{link}</code>\n\n"
            "👥 Приглашено вами: <b>{count}</b> чел."
        ),
        "stats_title": "📊 Статистика",
        "stats_text": (
            "📊 <b>{project_name}</b> — Рейтинг:\n\n"
            "{rows}\n\n"
            "👤 Ваш результат: <b>{my_count}</b> рефералов"
        ),
        "no_active_project": "⚠️ Сейчас нет активного реферального проекта.",
        "btn_friends": "👥 Пригласить друзей",
        "btn_stats": "📊 Статистика",
        "lang_changed": "✅ Язык изменён!",
        "referred_bonus": "🎉 Вы присоединились по приглашению {name}!",
    }
}

def t(lang: str, key: str, **kwargs):
    text = TEXTS.get(lang, TEXTS["uz"]).get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text
