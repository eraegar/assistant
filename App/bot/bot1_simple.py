import os
import traceback
import html
import json
import uuid
import requests
import telegram
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from dotenv import load_dotenv
from typing import Optional, Dict, Any

# Загружаем .env из папки Backend, где он создается при деплое
backend_dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'Backend', '.env')
if os.path.exists(backend_dotenv_path):
    load_dotenv(dotenv_path=backend_dotenv_path)
else:
    load_dotenv() # Fallback to root .env

TOKEN = os.getenv("BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# URL-адреса для ссылок
PLANS_URL = "https://t.me/assist_for_rent_bot/plans"
MANAGER_URL = "https://t.me/assist_for_rent_bot/manager"
ASSISTANT_URL = "https://t.me/assist_for_rent_bot/assistant"
CLIENT_WEBAPP_URL = os.getenv("CLIENT_WEBAPP_URL", "https://rent-assistant.ru")

def get_session_id(user_id: str) -> str:
    """Get or create session ID for user"""
    # For simplicity, we'll use a combination of user_id and hour
    # In production, you might want to store this in Redis or similar
    import datetime
    hour = datetime.datetime.now().hour
    return f"{user_id}_{hour}"

async def track_interaction(user: telegram.User, action: str, action_data: Optional[Dict[str, Any]] = None, conversion_stage: Optional[str] = None):
    """Track user interaction for analytics"""
    try:
        if not user:
            return
            
        user_info = {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'language_code': getattr(user, 'language_code', None)
        }
        
        session_id = get_session_id(str(user.id))
        
        tracking_data = {
            'telegram_user_id': str(user.id),
            'action': action,
            'action_data': action_data or {},
            'user_info': user_info,
            'session_id': session_id,
            'conversion_stage': conversion_stage
        }
        
        # Send to backend analytics endpoint
        # For now, we'll just print it. In production, you'd send to your backend
        print(f"📊 Analytics: {action} by user {user.first_name} ({user.id})")
        
        # Uncomment for real tracking:
        # requests.post(f"{BACKEND_URL}/api/v1/management/analytics/telegram/track", 
        #               json=tracking_data, timeout=5)
        
    except Exception as e:
        print(f"❌ Analytics tracking error: {e}")

async def start(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет приветственное сообщение с основным меню."""
    user = update.effective_user
    if not user:
        return
    
    # Track start interaction
    await track_interaction(user, 'start', conversion_stage='started_bot')
        
    welcome_text = (
        f"👋 Здравствуйте, {user.first_name}!\n\n"
        "Я ваш личный консьерж-бот сервиса «Ассистент в аренду».\n\n"
        "Готов помочь вам делегировать рутину и освободить время для самого важного.\n\n"
        "Что вас интересует?"
    )

    keyboard = [
        [telegram.InlineKeyboardButton("📄 Тарифы", callback_data='pricing')],
        [telegram.InlineKeyboardButton("💡 Примеры задач", callback_data='task_examples')],
        [telegram.InlineKeyboardButton("📄 Документы", callback_data='documents')],
        [telegram.InlineKeyboardButton("📞 Поддержка", callback_data='support')]
    ]
    
    markup = telegram.InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=markup)

async def handle_keywords(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ключевые слова и отправляет соответствующие ссылки."""
    if not update.message or not update.message.text:
        return
        
    user = update.effective_user
    user_message = update.message.text.lower()

    # Track keyword interactions
    if user:
        await track_interaction(user, 'keyword_search', {'keyword': user_message})

    if 'менеджер' in user_message:
        if user:
            await track_interaction(user, 'request_manager_app')
        await update.message.reply_text(f"Ссылка на приложение для менеджеров:\n{MANAGER_URL}")

    elif 'ассистент' in user_message:
        if user:
            await track_interaction(user, 'request_assistant_app')
        await update.message.reply_text(f"Ссылка на приложение для ассистентов:\n{ASSISTANT_URL}")


async def handle_callback(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает нажатия на inline-кнопки."""
    query = update.callback_query
    if not query:
        return

    await query.answer()
    user = update.effective_user
    if not user:
        return

    if query.data == 'pricing':
        await track_interaction(user, 'view_pricing', {'source': 'bot_menu'}, 'viewed_pricing')
        await query.edit_message_text(
            text=f"Вы можете ознакомиться с тарифами по ссылке:\n{PLANS_URL}",
            reply_markup=telegram.InlineKeyboardMarkup([
                [telegram.InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]
            ])
        )

    elif query.data == 'task_examples':
        await track_interaction(user, 'view_examples', {'source': 'bot_menu'}, 'viewed_examples')
        examples_text = (
            "💡 <b>Чем может помочь ассистент?</b>\n\n"
            "Практически всем! Вот несколько популярных примеров:\n\n"
            "<b>Личные дела:</b>\n"
            "✈️  Найти билеты и забронировать отель для отпуска\n"
            "🍽️  Заказать столик в ресторане на вечер\n"
            "🎁  Найти и заказать подарок коллеге на день рождения\n"
            "🚗  Записать машину на техническое обслуживание\n\n"
            "<b>Бизнес-задачи:</b>\n"
            "📊  Собрать информацию о 5 конкурентах в вашей нише\n"
            "📄  Расшифровать аудиозапись совещания в текст\n"
            "📅  Организовать встречу с партнерами, согласовав время\n"
            "📝  Найти и отфильтровать 10 резюме кандидатов\n\n"
            "Готовы попробовать? Нажмите на кнопку «Открыть Приложение» прямо сейчас!"
        )
        keyboard = [
            [telegram.InlineKeyboardButton("🚀 Открыть приложение", url=CLIENT_WEBAPP_URL)],
            [telegram.InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]
        ]
        markup = telegram.InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(examples_text, reply_markup=markup, parse_mode=telegram.constants.ParseMode.HTML)

    elif query.data == 'documents':
        await track_interaction(user, 'view_documents', {'source': 'bot_menu'})
        documents_text = (
            "📄 <b>Безопасность ваших данных</b>\n\n"
            "Ваши данные в полной безопасности. Мы строго соблюдаем законодательство (ФЗ-152) и используем шифрование для защиты информации.\n\n"
            "Мы собираем только то, что нужно для выполнения ваших задач, и никогда не передаем данные третьим лицам без вашего согласия.\n\n"
            "Для получения полных текстов документов или удаления данных, пожалуйста, свяжитесь со службой поддержки."
        )
        keyboard = [
            [telegram.InlineKeyboardButton("📞 Связаться по вопросам данных", callback_data='support')],
            [telegram.InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]
        ]
        markup = telegram.InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(documents_text, reply_markup=markup, parse_mode=telegram.constants.ParseMode.HTML)

    elif query.data == 'support':
        await track_interaction(user, 'contact_support', {'source': 'bot_menu'})
        support_text = (
            "📞 <b>Служба поддержки</b>\n\n"
            "Возникли вопросы? Наша команда на связи и готова помочь!\n\n"
            "<b>Время работы:</b>\n"
            "Пн-Пт: 9:00 - 21:00 (MSK)\n\n"
            "<b>Контакты:</b>\n"
            "• Email: support@assistant-for-rent.com\n"
            "• Telegram: @assistant_for_rent_support"
        )
        keyboard = [
            [telegram.InlineKeyboardButton("💬 Написать в поддержку", url="https://t.me/assistant_for_rent_support")],
            [telegram.InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]
        ]
        markup = telegram.InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(support_text, reply_markup=markup, parse_mode=telegram.constants.ParseMode.HTML)

    elif query.data == 'back_to_main':
        await track_interaction(user, 'back_to_main')
        welcome_text = (
            f"👋 Здравствуйте, {user.first_name}!\n\n"
            "Я ваш личный консьерж-бот сервиса «Ассистент в аренду».\n\n"
            "Готов помочь вам делегировать рутину и освободить время для самого важного.\n\n"
            "Что вас интересует?"
        )
        keyboard = [
            [telegram.InlineKeyboardButton("📄 Тарифы", callback_data='pricing')],
            [telegram.InlineKeyboardButton("💡 Примеры задач", callback_data='task_examples')],
            [telegram.InlineKeyboardButton("📄 Документы", callback_data='documents')],
            [telegram.InlineKeyboardButton("📞 Поддержка", callback_data='support')]
        ]
        markup = telegram.InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(welcome_text, reply_markup=markup)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Логирует ошибки и отправляет сообщение пользователю."""
    if context.error:
        print(f"ERROR in {__name__}: An error occurred")
        print(f"Update: {update}")
        print(f"Context: {context.error}")
        traceback.print_exception(type(context.error), context.error, context.error.__traceback__)
        
        DEVELOPER_CHAT_ID = os.getenv("DEVELOPER_CHAT_ID")
        if DEVELOPER_CHAT_ID:
            try:
                update_str = update.to_json() if isinstance(update, telegram.Update) else str(update)
                tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
                tb_string = "".join(tb_list)
                message = (
                    f"‼️ Произошла ошибка в боте\n\n"
                    f"<pre>update = {html.escape(json.dumps(json.loads(update_str), indent=2, ensure_ascii=False))}</pre>\n\n"
                    f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
                    f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
                    f"<pre>{html.escape(tb_string)}</pre>"
                )
                await context.bot.send_message(
                    chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=telegram.constants.ParseMode.HTML
                )
            except Exception as e:
                print(f"Failed to send error message to developer: {e}")
            
    if isinstance(update, telegram.Update) and update.effective_message:
        await update.effective_message.reply_text(
            "😕 Произошла непредвиденная ошибка. Мы уже работаем над ее устранением. Попробуйте позже."
        )

async def setup_bot_commands(application: Application):
    """Устанавливает команды и кнопку меню для бота."""
    await application.bot.set_my_commands([
        telegram.BotCommand("start", "🚀 Перезапустить бота")
    ])
    menu_button = telegram.MenuButtonDefault()
    await application.bot.set_chat_menu_button(menu_button=menu_button)
    
def main():
    if not TOKEN or TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Ошибка: Не установлен токен бота!")
        print("�� Создайте файл .env с вашим токеном: BOT_TOKEN=ваш_токен_от_botfather")
        return

    print("🤖 Starting Assistant-for-Rent Bot...")
    print(f"🔑 Token: {TOKEN[:10]}...")

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_keywords))
    
    application.add_error_handler(error_handler)

    print("🚀 Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main() 