from gtts import gTTS
from art import tprint
import pdfplumber
from pathlib import Path


def pdf_to_mp3(file_path='test.pdf', language='en', mp3s_folder_name='MP3s'):
    try:
        if Path(file_path).is_file() and Path(file_path).suffix == '.pdf':
            # print(f'[x] Got file {Path(file_path).name}')
            
            with pdfplumber.PDF(open(file=file_path, mode='rb')) as pdf:
                pages = [page.extract_text() for page in pdf.pages]
            
            text = ''.join(pages).replace('\n', '')
            
            # print(f'[x] Processing...')

            audio = gTTS(text=text, lang=language, slow=False)
            file_name = Path(file_path).stem
            
            # Create MP3s dir if it doesn't exists
            Path(f'{Path.cwd()}\\{mp3s_folder_name}').mkdir(parents=True, exist_ok=True)
            
            mp3_path = f'./Bot/{mp3s_folder_name}/{file_name}.mp3'
            
            audio.save(mp3_path)
            
            # print(f'[x] Done! Saved MP3 as {file_name}.mp3 to {mp3s_folder_name} folder')
            
            return mp3_path
        else:
            return False
    except Exception as e:
        print(e)
        return False
            

def main():
    tprint('PDF TO MP3', font="lean")
    print('Welcome to PDF to MP3 converter!\n')
    
    file_path = input('Input file path: ')
    language = input('Input language (for example, \'en\' or \'ru\'): ')
    mp3s_folder_name = input('Input MP3s folder name: ')
    
    print('\n')
    
    if pdf_to_mp3(file_path=file_path,
                  language=language,
                  mp3s_folder_name=mp3s_folder_name):
        print('\nThanks for using this program!\n')
    else:
        print('\nSomething went wrong! Check file path and language!\n')
    

if __name__ == "__main__":
    main()
