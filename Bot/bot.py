import configparser
import loguru

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.message import ContentType
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

import urllib

from convert import ConvertTextToAudio, available_languages

from pathlib import Path


import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(
    os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from Converter import converter


config = configparser.ConfigParser()
config.read("config.ini")

API_TOKEN = config['Settings']['API_TOKEN']

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands=['cancel'], state="*")
@dp.message_handler(Text(equals="cancel", ignore_case=True), state="*")
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Action <b>canceled</b>",
                         reply_markup=types.ReplyKeyboardRemove(),
                         parse_mode='HTML')


@dp.message_handler(commands=['help'])
async def send_welcome(message: types.Message):
    await message.reply("Hi!\nI'm <b>Text to Audio Converter Bot</b>! So I can <b>convert</b> your text (from <i>text file</i> or from <i>message</i>) to <b>audio file!</b>\nJust use command <code>/start</code> or <code>/convert</code>!",
                        parse_mode='HTML')


@dp.message_handler(commands=['start', 'convert'], state="*")
async def convert_start(message: types.Message):
    await ConvertTextToAudio.STATE_TEXT_WAITING.set()
    await message.answer('Send any <b>text file</b> or just <i>type</i> text!',
                         reply_markup=types.ReplyKeyboardRemove(),
                         parse_mode='HTML')


@dp.message_handler(content_types=[ContentType.DOCUMENT, ContentType.TEXT], state=ConvertTextToAudio.STATE_TEXT_WAITING)
async def convert_get_file_or_text(message: types.Message, state: FSMContext):
    if message.content_type == ContentType.DOCUMENT:
        try:
            document_id = message.document.file_id
            name = message.document.file_name
            local_file_path = f'./Bot/PDF/{name}'

            if not Path(local_file_path).is_file():
                file_info = await bot.get_file(document_id)
                file_path = file_info.file_path

                urllib.request.urlretrieve(
                    f'https://api.telegram.org/file/bot{API_TOKEN}/{file_path}', local_file_path)

                text = converter.file_to_text(local_file_path)

                await state.update_data(pdf_path=local_file_path)
            await state.update_data(text=text)
        except Exception:
            await message.answer('An <code>error</code> has occurred! <b>Check your file</b> and <i>try again</i>!',
                                 parse_mode='HTML')
            return
    elif message.content_type == ContentType.TEXT:
        await state.update_data(text=message.text)
    else:
        await message.answer(f"<b>Text file</b> or <b>text</b> needed!",
                             parse_mode='HTML')
        return

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for language in available_languages:
        keyboard.insert(language)

    await ConvertTextToAudio.next()
    await message.answer('Select <i>language</i> (or type it like <code>"en"</code> or <code>"ru"</code>):\n',
                         reply_markup=keyboard,
                         parse_mode='HTML')


@dp.message_handler(state=ConvertTextToAudio.STATE_LANGUAGE_WAITING)
async def convert_send_voice(message: types.Message, state: FSMContext):
    if message.text.lower() not in available_languages:
        await message.answer('Please select <i>language</i> using <b>keyboard</b>.',
                             parse_mode='HTML')
        return
    user_data = await state.get_data()

    text = user_data['text']
    language = message.text.lower()

    mp3_path = f"./Bot/MP3/{converter.unique_filename('MP3', 'voice')}.mp3"

    if not Path(mp3_path).is_file():
        msg = await message.answer('<i>Processing...</i>',
                                   reply_markup=types.ReplyKeyboardRemove(),
                                   parse_mode='HTML')
        mp3_path = converter.text_to_mp3(text=text, language=language,)

        if mp3_path:
            await message.answer('<b>Done!</b> Here\'s your <i>audio</i>:',
                                 parse_mode='HTML')
        else:
            await message.answer('<b>Something went wrong!</b> Try <i>again</i>.',
                                 parse_mode='HTML')
            await state.finish()

        await msg.delete()

    await bot.send_voice(message.from_user.id, types.input_file.InputFile(mp3_path, mp3_path.split('/')[-1]))

    # For memory optimization
    os.remove(mp3_path)
    if 'pdf_path' in user_data:
        os.remove(user_data['pdf_path'])

    await state.finish()


@dp.message_handler()
async def echo(message: types.Message):
    await message.answer("<i>Use</i> <code>/help</code> <i>command for info about this bot!</i>",
                         parse_mode='HTML')


if __name__ == '__main__':
    loguru.logger.info(f"Number of message handlers: {len(dp.message_handlers.handlers)}.")
    loguru.logger.info(f"Number of callback query handlers: {len(dp.callback_query_handlers.handlers)}.")
    loguru.logger.warning("The application is running in polling mode.")
    executor.start_polling(dp)
