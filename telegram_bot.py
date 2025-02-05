from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import asyncio
import time
import re
import threading

class TelegramBotHandler:
    def __init__(self, token):
        self.token = token
        self.bot = Bot(token=token)
        self._ready = threading.Event()
        self.last_message = None
        self.message_received = threading.Event()
        
    async def start_command(self, update: Update, context):
        print(f"Bot nhận được lệnh start từ user {update.message.chat.id}")
        await update.message.reply_text('Xin chào! Bot đã sẵn sàng nhận mã OTP.')
        
    async def handle_message(self, update: Update, context):
        if not update.message:
            return
            
        chat_id = update.message.chat.id
        text = update.message.text.strip()
        
        print(f"Bot nhận được tin nhắn từ {chat_id}: {text}")
        
        # Lưu tin nhắn mới nhất
        self.last_message = text
        self.message_received.set()
        
        await update.message.reply_text(f'Đã nhận tin nhắn của bạn: {text}')

    async def error(self, update, context):
        print(f'Lỗi: {context.error}')

    def start_bot(self):
        try:
            thread = threading.Thread(target=self._run_bot)
            thread.daemon = True
            thread.start()
            if self._ready.wait(timeout=10):
                print("Bot đã khởi động và sẵn sàng!")
            else:
                print("Timeout khi khởi động bot!")
        except Exception as e:
            print(f"Lỗi khi khởi động bot: {str(e)}")
        
    def _run_bot(self):
        async def main():
            try:
                self.application = Application.builder().token(self.token).build()
                
                self.application.add_handler(MessageHandler(filters.TEXT, self.handle_message))
                self.application.add_handler(CommandHandler('start', self.start_command))
                self.application.add_error_handler(self.error)
                
                await self.application.initialize()
                await self.application.start()
                self._ready.set()
                
                await self.application.run_polling(allowed_updates=Update.ALL_TYPES)
                
            except Exception as e:
                print(f"Lỗi trong main loop của bot: {str(e)}")
                self._ready.set()
            
        asyncio.run(main())
    
    async def send_message(self, chat_id, text):
        """Gửi tin nhắn đến Telegram chat."""
        try:
            await self.bot.send_message(chat_id=chat_id, text=text)
            print(f"Đã gửi tin nhắn thành công: {text}")
        except Exception as e:
            print(f"Lỗi khi gửi tin nhắn: {str(e)}")
            
    async def get_otp(self, chat_id, timeout=60):
        """
        Lấy mã OTP từ tin nhắn MỚI NHẤT trong Telegram chat.
        Chỉ nhận tin nhắn được gửi SAU khi bắt đầu chờ.
        """
        start_time = time.time()
        last_update_id = -1

        # Lấy update mới nhất ban đầu để làm baseline
        try:
            updates = await self.bot.get_updates(offset=-1, limit=1, timeout=10)
            if updates:
                last_update_id = updates[-1].update_id
        except Exception as e:
            print(f"Lỗi khi lấy update ban đầu: {str(e)}")

        print("Đang chờ mã OTP từ Telegram...")

        while time.time() - start_time < timeout:
            try:
                updates = await self.bot.get_updates(offset=last_update_id + 1, timeout=10)
                for update in updates:
                    last_update_id = update.update_id
                    if update.message and str(update.message.chat.id) == str(chat_id):
                        message_text = update.message.text
                        print(f"Nhận được tin nhắn mới: {message_text}")
                        otp_match = re.search(r"(\d{4,8})", message_text)
                        if otp_match:
                            otp_code = otp_match.group(1)
                            print(f"Đã tìm thấy mã OTP: {otp_code}")
                            return otp_code
            except Exception as e:
                print(f"Lỗi khi lấy updates: {str(e)}")
            await asyncio.sleep(2)

        print("Hết thời gian chờ OTP")
        return None