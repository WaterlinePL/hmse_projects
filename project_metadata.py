from dataclasses import dataclass, field
from typing import List, Optional, Set, Dict, Union

# Is represented as .json file in store, accessed via dao
from hmse_simulations.hmse_projects.project_exceptions import UnknownShape, UnknownHydrusModel
from hmse_simulations.hmse_projects.typing_help import HydrusID, ModflowID, WeatherID, ShapeID, ProjectID


@dataclass
class ProjectMetadata:
    project_id: ProjectID

    finished: bool = False
    lat: Optional[float] = None  # latitude of model
    long: Optional[float] = None  # longitude of model
    start_date: Optional[str] = None  # start date of the simulation (YYYY-mm-dd)
    end_date: Optional[str] = None  # end date of the simulation (YYYY-mm-dd)
    spin_up: Optional[int] = None  # how many days of hydrus simulation should be ignored
    rows: Optional[int] = None  # amount of rows in the model grid
    cols: Optional[int] = None  # amount of columns in the model grid
    grid_unit: Optional[str] = None  # unit in which the model grid size is represented (feet/meters/centimeters)
    row_cells: List[float] = field(default_factory=list)  # heights of the model's consecutive rows
    col_cells: List[float] = field(default_factory=list)  # widths of the model's consecutive columns

    modflow_model: Optional[ModflowID] = None  # name of the folder containing the modflow model
    hydrus_models: Set[HydrusID] = field(default_factory=set)  # list of names of folders containing the hydrus models
    weather_files: Set[WeatherID] = field(default_factory=set)
    shapes: Set[ShapeID] = field(default_factory=set)

    shapes_to_hydrus: Dict[ShapeID, Union[HydrusID, float]] = field(default_factory=dict)
    hydrus_to_weather: Dict[HydrusID, WeatherID] = field(default_factory=dict)

    def set_modflow_model(self, modflow_id: ModflowID):
        self.modflow_model = modflow_id

    def remove_modflow_model(self):
        self.modflow_model = None

    def add_hydrus_model(self, hydrus_id: HydrusID):
        self.hydrus_models.add(hydrus_id)

    def remove_hydrus_model(self, hydrus_id: HydrusID):
        self.hydrus_models.remove(hydrus_id)

    def add_weather_file(self, weather_file_id: WeatherID):
        self.weather_files.add(weather_file_id)

    def remove_weather_file(self, weather_file_id: WeatherID):
        self.weather_files.remove(weather_file_id)

    def map_shape_to_hydrus(self, shape_id: ShapeID, hydrus_id: HydrusID):
        if not self.contains_shape(shape_id):
            raise UnknownShape(f"No shape {shape_id} in project {self.project_id}")
        if not self.contains_hydrus_model(hydrus_id):
            raise UnknownHydrusModel(f"No Hydrus model {hydrus_id} in project {self.project_id}")
        self.shapes_to_hydrus[shape_id] = hydrus_id

    def map_shape_to_manual_value(self, shape_id: ShapeID, value: float):
        if not self.contains_shape(shape_id):
            raise UnknownShape(f"No shape {shape_id} in project {self.project_id}")
        self.shapes_to_hydrus[shape_id] = value

    def map_hydrus_to_weather(self, hydrus_id: HydrusID, weather_id: WeatherID):
        if not self.contains_hydrus_model(hydrus_id):
            raise UnknownHydrusModel(f"No Hydrus model {hydrus_id} in project {self.project_id}")
        if not self.contains_weather_model(weather_id):
            raise UnknownShape(f"No weather file {weather_id} in project {self.project_id}")
        self.shapes_to_hydrus[hydrus_id] = weather_id

    def remove_shape_mapping(self, shape_id: ShapeID):
        if not self.contains_shape(shape_id):
            raise UnknownShape(f"No shape {shape_id} in project {self.project_id}")
        del self.shapes_to_hydrus[shape_id]

    def remove_hydrus_weather_mapping(self, hydrus_id: HydrusID):
        if not self.contains_hydrus_model(hydrus_id):
            raise UnknownHydrusModel(f"No Hydrus model {hydrus_id} in project {self.project_id}")
        del self.hydrus_to_weather[hydrus_id]

    def contains_hydrus_model(self, hydrus_id: HydrusID) -> bool:
        return hydrus_id in self.hydrus_models

    def contains_modflow_model(self, modflow_id: ModflowID) -> bool:
        return modflow_id == self.modflow_model

    def contains_weather_model(self, weather_id: WeatherID) -> bool:
        return weather_id in self.weather_files

    def contains_shape(self, shape_id: ShapeID) -> bool:
        return shape_id in self.shapes

    def to_json(self):
        return self.__dict__
