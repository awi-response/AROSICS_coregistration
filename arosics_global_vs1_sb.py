# -*- coding: utf-8 -*-
"""
Created on May 28 2021

Author: Sophia Barth, Ingmar Nitze

Description: Multiple automated Image Co-registration using 'arosics'
"""

##import Packages
from arosics import COREG, DESHIFTER
import glob
import os
import sys

### SETTINGS ###
# please add path to reference image
REFERENCE = r''
# Check if file exists
assert os.path.exists(REFERENCE), "Reference image not found!"

# please add directory path to input images, for deeper structure add e.g. '/*'
IMAGE_DIR = r'input_images'
# please add output directory
OUT_DIR = r'output_images'
# add suffix to shifted output file names, empty quote to leave original name
SUFFIX = ''




# #### Load image list
flist = glob.glob(IMAGE_DIR + '/*SR*.tif')
assert len(flist) > 0, "No input images found!"

# ### Run Processing
for infile in flist[:]:
    # create outfile name for main image
    outfile = os.path.join(OUT_DIR, os.path.basename(infile)[:-4] + f'{SUFFIX}.tif')
    logfile = os.path.join(OUT_DIR, os.path.basename(infile)[:-4] + f'.log')
    # read aux files from main image basename
    base = os.path.basename(infile).split('_3B')[0]
    aux_list = glob.glob(os.path.join(IMAGE_DIR, f'{base}*udm*tif'))
    
    # start logfile
    sys.stdout = open(logfile, 'w')
    
    # detect and correct global spatial shift 
    try:
        CR = COREG(REFERENCE, infile, wp=(None,None), ws=(600,600),
                   max_shift=20, path_out=outfile, 
                   fmt_out='GTIFF',
                   out_crea_options=['COMPRESS=DEFLATE'],
                   r_b4match=4, 
                   s_b4match=4)
        output = CR.calculate_spatial_shifts()
        
        if CR.ssim_improved:
            CR.correct_shifts()
            
            # apply shift to auxilliary files
            for infile_aux in aux_list:
                outfile_aux = os.path.join(OUT_DIR, os.path.basename(infile_aux)[:-4] + f'{SUFFIX}.tif')
                _ = DESHIFTER(infile_aux, CR.coreg_info, 
                              path_out=outfile_aux, 
                              fmt_out='GTIFF',
                              out_crea_options=['COMPRESS=DEFLATE']).correct_shifts()

        else:
            print('\nImage kept in original position!')
    
    
        sys.stdout.close()
    except:
        print('Error')
        sys.stdout.close()
        continue