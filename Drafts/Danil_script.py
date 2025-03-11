from typing import List

import numpy as np
import json

from MimizeAngel import MinimizeAngel


class DelayRecord:
    def __init__(self, station_number: int, delay: float):
        self.station_number = int(station_number)
        self.delay = delay

    def to_dict(self):
        return {
            "StationNumber": self.station_number,
            "Delay": self.delay
        }


class DelaysContainer:
    def __init__(self, event_time: float):
        self.event_time = event_time
        self.delays: List[DelayRecord] = []

    def add_delay(self, delay_record: DelayRecord):
        self.delays.append(delay_record)

    def to_dict(self):
        return {
            "EventTime": self.event_time,
            "Delays": [delay.to_dict() for delay in self.delays]
        }



vsp_model_folder = r'D:\Coding apps\ramilTeorTimes\VSP 1012 обобщенная (правильная СРР).txt'
coords = r'E:\Для Данила\координаты 526 (65 тфн).txt'
events = r'E:\Для Данила\ExportData\7_main-62.dat'
exportpath = r'E:\Для Данила\ExportData\7_main-62_times.txt'

vsp_model = np.loadtxt(fname=vsp_model_folder, skiprows=1, dtype=float, delimiter='\t')
coords = np.loadtxt(fname=coords, skiprows=1, dtype=float, delimiter='\t')
events = np.loadtxt(fname=events, skiprows=1, dtype=float, delimiter='\t', usecols=[0, 1, 2, 3])

containers = []
eventscount = 0
for time, eventx, eventy, eventz in events:
    delays = []
    container = DelaysContainer(event_time=time)
    for name, x, y, z in coords:
        min_angel = MinimizeAngel(vsp_model=vsp_model, coord_sensor=[name, x, y, z], coord_source=[eventx, eventy, eventz])
        angel, delay = min_angel.get_refraction_wave(left_window=0)
        if delay is None:
            print("хуйня!!!")
        record = DelayRecord(name, delay)
        container.add_delay(record)
    containers.append(container)
    eventscount += 1
    print(str(eventscount) + ' ' + str(len(events)))

res = json.dumps([container.to_dict() for container in containers], indent=4)
file = open(exportpath, "w")
file.write(res)
file.close()
