import asyncio
import logging
from aiogram import Bot, Dispatcher
from app.handlers import router
from data.database.models import async_main
from data.database.models import scheduler
import config


bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

if config.DEBUG:
    logging.basicConfig(level=logging.INFO)


async def main():
    await async_main()
    scheduler.start()
    dp.include_router(router=router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, RuntimeError):
        print('Exit')
