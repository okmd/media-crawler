import pickle
import os
import pathlib
from ..crawler import settings
from threading import Lock

class File2:
    def __init__(self, name):
        self.save_link_filename = name
        
    def load_links(self):
        with open(self.save_link_filename, 'rb') as f:
            links = pickle.load(f)
            return links
    
    def save_links(self, links):
        with open(self.save_link_filename, 'wb+') as f:
            pickle.dump(links, f)
            
    def saved_links(self, show=("downloaded",True)):
        links = self.load_links()
        if show:
            custom_count = 0
            for link, value in links.items():
                if value[show[0]]==show[1]:
                    custom_count += 1
                    print(f"{link}:{value}.")
            print(f"Total count of {show[0]} = {show[1]} is {custom_count}.")
        else:
            for link, value in links.items():
                    print(f"{link}:{value}.")

class File:
    '''Structure: {link1:{porb1:val1, prop2:val2}, Link2:{..}..}'''
    
    def __init__(self, name):
        self._lock = Lock()
        self.save_link_filename = name
        self.read_content()
        self.get_size()
        
    def get_size(self):
        self.records = len(self.content.keys())
        return self.records
        
    def read_content(self):
        # create a file only if not exist.
        pathlib.Path(self.save_link_filename).touch(exist_ok=True)
        # reading empty file
        with self._lock:
            if not os.path.getsize(self.save_link_filename):
                self.content = {}
            else:
                with open(self.save_link_filename, 'rb') as f:
                    self.content = pickle.load(f)
            return self.content
    
    def write_content(self, content):
        with self._lock:
            with open(self.save_link_filename, 'wb+') as f:
                pickle.dump(content, f)
                self.content = content
                          
    def __get_content(self, key, value):
        query_content_count = 0
        query_content = {}
        for content_key, content_value in self.content.items():
            if self.content[content_key].get(key, None) == value:
                query_content_count += 1
                query_content[content_key] = self.content[content_key]
                print(f"{content_value}:{content_key}.")
        print(f"Total count where {key} = {value} is {query_content_count}.")
        return query_content
            
    def get_visited(self, value=True):
        return self.__get_content(settings.VISITED, value)
    
    def get_scrapped(self,value=True):
        return self.__get_content(settings.SCRAPPED, value)
    
    def get_downloaded(self, value=True):
        return self.__get_content(settings.DOWNLOADED, value)
    
    def get_media(self, media_type):
        return self.__get_content(settings.MEDIA, media_type)
      
    def __is_true(self, url, key, value):
        key_exists = self.content.get(url, None)
        if  key_exists and key_exists.get(key, None) == value:
            return True
        return False
                             
    def scrapped(self, url):
        return self.__is_true(url, settings.SCRAPPED, True)
    
    def visited(self, url):
        return self.__is_true(url, settings.VISITED, True)
    
    def downloded(self, url):
        return self.__is_true(url, settings.DOWNLOADED, True)
    
    def extension(self, url, ext):
        return self.__is_true(url, settings.MEDIA, ext)
    
    # update
    def update(self, key, value):
        # This will update all links key value.
        links = self.content
        for content_key, _ in links.items():
            links[content_key][key] = value
        self.write_content(links)
        
        print(f"Updated successfully {key}={value}.")
        
        
if __name__ == "__main__":
    file = File("file.txt")
    dic = {"A":{settings.DOWNLOADED:True, "C":4, "D":3}, "X":{settings.SCRAPPED:5}}
    file.write_content(dic)
    file.get_downloaded()
    file.get_scrapped()
    print(file.get_size())
             
              