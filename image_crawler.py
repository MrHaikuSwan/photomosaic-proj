import requests
from lxml import html
from PIL import Image
import numpy as np
from io import BytesIO
import os
import json
from Queue import Queue
#import threading (could feasibly implement with queues)

#TODO: scrape images for earth.png
#TODO: record what query got what images TRY NEBULA OR OTHER ASTRONOMICAL PHENOMENA
#TODO: colormap new rgbindex after scraping, associate with starting term
#TODO: use perceptual image hashing to get duplicated images
#TODO: save restoration copies of indexes in case you accidentally lose them

#TODO: potentially use Google Images API (if that exists?)
#TODO: potentially just turn this into a module to be imported rather than an entire class

#
#
#
#INDEX AND DUPLICATE METHODS ARE BOTH BROKEN
#
#
#

class ImageCrawler(object):
    
    def __init__(self, img_name):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
        self.counter = 0
        self.last_crawl_counter = 0
        self.img_query_index = {}
        self.img_name = img_name
        
        self.q = Queue()
        self.done_urls = []
        
        
    def crawlWebsite(self, start_query, maxpics, name = None):
        W, H = 0, 1
        
        if name is None:
            name = self.img_name
        else:
            self.img_name = name
        
        dirname = "ImageSets/%s_set" % (name)
        try:
            os.mkdir(dirname)
        except WindowsError:
            pass #is this bad?
        try:
            os.mkdir(dirname + '/Indexes')
        except WindowsError:
            pass #is this bad?
        
        start_query = start_query.replace(' ', '%20')
        start_url = "/search/%s/" % (start_query)
        self.q.put(start_url)
        
        self.update_counter()
        self.last_crawl_counter = self.counter
        
        while self.counter < maxpics:
            
            url = self.q.get(timeout = 10)
            self.done_urls.append(url)
            img_names = []
            
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
                    fp = "%s/image_%04d.png" % (dirname, self.counter)
                    img.save(fp)
                    img_names.append('image_%04d.png' % (self.counter))
                    self.counter += 1
                except IOError:
                    print "IOError encountered on image %04d" % (self.counter)
                    continue
                except Exception as e:
                    print "Something else happened on image %04d:\n    %s" % (self.counter, e)
                    continue
            
            for i in relatedurls:
                if i not in self.done_urls:
                    self.q.put(i)
                    
            query = url.split('/')[2]
            self.img_query_index[query] = img_names
    
    def rgb_index(self):
        RED, GREEN, BLUE = 0, 1, 2
        obj = {}
        
        indexdir = 'ImageSets/%s_set' % (self.img_name)
        imgs_to_index = sorted(os.listdir(indexdir))
        imgs_to_index = [i for i in imgs_to_index if '.' in i][self.last_crawl_counter:]
        
        for fp in imgs_to_index:
            img = Image.open(indexdir + '/' + fp)
            img = img.convert('RGB')
            avgpix = np.array(img.resize((1,1), resample = Image.BOX)).flatten()
            r, g, b = int(avgpix[RED]), int(avgpix[GREEN]), int(avgpix[BLUE])
            obj[fp] = (r, g, b)
        
        path = 'ImageSets/%s_set/Indexes' % (self.img_name)
        if 'rgb_index.json' not in os.listdir(path):    
            with open(path + '/rgb_index.json', 'w') as f:
                f.write('{}')
        with open(path + '/rgb_index.json', 'r') as f:
            jsonobj = json.load(f)
            jsonobj.update(obj)
        with open(path + '/rgb_index.json', 'w') as f:
            json.dump(jsonobj, f)
        
    def query_index(self):
        path = 'ImageSets/%s_set/Indexes/query_index.json' % (self.img_name)
        if 'query_index.json' not in os.listdir(path):
            with open(path + '/query_index.json', 'w') as f:
                f.write('{}')
        with open(path, 'r') as f:
            jsonobj = json.load(f)
            jsonobj.update(self.img_query_index)
        with open(path, 'w') as f:
            json.dump(jsonobj, f)
    
    def del_duplicates(self):
        imgdir = 'ImageSets/%s_set' % (self.img_name)
        images = [i for i in os.listdir(imgdir) if '.' in i]
        duphashes = {}
        for fname in images:
            img = Image.open(imgdir + '/' + fname).resize((8,8), resample = Image.LANCZOS).convert('L')
            mean = img.resize((1,1), Image.BOX).getpixel((0,0))
            imghash = sum((1 if p > mean else 0) << i for i, p in enumerate(img.getdata()))  #this is so smart
            # credit to answer on https://www.quora.com/How-can-I-write-a-Python-script-that-finds-duplicate-images-in-a-folder
            if imghash in duphashes:
                duphashes[imghash].append(fname)
            else:
                duphashes[imghash] = [fname]
        
        with open(imgdir + '/Indexes/query_index.json', 'r') as qf:
            with open(imgdir + '/Indexes/rgb_index.json', 'r') as cf:
                queryindex = json.load(qf)
                rgbindex = json.load(cf)
        
        for imghash in duphashes:
            while len(duphashes[imghash]) > 1:
                fname = duphashes[imghash][-1]
                duphashes[imghash].remove(fname)
                try:
                    os.remove(imgdir + '/' + fname)
                except Exception:
                    pass
                if rgbindex.get(fname) is not None:    
                    rgbindex.pop(fname)
                if queryindex.get(fname) is not None:    
                    queryindex.pop(fname)
        
        with open(imgdir + '/Indexes/query_index.json', 'w') as qf:
            with open(imgdir + '/Indexes/rgb_index.json', 'w') as cf:
                json.dump(queryindex, qf)
                json.dump(rgbindex, cf)
            
    def index_backup(self):
        indexdir = 'ImageSets/%s_set/Indexes' % (self.img_name)
        try:
            os.mkdir(indexdir + '/Backups')
        except WindowsError:
            pass #is this bad?
        with open(indexdir + '/query_index.json') as f:    
            queryindex = json.load(f)
        with open(indexdir + '/rgb_index.json') as f:
            rgbindex = json.load(f)
        with open(indexdir + '/Backups/query_index_copy.json', 'w') as f:
            json.dump(queryindex, f)
        with open(indexdir + '/Backups/rgb_index_copy.json', 'w') as f:
            json.dump(rgbindex, f)
        
    
    def update_counter(self):
        imgdir = "ImageSets/%s_set" % (self.img_name)
        images = [i for i in os.listdir(imgdir) if '.' in i]
        if not images:
            self.counter = 0
            return
        images.sort()
        last_fp = images[-1]
        n = last_fp.split('.')[0].split('_')[1]
        self.counter = int(n) + 1
