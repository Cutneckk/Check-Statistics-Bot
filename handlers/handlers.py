import asyncio
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from sqlalchemy import select
from htmlparser.htmlparser import check_listeners_yam, check_listeners_spotify
from keyboards.keyboards import inline_keyboard
from database.database import async_session, Stats, delete_oldest
from datetime import timezone
from asyncio import to_thread
import os

load_dotenv()

CHAT_ID = os.getenv('CHAT_ID')

router = Router()
processing_flag = set()


@router.message(CommandStart())
async def start(message: Message):
    username = message.from_user.username
    await message.answer(text=f'Привет, {username}!,\n'
                              f'я могу узнать статистику твоих слушателей!',
                         reply_markup=inline_keyboard())


async def collect_statistics(bot: Bot, chat_id: int = CHAT_ID):
    try:
        listeners_yam = await to_thread(check_listeners_yam)
        listeners_spotify = await to_thread(check_listeners_spotify)
        comparison = await comparison_statistics()

        async with async_session() as session:
            await delete_oldest(session)
            new_stat = Stats(listeners_yam=listeners_yam,
                         listeners_spotify=listeners_spotify)
            session.add(new_stat)
            await session.commit()
        if bot and chat_id:
            if comparison:
                try:
                    text = (f'--- Сводка слушателей по Яндекс Музыка и Spotify:\n'
                            f'--- на {comparison['new_time']}\n'
                            f'--- Яндекс музыка: {listeners_yam} слушателей в месяц.\n'
                            f'--- Spotify: {listeners_spotify} слушателей в месяц.\n'
                            f'\n'
                            f'--- Общее количество слушателей: {listeners_yam + listeners_spotify} в месяц.'
                            f'\n'
                            f'\n'
                            f'\n'
                            f'--- По сравнению со статистикой:\n'
                            f'--- на {comparison['old_time']}\n'
                            f'--- Яндекс музыка: {comparison['dif_yam']}\n '
                            f'--- Spotify: {comparison['dif_spotify']}\n'
                            f'--- Общие изменения слушателей: {comparison['dif_total']}\n')
                    await bot.send_message(chat_id=chat_id, text=text)
                except asyncio.exceptions.TimeoutError:
                    await bot.send_message(chat_id=chat_id, text='Не удалось отобразить статистику...\n'
                                                                 'Попробуйте позже или вручную...')
            else:
                try:
                    text = (f'--- На данный момент нельзя сравнить статистику,\n'
                            f'--- но вот сводка на сегодняшний день\n'
                            f'--- по Яндекс Музыка и Spotify:\n'
                            f'\n'
                            f'--- Яндекс музыка: {listeners_yam} слушателей в месяц.\n'
                            f'--- Spotify: {listeners_spotify} слушателей в месяц.\n'
                            f'\n'
                            f'--- Общее количество слушателей: {listeners_yam + listeners_spotify} в месяц.')
                    await bot.send_message(chat_id=chat_id, text=text)

                except asyncio.exceptions.TimeoutError:
                    await bot.send_message(chat_id=chat_id, text='Не удалось отобразить статистику...\n'
                                                                 'Попробуйте позже или вручную...')

    except asyncio.exceptions.TimeoutError:
        await bot.send_message(chat_id=chat_id, text='Не удалось получить данные с площадок или базы данных...')


@router.callback_query(F.data == 'statistics')
async def statistics(callback: CallbackQuery, bot: Bot):
    chat_id = callback.message.chat.id
    if chat_id in processing_flag:
        await callback.answer(text="❗️ Запрос уже выполняется, подождите...", show_alert=True)
        return

    loading_msg = await callback.message.answer('⏳ Выполняю запрос...')
    processing_flag.add(chat_id)
    await callback.answer()

    try:
        await collect_statistics(bot, chat_id)
        await loading_msg.delete()

    finally:
        processing_flag.remove(chat_id)


async def comparison_statistics():
    async with async_session() as session:
        try:
            stmt = select(Stats).order_by(Stats.id.desc()).limit(2)
            result = await session.execute(stmt)
            records = result.scalars().all()

            if len(records) < 2:
                return None

            new_record, old_record = records[0], records[1]
            dif_listeners_yam = new_record.listeners_yam - old_record.listeners_yam
            dif_listeners_spotify = old_record.listeners_spotify - new_record.listeners_spotify
            sum_dif = dif_listeners_yam + dif_listeners_spotify

            new_time = new_record.created_at.astimezone(timezone.utc).strftime('%d.%m.%Y')
            old_time = old_record.created_at.astimezone(timezone.utc).strftime('%d.%m.%Y')

            return {
                'old_time' : old_time,
                'new_time' : new_time,
                'dif_yam' : dif_listeners_yam,
                'dif_spotify' : dif_listeners_spotify,
                'dif_total' : sum_dif
            }
        except:
            return None


async def setup_scheduler(bot: Bot):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(collect_statistics, 'interval', hours=24, args=(bot, CHAT_ID))
    scheduler.start()


