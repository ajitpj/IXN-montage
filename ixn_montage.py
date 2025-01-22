import re
import os
from pathlib import Path
import tifffile as tiff
import numpy as np
import napari


p = Path('/Users/ajitj/Desktop/Timepoint_1')

class IXN_montage:
    def __init__(self, root_folder: Path):
        '''
        Object initializes with default parameter values and definitions of 
        root and inference folders. It also reads in tif files with either 
        intensity or background in their names as the corresponding, channel-
        specific correction maps.
        '''
        self.root_dir = root_folder
        self.wells = []
        self.positions = []
        self.wavelengths = []
        # self.__dict__.update((key, False) for key in self.suffixes)
        # self.__dict__.update((key, value) for key, value in file_dict.items() if key in self.suffixes)

    def find_wells_positions(self, ):
        '''
        Infers the number of wells, positions, and wavelengths used in the 
        colony imaging experiment. Stored as class object attributes.
        '''
        file_list = [f.name for f in os.scandir(self.root_dir) if 'thumb' not in f.name.casefold()]
        pattern = re.compile(r'_(\w\d+)_(\w\d+)_(\w\d)')

        wells = []
        positions = []
        wavelengths = []

        for f in file_list:
            well, pos, wv = pattern.findall(f)[0]
            wells.append(well)
            positions.append(pos)
            wavelengths.append(wv)

        self.wells = list(set(wells))
        self.positions   = sorted(list(set(positions)), key = lambda x: int(x[1::]))
        self.wavelengths = sorted(list(set(wavelengths)))

        print(f'Found a total of {len(self.wells)} wells, {len(self.positions)} positions, \
              and {len(self.wavelengths)} wavelengths')

        return


    def make_montage(wells: list, positions: list, wavelengths: list, nrow: int, ncol: int):
        '''
        Create a montage from the list of wells and wavelengths provided. 
        nrow and ncol indicate the number of rows and columns of images taken on IXN.
        Number of positions must equal nrows * ncols.
        Inputs:
        wells     : A list of wells acquired
        positions : A list of positions acquired
        wavelenths: A list of wavelengths acquired
        nrow      : number of rows 
        ncol      : number of columns
        Outputs:
        None
        '''
        try:
            nrow * ncol = len(positions)
        except:
            raise ValueError(f'{nrow} x {ncol} ~= Number of positions')
        
        all_files = [f.name for f in os.scandir(p) if 'thumb' not in f.name.casefold()]
        im_width, im_height = tiff.imread(all_files[0])
        montage = np.zeros((im_width*nrow, im_height*ncol), dtype='int16')

        for well in wells:
            for wavelength in wavelengths:
                globstr = '*_'+well+'_s*'+wavelength+'*'
                file_list = [f for f in p.glob(globstr) if 'thumb' not in f.name.casefold()]
                file_list = sorted(file_list, key=lambda x: int(x.name.split('_')[2][1::]))
                counter = 0
                for i in np.arange(9):
                    for j in np.arange(9):
                        xstart = i*im_width
                        xend   = (i+1)*im_width
                        ystart = j*im_height
                        yend   = (j+1)*im_height
                        montage[ystart:yend, xstart:xend]=tiff.imread(file_list[counter])
                        counter += 1

        return