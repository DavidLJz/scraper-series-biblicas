from datetime import datetime
import functions as f
from json import dump, load
from os import path, remove, makedirs
from gdown import download as gdown_download
from decouple import config
from time import sleep
import logging as logging_module

makedirs('./logs', exist_ok=True)

logfname = './logs/' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.log'

# format time - level - pid - message
fmt = '%(asctime)s - [%(levelname)s] - %(process)d - %(message)s'

# new logger that prints to console and file
logging = logging_module.getLogger('downloader')
logging.setLevel(logging_module.DEBUG)
logging.addHandler(logging_module.FileHandler(logfname))

# Add stdout handler
logging.addHandler(logging_module.StreamHandler())

# Set format
logging.handlers[0].setFormatter(logging_module.Formatter(fmt))
logging.handlers[1].setFormatter(logging_module.Formatter(fmt))

def get_url_dict(json_path:str, url:str) -> dict:
    logging.debug('Getting chapter urls from %s or %s' % (json_path, url))

    if not path.isfile(json_path):
        logging.debug('File not found, creating new one')

        driver = f.get_edge_driver(
            headless=True,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
            '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )

        driver.get(url)

        f.close_dialogs(driver)
        urls = f.get_chapter_url_list(driver)

        if urls is None or len(urls) == 0:
            raise Exception('No urls found')

        logging.debug('Found %d urls' % len(urls))
        
        with open(json_path, 'w') as fl:
            dump(urls, fl)
            fl.close()

        logging.debug('Saved urls to %s' % json_path)        
    
        driver.quit()
    else:
        logging.debug('Loading urls from ' + json_path)

        with open(json_path, 'r') as fl:
            urls = load(fl)
            fl.close()

    return urls

SERIE_URL = config('SERIE_URL', "https://series.net/miserie/")
OUTPUT_DIR = config('OUTPUT_DIR', './output')
NAME_FORMAT = config('NAME_FORMAT', 'CAPITULO_%03d.mp4')
JSON_CHAPTER_LIST = config('JSON_CHAPTER_LIST', './chapters.json')
CHAPTER_START = config('CHAPTER_START', 1, cast=int)

logging.debug('SERIE_URL: ' + SERIE_URL)
logging.debug('OUTPUT_DIR: ' + OUTPUT_DIR)
logging.debug('NAME_FORMAT: ' + NAME_FORMAT)
logging.debug('JSON_CHAPTER_LIST: ' + JSON_CHAPTER_LIST)
logging.debug('CHAPTER_START: ' + str(CHAPTER_START))

makedirs(OUTPUT_DIR, exist_ok=True)

try:
    chapter_urls = get_url_dict(JSON_CHAPTER_LIST, SERIE_URL)

    failed_downloads = []

    for i_chapter in range(CHAPTER_START, len(chapter_urls)):
        s_chapter = str(i_chapter)

        logging.debug('Downloading chapter ' + s_chapter)

        if s_chapter not in chapter_urls:
            logging.error('Chapter not found in chapter list: ' + s_chapter)
            continue

        chapter_fpath = path.join(OUTPUT_DIR, NAME_FORMAT % int(i_chapter))

        success = False

        for url in chapter_urls[s_chapter]:
            id = url.split('/')[5]
            
            try:
                logging.debug('Downloading from %s to %s' % (url, chapter_fpath))

                fname = gdown_download(id=id, output=chapter_fpath, quiet=True)
                
                if not path.isfile(chapter_fpath):
                    raise Exception('File not found after download ' + chapter_fpath)
        
                success = True
                break

            except Exception as e:
                logging.error('Error downloading')
                logging.error(e, exc_info=True)

        if not success:
            failed_downloads.append(chapter_fpath)
            continue

        logging.debug('Downloaded chapter ' + s_chapter)

        sleep(15)

    logging.debug('Failed downloads: %s' % failed_downloads)

    if len(failed_downloads) > 3:
        # Remove JSON_CHAPTER_LIST file
        logging.debug('Removing ' + JSON_CHAPTER_LIST)

        today = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

        with open(JSON_CHAPTER_LIST, 'r') as fl:
            content = fl.read()
            fl.close()

        with open(today + JSON_CHAPTER_LIST, 'w') as fl:
            fl.write(content)
            fl.close()

        remove(JSON_CHAPTER_LIST)

except Exception as e:
    logging.error(e, exc_info=True)

    quit(1)