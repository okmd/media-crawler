from pathlib import Path
from urllib.parse import urlparse
import concurrent.futures
import os
from ..crawler import settings

def get_extension(url):
    return Path(url).suffix.strip('.').lower()

def get_hostname(url):
    return urlparse(url.strip('/')).hostname

def get_filename(url):
    return os.path.basename(url)

def remove_forward_slash(url):
    return url.replace("\\", "/")

def download_media(saving_location, content):
    def download(saving_location, content):
        try:
            with open(saving_location, 'wb') as f:
                for chunk in content.iter_content(chunk_size=1024):
                    f.write(chunk)
        except Exception as e:
            print(f"Error Saving file {saving_location}.")
    # save with threading
    with concurrent.futures.ThreadPoolExecutor(max_workers=settings.MAX_THREADS) as executor:
        executor.submit(download, saving_location, content)
    
            
def content_filename(url):
    return f"{get_hostname(url)}.txt"

def is_scrapable(url):
    '''
    A url is scrapable if it not a valid url of any media like, jpg, 3gp, mp4 etc.
    A url is not scrapable if it is valid url of .mp3, .xmls etc.
    # urls like /, .php, .html 232/ are scrapable
    '''
    extension = get_extension(url)
    if not extension:
        return True
    if extension in settings.ALLOWED_TYPE or extension in settings.ALL_RESOURCE_TYPE:
        return False
    return True

