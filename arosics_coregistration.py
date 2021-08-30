# -*- coding: utf-8 -*-
"""
Created on May 28 2021
Updated on August 25 2021

Author: Sophia Barth, Ingmar Nitze

Description: Multiple automated Image Co-registration using 'arosics'
"""

# import Packages
import argparse
from arosics import COREG, DESHIFTER
import glob
import os
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-r', '--reference', type=str, default=r'reference_image/ref.tif',
        help='please add path to reference image')
parser.add_argument('-i', '--input', type=str, default=r'input_images',
        help='please add directory path to input images, for deeper structure add e.g. "/*"')
parser.add_argument('-o', '--output', type=str, default=r'output_images',
        help='output directory')
parser.add_argument('-it', '--input_type', type=str, default=r'MACS',
        help=' options: "None", "Planet Scene", "MACS"')
parser.add_argument('-b_ref', default=3, type=int,
        help='image band used for calculation on reference image')
parser.add_argument('-b_tgt', default=3, type=int,
        help='image band used for calculation on target images')
parser.add_argument('-s', '--suffix', type=str, default='',
        help='add suffix to shifted output file names, empty quote to leave original name')
args = parser.parse_args()

### SETTINGS ###
# please add path to reference image
REFERENCE = args.reference#r'reference_image/ref.tif'
# image band used for calculation on reference image
REF_Band = args.b_ref#3
# please add directory path to input images, for deeper structure add e.g. '/*'
IMAGE_DIR = args.input#r'input_images'#+'/*'
# image band used for calculation on target image
TGT_Band = args.b_tgt#3
# please add output directory
OUT_DIR = args.output#'output_images'
# add suffix to shifted output file names, empty quote to leave original name
MODE = args.input_type#'MACS' # options: None, 'Planet Scene', 'MACS'
SUFFIX = args.suffix#''

# set manually if no mode selected
AUX_FILES = True
REGEX_INFILE = '*SR*.tif'
REGEX_AUXFILES = '*udm*tif'
REGEX_SPLIT = '_3B'

modes = {
    'Planet Scene': {
        'regex_infile': '*SR*.tif',
        'split': '_3B',
        'regex_auxfiles': '*udm*tif'},
    'MACS':{
        'regex_infile': '*rgb*.tif',
        'split': '_transparent',
        'regex_auxfiles': '*dsm*tif'}
}
if MODE:
    AUX_FILES = True
    REGEX_INFILE = modes[MODE]['regex_infile']
    REGEX_AUXFILES = modes[MODE]['regex_auxfiles']
    REGEX_SPLIT = modes[MODE]['split']

# Check if files structure is hierarchical (using stupid workaround)
len_path = len([p for p in os.path.split(IMAGE_DIR) if p != ''])
hierarchy = len_path > 1

# Check if reference file exists
assert os.path.exists(REFERENCE), "Reference image not found!"
#TODO print error and scan for other images

# #### Load image list
flist = glob.glob(IMAGE_DIR + f'/{REGEX_INFILE}')
assert len(flist) > 0, "No input images found!"

# ### Run Processing
for infile in flist[:]:
    if hierarchy:
        out_dir = os.path.join(OUT_DIR, os.path.split(os.path.dirname(infile))[-1])
        os.makedirs(out_dir, exist_ok=True)
    else:
        out_dir = OUT_DIR
    # create outfile name for main image
    outfile = os.path.join(out_dir, os.path.basename(infile)[:-4] + f'{SUFFIX}_out.tif')
    outfile_final = os.path.join(out_dir, os.path.basename(infile)[:-4] + f'{SUFFIX}.tif')
    logfile = os.path.join(out_dir, os.path.basename(infile)[:-4] + f'.log')
    # compression setup
    translate = f'gdal_translate -co COMPRESS=DEFLATE {outfile} {outfile_final}'

    if AUX_FILES:
        # read aux files from main image basename
        base = os.path.basename(infile).split(f'{REGEX_SPLIT}')[0]
        aux_list = glob.glob(os.path.join(os.path.dirname(infile), f'{base}{REGEX_AUXFILES}'))

    # start logfile
    sys.stdout = open(logfile, 'w')
    
    # detect and correct global spatial shift 
    #try:
    CR = COREG(REFERENCE, infile, wp=(None,None), ws=(600,600),
               max_shift=200, path_out=outfile,
               fmt_out='GTIFF',
               out_crea_options=['COMPRESS=DEFLATE'],
               r_b4match=REF_Band,
               s_b4match=TGT_Band)
    output = CR.calculate_spatial_shifts()

    if CR.ssim_improved:
        CR.correct_shifts()
        # apply compression (broken in arosics 1.5.1)?
        os.system(translate)
        os.remove(outfile)

        # apply shift to auxilliary files
        for infile_aux in aux_list:
            outfile_aux = os.path.join(out_dir, os.path.basename(infile_aux)[:-4] + f'{SUFFIX}_out.tif')
            outfile_aux_final = os.path.join(out_dir, os.path.basename(infile_aux)[:-4] + f'{SUFFIX}.tif')
            _ = DESHIFTER(infile_aux, CR.coreg_info,
                          path_out=outfile_aux,
                          fmt_out='GTIFF',
                          out_crea_options=['COMPRESS=DEFLATE']).correct_shifts()
            # apply compression to aux files
            translate_aux = f'gdal_translate -co COMPRESS=DEFLATE {outfile_aux} {outfile_aux_final}'
            os.system(translate_aux)
            os.remove(outfile_aux)

    else:
        print('\nImage kept in original position!')

    sys.stdout.close()