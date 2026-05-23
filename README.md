# 🤖 Telegram AI Bot з Gemini API

Багатофункціональний Telegram бот на Python з інтеграцією Google Gemini AI. Бот підтримує інтерактивні діалоги, квізи, випадкові факти та розмови з відомими особистостями.

## ✨ Функціонал

- **💬 Gemini режим** — інтерактивний діалог з AI асистентом
- **🧠 Випадкові факти** — генерація цікавих фактів на різні теми
- **❓ Квізи** — інтерактивні квізи з різних тем (програмування, математика, історія)
- **👤 Розмови з особистостями** — спілкування з AI в образі відомих людей:
  - Курт Кобейн
  - Стівен Гокінг
  - Фрідріх Ніцше
  - Єлизавета II
  - Джон Толкін

## 🚀 Встановлення

### Вимоги

- Python 3.8+
- Telegram Bot Token
- Google Gemini API Key

### Крок 1: Клонування репозиторію

```bash
git clone https://github.com/yourusername/telegram-gemini-bot.git
cd telegram-gemini-bot
```

### Крок 2: Встановлення залежностей

```bash
pip install -r requirements.txt
```

### Крок 3: Налаштування змінних середовища

Створіть файл `.env` на основі `.env.example`:

```bash
cp .env.example .env
```

Відредагуйте `.env` та додайте свої ключі:

```env
BOT_TOKEN=your_telegram_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
```

#### Як отримати токени:

**Telegram Bot Token:**
1. Відкрийте [@BotFather](https://t.me/botfather) в Telegram
2. Відправте команду `/newbot`
3. Слідуйте інструкціям та отримайте токен

**Gemini API Key:**
1. Перейдіть на [Google AI Studio](https://aistudio.google.com/apikey)
2. Створіть новий API ключ
3. Скопіюйте ключ

### Крок 4: Запуск бота

```bash
python bot.py
```

## 📋 Команди бота

- `/start` — Головне меню
- `/gemini` — Режим Gemini діалогу
- `/random` — Отримати випадковий факт
- `/quiz` — Почати квіз
- `/talk` — Поговорити з відомою особистістю

## 🛠️ Технології

- **python-telegram-bot** — Telegram Bot API
- **google-genai** — Google Gemini AI API
- **python-dotenv** — Управління змінними середовища
- **asyncio** — Асинхронне виконання

## 📁 Структура проекту

```
telegram-gemini-bot/
├── bot.py              # Основний файл бота
├── gemini.py           # Сервіс для роботи з Gemini API
├── credentials.py      # Конфігурація та змінні середовища
├── util.py             # Допоміжні функції
├── resources/          # Ресурси бота
│   ├── messages/       # Текстові повідомлення
│   ├── prompts/        # Промпти для AI
│   └── images/         # Зображення для бота
├── .env.example        # Приклад файлу змінних середовища
├── .gitignore          # Git ignore файл
└── README.md           # Документація
```

## 🔧 Налаштування

Ви можете налаштувати промпти для AI в папці `resources/prompts/` та текстові повідомлення в `resources/messages/`.

## 📝 Ліцензія

MIT License

## 🤝 Внесок

Pull requests вітаються! Для великих змін спочатку відкрийте issue для обговорення.

## 📧 Контакти

Якщо у вас є питання або пропозиції, створіть issue в репозиторії.

---

⭐ Якщо проект вам сподобався, поставте зірку!