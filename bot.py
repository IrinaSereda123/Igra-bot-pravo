import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Токен бота из переменных окружения
TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден в .env файле\nСоздайте .env файл с BOT_TOKEN=ваш_токен")

# Инициализация бота с настройками по умолчанию
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)
dp = Dispatcher()


# ============ КОМАНДЫ БОТА ============

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    welcome_text = """
<b>🎮 Добро пожаловать в Игровой Бот!</b>

Я помогу вам прокачать знания в игровой форме.
Выберите действие:
    """

    # Создаем клавиатуру с кнопками
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎮 Начать игру")],
            [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="❓ Помощь")],
            [KeyboardButton(text="👤 Профиль")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )

    await message.answer(welcome_text, reply_markup=keyboard)


@dp.message(Command("game"))
async def cmd_game(message: types.Message):
    """Обработчик команды /game"""
    await send_game_menu(message.chat.id)


@dp.message(F.text == "🎮 Начать игру")
async def start_game_button(message: types.Message):
    """Обработчик кнопки 'Начать игру'"""
    await send_game_menu(message.chat.id)


async def send_game_menu(chat_id: int):
    """Отправка меню игры с inline-кнопками"""
    menu_text = """
<b>🎯 Выберите раздел игры:</b>

• <b>Уровни</b> - Пройдите обучение от простого к сложному
• <b>Викторина</b> - Ответьте на вопросы на время
• <b>Сортировка</b> - Расставьте элементы в правильном порядке
    """

    # Создаем inline клавиатуру
    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            # Кнопка с WebApp для игры с уровнями - ИСПРАВЛЕНО: HTTP вместо HTTPS
            [InlineKeyboardButton(
                text="🚀 Уровни (WebApp)",
                web_app=WebAppInfo(url="http://localhost:8000/test_game.html")
            )],
            [
                InlineKeyboardButton(text="📝 Викторина", callback_data="game_quiz"),
                InlineKeyboardButton(text="🧩 Сортировка", callback_data="game_sort")
            ],
            [
                InlineKeyboardButton(text="🏆 Таблица лидеров", callback_data="leaders"),
                InlineKeyboardButton(text="📊 Моя статистика", callback_data="stats")
            ]
        ]
    )

    await bot.send_message(
        chat_id,
        menu_text,
        reply_markup=inline_keyboard
    )


# ============ ОБРАБОТКА CALLBACK-КНОПОК ============

@dp.callback_query(F.data == "game_quiz")
async def process_game_quiz(callback_query: types.CallbackQuery):
    """Обработка выбора викторины"""
    await callback_query.answer("🎮 Викторина скоро будет доступна!", show_alert=True)


@dp.callback_query(F.data == "game_sort")
async def process_game_sort(callback_query: types.CallbackQuery):
    """Обработка выбора сортировки"""
    await callback_query.answer("🧩 Игра 'Сортировка' в разработке!", show_alert=True)


@dp.callback_query(F.data == "leaders")
async def process_leaders(callback_query: types.CallbackQuery):
    """Показать таблицу лидеров"""
    leaders_text = """
<b>🏆 Топ-5 игроков:</b>

1. @player1 - 1500 очков 🥇
2. @player2 - 1200 очков 🥈
3. @player3 - 900 очков 🥉
4. @player4 - 750 очков
5. @player5 - 600 очков

<i>Хотите попасть в топ? Играйте больше!</i>
    """

    # Создаем кнопку для возврата
    back_button = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
        ]
    )

    await callback_query.message.edit_text(
        leaders_text,
        reply_markup=back_button
    )


@dp.callback_query(F.data == "stats")
async def process_stats(callback_query: types.CallbackQuery):
    """Показать статистику игрока"""
    user = callback_query.from_user

    stats_text = f"""
<b>📊 Ваша статистика:</b>

👤 Игрок: {user.first_name}
🏆 Очки: 1250
📈 Уровень: 8/15
✅ Пройдено заданий: 24
🎯 Процент побед: 85%

<i>Продолжайте в том же духе!</i>
    """

    # Создаем кнопку для возврата
    back_button = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
        ]
    )

    await callback_query.message.edit_text(
        stats_text,
        reply_markup=back_button
    )


