from PIL import Image
import numpy as np
import json
import os

W, H = 0, 1
RED, GREEN, BLUE = 0, 1, 2
sqsize = 50

img = Image.open('earth.png')
newHeight = img.size[H]-(img.size[H] % sqsize)
newWidth = img.size[W]-(img.size[W] % sqsize)
img = img.crop((0, 0, newWidth, newHeight))
outimg = img.copy()

print 'Width: %spx\nHeight: %spx' % (img.size[W],img.size[H])

avgpixels = np.zeros((img.size[H]/sqsize, img.size[W]/sqsize, 3), dtype='uint8')

for x in range(0, img.size[W], sqsize):
    for y in range(0, img.size[H], sqsize):
        box = (x,y,x+sqsize,y+sqsize)
        subparr = np.array(img.crop(box))
        
#        r, g, b = 0, 0, 0
#        for i in range(len(subparr)):
#            for j in range(len(subparr[i])):
#                r += subparr[i,j,RED]
#                g += subparr[i,j,GREEN]
#                b += subparr[i,j,BLUE]
#        r /= sqsize*sqsize
#        g /= sqsize*sqsize
#        b /= sqsize*sqsize
        
        avgpix = np.array(subparr.resize((1,1), resample = Image.BOX))
        r, g, b = subparr[0,0,RED], subparr[0,0,GREEN], subparr[0,0,BLUE]

        avgpixels[y/sqsize,x/sqsize,RED] = r
        avgpixels[y/sqsize,x/sqsize,GREEN] = g
        avgpixels[y/sqsize,x/sqsize,BLUE] = b

        
imgarr = np.zeros((avgpixels.shape[0], avgpixels.shape[1]), dtype='S14')

with open('rgbindex.json', 'r') as f:
    rgbindex = json.load(f)

for x in range(len(avgpixels)):
    for y in range(len(avgpixels[x])):
        mindiff = 195076 #max difference possible + 1
        mindiffpic = ''
        pixrgb = [avgpixels[x,y,RED], avgpixels[x,y,GREEN], avgpixels[x,y,BLUE]]
        for fp in os.listdir('./ImageSet'):
            picrgb = rgbindex[fp]
            diff = sum([(pixrgb[i]-picrgb[i])**2 for i in range(3)])
            if diff < mindiff:
                mindiff = diff
                mindiffpic = fp
            imgarr[x,y] = mindiffpic

for x in range(len(imgarr)):
    for y in range(len(imgarr[x])):
        smimg = Image.open('./ImageSet/' + imgarr[x,y]).resize((sqsize, sqsize))
        box = (y*sqsize, x*sqsize, y*sqsize + sqsize, x*sqsize + sqsize)
        outimg.paste(smimg, box)

img.show()
outimg.show()
outimg.save('earth-photomosaic.png')
        
            
    