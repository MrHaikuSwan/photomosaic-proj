import requests
from lxml import html
from PIL import Image
import numpy as np
from io import BytesIO
import os
import json
from Queue import Queue
#import threading (could feasibly implement with queues)

def zero_pad(n, digits):
    zeros = digits - len(str(n))
    if zeros < 0:
        zeros = 0
    return '0'*zeros + str(n)

W, H = 0, 1
RED, GREEN, BLUE = 0, 1, 2
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
c = 0
maxpics = 1600

start_url = "/search/%s/" % ("flowers")
q = Queue()
q.put(start_url)
done_urls = []


while c < maxpics:
        
    url = q.get(timeout = 10)
    
    page = requests.get('https://www.pexels.com' + url, headers = headers)
    doc = html.fromstring(page.content)
    relatedurls = doc.xpath("//a[contains(@class,'js-related-search-item')]/@href")
    imgurls = doc.xpath("//img[@class='photo-item__img']/@src")

    for i in imgurls:
        r = requests.get(i, headers = headers)
        try:
            img = Image.open(BytesIO(r.content))
            # square cropping code
            halfside = min(img.size)/2
            center = (img.size[W]/2, img.size[H]/2)
            box = (center[W]-halfside, center[H]-halfside, center[W]+halfside, center[H]+halfside)
            img = img.crop(box)
            #end of square crop
            fp = "./ImageSet/image_%s.png" % (zero_pad(c, 4))
            img.save(fp, format = 'png')
            c += 1
        except IOError:
            print "IOError encountered on image %s" % (zero_pad(c, 4))
            continue
    
    for i in relatedurls:
        if i not in done_urls:
            q.put(i)
    
    done_urls.append(url)

obj = {}

#for fp in os.listdir('./ImageSet'):
#    img = Image.open('./ImageSet/' + fp)
#    pixels = np.array(img)
#    r,g,b = 0,0,0
#    for x in range(len(pixels)):
#        for y in range(len(pixels[x])):
#            r += pixels[x,y,RED]
#            g += pixels[x,y,GREEN]
#            b += pixels[x,y,BLUE]
#    r /= img.size[W]*img.size[H]
#    g /= img.size[W]*img.size[H]
#    b /= img.size[W]*img.size[H]
#    obj[fp] = (r, g, b)
    
for fp in os.listdir('./ImageSet'):
    img = Image.open('./ImageSet/' + fp)
    avgpix = np.array(img.resize((1,1), resample = Image.BOX))
    r, g, b = avgpix[0,0,RED], avgpix[0,0,GREEN], avgpix[0,0,BLUE]
    obj[fp] = (r, g, b)
    
with open('rgbindex2.json', 'w') as f:
    json.dump(obj, f)

    
    