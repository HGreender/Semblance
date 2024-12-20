from typing import Union, List
from dataclasses import dataclass


@dataclass
class Coordinate3D:
    x: float
    y: float
    altitude: float

    def __eq__(self, other: 'Coordinate3D') -> bool:
        return self.x == other.x and self.y == other.y and (
            self.altitude == other.altitude
        )

    def __ne__(self, other: 'Coordinate3D') -> bool:
        return self.x != other.x or self.y != other.y or (
            self.altitude != other.altitude
        )

    def to_list(self) -> List[float]:
        return [self.x, self.y, self.altitude]

@dataclass
class Range:
    min_: Union[int, float]
    max_: Union[int, float]

    def __eq__(self, other: 'Range') -> bool:
        return self.min_ == other.min_ and self.max_ == other.max_

    def __ne__(self, other: 'Range') -> bool:
        return self.min_ != other.min_ or self.max_ != other.max_

    @property
    def size(self) -> Union[int, float]:
        return self.max_ - self.min_

    @property
    def middle(self) -> float:
        return (self.max_ - self.min_) / 2

    def is_value_belong(self, value: Union[int, float]) -> bool:
        return self.min_ <= value < self.max_

    def to_list(self) -> List[Union[int, float]]:
        return [self.min_, self.max_]

    def __post_init__(self):
        if self.max_ < self.min_:
            raise ValueError('The min value is greater than the max')

@dataclass
class SearchArea:
    x_range: Range
    y_range: Range
    altitude_range: Range
    nx = 10
    ny = 10
    nz = 10

    @property
    def cubes_count_per_axis(self):
        return [self.nx, self.ny, self.nz]

    @cubes_count_per_axis.setter
    def cubes_count_per_axis(self, values):
        if len(values) != 3:
            raise ValueError(
                "Expected a list or tuple with 3 elements (nx, ny, nz)")
        self.nx, self.ny, self.nz = values

    def is_point_belong(self, point: Coordinate3D) -> bool:
        is_x_belong = self.x_range.is_value_belong(value=point.x)
        is_y_belong = self.y_range.is_value_belong(value=point.y)
        is_z_belong = self.altitude_range.is_value_belong(value=point.altitude)
        return is_x_belong and is_y_belong and is_z_belong

    @property
    def center(self) -> Coordinate3D:
        return Coordinate3D(
            x=self.x_range.middle,
            y=self.y_range.middle,
            altitude=self.altitude_range.middle
        )

    @property
    def dx(self):
        return self.x_range.size / self.nx

    @property
    def dy(self):
        return self.y_range.size / self.ny

    @property
    def dz(self):
        return self.altitude_range.size / self.nz

    @property
    def spacing(self):
        return [self.dx, self.dy, self.dz]

    @property
    def cube_array(self):
        start_point = Coordinate3D(
            x= self.x_range.min_,
            y= self.y_range.min_,
            altitude=self.altitude_range.min_
        )
        cubes = list()
        for x_index in range(self.nx):
            for y_index in range(self.ny):
                for z_index in range(self.nz):
                    point = Coordinate3D(
                        x=x_index * self.dx + start_point.x,
                        y = y_index * self.dy + start_point.y,
                        altitude = z_index * self.dz + start_point.altitude
                    )
                    cubes.append(point)
        return cubes

    def cubes_coordinate_to_list(self):
        list_cube_coordinates = [cube.to_list() for cube in self.cube_array]
        return list_cube_coordinates
