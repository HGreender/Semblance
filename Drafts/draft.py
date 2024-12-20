import os
from datetime import datetime

from seiscore.binaryfile.binaryfile import BinaryFile


directory_in_str = ('/home/sigma-st-4/Рабочий стол/Semblance/Semblance/Drafts'
                    '/Data/semblance 1803 TDsh/bin/')
directory = os.fsencode(directory_in_str)
station_num = '2'
station_list = list()
for file in os.listdir(directory):
    filename = os.fsdecode(file)
    if filename.endswith(".00") or filename.endswith(".py"):
        file_name_str = os.path.join(filename)
        n = file_name_str.find('_')
        station_name = file_name_str[:n]
        if station_name == station_num:
            bfile = BinaryFile(directory_in_str + file_name_str)
            bfile.read_date_time_start = datetime(
                2022, 8, 14, 15, 24, 45
            )
            bfile.read_date_time_stop = datetime(
                2022, 8, 14, 15, 25, 0
            )
            signal = bfile.read_signal()
        continue
    else:
        continue
print(signal) # [11744 12591 12063 ...  -301  1536  2514]
print(len(signal)) # 15000
