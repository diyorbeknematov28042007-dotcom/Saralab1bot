from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import os

from database.queries import (
    add_channel, get_active_channels, remove_channel,
    create_project, get_active_project, end_project,
    get_project_stats, get_total_users, get_today_users,
    get_total_referral_links, get_all_user_ids
)
from keyboards.admin_kb import (
    admin_main_keyboard, referral_manage_keyboard,
    auto_link_keyboard, confirm_keyboard, channels_list_keyboard
)
from utils.states import AddChannel, NewProject, Broadcast

router = Router()
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "6552126335,8013328081").split(",")]

def is_admin(user_id): return user_id in ADMIN_IDS

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id): return
    await message.answer("🔐 Admin panel", reply_markup=admin_main_keyboard())

# ─── CHANNELS ────────────────────────────────────────────
@router.message(F.text == "📢 Kanal qo'shish")
async def add_channel_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    await state.set_state(AddChannel.waiting_channel_id)
    await message.answer("Kanal ID sini yuboring:\n<i>Masalan: -1001234567890</i>\n\nBotni kanalga admin qilib qo'shing!", parse_mode="HTML")

@router.message(AddChannel.waiting_channel_id)
async def add_channel_id(message: Message, state: FSMContext):
    await state.update_data(channel_id=message.text.strip())
    await state.set_state(AddChannel.waiting_channel_link)
    await message.answer("Kanal havolasini yuboring (https://t.me/...):")

@router.message(AddChannel.waiting_channel_link)
async def add_channel_link(message: Message, state: FSMContext):
    await state.update_data(channel_link=message.text.strip())
    await state.set_state(AddChannel.waiting_channel_name)
    await message.answer("Kanal nomini yuboring:")

@router.message(AddChannel.waiting_channel_name)
async def add_channel_name(message: Message, state: FSMContext):
    data = await state.get_data()
    await add_channel(data['channel_id'], data['channel_link'], message.text.strip())
    await state.clear()
    await message.answer(f"✅ Kanal qo'shildi: <b>{message.text.strip()}</b>", parse_mode="HTML")

@router.message(F.text == "🗑 Kanalni o'chirish")
async def remove_channel_start(message: Message):
    if not is_admin(message.from_user.id): return
    channels = await get_active_channels()
    if not channels:
        await message.answer("❌ Hozircha kanallar yo'q.")
        return
    await message.answer("O'chirmoqchi bo'lgan kanalni tanlang:", reply_markup=channels_list_keyboard(channels))

@router.callback_query(F.data.startswith("delch_"))
async def delete_channel(call: CallbackQuery):
    await remove_channel(int(call.data.split("_")[1]))
    await call.answer("✅ Kanal o'chirildi!", show_alert=True)
    await call.message.delete()

# ─── REFERRAL ────────────────────────────────────────────
@router.message(F.text == "🏆 Referral boshqaruv")
async def referral_manage(message: Message):
    if not is_admin(message.from_user.id): return
    project = await get_active_project()
    has_active = project is not None
    text = f"🏆 Faol loyiha: <b>{project['name']}</b>" if has_active else "ℹ️ Faol loyiha yo'q."
    await message.answer(text, reply_markup=referral_manage_keyboard(has_active), parse_mode="HTML")

@router.callback_query(F.data == "new_project")
async def new_project_start(call: CallbackQuery, state: FSMContext):
    await state.set_state(NewProject.waiting_name)
    await call.message.edit_text("📝 Loyiha nomini kiriting:")

@router.message(NewProject.waiting_name)
async def new_project_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(NewProject.waiting_post)
    await message.answer("📄 Loyiha postini yuboring (matn yoki rasm+caption):\n<i>Bu post foydalanuvchilarga ko'rsatiladi</i>", parse_mode="HTML")

@router.message(NewProject.waiting_post)
async def new_project_post(message: Message, state: FSMContext):
    if message.photo:
        await state.update_data(post_photo=message.photo[-1].file_id, post_text=message.caption or "")
    else:
        await state.update_data(post_text=message.text, post_photo=None)
    await state.set_state(NewProject.waiting_channel_info)
    await message.answer("📢 Referral kanali ID va havolasini yuboring:\n<i>Format: -1001234567890 | https://t.me/kanal</i>", parse_mode="HTML")

@router.message(NewProject.waiting_channel_info)
async def new_project_channel(message: Message, state: FSMContext):
    try:
        parts = [p.strip() for p in message.text.split("|")]
        await state.update_data(channel_id=parts[0], channel_link=parts[1])
    except Exception:
        await message.answer("❌ Format noto'g'ri! Qaytadan:\n<i>-1001234567890 | https://t.me/kanal</i>", parse_mode="HTML")
        return
    await state.set_state(NewProject.waiting_auto_link)
    await message.answer("🔗 Avtomatik link jo'natish tizimini yoqamizmi?", reply_markup=auto_link_keyboard())

@router.callback_query(F.data == "auto_yes")
async def auto_link_yes(call: CallbackQuery, state: FSMContext):
    await state.update_data(auto_link_enabled=True)
    await state.set_state(NewProject.waiting_threshold)
    await call.message.edit_text("🔢 Nechta taklif qilishsa link jo'natay? (son kiriting):")

@router.callback_query(F.data == "auto_no")
async def auto_link_no(call: CallbackQuery, state: FSMContext):
    await state.update_data(auto_link_enabled=False, auto_link_threshold=None, auto_link_url=None)
    data = await state.get_data()
    await state.set_state(NewProject.confirm)
    await call.message.edit_text(
        f"✅ Loyiha ma'lumotlari:\n\n📌 Nom: <b>{data['name']}</b>\n📢 Kanal: {data['channel_link']}\n🔗 Auto link: <b>Yo'q</b>\n\nTasdiqlaysizmi?",
        reply_markup=confirm_keyboard(), parse_mode="HTML"
    )

