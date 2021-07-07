from MediaCrawler.crawler import settings
from MediaCrawler.utilities.file import File
from MediaCrawler.utilities import utils
from MediaCrawler.crawler.media import Media
from MediaCrawler.crawler.website import Website
from MediaCrawler.crawler.page import Page
from urllib.parse import urlparse
from MediaCrawler.utilities import utils
import logging

if __name__ =="__main__":
    domain =  "https://axy.com/"
    filename = utils.content_filename(domain)
    logging.basicConfig(filename=f'{utils.content_filename(domain, "log")}', format='%(levelname)s:%(message)s', level=logging.DEBUG)
    file = File(filename)
    
    only_show = True
    
    if only_show:
        
        # file.read_content()
        # file.update(settings.VISITED, False)
        file.get_media("mp3")
        file.get_downloaded()
        # file.update("visited", False)
        
    else:
        webdownloader = Website(domain, filename)
        webdownloader.download_website_media()
        
    print("Total:",file.get_size())
        
    
    
    # # 
    # p = Page("https://axy.com/hasb/", filename)
    # p.download_page_media()
    
    # p = Media("https://axy.com/ab.mp3", filename)
    # p.media_download()
    
    # NOTE: Threading is causing data curruption.