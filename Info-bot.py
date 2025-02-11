from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# Укажи chat_id администратора
ADMIN_CHAT_ID = chat_id  # Замени на реальный chat_id

# Данные для бота
PRICES = {
    "Стрижка": "1000 руб.",
    "Маникюр": "1500 руб.",
    "Массаж": "2000 руб."
}

PRICES_MESSAGE = "ПРАЙС-ЛИСТ:\n\n" + "\n".join([f"{service}: {price}" for service, price in PRICES.items()])

SCHEDULE = {
    "Стрижка": "Пн-Пт, 10:00 - 18:00",
    "Маникюр": "Вт-Чт, 12:00 - 20:00",
    "Массаж": "Ср-Сб, 9:00 - 17:00"
}

SCHEDULE_MESSAGE = "РАСПИСАНИЕ:\n\n" + "\n".join([f"{service}: {time}" for service, time in SCHEDULE.items()])

CONTACTS = {
    "Имя": "Иван Иванов",
    "Телефон": "8-123-456-78-90"
}

CONTACTS_MESSAGE = "КОНТАКТЫ:\n\n" + "\n".join([f"{key}: {value}" for key, value in CONTACTS.items()])

SERVICES = ["Стрижка", "Маникюр", "Массаж"]

# Функция для отображения основного меню
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Узнать прайс", callback_data='price')],
        [InlineKeyboardButton("Узнать расписание", callback_data='schedule')],
        [InlineKeyboardButton("Контакты", callback_data='contacts')],
        [InlineKeyboardButton("Записаться", callback_data='book')],
        [InlineKeyboardButton("Посмотреть фото зала", callback_data='photo')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        await update.callback_query.edit_message_text("Выберите опцию:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Выберите опцию:", reply_markup=reply_markup)

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_main_menu(update, context)

# Обработчик команды /price
async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_price(update, context)

# Обработчик команды /schedule
async def schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_schedule(update, context)

# Обработчик команды /contacts
async def contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_contacts(update, context)

# Обработчик команды /book
async def book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_book(update, context)

# Обработчик команды /photo
async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_photo(update, context)

# Обработчик нажатий на кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'price':
        await handle_price(update, context)
    elif query.data == 'schedule':
        await handle_schedule(update, context)
    elif query.data == 'contacts':
        await handle_contacts(update, context)
    elif query.data == 'photo':
        await handle_photo(update, context)
    elif query.data == 'book':
        await handle_book(update, context)
    elif query.data.startswith('book_'):
        service = query.data.split('_')[1]
        context.user_data['service'] = service
        if 'name' not in context.user_data:
            await query.edit_message_text(f"Вы выбрали: {service}.\n\nДля записи введите ваше имя:")
        else:
            await query.edit_message_text(f"{context.user_data['name']}, Вы выбрали: {service}.\n\nДля продолжения записи введите Ваш телефон:")
    elif query.data == 'back':
        await show_main_menu(update, context)

# Обработчик текстовых сообщений (для записи)
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'service' in context.user_data:
        if 'name' not in context.user_data:
            context.user_data['name'] = update.message.text
            await update.message.reply_text("Введите ваш номер телефона:")
        else:
            phone = update.message.text
            service = context.user_data['service']
            name = context.user_data['name']

            # Отправка информации администратору
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=f"Новая запись:\nУслуга: {service}\nИмя: {name}\nТелефон: {phone}"
            )

            await update.message.reply_text("Спасибо! Ваша запись отправлена администратору.")
            context.user_data.clear()  # Очистка данных
            await show_main_menu(update, context)

# Функция для обработки прайса
async def handle_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.edit_message_text(PRICES_MESSAGE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data='back')]]))
    else:
        await update.message.reply_text(PRICES_MESSAGE)
        await show_main_menu(update, context)

# Функция для обработки расписания
async def handle_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.edit_message_text(SCHEDULE_MESSAGE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data='back')]]))
    else:
        await update.message.reply_text(SCHEDULE_MESSAGE)
        await show_main_menu(update, context)

# Функция для обработки контактов
async def handle_contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.edit_message_text(CONTACTS_MESSAGE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data='back')]]))
    else:
        await update.message.reply_text(CONTACTS_MESSAGE)
        await show_main_menu(update, context)

# Функция для обработки записи
async def handle_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(service, callback_data=f"book_{service}")] for service in SERVICES]
    keyboard.append([InlineKeyboardButton("Назад", callback_data='back')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        await update.callback_query.edit_message_text("Выберите услугу:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Выберите услугу:", reply_markup=reply_markup)

# Функция для обработки фото
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_url = "https://avatars.mds.yandex.net/get-ydo/1653787/2a00000174ac5244021e5131620708d16fd4/diploma"
    if update.callback_query:
        await update.callback_query.message.reply_photo(photo_url, caption="Вот фото зала")
        await update.callback_query.message.reply_text("", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data='back')]]))
    else:
        await update.message.reply_photo(photo_url, caption="Вот фото зала")
        await update.message.reply_text("", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data='back')]]))

# Основная функция
def main():
    # Вставь сюда свой токен
    token = 'BOT_TOKEN'
    application = ApplicationBuilder().token(token).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("price", price))
    application.add_handler(CommandHandler("schedule", schedule))
    application.add_handler(CommandHandler("contacts", contacts))
    application.add_handler(CommandHandler("book", book))
    application.add_handler(CommandHandler("photo", photo))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
