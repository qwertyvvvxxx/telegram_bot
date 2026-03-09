from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters
from credentials import config
from gpt import ChatGptService
from util import (load_message, send_text, send_image, show_main_menu, default_callback_handler, load_prompt)

GPT: int = 1

# клава (кнопка) для чату щоб виключити режим GPT

finish_button = ReplyKeyboardMarkup([[KeyboardButton("Закінчити")]], resize_keyboard=True)



#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------




async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = load_message('main')
    await send_image(update, context, 'main')
    await send_text(update, context, text)
    await show_main_menu(update, context, {
        'start': 'Головне меню',
        'random': 'Дізнатися випадковий цікавий факт 🧠',
        'gpt': 'Задати питання чату GPT 🤖',
        'talk': 'Поговорити з відомою особистістю 👤',
        'quiz': 'Взяти участь у квізі ❓'
        # Додати команду в меню можна так:
        # 'command': 'button text'

    })
async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    random_buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("Хочу ще факт ", callback_data='next_random')],
        [InlineKeyboardButton("Завершити ", callback_data='stop_random')]
    ])

    is_callback = update.callback_query is not None

    if is_callback:
        await update.callback_query.answer()
        target_message = update.callback_query.message
    else:
        target_message = update.message

    prompt = load_prompt('random')
    status_message = await target_message.reply_text(load_message('random'))

    chat_gpt.set_prompt(prompt)

    response_text = await chat_gpt.send_message_list()
    await status_message.delete()
    await target_message.reply_text(response_text, reply_markup=random_buttons)

async def random_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data == 'next_random':
        await random(update, context)
    elif data == 'stop_random':
        await query.edit_message_reply_markup(reply_markup=None)
        await start(update, context)



async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_gpt.set_prompt(load_prompt('gpt'))
    await send_image(update, context, 'gpt')
    await update.message.reply_text(load_message('gpt'), reply_markup=finish_button)

    return GPT

async def gpt_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    if user_text == "Закінчити":
        await update.message.reply_text("Режим ChatGPT вимкненно", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    message = await update.message.reply_text("ChatGPT готує відповідь...")
    prompt = load_prompt('gpt')
    response_text = await chat_gpt.send_question(prompt, user_text)
    await message.edit_text(response_text)

    return GPT




#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------




chat_gpt = ChatGptService(config.GPT_API_KEY)

if __name__ == '__main__':
    app = ApplicationBuilder().token(config.BOT_TOKEN).concurrent_updates(True).build()

    gpt_handler = ConversationHandler(
        entry_points=[
            CommandHandler('gpt', gpt)
        ],
        states={
            GPT: [MessageHandler(filters.TEXT & ~filters.COMMAND, gpt_dialog)]
        },
        fallbacks=[
            CommandHandler('start', start),
            MessageHandler(filters.Regex("Закінчити"), start)
        ]
    )

    # РЕЄСТРУЮ ХЕНДЛЕРИ:
    app.add_handler(gpt_handler)
    app.add_handler(CommandHandler('random', random))
    app.add_handler(CommandHandler('start', start))

    app.add_handler(CallbackQueryHandler(random_button_handler, pattern='^next_random$|^stop_random$'))
    # обробник кнопки "Закінчити"
    app.add_handler(MessageHandler(filters.Regex("Закінчити"), start))
    print("-----------------бота запущено без помилок-----------------")
    app.run_polling()
