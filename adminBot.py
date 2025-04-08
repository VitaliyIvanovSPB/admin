import logging
import os
import pymongo
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

load_dotenv('.env')
TOKEN = os.getenv('BOT_TOKEN')
ADMIN = os.getenv('ADMIN')
CONNECTION_STRING = os.getenv('CONNECTION_STRING')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)



class MongoDB:
    def __init__(self, connection_string):
        self.client = pymongo.MongoClient(connection_string)
        self.admin_bot_db = self.client['admin_bot']
        self.admin_bot_users_col = self.admin_bot_db['admin_bot_users']

    def set_user_info(self, user, new_value):
        self.admin_bot_users_col.update_one(user, {'$set': new_value}, upsert=True)


class AdminBot:
    def __init__(self, token):
        application = ApplicationBuilder().token(token).build()

        start_handler = CommandHandler('start', self.start)
        echo_handler = MessageHandler(filters.TEXT, self.echo)
        unknown_handler = MessageHandler(filters.COMMAND, self.unknown)

        application.add_handler(start_handler)
        application.add_handler(echo_handler)
        application.add_handler(unknown_handler)

        application.run_polling()

    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        db.set_user_info(
            {'user_id': update.effective_user.id},
            {'user_id': update.effective_user.id,
             'username': update.effective_user.username,
             }
        )
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Отправь мне сообщение, я отправлю его администратору.")

    @staticmethod
    async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        if chat_id == int(ADMIN):
            if update.message.reply_to_message:
                await context.bot.send_message(chat_id=update.message.reply_to_message.forward_origin.sender_user.id,
                                               text=update.message.text)
        else:
            await update.message.reply_text('Запрос отправлен.')
            await context.bot.forward_message(chat_id=int(ADMIN), from_chat_id=chat_id,
                                              message_id=update.message.message_id)

    @staticmethod
    async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Sorry, I didn't understand that command.")


if __name__ == '__main__':
    db = MongoDB(CONNECTION_STRING)
    AdminBot(TOKEN)
