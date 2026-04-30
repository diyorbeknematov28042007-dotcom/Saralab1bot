from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from database.queries import (
    get_user, create_user, update_user_language,
    get_active_channels, get_active_project,
    get_user_referral_count, get_project_stats,
    add_referral_stat
)
from keyboards.user_kb import lang_keyboard, subscribe_keyboard, main_keyboard
from utils.texts import t
import os

router = Router()
BOT_USERNAME = None

async def get_bot_username(bot: Bot):
    global BOT_USERNAME
    if not BOT_USERNAME:
        me = await bot.get_me()
        BOT_USERNAME = me.username
    return BOT_USERNAME

async def check_subscriptions(bot: Bot, user_id: int, channels: list) -> bool:
    for ch in channels:
        try:
            member = await bot.get_chat_member(ch['channel_id'], user_id)
            if member.status in ("left", "kicked", "banned"):
                return False
        except Exception:
            return False
    return True

@router.message(CommandStart())
async def start_handler(message: Message, bot: Bot, state: FSMContext):
    await state.clear()
    args = message.text.split()
    ref_id = None
    if len(args) > 1:
        try:
            ref_id = int(args[1])
            if ref_id == message.from_user.id:
                ref_id = None
        except Exception:
            ref_id = None

    user = await get_user(message.from_user.id)
    if not user:
        # New user — save ref_id in state temporarily
        await state.update_data(ref_id=ref_id)
        await message.answer(t("uz", "choose_lang"), reply_markup=lang_keyboard())
        return

    lang = user['language']
    channels = await get_active_channels()
    if channels:
        subbed = await check_subscriptions(bot, message.from_user.id, channels)
        if not subbed:
            ch_text = "\n".join([f"• <a href='{c['channel_link']}'>{c['channel_name']}</a>" for c in channels])
            await message.answer(
                t(lang, "subscribe_required", channels=ch_text),
                reply_markup=subscribe_keyboard(channels, lang),
                parse_mode="HTML", disable_web_page_preview=True
            )
            return

    await show_main_menu(message, lang)

@router.callback_query(F.data.startswith("lang_"))
async def lang_chosen(call: CallbackQuery, bot: Bot, state: FSMContext):
    lang = call.data.split("_")[1]
    data = await state.get_data()
    ref_id = data.get("ref_id")

    full_name = call.from_user.full_name
    username = call.from_user.username

    await create_user(call.from_user.id, username, full_name, lang, ref_id)
    await state.clear()

    # Count referral for active project
    if ref_id:
        project = await get_active_project()
        if project:
            await add_referral_stat(project['id'], ref_id)
            # Auto link check
            if project['auto_link_enabled'] and project['auto_link_threshold']:
                count = await get_user_referral_count(project['id'], ref_id)
                if count == project['auto_link_threshold']:
                    try:
                        ref_user = await get_user(ref_id)
                        ref_lang = ref_user['language'] if ref_user else 'uz'
                        await bot.send_message(
                            ref_id,
                            f"🎉 Tabriklaymiz! Siz {count} ta do'st taklif qildingiz!\n\n"
                            f"🔗 Sizning maxsus havolangiz:\n{project['auto_link_url']}"
                        )
                    except Exception:
                        pass

    # Check subscriptions
    channels = await get_active_channels()
    if channels:
        subbed = await check_subscriptions(bot, call.from_user.id, channels)
        if not subbed:
            ch_text = "\n".join([f"• <a href='{c['channel_link']}'>{c['channel_name']}</a>" for c in channels])
            await call.message.edit_text(
                t(lang, "subscribe_required", channels=ch_text),
                reply_markup=subscribe_keyboard(channels, lang),
                parse_mode="HTML", disable_web_page_preview=True
            )
            return

    await call.message.delete()
    await show_main_menu(call.message, lang, user_id=call.from_user.id)

@router.callback_query(F.data == "check_sub")
async def check_sub_callback(call: CallbackQuery, bot: Bot):
    user = await get_user(call.from_user.id)
    lang = user['language'] if user else 'uz'
    channels = await get_active_channels()

    subbed = await check_subscriptions(bot, call.from_user.id, channels)
    if not subbed:
        await call.answer(t(lang, "not_subscribed"), show_alert=True)
        return

    await call.answer(t(lang, "subscribed_ok"), show_alert=True)
    await call.message.delete()
    await show_main_menu(call.message, lang, user_id=call.from_user.id)

async def show_main_menu(message: Message, lang: str, user_id: int = None):
    uid = user_id or message.from_user.id
    user = await get_user(uid)
    name = user['full_name'] if user else message.from_user.full_name

    project = await get_active_project()
    if project and project.get('post_text'):
        try:
            if project.get('post_photo'):
                await message.answer_photo(
                    photo=project['post_photo'],
                    caption=project['post_text'],
                    parse_mode="HTML"
                )
            else:
                await message.answer(project['post_text'], parse_mode="HTML")
        except Exception:
            pass

    await message.answer(
        t(lang, "welcome", name=name),
        reply_markup=main_keyboard(lang),
        parse_mode="HTML"
    )

@router.message(F.text.in_(["👥 Do'stlarni taklif qilish", "👥 Пригласить друзей"]))
async def friends_handler(message: Message, bot: Bot):
    user = await get_user(message.from_user.id)
    lang = user['language'] if user else 'uz'

    username = await get_bot_username(bot)
    link = f"https://t.me/{username}?start={message.from_user.id}"

    project = await get_active_project()
    count = 0
    if project:
        count = await get_user_referral_count(project['id'], message.from_user.id)

    await message.answer(
        t(lang, "friends_text", link=link, count=count),
        parse_mode="HTML"
    )

@router.message(F.text.in_(["📊 Statistika", "📊 Статистика"]))
async def stats_handler(message: Message):
    user = await get_user(message.from_user.id)
    lang = user['language'] if user else 'uz'

    project = await get_active_project()
    if not project:
        await message.answer(t(lang, "no_active_project"))
        return

    stats = await get_project_stats(project['id'])
    my_count = await get_user_referral_count(project['id'], message.from_user.id)

    if not stats:
        rows = "— hali hech kim yo'q —" if lang == 'uz' else "— пока никого нет —"
    else:
        rows = ""
        medals = ["🥇", "🥈", "🥉"]
        for i, s in enumerate(stats[:20]):
            medal = medals[i] if i < 3 else f"{i+1}."
            uname = f"@{s['username']}" if s['username'] else s['full_name']
            rows += f"{medal} {uname} — <b>{s['referral_count']}</b>\n"

    await message.answer(
        t(lang, "stats_text",
          project_name=project['name'],
          rows=rows,
          my_count=my_count),
        parse_mode="HTML"
    )
