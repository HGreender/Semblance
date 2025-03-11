import json

import numpy as np
from datetime import datetime

from msgpack import unpack

from containers import SearchArea, Range, Coordinate3D
from functions import (
    semblance_value,
    get_directory_bin_files_names,
    get_signal_by_name_from_directory,
    is_file
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
cubes = cubes[0:15]

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
start_day_time = datetime(
    2022, 8, 14, 15, 25, 4
)
stop_day_time = datetime(
    2022, 8, 14, 15, 25, 6
)
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

import_delays_path = ('/home/sigma-st-4/Рабочий стол/Semblance/Semblance/'
                      'saved_delays.json')
if is_file(import_delays_path):
    with open(import_delays_path) as json_file:
        data = json.load(json_file)
else:
    # Рассчёт задержек
    data = False
    events_count = 0
    cube_delays = dict()
    cubes_coordinates = dict()
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
        cubes_coordinates[f'Cube_{events_count}'] = cube
        events_count += 1
        if events_count % 10 == 0:
            print(f'{int(events_count / 10)}', end='.') #/{len(cubes)}')

    # Поиск станции с минимальным значением (базовой станции) в каждом кубике
    # А также вычитание минимальной задержки из задержек всех станций
    min_station_dict = dict()
    for cube_number, stations_delays in cube_delays.items():
        min_station_dict[cube_number] = min(stations_delays.values())
        for station_ in stations_delays.keys():
            stations_delays[station_] =  int(
                round(
                    (stations_delays[station_] - min_station_dict[cube_number]) \
                    * 1000,
                    0
                )
            )

    # Сохранение задержек
    json_prepare = list()
    for cube, delays in cube_delays.items():
        # json_prepare.append([cube, int(cube[cube.find('_') + 1:]), cubes_coordinates[cube], delays])
        json_prepare.append([cube, delays])
    path_to_save_delays = '/home/sigma-st-4/Рабочий стол/Semblance/Semblance/saved_delays'
    with open(path_to_save_delays+'.json', 'w', encoding='utf-8') as json_file:
        json.dump(json_prepare, json_file, ensure_ascii=False, indent=4)
    # with open(path_to_save_delays+'.txt', 'w') as f:
    #     for cube, delays in cube_delays.items():
    #         f.write(f"{cube}\t{int(cube[cube.find('_') + 1:])}\t{cubes_coordinates[cube]}\t{delays}\n")

# Вычисление сЕмБаЛаНсА
if data:
    cube_delays = dict()
    for cube in range(len(data)):
        cube_delays[cube[0]] = cube[1]
print('\nSemblance calculating:')
min_semblance_value = len(stations) * 0.01
semblance_window = 40
semblance_values = list()
for start_discrete in range(0, 1000, semblance_window):
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
        if cube_semblance_value > min_semblance_value:
            semblance_values.append((start_discrete, cube_x, cube_y, cube_z, cube_semblance_value))
        # print(f'{cube_index / 10}', end='.') #/{len(cubes) / 10}')
    print(f'Time {start_discrete}/{len(stations[0][4])}')

with open('/home/sigma-st-4/Рабочий стол/Semblance/Semblance/sembalance_full.txt', 'w') as f:
    for line in semblance_values:
        f.write(f"{line[0]}\t{line[1]}\t{line[2]}\t{line[3]}\t{line[4]}\n")

