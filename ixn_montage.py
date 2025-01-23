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
        self.nrows = 9
        self.ncols = 9
        self.imwidth = 2048
        self.imheight = 2048
        
        self.pattern = re.compile(r'_(\w\d+)_(\w\d+)_(\w\d)')
        rows = ['A','B','C','D','E','F','G','H']
        cols = [str(i).zfill(2) for i in np.arange(1,13).tolist()]
        self.all_wells = []
        for row in rows:
            for col in cols:
                self.all_wells.append(row+col)

        self.all_files = []
        self.master_dict = {}
        self.file_list = []
        # self.__dict__.update((key, False) for key in self.suffixes)
        # self.__dict__.update((key, value) for key, value in file_dict.items() if key in self.suffixes)

    def assemble_file_lists(self, ):
        '''
        Infers the number of wells, positions, and wavelengths used in the 
        colony imaging experiment. Stored as class object attributes.
        '''
        self.all_files = [f for f in self.root_dir.glob('*') if 'thumb' not in f.name.casefold()]
        

        for well in self.all_wells:
            well_pattern = '_'+well+'_'
            current_list = [f for f in self.all_files if well_pattern in f.name]
            self.master_dict[well] = current_list

        return


    def make_montage(self, wavelength: str, well = None):
        '''
        Create a montage from the list of wells and wavelengths provided. 
        nrow and ncol indicate the number of rows and columns of images taken on IXN.
        Number of positions must equal nrows * ncols.
        Inputs:
        
        Outputs:
        None
        '''
        if not well:
            wells = self.master_dict.keys()
            
        for well in wells:
            print(f"Now processing {wavelength} for {well}")
            
            montage = np.zeros((self.imwidth*self.nrows, 
                                self.imheight*self.ncols), dtype='int16')
            
            wavelength_pattern = '_' + wavelength
            
            self.file_list = [f for f in self.master_dict[well] if wavelength_pattern in f.name]
            self.file_list = list(set(self.file_list))
            self.file_list = sorted(self.file_list, key=lambda x: int(self.pattern.findall(x.name)[0][1].split('s')[-1]))

            for file in self.file_list:

                numerical_position = self.pattern.findall(file.name)[0][1].split('s')[-1]

                i = (int(numerical_position) - 1) % self.ncols
                j = (int(numerical_position) - 1) // self.nrows
                xstart = i*self.imwidth
                xend   = (i+1)*self.imwidth
                ystart = j*self.imheight
                yend   = (j+1)*self.imheight

                montage[ystart:yend, xstart:xend]=tiff.imread(file)

            # tiff.imwrite(well+'_'+wavelength+'.tif', self.montage)
            tiff.imwrite(self.root_dir / Path(well+'_'+wavelength+'.tif'), montage)

        return