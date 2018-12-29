from PIL import Image
import numpy as np
import json
import os
import time

BEG = time.time()

W, H = 0, 1
RED, GREEN, BLUE = 0, 1, 2
sqsize = 50

img = Image.open('earth.png')
newHeight = img.size[H]-(img.size[H] % sqsize)
newWidth = img.size[W]-(img.size[W] % sqsize)
img = img.crop((0, 0, newWidth, newHeight))
outimg = img.copy()

print 'Width: %spx\nHeight: %spx' % (img.size[W],img.size[H])

#implicit calculation of average pixels: Image.BOX averages in same manner, passed directly into array
#no significant performance difference
avgpixels = np.array(img.resize((img.size[W]/sqsize, img.size[H]/sqsize), resample = Image.BOX))
        
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
outimg.save('photomosaic.png')
        
END = time.time()
print END-BEG       
    