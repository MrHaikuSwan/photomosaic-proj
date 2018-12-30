### RUN THIS TO MAKE ALL USED DIRECTORIES FOR PROGRAM ###

import os

directories = [
        'ColorMaps',
        'DifferenceMaps',
        'ImageSets',
        'InputImages',
        'Photomosaics'
        ]

for d in directories:
    try:    
        os.mkdir(d)
    except:
        print "Failed to create directory " + d