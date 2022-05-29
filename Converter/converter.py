from gtts import gTTS
from pathlib import Path
import textract
import pdfplumber


def unique_filename(dir, filename):
    counter = 0
    if Path(f"./Bot/{dir}/{filename}{counter if counter else ''}.mp3").is_file():
        counter += 1
    return f"{filename}{counter if counter else ''}"


def file_to_text(file_path: str):
    if not file_path.endswith('.pdf'):
        return textract.process(file_path, encoding='utf-8').decode('utf-8').replace('\n', '')
    else:
        with pdfplumber.PDF(open(file=file_path, mode='rb')) as pdf:
            pages = [page.extract_text() for page in pdf.pages]
        text = ''.join(pages).replace('\n', '')
        return text


def text_to_mp3(text, language='ru', mp3_dir='MP3s'):
    file_name = unique_filename(mp3_dir, 'voice')

    try:
        if Path(text).is_file():
            file_name = Path(text).stem
            text = file_to_text(file_path=text)

        # Make audio
        audio = gTTS(text=text, lang=language, slow=False)

        # Create MP3s dir if it doesn't exists
        Path(f'{Path.cwd()}\\{mp3_dir}').mkdir(parents=True, exist_ok=True)

        mp3_path = f'./Bot/{mp3_dir}/{file_name}.mp3'
        audio.save(mp3_path)
        return mp3_path
    except Exception as e:
        return e


def main():
    print('PDF TO MP3\n\nWelcome to PDF to MP3 converter!\n')

    file_path = input('Input file path or text: ')
    language = input('Input language (for example, \'en\' or \'ru\'): ')
    mp3s_folder_name = input('Input MP3s folder name: ')

    print('\n')

    if text_to_mp3(text=file_path,
                  language=language,
                  mp3_dir=mp3s_folder_name):
        print('\nThanks for using this program!\n')
    else:
        print('\nSomething went wrong! Check file path and language!\n')


if __name__ == "__main__":
    main()
