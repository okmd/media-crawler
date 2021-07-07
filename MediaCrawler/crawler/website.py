import os
from tqdm import tqdm
import concurrent.futures
from lxml import html
import time
import logging

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
        logging.info("Crawler finding links..")
        # crawal all pages and store so that is will not be crawled again.
        # if link is of type media then set status to media
        # if time limit exceeds then retuen crawled data
        queued_links = set()
        file = File(self.save_link_filename)
        content_links = file.read_content()
        for content_key, content_value in content_links.items():
            if utils.is_scrapable(content_key) and not file.scrapped(content_key) and not file.downloded(content_key):
                queued_links.add(content_key)
        
        # add to queue if not in content links
        if not content_links.get(self.domain, None) and not file.scrapped(self.domain):
            queued_links.add(self.domain)

        time_start = time.time()
        while len(queued_links): #not queued_links.empty():
            if utils.time_limit_exceeds(time_start):
                logging.info(f"Finished crawling links in {settings.CRAWL_TIME_MINUTE} minutes.")
                # file.write_content(content_links)
                break
            
            current_link = queued_links.pop()
            # current link present or not or scrapped or not.
            if file.scrapped(current_link):
                continue
            
            response = utils.get_response(current_link)
            utils.sleep()  # do not attack the system
            if response:
                extracted_html = html.fromstring(response.content)
                anchor_urls = extracted_html.xpath(settings.ANCHOR_TYPE)
                for anchor_url in anchor_urls:
                    anchor_url = utils.remove_forward_slash(anchor_url)
                    if content_links.get(anchor_url, None):
                        continue
                    # if contain javascript code or it is link of other website.
                    # what if media is hosted on other webite?
                    if "javascript:" in anchor_url:
                        continue
                    
                    if not anchor_url.startswith("http"):
                        anchor_url = os.path.join(utils.get_hostname(self.domain), anchor_url)
                    
                    # if this is media then don't add to Q, and not already scrapped earlier
                    if utils.is_scrapable(anchor_url) and not file.scrapped(anchor_url) and not file.downloded(anchor_url) and utils.get_hostname(self.domain) == utils.get_hostname(anchor_url):
                        queued_links.add(anchor_url)
                        
                    content_links[anchor_url] = dict()
                    content_links[anchor_url][settings.MEDIA] = utils.get_extension(anchor_url)
                    content_links[anchor_url][settings.SCRAPPED] = file.scrapped(anchor_url)
                    content_links[anchor_url][settings.VISITED] = file.visited(anchor_url)
                    content_links[anchor_url][settings.DOWNLOADED] = file.downloded(anchor_url)
                    file.write_content(content_links)
                    
                if content_links.get(current_link, None):
                    content_links[current_link][settings.SCRAPPED] = True
                else:
                    content_links[current_link] = {self.domain: {
                        settings.MEDIA: utils.get_extension(current_link), settings.SCRAPPED: file.scrapped(anchor_url),
                        settings.VISITED: file.visited(anchor_url), settings.DOWNLOADED: file.downloded(anchor_url)}}
                file.write_content(content_links)
                
                logging.info(f"Q={len(queued_links)} links and links={len(content_links.keys())} links.")
                   
        return content_links

    def download_website_media(self):
        page_links = self.find_website_links()
        logging.error("Crawler started finding media..")
        if len(page_links):
            file = File(self.save_link_filename)
            with concurrent.futures.ThreadPoolExecutor(max_workers=settings.MAX_THREADS) as executor:
                # NOTE: ALLOWED_TYPE will always be visited=false
                for link, value in tqdm(page_links.items(), position=0, leave=True, ncols=100, desc="Website "):
                    if not utils.is_scrapable(link):
                        media = Media(link, self.save_link_filename)
                        executor.submit(media.media_download)
                    elif not file.visited(link) and utils.get_hostname(self.domain) == utils.get_hostname(link):
                        page = Page(link, self.save_link_filename)
                        executor.submit(page.download_page_media)
        else:
            logging.info(f"No links found in {self.domain}.")