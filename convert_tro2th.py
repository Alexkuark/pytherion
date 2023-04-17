#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pytro2th import tro2th
from pytrox2th import trox2th
import subprocess
import sys
from os import listdir
from os.path import isfile, isdir

# find the first .tro file and process it
#tro_file = [f for f in listdir() if (isfile(f) and f[-4:] == '.tro')]
#print('\n\t\tProcessing : '+tro_file[0]+'\n')
#tro2th (fle_tro_fnme = tro_file[0])

# find the first .thconfig file and run therion
#thconfig_file = [f for f in listdir() if (isfile(f) and f[-9:] == '.thconfig')]
#print('\n\t\tProcessing : '+thconfig_file[0]+'\n')
#subprocess.run(['therion', thconfig_file[0]])

if (len(sys.argv) > 1 and isfile(sys.argv[1])):

    if f[-4:] == '.tro':
        print('\n\t\tProcessing : '+sys.argv[1]+'\n')
        th, thconf = tro2th (fle_tro_fnme = sys.argv[1])
                
        #print('\n\t\tProcessing : '+thconf+'\n')
        #subprocess.run(['therion', thconf])

    elif f[-5:] == '.trox':
        print('\n\t\tProcessing : '+sys.argv[1]+'\n')
        th, thconf = trox2th (fle_trox_fnme = sys.argv[1])
                
        #print('\n\t\tProcessing : '+thconf+'\n')
        #subprocess.run(['therion', thconf])

else:

    for f in listdir():
        if isfile(f):
            if f[-4:] == '.tro':
                print('\n\t\tProcessing : '+f+'\n')
                th, thconf = tro2th (fle_tro_fnme = f)
                
                #print('\n\t\tProcessing : '+thconf+'\n')
                #subprocess.run(['therion', thconf])

            elif f[-5:] == '.trox':
                print('\n\t\tProcessing : '+f+'\n')
                th, thconf = trox2th (fle_trox_fnme = f)
                
                #print('\n\t\tProcessing : '+thconf+'\n')
                #subprocess.run(['therion', thconf])
