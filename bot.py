from aiogram import executor, types, Bot, Dispatcher
from dispatcher import dp, bot
import handlers
import filters
import time, threading
import asyncio

from db import BotDB

# функция поллинга базы данных для уведомления клиента
async def scheduled(wait_for=20):
    while True:
        try:
            await bot.send_message(BotDB.check_notify(), f"Изменился статус ваших документов!\nМяч на вашей стороне\nПроверить нужные документы можно командой /Документы", disable_notification = True)
        except:
            print("nobody to update")
            await asyncio.sleep(wait_for)


BotDB = BotDB('on_your_side.db')


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(scheduled())
    #dp.loop.create_task( scheduled(3600))

    executor.start_polling(dp, skip_updates = True)
