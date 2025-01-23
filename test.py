from pathlib import Path
from ixn_montage import IXN_montage

root_folder = Path('/Volumes/SharedHITSX/cdb-Joglekar-Lab-GL/Ajit_Joglekar/20250121/U2OS-mNG-Bub1-CRISPR/2025-01-21/20334/TimePoint_1/')

montage = IXN_montage(root_folder=root_folder)
montage.assemble_file_lists()
montage.make_montage('w1')
# montage.make_montage('w2')