@router.message(NewProject.waiting_threshold)
async def auto_link_threshold(message: Message, state: FSMContext):
    try:
        await state.update_data(auto_link_threshold=int(message.text.strip()))
    except Exception:
        await message.answer("❌ Son kiriting!")
        return
    await state.set_state(NewProject.waiting_auto_url)
    await message.answer("🔗 Jo'natiladigan linkni kiriting:")

@router.message(NewProject.waiting_auto_url)
async def auto_link_url(message: Message, state: FSMContext):
    await state.update_data(auto_link_url=message.text.strip())
    data = await state.get_data()
    await state.set_state(NewProject.confirm)
    await message.answer(
        f"✅ Loyiha ma'lumotlari:\n\n📌 Nom: <b>{data['name']}</b>\n📢 Kanal: {data['channel_link']}\n🔗 Auto link: <b>Ha</b>, {data['auto_link_threshold']} ta referal\n\nTasdiqlaysizmi?",
        reply_markup=confirm_keyboard(), parse_mode="HTML"
    )

@router.callback_query(F.data == "confirm_project")
async def confirm_project(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await create_project(
        name=data['name'], post_text=data.get('post_text'), post_photo=data.get('post_photo'),
        channel_id=data.get('channel_id'), channel_link=data.get('channel_link'),
        auto_link_enabled=data.get('auto_link_enabled', False),
        auto_link_threshold=data.get('auto_link_threshold'),
        auto_link_url=data.get('auto_link_url'),
    )
    await state.clear()
    await call.message.edit_text(f"✅ <b>{data['name']}</b> loyihasi yaratildi!", parse_mode="HTML")

@router.callback_query(F.data == "cancel_project")
async def cancel_project(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("❌ Bekor qilindi.")

@router.callback_query(F.data == "end_project")
async def end_project_handler(call: CallbackQuery):
    project = await get_active_project()
    if not project:
        await call.answer("Faol loyiha yo'q!", show_alert=True)
        return
    await end_project(project['id'])
    stats = await get_project_stats(project['id'])
    if stats:
        medals = ["🥇", "🥈", "🥉"]
        result = f"🏆 <b>{project['name']}</b> — Yakuniy natija:\n\n"
        for i, s in enumerate(stats):
            medal = medals[i] if i < 3 else f"{i+1}."
            uname = f"@{s['username']}" if s['username'] else s['full_name']
            result += f"{medal} {uname} — <b>{s['referral_count']}</b> ta\n"
    else:
        result = "📊 Hech kim ishtirok etmadi."
    await call.message.edit_text(result, parse_mode="HTML")

@router.callback_query(F.data == "project_stats")
async def project_stats_handler(call: CallbackQuery):
    project = await get_active_project()
    if not project:
        await call.answer("Faol loyiha yo'q!", show_alert=True)
        return
    stats = await get_project_stats(project['id'])
    if not stats:
        await call.message.edit_text("📊 Hali statistika yo'q.")
        return
    medals = ["🥇", "🥈", "🥉"]
    result = f"📊 <b>{project['name']}</b> — Joriy statistika:\n\n"
    for i, s in enumerate(stats[:30]):
        medal = medals[i] if i < 3 else f"{i+1}."
        uname = f"@{s['username']}" if s['username'] else s['full_name']
        result += f"{medal} {uname} — <b>{s['referral_count']}</b> ta\n"
    await call.message.edit_text(result, parse_mode="HTML")

# ─── BROADCAST ───────────────────────────────────────────
@router.message(F.text == "📨 Ommaviy post")
async def broadcast_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    await state.set_state(Broadcast.waiting_content)
    await message.answer("📨 Jo'natmoqchi bo'lgan xabarni yuboring:")

@router.message(Broadcast.waiting_content)
async def broadcast_content(message: Message, state: FSMContext):
    await state.update_data(
        text=message.text or message.caption,
        photo=message.photo[-1].file_id if message.photo else None
    )
    await state.set_state(Broadcast.confirm)
    await message.answer("Ommaviy postni jo'natamizmi?", reply_markup=confirm_keyboard())

@router.callback_query(F.data == "confirm_project", Broadcast.confirm)
async def broadcast_confirm(call: CallbackQuery, bot: Bot, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    users = await get_all_user_ids()
    sent, failed = 0, 0
    for uid in users:
        try:
            if data.get('photo'):
                await bot.send_photo(uid, photo=data['photo'], caption=data.get('text'), parse_mode="HTML")
            else:
                await bot.send_message(uid, data['text'], parse_mode="HTML")
            sent += 1
        except Exception:
            failed += 1
    await call.message.edit_text(f"✅ Jo'natildi: {sent}\n❌ Xato: {failed}")

# ─── MONITORING ──────────────────────────────────────────
@router.message(F.text == "📊 Monitoring")
async def monitoring(message: Message):
    if not is_admin(message.from_user.id): return
    total = await get_total_users()
    today = await get_today_users()
    links = await get_total_referral_links()
    project = await get_active_project()
    proj_text = f"<b>{project['name']}</b>" if project else "Yo'q"
    await message.answer(
        f"📊 <b>Monitoring</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{total}</b>\n"
        f"📅 Bugun qo'shilganlar: <b>{today}</b>\n"
        f"🔗 Referral linklar soni: <b>{links}</b>\n"
        f"🏆 Faol loyiha: {proj_text}",
        parse_mode="HTML"
    )
