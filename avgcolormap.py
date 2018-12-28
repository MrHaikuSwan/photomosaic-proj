import json
from colorsys import rgb_to_hls
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

def unzip(zipped):
    lists = []
    for i in range(len(zipped[0])):
        orig = [x[i] for x in zipped]
        lists.append(orig)
    return lists



#with open('rgbindex.json') as f:
#    rgbindex = json.load(f)

coordlist = []
colorlist = []


#for key in rgbindex:
#    rgbtup = tuple([x/255.0 for x in rgbindex[key]])
#    pttup = rgb_to_hls(rgbtup[0], rgbtup[1], rgbtup[2])[:2]
##    pttup = (rgb_to_hls(r/255.0, g/255.0, b/255.0)[0], (r+g+b)/765.0)
#    colorlist.append(rgbtup)
#    coordlist.append(pttup)

img = Image.open('earth.png')
img = img.resize((img.size[0]/50,img.size[1]/50), Image.BOX)
pixels = np.array(img)
for x in range(len(pixels)):
    for y in range(len(pixels[x])):
        rgbtup = tuple([i/255.0 for i in pixels[x,y]])
        pttup = rgb_to_hls(rgbtup[0], rgbtup[1], rgbtup[2])[:2]
        colorlist.append(rgbtup)
        coordlist.append(pttup)

def plot_colormap(coordlist, colorlist, subject_name):
    coordlist = unzip(coordlist)
    plt.scatter(coordlist[0], coordlist[1], c = colorlist, s = 5)
    plt.xlabel('Hue')
    plt.ylabel('Brightness')
    plt.savefig('./Colormaps/%s_colormap.png' % (subject_name))
    plt.show()

plot_colormap(coordlist, colorlist, 'earth')