import numpy as np


class MinimizeAngel:
    def __init__(self, vsp_model: np.ndarray,
                 coord_sensor: list[float],
                 coord_source: list[float]):
        self.__coord_source = coord_source
        self.__coord_sensor = coord_sensor
        self.__vsp_model = self.__correction_vsp_model(vsp_model=vsp_model.copy())

    @property
    def point_number(self):
        return int(self.__coord_sensor[0])

    @property
    def point_x(self):
        return self.__coord_sensor[1]

    @property
    def point_y(self):
        return self.__coord_sensor[2]

    @property
    def point_z(self):
        return self.__coord_sensor[3]

    @property
    def source_x(self):
        return self.__coord_source[0]

    @property
    def source_y(self):
        return self.__coord_source[1]

    @property
    def source_z(self):
        return self.__coord_source[2]

    @property
    def get_vsp_model(self):
        return self.__vsp_model

    @property
    def get_distance(self):
        return ((self.source_x - self.point_x)**2
                + (self.source_y - self.point_y)**2)**0.5


    def __correction_vsp_model(self, vsp_model):
        skip_row_top = skip_row_bot = 0
        flag_top = flag_bot = False

        for i in range(vsp_model.shape[0]):
            if not flag_bot and vsp_model[i, 0] <= self.source_z:
                skip_row_bot = i + 1
                flag_bot = True

            if not flag_top and vsp_model[i, 0] <= self.point_z:
                skip_row_top = 0 if i - 1 == -1 else i
                flag_top = True

            if flag_top and flag_bot:
                break

        skip_row_bot = skip_row_bot if skip_row_bot else vsp_model.shape[0]

        vsp_model = vsp_model[skip_row_top:skip_row_bot, :]
        vsp_model[-1, 0], vsp_model[0, 0] = self.source_z, self.point_z

        return vsp_model

    def __score_refraction_wave(self, angel):
        refraction_angel = np.radians(angel)
        l = [0]
        time = 0

        for i in range(self.get_vsp_model.shape[0] - 2):
            mileage_length = ((self.get_vsp_model[~i-1, 0]
                               - self.get_vsp_model[~i, 0])
                              * np.tan(refraction_angel) + l[-1])

            l.append(mileage_length)


            time += (((l[-2] - l[-1])**2
                      + (self.get_vsp_model[~i, 0]
                         - self.get_vsp_model[~i-1, 0])**2)**0.5
                     / self.get_vsp_model[~i-1, 1])

            refraction_angel = np.arcsin(np.sin(refraction_angel)
                                         * self.get_vsp_model[~i-2, 1]
                                         / self.get_vsp_model[~i-1, 1])

            if np.isnan(refraction_angel):
                return None, None

        mileage_length = ((self.get_vsp_model[0, 0]
                           - self.get_vsp_model[1, 0])
                          * np.tan(refraction_angel) + l[-1])
        l.append(mileage_length)

        time += (((l[-2] - l[-1]) ** 2
                  + (self.get_vsp_model[1, 0]
                     - self.get_vsp_model[0, 0]) ** 2) ** 0.5
                 / self.get_vsp_model[1 - 1, 1])


        return l[-1], time

    def get_refraction_wave(self, left_window: int = 0):

        distance = self.get_distance
        left_window, right_window = left_window, 90

        previous_mid = 0
        mid = round((left_window + right_window) / 2, 10)

        while True:

            refraction_l, time = self.__score_refraction_wave(mid)

            if refraction_l is None:
                previous_mid = right_window = mid
                mid = round((left_window + right_window) / 2, 10)
                continue

            if -0.1 <= refraction_l - distance <= 0.1:
                return mid, time

            elif refraction_l > distance:
                previous_mid = right_window = mid
                mid = round((left_window + right_window) / 2, 10)

            elif refraction_l < distance:
                previous_mid