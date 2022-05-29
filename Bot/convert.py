from aiogram.dispatcher.filters.state import State, StatesGroup


available_languages = ['en', 'ru']


class ConvertPdfToMp3(StatesGroup):
    STATE_PDF_WAITING = State()
    STATE_LANGUAGE_WAITING = State()
