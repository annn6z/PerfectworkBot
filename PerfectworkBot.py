import telebot
from datetime import datetime
import json
import os

# Замените 'YOUR_BOT_TOKEN' на токен, полученный от @BotFather
TOKEN = '8495781654:AAGRQ0rpvLhpvfe6Vza1AC-fAoqteAuaEZc'
bot = telebot.TeleBot(TOKEN)

# Файл для хранения задач
TASKS_FILE = 'tasks.json'

# Загрузка задач из файла
def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# Сохранение задач в файл
def save_tasks(tasks):
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

# Инициализация хранилища задач
tasks = load_tasks()

@bot.message_handler(commands=['help'])
def help_command(message):
    """Обработчик команды /help - показывает доступные команды"""
    help_text = """
🤖 *Доступные команды:*

/help - Показать это сообщение
/add <задача> <дата в формате ДД.ММ.ГГГГ> - Добавить задачу
/show <дата в формате ДД.ММ.ГГГГ> - Показать задачи на дату

*Пример:*
`/add Купить молоко 15.02.2026`
`/show 15.02.2026`

*Поддерживает пробелы вокруг даты!*
    """
    bot.reply_to(message, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['add'])
def add_task(message):
    """Обработчик команды /add - добавляет задачу"""
    try:
        # Получаем текст после команды
        command_parts = message.text.split(maxsplit=2)
        if len(command_parts) < 3:
            bot.reply_to(message, "❌ Неверный формат! Используйте: /add <задача> <дата ДД.ММ.ГГГГ>")
            return
        
        task_text = command_parts[1]
        date_str = command_parts[2].strip()  # ✅ ИСПРАВЛЕНО: убираем пробелы
        
        # Парсим дату
        task_date = datetime.strptime(date_str, '%d.%m.%Y').strftime('%Y-%m-%d')
        
        # Получаем chat_id пользователя
        user_id = str(message.from_user.id)
        
        # Добавляем задачу
        if user_id not in tasks:
            tasks[user_id] = {}
        if task_date not in tasks[user_id]:
            tasks[user_id][task_date] = []
        
        tasks[user_id][task_date].append(task_text)
        save_tasks(tasks)
        
        bot.reply_to(message, f"✅ Задача добавлена!\n📝 *{task_text}*\n📅 *{date_str}*", parse_mode='Markdown')
        
    except ValueError:
        bot.reply_to(message, "❌ Неверный формат даты! Используйте ДД.ММ.ГГГГ (например, 01.02.2026)")
    except Exception as e:
        bot.reply_to(message, "❌ Ошибка при добавлении задачи")

@bot.message_handler(commands=['show'])
def show_tasks(message):
    """Обработчик команды /show - показывает задачи на дату"""
    try:
        # Получаем дату из команды
        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) < 2:
            bot.reply_to(message, "❌ Укажите дату! Используйте: /show ДД.ММ.ГГГГ")
            return
        
        date_str = command_parts[1].strip()  # ✅ ИСПРАВЛЕНО: убираем пробелы
        task_date = datetime.strptime(date_str, '%d.%m.%Y').strftime('%Y-%m-%d')
        user_id = str(message.from_user.id)
        
        # Проверяем наличие задач
        if user_id in tasks and task_date in tasks[user_id]:
            tasks_list = tasks[user_id][task_date]
            response = f"📋 *Задачи на {date_str}:*\n\n"
            for i, task in enumerate(tasks_list, 1):
                response += f"{i}. {task}\n"
            bot.reply_to(message, response, parse_mode='Markdown')
        else:
            bot.reply_to(message, f"📭 На {date_str} задач нет")
            
    except ValueError:
        bot.reply_to(message, "❌ Неверный формат даты! Используйте ДД.ММ.ГГГГ (например, 01.02.2026)")
    except Exception as e:
        bot.reply_to(message, "❌ Ошибка при показе задач")

# Запуск бота
if __name__ == '__main__':
    print("🚀 Бот запущен! Нажмите Ctrl+C для остановки.")
    bot.polling(none_stop=True)