import os
import logging

from . import settings
from ..utilities import utils
from ..utilities.file import File

class Media:
    def __init__(self, url, filename):
        self.url = url
        self.save_link_filename = filename
        
    def media_filename(self):
        try:
            self.extention = utils.get_extension(self.url)
            if self.extention in settings.ALLOWED_TYPE:
                location = os.path.join(settings.ROOT_LOCATION, utils.get_hostname(self.url), self.extention.title())
                os.makedirs(location, exist_ok=True)
                return os.path.join(location, utils.get_filename(self.url)).lower()
            else:
                logging.info(f"File is of type {self.extention} only {settings.ALLOWED_TYPE} are allowed.")
        except Exception as e:
            logging.error(f"Error! {e}.")

    def media_download(self):
        logging.info("Crawler started downloading media..")
        saving_location = self.media_filename()
        if saving_location:
            # check if already downloaded:
            file = File(self.save_link_filename)            
            if file.downloded(self.url) and os.path.exists(saving_location):
                logging.info(f"Already downloaded: {self.url}")
                logging.info(f"Stored at: {saving_location}.")
                return
            
            response = utils.get_response(self.url, stream=True)
            if response:
                if self.extention in settings.ALLOWED_TYPE:
                    # download media 
                    logging.info(f"Downloading: {self.url}.")
                    utils.download_media(saving_location, response)
                    logging.info(f"Downloaded: {saving_location}.")
                    download = True
                else:
                    download = False
                file_links = file.read_content()
                # if media link is present and allowed to download
                if file_links.get(self.url, None):
                    file_links[self.url][settings.DOWNLOADED] = download
                else:
                    file_links[self.url] = {settings.MEDIA: self.extention, settings.SCRAPPED: True, settings.VISITED: True, settings.DOWNLOADED: download}
                file.write_content(file_links)
            utils.sleep()
        else:
            logging.info(f"Not a valid filename {saving_location}.")
