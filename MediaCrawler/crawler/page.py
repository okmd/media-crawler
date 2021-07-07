import os
from tqdm import tqdm
import concurrent.futures
from lxml import html
import logging

from ..utilities.file import File
from ..utilities import utils
from .media import Media
from . import settings



class Page:
    def __init__(self, root, filename):
        self.root = root
        self.save_link_filename = filename

    def find_page_links(self):
        response = utils.get_response(self.root)
        links = set()
        if response:
            extracted_html = html.fromstring(response.content)
            media_urls = extracted_html.xpath(settings.MEDIA_TYPE['media'])
            # find all types of media
            for media_type in settings.MEDIA_TYPE.keys():
                media_urls += extracted_html.xpath(settings.MEDIA_TYPE[media_type])

            domain_name = utils.get_hostname(self.root)
            for media_url in media_urls:
                media_url =utils.remove_forward_slash(media_url)
                if not media_url.startswith("http"):
                    media_url = os.path.join(domain_name, media_url)
                # remove wrong slash
                links.add(media_url)
        return links

    def download_page_media(self):
        # Make this link visited, all link comming here not visited earlier.
        file = File(self.save_link_filename)
        file_links = file.read_content()
        # check if already visited:
        if file.visited(self.root):
            logging.info(f"Already Visited: {self.root}")
            return

        media_links = self.find_page_links()
        utils.sleep()
        with concurrent.futures.ThreadPoolExecutor(max_workers=settings.MAX_THREADS) as executor:
            for link in tqdm(media_links, position=0, leave=True, ncols=100, desc="Page "):
                media = Media(link, self.save_link_filename)
                executor.submit(media.media_download)
                file_links[link] = {settings.MEDIA: utils.get_extension(link), settings.SCRAPPED: True, settings.VISITED: True, settings.DOWNLOADED: True}
                file.write_content(file_links)
                
        if file_links.get(self.root, None):
            file_links[self.root][settings.VISITED] = True
        else:
            file_links[self.root] = {settings.MEDIA: utils.get_extension(self.root), settings.SCRAPPED: False, settings.VISITED: True, settings.DOWNLOADED: False}
        file.write_content(file_links)
