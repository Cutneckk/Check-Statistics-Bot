import asyncio
from aiogram import Dispatcher,Bot
from aiogram.types import BotCommandScopeDefault, BotCommand
from handlers.handlers import router, setup_scheduler
from dotenv import load_dotenv
import os

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

commands = [BotCommand(command='start', description='Начать работу!')]


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())
    await bot.delete_webhook(drop_pending_updates=True)
    await setup_scheduler(bot)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())