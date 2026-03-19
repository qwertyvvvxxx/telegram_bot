import re

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters
from credentials import config
from gpt import ChatGptService
from util import (load_message, send_text, send_image, show_main_menu, default_callback_handler, load_prompt,
                  send_text_with_buttons, cancel)
import asyncio

GPT, TALK_SELECT, TALK_DIALOG = range(3)



#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# клава (кнопка) для чату щоб виключити режим GPT

finish_button = ReplyKeyboardMarkup([[KeyboardButton("Закінчити")]], resize_keyboard=True)

QUIZ_THEMES_KEYBOARD = {
    "quiz_prog": "Програмування 💻",
    "quiz_math": "Математика 🧮",
    "quiz_hist": "Історія 📜"
}

def get_quiz_after_action_keyboard(theme):
    return {
        f"quiz_{theme}": "Ще питання на цю тему 🔄",
        "quiz_change_theme": "Змінити тему 📋",
        "quiz_stop": "Закінчити квіз 🏁"
    }
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
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def get_gpt_service(context: ContextTypes.DEFAULT_TYPE):
    if 'gpt_service' not in context.user_data:
        context.user_data['gpt_service'] = ChatGptService()
    return context.user_data['gpt_service']


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

    gpt = get_gpt_service(context)
    gpt.set_prompt(prompt)
    response_text = await gpt.send_message_list()

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

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gpt = get_gpt_service(context)
    gpt.set_prompt(load_prompt('gpt'))
    await send_image(update, context, 'gpt')
    await update.message.reply_text(load_message('gpt'), reply_markup=finish_button)

    return GPT

