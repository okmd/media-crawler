import requests
import os
from tqdm import tqdm
import concurrent.futures
from lxml import html
import time

from ..utilities.file import File
from ..utilities import utils
from .media import Media
from . import settings



class Page:
    def __init__(self, root, filename):
        self.root = root
        # self.media_type = settings.ALLOWED_TYPE
        self.save_link_filename = filename

    def find_page_links(self):
        response = requests.get(self.root, headers=settings.HEADERS)
        links = []
        if response.status_code == 200:
            extracted_html = html.fromstring(response.content)
            media_urls = extracted_html.xpath(settings.MEDIA_TYPE['media'])
            # find all types of media
            for media_type in settings.MEDIA_TYPE.keys():
                media_urls += extracted_html.xpath(settings.MEDIA_TYPE[media_type])

            domain_name = utils.get_hostname(self.root)
            for media_url in media_urls:
                if not media_url.startswith("http"):
                    media_url = os.path.join(domain_name, media_url)
                # remove wrong slash
                links.append(utils.remove_forward_slash(media_url))
            return links
        else:
            print(f"Response {response.status_code} for {self.root} !")
        response.close()

    def download_page_media(self):
        # Make this link visited, all link comming here not visited earlier.
        file = File(self.save_link_filename)
        file_links = file.read_content()
        # check if already visited:
        if file.visited(self.root):
            print(f"Already Visited: {self.root}")
            file_links[self.root]['visited'] = False
            file.write_content(file_links)
            return

        media_links = self.find_page_links()
        if len(media_links) == 0:
            print(f"No links found in {self.root}.")
            return
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=settings.MAX_THREADS) as executor:
            for link in tqdm(media_links):
                media = Media(link, self.save_link_filename)
                executor.submit(media.media_download)
                media = utils.get_extension(link)
                file_links[link] = {settings.MEDIA: media, settings.SCRAPPED: True, settings.VISITED: True, settings.DOWNLOADED: False}
                file.write_content(file_links)
                time.sleep(10)
                
        file_links[self.root]['visited'] = True
        file.write_content(file_links)
