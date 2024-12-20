import os
from datetime import datetime

from seiscore.binaryfile.binaryfile import BinaryFile


def semblance_value(signals: list):
    numerator = 0
    denominator = 0
    for row in range(len(signals[0])):
        sum_of_values = 0
        for column in range(len(signals)):
            sum_of_values += signals[column][row]
            denominator += signals[column][row] ** 2
        numerator = sum_of_values ** 2

    return numerator / denominator

def get_directory_bin_files_names(directory_path):
    directory = os.fsencode(directory_path)
    station_list = list()
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".00") or filename.endswith(".xx") \
                or filename.endswith(".bin"):
            file_name_str = os.path.join(filename)
            n = file_name_str.find('_')
            station_name = file_name_str[:n]
            station_list.append(int(station_name))
            continue
        else:
            continue
    return station_list

# Функция добавления сигнала в список по номеру из директории и первому эл-ту списка
def get_signal_by_name_from_directory(
        directory_path: str,
        station_num: int,
        start: datetime,
        stop: datetime
):
    station_num = str(station_num)
    directory = os.fsencode(directory_path)
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".00") or filename.endswith(".xx") \
                or filename.endswith(".bin"):
            file_name_str = os.path.join(filename)
            n = file_name_str.find('_')
            station_name = file_name_str[:n]
            if station_name == station_num:
                bfile = BinaryFile(directory_path + file_name_str)
                bfile.read_date_time_start = start
                bfile.read_date_time_stop = stop
                signal = bfile.read_signal()
                return signal
            continue
        else:
            continue