async def gpt_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    if user_text == "Закінчити":
        if 'gpt_service' in context.user_data:
            context.user_data['gpt_service'].message_list.clear()

        await update.message.reply_text("Режим ChatGPT вимкнено", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    status_message = await update.message.reply_text("ChatGPT готує відповідь...")

    gpt_service = get_gpt_service(context)
    response_text = await gpt_service.add_message(user_text)

    await status_message.edit_text(response_text)
    return GPT




#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["quiz_score"] = 0

    await send_image(update, context, 'quiz')

    await send_text_with_buttons(update, context,
        "Виберіть тему для квізу:",
        QUIZ_THEMES_KEYBOARD
    )


async def quiz_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "quiz_stop":
        await query.edit_message_reply_markup(reply_markup=None)
        await start(update, context)
        return

    if data == "quiz_change_theme":
        await send_text_with_buttons(update, context, "Виберіть нову тему:", QUIZ_THEMES_KEYBOARD)
        return

    if data.startswith("quiz_answer_"):
        selected_num = data.split("_")[-1]
        correct_num = str(context.user_data.get('quiz_correct_answer', ""))
        theme = context.user_data.get('quiz_theme')

        question_text = context.user_data.get('last_question', "Питання")
        choices = context.user_data.get('last_choices', {})

        user_choice_text = choices.get(selected_num, selected_num)

        if selected_num == correct_num:
            result_text = "✅ Правильно!"
            context.user_data['quiz_score'] = context.user_data.get('quiz_score', 0) + 1
        else:
            correct_val = choices.get(correct_num, f"№{correct_num}")
            result_text = f"❌ Неправильно.\nПравильна відповідь: {correct_val}"

        score = context.user_data.get('quiz_score', 0)

        final_report = (
            f"❓ {question_text}\n\n"
            f"Твоя відповідь: {user_choice_text}\n"
            f"{result_text}\n\n"
            f"Ваш рахунок: {score} 🔥"
        )

        try:
            await query.edit_message_text(text=final_report)
        except Exception:
            pass

        await asyncio.sleep(3.5)

        await send_text_with_buttons(update, context, "Що робимо далі? 👇", get_quiz_after_action_keyboard(theme))
        return

    if data.startswith("quiz_"):
        theme = data.split("_")[1]
        context.user_data['quiz_theme'] = theme

        await query.edit_message_text("⏳ ChatGPT готує питання...")

        gpt = get_gpt_service(context)
        gpt.message_list = []

        prompt = (f"Згенеруй ОДНЕ питання для квізу на тему: {theme}.\n"
                  f"Формат відповіді (РІВНО 6 РЯДКІВ):\n"
                  f"1. Питання\n"
                  f"2. Варіант 1\n"
                  f"3. Варіант 2\n"
                  f"4. Варіант 3\n"
                  f"5. Варіант 4\n"
                  f"6. Правильна відповідь: [лише цифра 1-4]")

        response = await gpt.send_question("Ти — технічний API. Пиши суворо 6 рядків без вступу.", prompt)

        lines = [l.strip() for l in response.strip().split('\n') if l.strip()]

        if len(lines) > 6:
            lines = lines[-6:]

        if len(lines) < 6:
            await query.edit_message_text(
                "😵 Помилка формату. Спробуйте ще раз.",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🔄 Повторити", callback_data=f"quiz_{theme}")]])
            )
            return

        def clean_choice(text):
            return re.sub(r'^(\d[\.\)\s]+|[a-z][\.\)\s]+)', '', text).strip()

        question_text = lines[0]
        c1, c2, c3, c4 = clean_choice(lines[1]), clean_choice(lines[2]), clean_choice(lines[3]), clean_choice(lines[4])

        context.user_data['last_question'] = question_text
        context.user_data['last_choices'] = {"1": c1, "2": c2, "3": c3, "4": c4}

        match = re.search(r'[1-4]', lines[5])
        context.user_data['quiz_correct_answer'] = match.group() if match else "1"

        choices_buttons = {
            "quiz_answer_1": c1,
            "quiz_answer_2": c2,
            "quiz_answer_3": c3,
            "quiz_answer_4": c4
        }

        await send_text_with_buttons(update, context, f"❓ {question_text}", choices_buttons)


#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

async def talk(update, context):
    msg = load_message("talk")

    await send_image(update, context, "talk")

    choices_buttons = {
        "talk_cobain": "Курт Кобейн",
        "talk_hawking": "Стівен Гокінг",
        "talk_nietzsche": "Фрідріх Ніцше",
        "talk_queen": "Єлизавета II",
        "talk_tolkien": "Джон Толкін",
    }

    await send_text_with_buttons(update, context, msg, choices_buttons)
    return TALK_SELECT


async def talk_button(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()
    await send_image(update, context, query)
    await update.callback_query.message.reply_text(
        "Гарний вибір! Можеш починати спілкування. Коли захочеш вийти — натисни кнопку нижче.",
        reply_markup=finish_button
    )
    promt = load_prompt(query)

    gpt_service = get_gpt_service(context)
    gpt_service.set_prompt(promt)

    return TALK_DIALOG


async def talk_dialog(update, context):
    if not update.message or not update.message.text:
        return TALK_DIALOG

    text = update.message.text

    if text == "Закінчити":
        gpt_service = get_gpt_service(context)
        gpt_service.message_list.clear()

        await update.message.reply_text("Діалог завершено.", reply_markup=ReplyKeyboardRemove())

        return ConversationHandler.END

    my_message = await send_text(update, context, "набирає повідомлення....")

    gpt_service = get_gpt_service(context)
    answer = await gpt_service.add_message(text)

    await my_message.edit_text(answer)

    return TALK_DIALOG






#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    app = ApplicationBuilder().token(config.BOT_TOKEN).concurrent_updates(True).build()

    #  Conversation для talk
    talk_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('talk', talk)],
        states={
            TALK_SELECT: [CallbackQueryHandler(talk_button, pattern="^talk_")],
            TALK_DIALOG: [MessageHandler(filters.TEXT & ~filters.COMMAND, talk_dialog)]
        },
        fallbacks=[MessageHandler(filters.Regex("^Закінчити$"), cancel)],
        per_message=False
    )

    #  Conversation GPT
    gpt_handler = ConversationHandler(
        entry_points=[CommandHandler('gpt', gpt)],
        states={
            GPT: [MessageHandler(filters.TEXT & ~filters.COMMAND, gpt_dialog)]
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            MessageHandler(filters.Regex("Закінчити"), cancel)
        ],
        per_message=False
    )

    # РЕЄСТРАЦІЯ
    app.add_handler(talk_conversation_handler)
    app.add_handler(gpt_handler)

    # Глобальні команди
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('random', random))
    app.add_handler(CommandHandler('quiz', quiz))

    # Колбеки для quiz та random
    app.add_handler(CallbackQueryHandler(quiz_button_handler, pattern='^quiz_.*'))
    app.add_handler(CallbackQueryHandler(random_button_handler, pattern='^next_random$|^stop_random$'))

    # Глобальний фільтр "Закінчити"
    app.add_handler(MessageHandler(filters.Regex("Закінчити"), start))

    print("-----------------бота запущено без помилок-----------------")
    app.run_polling()
