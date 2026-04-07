import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import json
import os
from datetime import datetime

TOKEN = "8708721942:AAES9a9FlPcaPP6m7EZjXSYqZNg9baHon5g"
REF_LINK = "https://reg.eda.yandex.ru/?advertisement_campaign=forms_for_agents&user_invite_code=d8ec2934040d45009a5225ef56a0b5ae&utm_content=blank"
STATS_FILE = "stats.json"
PHOTO_URL = "https://avatars.mds.yandex.net/i?id=dbcceb129b60f01748ed59d866465298f184211b-7665183-images-thumbs&n=13"

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

def load_stats():
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r") as f:
            return json.load(f)
    return {"total_starts": 0, "ref_clicks": 0, "users": []}

def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

def track_user(user_id, username, action):
    stats = load_stats()
    if action == "start":
        stats["total_starts"] += 1
        if user_id not in [u["id"] for u in stats["users"]]:
            stats["users"].append({"id": user_id, "username": username, "joined": datetime.now().isoformat()})
    elif action == "ref_click":
        stats["ref_clicks"] += 1
    save_stats(stats)

def main_keyboard():
    keyboard = [
        [KeyboardButton("🚀 Зарегистрироваться")],
        [KeyboardButton("💰 Условия и заработок"), KeyboardButton("❓ Частые вопросы")],
        [KeyboardButton("📊 Статистика")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    track_user(user.id, user.username or "", "start")

    caption = (
        f"👋 Привет, {user.first_name}!\n\n"
        "🛵 <b>Стань курьером Яндекс Еды в Москве</b>\n\n"
        "✅ Работай когда удобно — гибкий график\n"
        "✅ Выплаты <b>от 2 до 5 раз в неделю</b>\n"
        "✅ Быстрая регистрация — <b>за 1 день</b>\n"
        "✅ Нужен только телефон и желание работать\n\n"
        "👇 Выбери действие в меню внизу:"
    )

    await update.message.reply_photo(
        photo=PHOTO_URL,
        caption=caption,
        parse_mode="HTML",
        reply_markup=main_keyboard()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    if text == "🚀 Зарегистрироваться":
        track_user(user.id, user.username or "", "ref_click")
        keyboard = [
            [InlineKeyboardButton("📝 Перейти к регистрации", url=REF_LINK)],
            [InlineKeyboardButton("✅ Я заполнил анкету!", callback_data="registered")]
        ]
        await update.message.reply_text(
            "🎉 <b>Отлично! Для регистрации нажми кнопку ниже:</b>\n\n"
            "📋 <b>Что нужно сделать:</b>\n"
            "1. Нажми кнопку <b>«Перейти к регистрации»</b>\n"
            "2. Заполни анкету (~5 минут)\n"
            "3. После заполнения вернись сюда и нажми <b>«Я заполнил анкету!»</b>\n\n"
            "💬 Если возникнут вопросы — напиши нам, поможем!",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif text == "💰 Условия и заработок":
        await update.message.reply_text(
            "💰 <b>Условия работы курьером Яндекс Еды</b>\n\n"
            "📍 <b>Город:</b> Москва\n\n"
            "💵 <b>Заработок:</b>\n"
            "• Пеший курьер — от <b>1 500 до 3 000 ₽/день</b>\n"
            "• Велокурьер — от <b>2 000 до 4 000 ₽/день</b>\n"
            "• Авто/мото — от <b>3 000 до 6 000 ₽/день</b>\n\n"
            "⏰ <b>График:</b> Полностью свободный\n\n"
            "📱 <b>Требования:</b>\n"
            "• Смартфон (Android или iPhone)\n"
            "• Возраст от 18 лет\n\n"
            "💳 <b>Выплаты:</b> 2-5 раз в неделю на карту",
            parse_mode="HTML",
            reply_markup=main_keyboard()
        )

    elif text == "❓ Частые вопросы":
        await update.message.reply_text(
            "❓ <b>Частые вопросы</b>\n\n"
            "❔ <b>Нужен ли опыт работы?</b>\n"
            "Нет, опыт не нужен. Всему научат.\n\n"
            "❔ <b>Нужно ли своё оборудование?</b>\n"
            "Нет, термосумку выдают бесплатно.\n\n"
            "❔ <b>Как быстро одобрят заявку?</b>\n"
            "Обычно в течение 1-2 часов.\n\n"
            "❔ <b>Можно работать без гражданства РФ?</b>\n"
            "Да, нужен действующий документ.\n\n"
            "❔ <b>Когда первая выплата?</b>\n"
            "Уже после первой смены.",
            parse_mode="HTML",
            reply_markup=main_keyboard()
        )

    elif text == "📊 Статистика":
        stats = load_stats()
        text_msg = (
            "📊 <b>Статистика бота</b>\n\n"
            f"👥 Всего запусков: <b>{stats['total_starts']}</b>\n"
            f"🔗 Кликов по ссылке: <b>{stats['ref_clicks']}</b>\n"
            f"👤 Уникальных пользователей: <b>{len(stats['users'])}</b>\n"
        )
        if stats['total_starts'] > 0:
            text_msg += f"📈 Конверсия: <b>{round(stats['ref_clicks'] / stats['total_starts'] * 100, 1)}%</b>"
        await update.message.reply_text(text_msg, parse_mode="HTML", reply_markup=main_keyboard())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "registered":
        await query.edit_message_text(
            "🎊 <b>Спасибо, что заполнил анкету!</b>\n\n"
            "⏳ Ожидай одобрения от Яндекс Еды — обычно <b>1-2 часа</b>.\n\n"
            "📲 После одобрения тебе придёт уведомление в приложение.\n\n"
            "💬 Если что-то пошло не так — напиши нам, поможем разобраться!",
            parse_mode="HTML"
        )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Бот запущен!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
