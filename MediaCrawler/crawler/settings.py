import os

# Make false when crawling
DEBUG = False

ROOT_LOCATION = os.path.join(os.getcwd(), "media")
# Maximum threads to use
# NOTE: Not sure working or not
MAX_THREADS = 2
# time to sleep between two requests in seconds
SLEEP_TIME = 2
# Minutes to only get links from the main websites
CRAWL_TIME_MINUTE = 1 # -1 for no limit

# add all type of file extensions you think is a valid file but not a web page in website you are scraping.
ALL_RESOURCE_TYPE = ['jpg', 'jpeg', 'mp3', 'mp4', 'wma', 'png', '3gp']
# all types of file you are willing to download
ALLOWED_TYPE = ['mp3', 'mp4', 'wma']
# types of link to scrape from website
MEDIA_TYPE = {'audio':"//audio/@src",
               'video':"//video/@src",
            #    'img':"//img/@src",
               "media":"//source/@src"}

# used to find the links of other page in page.
ANCHOR_TYPE = "//a/@href"


# CONSTANTS
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',}
DOWNLOADED = "downloaded"
SCRAPPED = "scrapped"
VISITED = "visited"
MEDIA = "media"
        