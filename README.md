# 🤖 Referral Bot

Aiogram 3 + Supabase (PostgreSQL) asosidagi Referral Bot.

## 📁 Fayl tuzilmasi

```
referral_bot/
├── main.py                  # Asosiy kirish nuqtasi
├── requirements.txt
├── Procfile                 # Railway uchun
├── .env.example
├── database/
│   ├── db.py               # Ulanish va jadval yaratish
│   └── queries.py          # Barcha SQL so'rovlar
├── handlers/
│   ├── user.py             # Foydalanuvchi handlerlari
│   └── admin.py            # Admin handlerlari
├── keyboards/
│   ├── user_kb.py          # Foydalanuvchi klaviaturalari
│   └── admin_kb.py         # Admin klaviaturalari
└── utils/
    ├── texts.py            # UZ/RU matnlar
    └── states.py           # FSM holatlari
```

## ⚙️ O'rnatish

### 1. .env fayl yarating
```
BOT_TOKEN=your_telegram_bot_token
DATABASE_URL=postgresql://user:password@host:5432/dbname
ADMIN_IDS=6552126335,8013328081
```

### 2. Supabase sozlash
1. [supabase.com](https://supabase.com) ga kiring
2. Yangi project yarating
3. Settings → Database → Connection String → URI ni oling
4. Uni `DATABASE_URL` ga joylashtiring

### 3. Lokal ishga tushirish
```bash
pip install -r requirements.txt
python main.py
```

## 🚀 Railway Deploy

1. GitHub ga push qiling
2. [railway.app](https://railway.app) da yangi project oching
3. GitHub repo ni ulang
4. Environment Variables ga `.env` dagi qiymatlarni kiriting:
   - `BOT_TOKEN`
   - `DATABASE_URL`
   - `ADMIN_IDS`
5. Deploy tugmasi!

## 👤 Foydalanuvchi Panel

| Funksiya | Tavsif |
|---|---|
| Til tanlash | O'zbek / Rus |
| Majburiy obuna | Admin qo'shgan kanallar |
| Loyiha posti | Faol loyiha haqida |
| Do'stlarni taklif | Shaxsiy referal havola |
| Statistika | Reyting ko'rish |

## 🔐 Admin Panel (`/admin`)

| Tugma | Funksiya |
|---|---|
| 📢 Kanal qo'shish | Majburiy obuna kanali qo'shish |
| 🗑 Kanalni o'chirish | Kanalni o'chirish |
| 🏆 Referral boshqaruv | Loyiha yaratish/tugatish |
| 📨 Ommaviy post | Barcha userlarga xabar |
| 📊 Monitoring | Statistika ko'rish |

## 📊 Database Jadvallari

- `users` — Foydalanuvchilar
- `channels` — Majburiy obuna kanallari  
- `referral_projects` — Referral loyihalar
- `referral_stats` — Har loyiha bo'yicha statistika
