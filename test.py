from pathlib import Path
from ixn_montage import IXN_montage

root_folder = Path('/Volumes/SharedHITSX/cdb-Joglekar-Lab-GL/Ajit_Joglekar/20250121/mNG-BubR1/2025-01-23/20335/TimePoint_1/')

montage = IXN_montage(root_folder=root_folder)
montage.assemble_file_lists()
montage.make_montage('w1')
# montage.make_montage('w2')