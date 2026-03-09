from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters

from credentials import config
from gpt import ChatGptService
from util import (load_message, send_text, send_image, show_main_menu,
                  default_callback_handler, load_prompt)
from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

GPT: int = 1

# клава (кнопка) для чату щоб виключити режим GPT

gpt_keyboard = ReplyKeyboardMarkup([[KeyboardButton("Закінчити")]], resize_keyboard=True)



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
    prompt_text = load_prompt('random')
    message = await update.message.reply_text(load_message('random'))
    chat_gpt.set_prompt(prompt_text)
    response_text = await chat_gpt.send_message_list()
    await message.edit_text(response_text)

async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_gpt.set_prompt(load_prompt('gpt'))
    await send_image(update, context, 'gpt')
    await update.message.reply_text(load_message('gpt'), reply_markup=gpt_keyboard)

    return GPT

async def gpt_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    if user_text == "Закінчити":
        await update.message.reply_text("Режим ChatGPT вимкненно", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    message = await update.message.reply_text("ChatGPT готує відповідь...")
    response_text = await chat_gpt.send_question(user_text)

    await message.edit_text(response_text)

    return GPT




#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------




chat_gpt = ChatGptService(config.GPT_API_KEY)

if __name__ == '__main__':
    app = ApplicationBuilder().token(config.BOT_TOKEN).build()

    gpt_handler = ConversationHandler(
        entry_points=[CommandHandler('gpt', gpt)],
        states={
            # Коли ми в стані GPT (1), чекаємо на текст від користувача
            GPT: [MessageHandler(filters.TEXT & ~filters.COMMAND, gpt_dialog)]
        },
        fallbacks=[CommandHandler('start', start)] # Вихід з режиму при /start
    )

    # РЕЄСТРУЮ ХЕНДЛЕРИ:
    app.add_handler(gpt_handler)
    app.add_handler(CommandHandler('random', random)) # Потім прості команди
    app.add_handler(CommandHandler('start', start)) # Потім головне меню
    print("-----------------бота запущено без помилок-----------------")
    app.run_polling()
