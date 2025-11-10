from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def inline_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text='Запросить статистику', callback_data='statistics')

    builder.adjust(2)

    return builder.as_markup()


