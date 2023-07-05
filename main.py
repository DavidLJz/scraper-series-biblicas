import argparse
from json import dump
import functions as f
from os import path
from gdown import download as gdown_download
from decouple import config

SERIE_URL = config('SERIE_URL', "https://series.net/miserie/")
OUTPUT_DIR = config('OUTPUT_DIR', './output')
NAME_FORMAT = config('NAME_FORMAT', 'CAPITULO_%03d.mp4')
JSON_CHAPTER_LIST = config('JSON_CHAPTER_LIST', './chapters.json')
CHAPTER_START = config('CHAPTER_START', 1, cast=int)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape the website')

    parser.add_argument('chapter', type=int, help='Chapter to scrape')
    parser.add_argument('output', type=str, help='Output directory')

    args = parser.parse_args()
    
    # Check if output can be written
    dir_out = path.dirname(args.output)

    if not path.isdir(dir_out):
        raise Exception('Output path is not a directory')

    basename = NAME_FORMAT % args.chapter
    output = path.join(dir_out, basename)

    if path.isfile(output):
        # Ask if overwrite
        userinput = input('File already exists. Do you want to overwrite? [y/N] ')

        if userinput.lower() != 'y':
            print('Aborted')
            quit()

    driver = f.get_edge_driver(
        headless=True,
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
        '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    )

    driver.get(SERIE_URL)

    f.close_dialogs(driver)
    urls = f.get_chapter_url(driver, args.chapter)

    driver.quit()

    if urls is None or len(urls) == 0:
        raise Exception('No urls found')

    for url in urls:
        id = url.split('/')[5]
        
        try:
            fname = gdown_download(id=id, output=output, quiet=False)

            print(f'Saved: {fname}')
            quit()

        except Exception as e:
            print(e)
            continue

    print('No files could be downloaded')
    quit(1)