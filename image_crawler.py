import requests
from lxml import html
from PIL import Image
import numpy as np
from io import BytesIO
import os
import json

def zero_pad(n, digits):
    zeros = digits - len(str(n))
    if zeros < 0:
        zeros = 0
    return '0'*zeros + str(n)

W, H = 0, 1
RED, GREEN, BLUE = 0, 1, 2
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
search_queries = ["nature", "flowers", "forest", "tree", "mountains"] #replace later with crawler that uses related searches to go through
c = 0
maxpics = 100

for search_query in search_queries:

    search_query = search_query.replace(' ', '+')
    url = "https://www.pexels.com/search/%s/" % (search_query)
    
    page = requests.get(url, headers = headers)
    doc = html.fromstring(page.content)
    imgurls = doc.xpath("//img[@class='photo-item__img']/@src")
    
    for imgurl in imgurls:
        r = requests.get(imgurl, headers = headers)
        try:
            img = Image.open(BytesIO(r.content))
            fp = "./ImageSet/image_%s.png" % (zero_pad(c, 4))
            img.save(fp, format = 'png')
            c += 1
        except IOError:
            print "IOError encountered on image %s" % (zero_pad(c, 4))
            continue
    
    if c >= maxpics:
        break

for fp in os.listdir('./ImageSet'):
    img = Image.open('./ImageSet/' + fp)
    if img.size[W] == img.size[H]:
        continue
    halfside = min(img.size)/2
    center = (img.size[W]/2, img.size[H]/2)
    box = (center[W]-halfside, center[H]-halfside, center[W]+halfside, center[H]+halfside)
    img = img.crop(box)
    img.save('./ImageSet/' + fp)

obj = {}
for fp in os.listdir('./ImageSet'):
    img = Image.open('./ImageSet/' + fp)
    pixels = np.array(img)
    r,g,b = 0,0,0
    for x in range(len(pixels)):
        for y in range(len(pixels[x])):
            r += pixels[x,y,RED]
            g += pixels[x,y,GREEN]
            b += pixels[x,y,BLUE]
    r /= img.size[W]*img.size[H]
    g /= img.size[W]*img.size[H]
    b /= img.size[W]*img.size[H]
    obj[fp] = (r, g, b)
with open('rgbindex.json', 'w') as f:
    json.dump(obj, f)

    
    