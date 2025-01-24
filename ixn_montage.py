import re
from pathlib import Path, PurePath
import tifffile as tiff
import numpy as np



class IXN_montage:
    
    def __init__(self, root_folder: Path):
        '''
        Object initializes with default parameter values and definitions of 
        root and inference folders. It also reads in tif files with either 
        intensity or background in their names as the corresponding, channel-
        specific correction maps.
        '''
        try:
            isinstance(root_folder, PurePath)
            self.root_dir = root_folder
        except:
            raise TypeError(f"{root_folder} not a valid Path")
        
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


    def make_montage(self, wavelength: str, well_list = None, save_path = None):
        '''
        Create a montage from the list of wells and wavelengths provided. 
        nrow and ncol indicate the number of rows and columns of images taken on IXN.
        Number of positions must equal nrows * ncols.
        Inputs:
        wavelength: Specify as 'w1', 'w2', etc/
        Outputs:
        None
        '''

        if not well_list:
            well_list = self.master_dict.keys()
            
        for well in well_list:
            print(f"Now processing {wavelength} for {well}")
            
            montage = np.zeros((self.imwidth*self.nrows, 
                                self.imheight*self.ncols), dtype='int16')
            
            wavelength_pattern = '_' + wavelength
            
            file_list = [f for f in self.master_dict[well] if wavelength_pattern in f.name]

            if file_list:
                file_list = list(set(file_list))
                # The complicated RE is required to break up the filename and extract well, position and wavelength
                # designations. The key sorts the filenames by the digits in the positoin designation.
                file_list = sorted(file_list, 
                                        key=lambda x: int(self.pattern.findall(x.name)[0][1].split('s')[-1]))

                for file in file_list:

                    numerical_position = self.pattern.findall(file.name)[0][1].split('s')[-1]

                    i = (int(numerical_position) - 1) % self.ncols
                    j = (int(numerical_position) - 1) // self.nrows
                    xstart = i*self.imwidth
                    xend   = (i+1)*self.imwidth
                    ystart = j*self.imheight
                    yend   = (j+1)*self.imheight

                    montage[ystart:yend, xstart:xend]=tiff.imread(file)

                # tiff.imwrite(well+'_'+wavelength+'.tif', self.montage)
                if not save_path:
                    tiff.imwrite(self.root_dir / Path(well+'_'+wavelength+'.tif'), montage)
                else:
                    if isinstance(save_path, PurePath):
                        tiff.imwrite(save_path / Path(well+'_'+wavelength+'.tif'), montage)
                    else:
                        print("Save path not a valid Path object")
            else:
                print(f"No files found for {wavelength} and/or {well}")

        return