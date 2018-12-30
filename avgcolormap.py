from colorsys import rgb_to_hls
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from math import sqrt
import json

#TODO: rename file
#TODO: look at turning this into a module instead of a class

#TODO: [POTENTIALLY] Look up where the divisions between colors are to a human,
#                    divide up the colormap into boxes for each of these divisions,
#                    then use densities of each box to determine what colors you
#                    need the most of, then possibly use aggregated search terms
#                    that correspond to said boxes to scrape the best data
#                    THIS SHOULD NOT BE PURSUED UNTIL PIC-MATCHING ALGORITHM IS BETTER

class ImageAnalyzer(object):
    
    def __init__(self):
        self.coordlist = []
        self.colorlist = []
        self.last_loaded_name = ''
    
    def plot_colormap(self, subject_name = None, pt_size = 5):
        if subject_name is None:
            subject_name = self.last_loaded_name
        self.coordlist = self.unzip(self.coordlist)
        plt.scatter(self.coordlist[0], self.coordlist[1], c = self.colorlist, s = pt_size)
        plt.xlabel('Hue')
        plt.ylabel('Lightness')
        plt.savefig('Colormaps/%s_colormap.png' % (subject_name))
        plt.show()
    
    def unzip(self, zipped):
        lists = []
        for i in range(len(zipped[0])):
            orig = [x[i] for x in zipped]
            lists.append(orig)
        return lists
    
    def load_rgbindex(self, fp = 'rgbindex.json'):
        self.__init__()
        self.last_loaded_name = fp.split('.')[0]
        with open(fp, 'r') as f:
            rgbindex = json.load(f)
        for key in rgbindex:
            rgbtup = tuple([x/255.0 for x in rgbindex[key]])
            pttup = rgb_to_hls(rgbtup[0], rgbtup[1], rgbtup[2])[:2]
            self.colorlist.append(rgbtup)
            self.coordlist.append(pttup)
    
    def load_image(self, fp, sq_size = None):
        self.__init__()
        self.last_loaded_name = fp.split('.')[0]
        img = Image.open(fp)
        img = img.convert('RGB')
        if sq_size is None or sq_size <= 1:
            sq_size = int(sqrt(img.size[0]*img.size[1]) / 45) # calculate sq_size for higher end of ~2000 points of data
        img = img.resize((img.size[0]/sq_size,img.size[1]/sq_size), Image.BOX)
        pixels = np.array(img)
        for x in range(len(pixels)):
            for y in range(len(pixels[x])):
                rgbtup = tuple([i/255.0 for i in pixels[x,y]])
                pttup = rgb_to_hls(rgbtup[0], rgbtup[1], rgbtup[2])[:2]
                self.colorlist.append(rgbtup)
                self.coordlist.append(pttup)
                
                
                
mapper = ImageAnalyzer()
mapper.load_image('InputImages/earth.png')
mapper.plot_colormap()