@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback_query: types.CallbackQuery):
    """Возврат в главное меню"""
    await send_game_menu(callback_query.message.chat.id)
    await callback_query.answer()


# ============ ОБРАБОТКА ДАННЫХ ИЗ WEB APP ============

@dp.message(F.content_type == "web_app_data")
async def handle_web_app_data(message: types.Message):
    """Обработка данных из Web App"""
    try:
        import json
        data = json.loads(message.web_app_data.data)

        logger.info(f"Получены данные из WebApp: {data}")

        user = message.from_user

        if data.get('action') == 'game_complete':
            score = data.get('score', 0)
            level = data.get('level', 1)

            # Сохраняем прогресс (в реальном проекте - в базу данных)
            progress_text = f"""
✅ <b>Игра завершена успешно!</b>

👤 Игрок: {user.first_name}
🏆 Набрано очков: <b>{score}</b>
📈 Достигнут уровень: <b>{level}</b>

<i>Продолжайте играть, чтобы улучшить результат!</i>
            """

            # Кнопка для новой игры - ИСПРАВЛЕНО: тот же URL
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(
                        text="🎮 Играть снова",
                        web_app=WebAppInfo(url="http://localhost:8000/test_game.html")
                    )],
                    [InlineKeyboardButton(text="📊 Статистика", callback_data="stats")]
                ]
            )

            await message.answer(progress_text, reply_markup=keyboard)

        elif data.get('action') == 'save_progress':
            # Сохранение промежуточного прогресса
            await message.answer("📁 Прогресс сохранен! Можете продолжить позже.")

    except json.JSONDecodeError as e:
        logger.error(f"Ошибка парсинга JSON: {e}")
        await message.answer("❌ Ошибка обработки данных игры")
    except Exception as e:
        logger.error(f"Ошибка обработки Web App данных: {e}")
        await message.answer("❌ Произошла ошибка при сохранении прогресса")


# ============ ВСПОМОГАТЕЛЬНЫЕ КОМАНДЫ ============

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Помощь по боту"""
    help_text = """
<b>❓ Помощь по использованию бота:</b>

• <b>Начать игру</b> - нажмите кнопку "🎮 Начать игру"
• <b>Игра в WebApp</b> - откроется в браузере с уровнями и заданиями
• <b>Статистика</b> - просмотр ваших результатов
• <b>Таблица лидеров</b> - сравнение с другими игроками

<b>Как играть:</b>
1. Нажмите "🚀 Уровни (WebApp)"
2. Игра откроется в окне Telegram
3. Проходите уровни, перетаскивая блоки
4. Получайте очки и улучшайте результат

<i>Для связи с разработчиком: @ваш_username</i>
    """

    await message.answer(help_text)


@dp.message(Command("profile"))
async def cmd_profile(message: types.Message):
    """Профиль пользователя"""
    user = message.from_user

    profile_text = f"""
<b>👤 Ваш профиль:</b>

🆔 ID: <code>{user.id}</code>
👤 Имя: {user.first_name}
📛 Фамилия: {user.last_name or "Не указана"}
🔗 Username: @{user.username or "Не указан"}

<i>Данные профиля используются для сохранения прогресса в игре.</i>
    """

    await message.answer(profile_text)


# ============ ЗАПУСК БОТА ============

async def main():
    """Основная функция запуска бота"""
    logger.info("🚀 Бот запускается...")

    try:
        # Проверка соединения
        bot_info = await bot.get_me()
        logger.info(f"🤖 Бот @{bot_info.username} успешно инициализирован!")

        # Запуск polling
        await dp.start_polling(bot, skip_updates=True)

    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")
    finally:
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹ Бот остановлен пользователем")