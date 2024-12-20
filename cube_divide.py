import json

import numpy as np
from datetime import datetime

from containers import SearchArea, Range, Coordinate3D
from functions import (
    semblance_value,
    get_directory_bin_files_names,
    get_signal_by_name_from_directory
)
from MimizeAngel import MinimizeAngel

port = Coordinate3D(9638773.51, 5848147.68, -867.13)
offset = 150

# Создание области поиска
search_area = SearchArea(
    x_range=Range(min_=port.x - offset, max_=port.x + offset),
    y_range=Range(min_=port.y - offset, max_=port.y + offset),
    altitude_range=Range(min_=port.altitude - offset, max_=port.altitude + offset)
)

# Разбиение области поиска на массив координат угла кубиков
cubes = search_area.cubes_coordinate_to_list()
cubes = [[9638713.53, 5848147.6,-867.13]]
# Загрузка Сигналов
bin_directory_path = 'Drafts/Data/semblance 1803 TDsh/bin/'

# Загрузка списка станций, для которых есть сигнал
bin_files_names_list = get_directory_bin_files_names(bin_directory_path)
bin_files_names_list.sort()

# Загрузка станций
## Station: PatchNumber, xGK9, yGK9, AltitudeReal
stations = np.loadtxt(
    'Drafts/Data/semblance 1803 TDsh/stations.txt',
    delimiter='\t',
    skiprows=1,
    dtype=np.float32
# )
).tolist()
stations = [[int(row[0]), *row[1:]] for row in stations]

# Удаляем станции, на которых нет сигнала и добавляем сигнал туда, где он есть
start_day_time = datetime(2022, 8, 14, 15, 25, 4)
stop_day_time = datetime(2022, 8, 14, 15, 25, 7)
for station in stations[:]:
    if station[0] not in bin_files_names_list:
        stations.remove(station)
    else:
        station_name = station[0]
        signal = get_signal_by_name_from_directory(
            directory_path=bin_directory_path,
            station_num=station_name,
            start=start_day_time,
            stop=stop_day_time
        ).tolist()
        station.append(signal)

# Каждой станции присваиваем свой сигнал
station_signals_dict = dict()

# Загрузка сейсмической vsp-модели
## VSP: h_vert, h_abs, V
vsp_model = np.loadtxt(
    'Drafts/Data/semblance 1803 TDsh/vsp.txt',
    delimiter='\t',
    skiprows=1,
    usecols=(1, 2),
    dtype=np.float32
)
#
# cubes = cubes[0:10]

# Рассчёт задержек
events_count = 0
cube_delays = dict()
print('Delays in %:', end=' ')
for cube in cubes:
    station_delays = dict()
    for station in stations:
        min_angel = MinimizeAngel(
            vsp_model=vsp_model,
            coord_sensor=station,
            coord_source=cube
        )
        angel, delay = min_angel.get_refraction_wave(left_window=0)
        if delay is None:
            print("Хуйня!!!")
        station_delays[station[0]] = delay
    cube_delays[f'Cube_{events_count}'] = station_delays
    events_count += 1
    if events_count % 10 == 0:
        print(f'{int(events_count / 10)}', end='.') #/{len(cubes)}')

# Поиск станции с минимальным значением (базовой станции) в каждом кубике
# А также вычитание минимальной задержки из задержек всех станций
min_station_dict = dict()
semblance = dict()
for cube_number, stations_delays in cube_delays.items():
    min_station_dict[cube_number] = min(stations_delays.values())
    for station_ in stations_delays.keys():
        stations_delays[station_] =  int(
            round(
                (stations_delays[station_] - min_station_dict[cube_number]) * 1000, 0
            )
        )

print()

# Вычисление сЕмБаЛаНсА
print('Cubes in %:')
semblance_window = 40
semblance_values = list()
for start_discrete in range(350, 2000, 40):
    for cube_index in range(len(cubes)):
        cube_x, cube_y, cube_z = cubes[cube_index]
        cube_station_delays = cube_delays[f'Cube_{cube_index}']
        cube_semblance_signals = list()
        for station in stations:
            start_cube_station_discrete = (start_discrete +
                                           cube_station_delays[station[0]])
            stop_cube_station_discrete = (start_cube_station_discrete
                                          + semblance_window)
            cube_semblance_signals.append(
                station[4][start_cube_station_discrete:stop_cube_station_discrete]
            )
        cube_semblance_value = semblance_value(cube_semblance_signals)
        semblance_values.append((start_discrete, cube_x, cube_y, cube_z, cube_semblance_value))
        # print(f'{cube_index / 10}', end='.') #/{len(cubes) / 10}')
    print(f'Time {start_discrete}/{len(stations[0][4])}')

with open('/home/sigma-st-4/Рабочий стол/Semblance/Semblance/sembalance_full.txt', 'w') as f:
    for line in semblance_values:
        f.write(f"{line[0]}\t{line[1]}\t{line[2]}\t{line[3]}\t{line[4]}\n")



print(cube_delays)
print()


# with open('Drafts/Data/Saved_cube_delays.json', 'w', encoding='utf-8') as file:
#     json.dump(cube_delays, file, ensure_ascii=False, indent=4)