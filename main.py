from MediaCrawler.utilities.file import File
from MediaCrawler.utilities import utils
from MediaCrawler.crawler.website import Website
from MediaCrawler.utilities import utils

if __name__ =="__main__":
    domain =  "https://xyz.com/"
    filename = utils.content_filename(domain)
    
    only_show = False
    
    if only_show:
        file = File(filename)
        # file.update(settings.VISITED, False)
        file.get_visited()
    else:
        webdownloader = Website(domain, filename)
        webdownloader.download_website_media()
        
    
    
    # p = Page("https://xyx.com/abc", filename)
    # p.download_page_media()
    
    # p = Media("https://xyx.com/abc.mp3", filename)
    # p.media_download()