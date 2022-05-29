import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.message import ContentType
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

import urllib

from convert import ConvertPdfToMp3, available_languages

from pathlib import Path


import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))


from Converter import converter

import configparser

config = configparser.ConfigParser()
config.read("config.ini")

API_TOKEN = config['Settings']['API_TOKEN']

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands=['cancel'], state="*")
@dp.message_handler(Text(equals="отмена", ignore_case=True), state="*")
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Action canceled", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands=['help'])
async def send_welcome(message: types.Message):
    await message.reply("Hi!\nI'm PDF to MP3 Converter Bot! So I can convert your PDF with text to <b>audio file!</b>",
                        parse_mode='HTML')


@dp.message_handler(commands=['start', 'convert'], state="*")
async def convert_start(message: types.Message):
    await ConvertPdfToMp3.STATE_PDF_WAITING.set()
    await message.answer('Send PDF file', reply_markup=types.ReplyKeyboardRemove())
    

@dp.message_handler(content_types=ContentType.DOCUMENT, state=ConvertPdfToMp3.STATE_PDF_WAITING)
async def convert_get_pdf(message: types.Message, state: FSMContext):
    document_id = message.document.file_id
    name = message.document.file_name
    local_file_path = f'./Bot/PDF/{name}'
    
    if not Path(local_file_path).is_file():
        file_info = await bot.get_file(document_id)
        file_path = file_info.file_path
        
        if file_path.split('.')[-1] != 'pdf':
            await message.answer(f"PDF-file needed! (Not {file_path.split('.')[-1].upper()})")
            return
        
        urllib.request.urlretrieve(f'https://api.telegram.org/file/bot{API_TOKEN}/{file_path}', local_file_path)
    await state.update_data(pdf_path=local_file_path)
    
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for language in available_languages:
        keyboard.add(language)
    
    await ConvertPdfToMp3.next()
    await message.answer('Select language (or type it like "en" or "ru"):\n', reply_markup=keyboard)
    

@dp.message_handler(state=ConvertPdfToMp3.STATE_LANGUAGE_WAITING)
async def convert_give_mp3(message: types.Message, state: FSMContext):
    if message.text.lower() not in available_languages:
        await message.answer('Please select language using keyboard.')
        return
    user_data = await state.get_data()
    
    pdf_path = user_data['pdf_path']
    language = message.text.lower()
    
    mp3_path = Path(pdf_path.replace('/PDF/', '/MP3s/'))
    mp3_path = str(mp3_path.with_suffix('.mp3'))
    
    if not Path(mp3_path).is_file():
        msg = await message.answer('Processing...', reply_markup=types.ReplyKeyboardRemove())
        mp3_path = converter.pdf_to_mp3(file_path=pdf_path,language=language,)
    
        if mp3_path:
            await message.answer('Done! Here\'s your audio:')
        else:
            await message.answer('Something went wrong! Try again.')
            await state.finish()
    
        await msg.delete()
    
    await bot.send_voice(message.from_user.id, types.input_file.InputFile(mp3_path, mp3_path.split('/')[-1]))
    
    # For memory optimization
    # os.remove(mp3_path)
    # os.remove(pdf_path)
    
    await state.finish()
    

@dp.message_handler()
async def echo(message: types.Message):
    await message.answer("<i>Use</i> <code>/help</code> <i>command for info about this bot!</i>", parse_mode='HTML')


if __name__ == '__main__':
    executor.start_polling(dp)
    