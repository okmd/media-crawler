import requests
import os
from tqdm import tqdm
import concurrent.futures
from lxml import html
import time
from queue import Queue

from .media import Media
from .page import Page
from . import settings
from ..utilities.file import File
from ..utilities import utils


class Website:
    def __init__(self, domain, filename):
        self.domain = domain
        self.save_link_filename = filename
        

    def find_website_links(self):
        # crawal all pages and store so that is will not be crawled again.
        # if link is of type media then set status to media
        # if time limit exceeds then retuen crawled data
        queued_links = set()
        file = File(self.save_link_filename)
        if not os.path.getsize(self.save_link_filename):
            file.write_content({self.domain: {settings.MEDIA: None, settings.SCRAPPED: False, settings.VISITED: False, settings.DOWNLOADED: False}})
            queued_links.add(self.domain)
            links = file.read_content()
        else:
            links = file.read_content()
            for link in links.keys():
                # add the links to queue to be scrapped
                # check if not scrapped and not a valid media url
                if utils.is_scrapable(link) and not file.visited(link) and not file.scrapped(link) and not file.downloded(link):
                    queued_links.add(link)

        time_start = time.time()
        while len(queued_links)>0: #not queued_links.empty():
            # if crawled more than CRAWL_TIME_MINUTE min
            if time.time() - time_start > settings.CRAWL_TIME_MINUTE*60:
                print(f"Finished crawling links in {settings.CRAWL_TIME_MINUTE} minutes.")
                break
            
            query_link = queued_links.pop()
            # if link is present in file and already scrapped
            if query_link in links.keys() and file.scrapped(query_link):
                continue
            response = requests.get(query_link, headers=settings.HEADERS)
            if response.status_code == 200:
                extracted_html = html.fromstring(response.content)
                anchor_urls = extracted_html.xpath(settings.ANCHOR_TYPE)
                for anchor_url in anchor_urls:
                    # if contain javascript code or it is link of other website.
                    
                    if "javascript:" in anchor_url or utils.get_hostname(self.domain) != utils.get_hostname(anchor_url):
                        continue
                    
                    if not anchor_url.startswith("http"):
                        anchor_url = os.path.join(self.domain, anchor_url.strip("/"))
                    anchor_url = utils.remove_forward_slash(anchor_url)
                    
                    # if this is media then don't add to Q, and not already scrapped earlier
                    if utils.is_scrapable(anchor_url) and not file.scrapped(anchor_url) and not file.downloded(anchor_url):
                        queued_links.add(anchor_url)
                        
                    media = utils.get_extension(anchor_url)
                    links[anchor_url] = dict()
                    links[anchor_url][settings.MEDIA] = media
                    links[anchor_url][settings.SCRAPPED] = file.scrapped(anchor_url)
                    links[anchor_url][settings.VISITED] = file.visited(anchor_url)
                    links[anchor_url][settings.DOWNLOADED] = file.downloded(anchor_url)
                    
                links[query_link][settings.SCRAPPED] = True
                file.write_content(links)
            else:
                print(f"Response {response.status_code} for {query_link} !")
            
            response.close()
            print(f"Waiting for 10 seconds.\nQ={len(queued_links)} links and links={len(links.keys())} links.")
            time.sleep(10)  # do not attack the system
                   
        return links

    def download_website_media(self):
        page_links = self.find_website_links()
        print(len(page_links))
        if len(page_links)>0:
            file = File(self.save_link_filename)
            with concurrent.futures.ThreadPoolExecutor(max_workers=settings.MAX_THREADS) as executor:
                # NOTE: ALLOWED_TYPE will always be visited=false
                for link, value in tqdm(page_links.items()):
                    if not utils.is_scrapable(link):
                        media = Media(link, self.save_link_filename)
                        executor.submit(media.media_download)
                    elif not file.visited(link):
                        page = Page(link, self.save_link_filename)
                        executor.submit(page.download_page_media)
        else:
            print(f"No links found in {self.domain}.")
