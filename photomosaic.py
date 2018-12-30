from PIL import Image
import numpy as np
import json
import os
    

W, H = 0, 1
RED, GREEN, BLUE = 0, 1, 2
sqsize = 50 #maybe add formula to auto-calculate square size??
imgfp = 'InputImages/earth.png' #later modify to allow multiple images
imgname = imgfp.split('.')[0].split('/')[1]
rgbindexfp = 'ImageSets/%s_set/Indexes/rgb_index.json' % (imgname)

img = Image.open(imgfp)
img = img.convert('RGB')
newHeight = img.size[H]-(img.size[H] % sqsize)
newWidth = img.size[W]-(img.size[W] % sqsize)
img = img.crop((0, 0, newWidth, newHeight))
outimg = img.copy()

print 'Width: %spx\nHeight: %spx' % (img.size[W],img.size[H])

#implicit calculation of average pixels: Image.BOX averages in same manner, passed directly into array
#no significant performance difference
avgpixels = np.array(img.resize((img.size[W]/sqsize, img.size[H]/sqsize), resample = Image.BOX))
        
imgarr = np.zeros((avgpixels.shape[0], avgpixels.shape[1]), dtype='S14')
diffarr = np.zeros((avgpixels.shape[0], avgpixels.shape[1]))

with open(rgbindexfp, 'r') as f:
    rgbindex = json.load(f)

for x in range(len(avgpixels)):
    for y in range(len(avgpixels[x])):
        mindiff = 195076 #max difference possible + 1
        mindiffpic = ''
        pixrgb = [avgpixels[x,y,RED], avgpixels[x,y,GREEN], avgpixels[x,y,BLUE]]
        fps = os.listdir('ImageSets/%s_set' % imgname)
        fps = [i for i in fps if '.' in i]
        for fp in fps:
            picrgb = rgbindex[fp]
            diff = sum([(pixrgb[i]-picrgb[i])**2 for i in range(3)])
            if diff < mindiff:
                mindiff = diff
                mindiffpic = fp
        imgarr[x,y] = mindiffpic
        diffarr[x,y] = mindiff

for x in range(len(imgarr)):
    for y in range(len(imgarr[x])):
        smimg = Image.open('ImageSets/%s_set/' % (imgname) + imgarr[x,y]).resize((sqsize, sqsize))
        box = (y*sqsize, x*sqsize, y*sqsize + sqsize, x*sqsize + sqsize)
        outimg.paste(smimg, box)
        
diffarr = np.sqrt(diffarr)
diffarr *= 255.0/np.max(diffarr)
diffimg = Image.fromarray(diffarr.astype('uint8'), mode = 'L').resize((img.size[W], img.size[H]))

img.show()
outimg.show()
diffimg.show()

diffimg.save('DifferenceMaps/%s_diff.png' % (imgname))
outimg.save('Photomosaics/%s_photomosaic.png' % (imgname))
