import requests
from lxml import html
from PIL import Image
import numpy as np
from io import BytesIO
import os
import json
from Queue import Queue
#import threading (could feasibly implement with queues)

class ImageCrawler(object):
    
    def __init__(self, imgdir = 'ImageSet/'):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
        self.counter = 0
        self.last_crawl_counter = 0
        self.zero_padding = 4
        self.imgdir = imgdir
        
        self.q = Queue()
        self.done_urls = []
        
        
    def crawlWebsite(self, start_query, maxpics):
        W, H = 0, 1
        
        start_url = "/search/%s/" % (start_query)
        self.q.put(start_url)
        
        self.update_counter()
        self.last_crawl_counter = self.counter
        
        while self.counter < maxpics:
            
            url = self.q.get(timeout = 10)
            self.done_urls.append(url)
            
            page = requests.get('https://www.pexels.com' + url, headers = self.headers)
            doc = html.fromstring(page.content)
            relatedurls = doc.xpath("//a[contains(@class,'js-related-search-item')]/@href")
            imgurls = doc.xpath("//img[@class='photo-item__img']/@src")
        
            for i in imgurls:
                r = requests.get(i, headers = self.headers)
                try:
                    img = Image.open(BytesIO(r.content))
                    # square cropping code
                    halfside = min(img.size)/2
                    center = (img.size[W]/2, img.size[H]/2)
                    box = (center[W]-halfside, center[H]-halfside, center[W]+halfside, center[H]+halfside)
                    img = img.crop(box)
                    #end of square crop
                    fp = "ImageSet/image_%s.png" % (self.zero_pad(self.counter))
                    img.save(fp)
                    self.counter += 1
                except IOError:
                    print "IOError encountered on image %s" % (self.zero_pad(self.counter))
                    continue
                except Exception as e:
                    print "Something else happened on image %s:\n    %s" % (self.zeropad(self.counter), e)
                    continue
            
            for i in relatedurls:
                if i not in self.done_urls:
                    self.q.put(i)
    
    def json_index(self, mode = 'a'):
        RED, GREEN, BLUE = 0, 1, 2
        
        obj = {}
        imgs_to_index = sorted(os.listdir(self.imgdir))[self.last_crawl_counter:]
        
        for fp in imgs_to_index:
            img = Image.open(self.imgdir + fp)
            avgpix = np.array(img.resize((1,1), resample = Image.BOX))
            r, g, b = int(avgpix[0,0,RED]), int(avgpix[0,0,GREEN]), int(avgpix[0,0,BLUE])
            obj[fp] = (r, g, b)
        
        if mode == 'a':
            with open('rgbindex.json', 'r') as f:
                jsonobj = json.load(f)
                jsonobj.update(obj)
            with open('rgbindex.json', 'w') as f:
                json.dump(jsonobj, f)
        elif mode == 'w':
            with open('rgbindex.json', 'w') as f:
                json.dump(obj, f)
        else:
            print "Invalid mode"
        

    def update_counter(self):
        last_fp = sorted(os.listdir(self.imgdir)[-1])
        self.counter = int(last_fp[-1][6:-4]) + 1
        
    def zero_pad(self, n):
        zeros = self.zero_padding - len(str(n))
        if zeros < 0:
            zeros = 0
        return '0'*zeros + str(n)
