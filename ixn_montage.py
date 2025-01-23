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
        # self.__dict__.update((key, False) for key in self.suffixes)
        # self.__dict__.update((key, value) for key, value in file_dict.items() if key in self.suffixes)

    def find_wells_positions(self, ):
        '''
        Infers the number of wells, positions, and wavelengths used in the 
        colony imaging experiment. Stored as class object attributes.
        '''
        file_list = [f.name for f in os.scandir(self.root_dir) if 'thumb' not in f.name.casefold()]
        
        self.imwidth, self.imheight = tiff.imread(self.root_dir / Path(file_list[0])).shape
        
        pattern = re.compile(r'_(\w\d+)_(\w\d+)_(\w\d)')
        
        wells = []
        positions = []
        wavelengths = []

        for f in file_list:
            well, pos, wv = pattern.findall(f)[0]
            wells.append(well)
            positions.append(pos)
            wavelengths.append(wv)

        self.wells       = sorted(list(set(wells)))
        self.positions   = sorted(list(set(positions)), key = lambda x: int(x[1::]))
        self.wavelengths = sorted(list(set(wavelengths)))

        print(f'Found a total of {len(self.wells)} wells, {len(self.positions)} positions, \
              and {len(self.wavelengths)} wavelengths')

        return


    def make_montage(self, well: None, position: None, wavelength: None):
        '''
        Create a montage from the list of wells and wavelengths provided. 
        nrow and ncol indicate the number of rows and columns of images taken on IXN.
        Number of positions must equal nrows * ncols.
        Inputs:
        
        Outputs:
        None
        '''
        try:
            self.nrows * self.ncols == len(self.positions)
        except:
            raise ValueError(f'{self.nrows} x {self.ncols} ~= Number of positions')
        
        dummy = np.zeros((self.imwidth, self.imheight), dtype='int16')
        
        for well in self.wells:
            for wavelength in self.wavelengths:
                print(f"Now processing {wavelength} for {well}")

                
                montage = np.zeros((self.imwidth*self.nrows, 
                                    self.imheight*self.ncols), dtype='int16')
                
                for position in self.positions:
                    globstr = '*_'+ well + '_' + position + '_' +wavelength + '*'
                    file_path = [f for f in p.glob(globstr) if 'thumb' not in f.name.casefold()]
                    
                    counter = 0
                    for i in np.arange(self.nrows):
                        for j in np.arange(self.ncols):
                            xstart = i*self.imwidth
                            xend   = (i+1)*self.imwidth
                            ystart = j*self.imheight
                            yend   = (j+1)*self.imheight
                            if file_path:
                                montage[ystart:yend, xstart:xend]=tiff.imread(file_path[0])
                                print(f"{well}, {position}, {wavelength} file found")
                            else:
                                print(f"{well}, {position}, {wavelength} file NOT found")
                                montage[ystart:yend, xstart:xend]=dummy
                            
                            counter += 1

                tiff.imwrite(self.root_dir / Path(well+'_'+wavelength+'.tif'), montage)

        return