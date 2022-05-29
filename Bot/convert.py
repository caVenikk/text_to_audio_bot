from aiogram.dispatcher.filters.state import State, StatesGroup


available_languages = ['en', 'ru']


class ConvertTextToAudio(StatesGroup):
    STATE_TEXT_WAITING = State()
    STATE_LANGUAGE_WAITING = State()
