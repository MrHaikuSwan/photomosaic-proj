from colorsys import rgb_to_hls
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from math import sqrt
import json

#TODO: rename file
#TODO: look at turning this into a module instead of a class
#TODO: figure out gamma correction to get relative luminance for colormap y-axis

#TODO: [POTENTIALLY] Look up where the divisions between colors are to a human,
#                    divide up the colormap into boxes for each of these divisions,
#                    then use densities of each box to determine what colors you
#                    need the most of, then possibly use aggregated search terms
#                    that correspond to said boxes to scrape the best data
#                    THIS SHOULD NOT BE PURSUED UNTIL PIC-MATCHING ALGORITHM IS BETTER

class ImageAnalyzer(object):
    
    def __init__(self, imgdir):
        self.imgdir = imgdir
        self.coordlist = []
        self.colorlist = []
        self.last_loaded_name = ''
        self.last_loaded_type = ''
        
        if self.imgdir.endswith('/'):
            self.imgdir = self.imgdir[:-1]
    
    def plot_colormap(self, subject_name = None, pt_size = 10):
        
        if self.last_loaded_type == 'image':
            save_folder = 'Images'
        elif self.last_loaded_type == 'rgbindex':
            save_folder = 'ImageSets'
        elif self.last_loaded_type == 'query':
            save_folder = 'Queries'
        else:
            save_folder = ''
        
        if 0 in (len(self.coordlist), len(self.colorlist)):
            print "Data is unable to be plotted"
            return
        if subject_name is None:
            subject_name = self.last_loaded_name
        coordlist = self.coordlist[:]
        colorlist = self.colorlist[:]
        coordlist = self.unzip(coordlist)
        plt.scatter(coordlist[0], coordlist[1], c = colorlist, s = pt_size)
        plt.xlabel('Hue')
        plt.ylabel('Lightness')
        plt.savefig('Colormaps/%s/%s_colormap.png' % (save_folder, subject_name))
        plt.show()
    
    def unzip(self, zipped): #look for better way to do this
        lists = []
        for i in range(len(zipped[0])):
            orig = [x[i] for x in zipped]
            lists.append(orig)
        return lists
    
    def load_rgbindex(self, fp):
        self.coordlist = []
        self.colorlist = []
        self.last_loaded_name = fp.split('/')[-1].split('.')[0]
        self.last_loaded_type = 'rgbindex'
        with open(fp, 'r') as f:
            rgbindex = json.load(f)
        for key in rgbindex:
            rgbtup = tuple([x/255.0 for x in rgbindex[key]])
            pttup = rgb_to_hls(rgbtup[0], rgbtup[1], rgbtup[2])[:2]
            self.colorlist.append(rgbtup)
            self.coordlist.append(pttup)
    
    def load_image(self, name, sq_size = None):
        self.coordlist = []
        self.colorlist = []
        fp = self.imgdir + '/' + name
        self.last_loaded_name = name
        self.last_loaded_type = 'image'
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
                
    def load_query_map(self, query):
        self.coordlist = []
        self.colorlist = []
        queryfp = self.imgdir + '/Indexes/query_index.json'
        rgbfp = self.imgdir + '/Indexes/rgb_index.json'
        
        with open(queryfp, 'r') as f:
            queryindex = json.load(f)
            
        try:
            rgbimgs = queryindex[query]
            self.last_loaded_name = query
            self.last_loaded_type = 'query'
        except IndexError:
            print "query unavailable"
            return
        
        with open(rgbfp, 'r') as f:
            rgbindex = json.load(f)
        for img in rgbimgs:
            rgbtup = tuple([x/255.0 for x in rgbindex[img]])
            pttup = rgb_to_hls(rgbtup[0], rgbtup[1], rgbtup[2])[:2]
            self.colorlist.append(rgbtup)
            self.coordlist.append(pttup)
            
    def switchimgdir(self, imgdir):
        self.imgdir = imgdir
        if self.imgdir.endswith('/'):
            self.imgdir = self.imgdir[:-1]