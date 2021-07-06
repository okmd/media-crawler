import requests
import os

from . import settings
from ..utilities import utils
from ..utilities.file import File

class Media:
    def __init__(self, url, filename):
        self.url = url
        self.save_link_filename = filename
        
    def media_filename(self):
        try:
            name = utils.get_filename(self.url)
            domain = utils.get_hostname(self.url)
            extention = utils.get_extension(self.url)
            if extention in settings.ALLOWED_TYPE:
                location = os.path.join(settings.ROOT_LOCATION, domain, extention.title())
                os.makedirs(location, exist_ok=True)
                return os.path.join(location, name).lower()
            else:
                print(f"File is of type {extention} only {settings.ALLOWED_TYPE} are allowed.")
        except Exception as e:
            print(f"Error! {e}.")

    def media_download(self):
        # check if already downloaded:
        file = File(self.save_link_filename)
        if file.downloded(self.url):
            print(f"Already downloaded: {self.url}")
            return
        
        response = requests.get(self.url, stream=True,headers=settings.HEADERS)
        if response.status_code == 200:
            if not response.content:
                raise ValueError("Content is not available in response.")
            print(f"\nDownloading: {self.url}.")
            saving_location = self.media_filename()
            if saving_location:
                if os.path.exists(saving_location):
                    print(f"Stored at: {saving_location}.")
                    return
                
                # download media 
                utils.download_media(saving_location, response)
                print(f"Downloaded: {saving_location}.")
                file_links = file.read_content()
                # if media link is present and allowed to download
                if file_links.get(self.url, None) and file_links[self.url].get(settings.MEDIA, None) in settings.ALLOWED_TYPE:
                    file_links[self.url][settings.DOWNLOADED] = True
                else:
                    file_links[self.url] = {settings.MEDIA: utils.get_extension(self.url), settings.SCRAPPED: True, settings.VISITED: True, settings.DOWNLOADED: False}
                file.write_content(file_links)
            else:
                print(f"Not a valid filename {saving_location}.")
        else:
            print(f"Response {response.status_code} for {self.url}!")
        response.close()
