from dataclasses import dataclass, field
from typing import List, Optional, Set, Dict, Union

# Is represented as .json file in store, accessed via dao
from flask import jsonify

from hmse_simulations.hmse_projects.hmse_hydrological_models.modflow.modflow_metadata import ModflowMetadata
from hmse_simulations.hmse_projects.project_exceptions import UnknownShape, UnknownHydrusModel
from hmse_simulations.hmse_projects.typing_help import HydrusID, ModflowID, WeatherID, ShapeID, ProjectID, ShapeColor


@dataclass
class ProjectMetadata:
    project_id: ProjectID
    project_name: str

    finished: bool = False
    lat: Optional[float] = None  # latitude of model
    long: Optional[float] = None  # longitude of model
    start_date: Optional[str] = None  # start date of the simulation (YYYY-mm-dd)
    end_date: Optional[str] = None  # end date of the simulation (YYYY-mm-dd)
    spin_up: Optional[int] = None  # how many days of hydrus simulation should be ignored
    modflow_metadata: Optional[ModflowMetadata] = None
    hydrus_models: Set[HydrusID] = field(default_factory=set)  # list of names of folders containing the hydrus models
    weather_files: Set[WeatherID] = field(default_factory=set)
    shapes: Dict[ShapeID, ShapeColor] = field(default_factory=dict)

    shapes_to_hydrus: Dict[ShapeID, Union[HydrusID, float]] = field(default_factory=dict)
    hydrus_to_weather: Dict[HydrusID, WeatherID] = field(default_factory=dict)

    def set_modflow_metadata(self, modflow_metadata: ModflowMetadata):
        self.modflow_metadata = modflow_metadata

    def remove_modflow_metadata(self):
        self.modflow_metadata = None

    def add_hydrus_model(self, hydrus_id: HydrusID):
        self.hydrus_models.add(hydrus_id)

    def remove_hydrus_model(self, hydrus_id: HydrusID):
        self.hydrus_models.remove(hydrus_id)

    def add_weather_file(self, weather_file_id: WeatherID):
        self.weather_files.add(weather_file_id)

    def remove_weather_file(self, weather_file_id: WeatherID):
        self.weather_files.remove(weather_file_id)

    def add_shape_metadata(self, shape_id: ShapeID, shape_color: ShapeColor):
        self.shapes[shape_id] = shape_color

    def remove_shape_metadata(self, shape_id: ShapeID):
        del self.shapes[shape_id]

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
        return modflow_id == self.modflow_metadata.modflow_id

    def contains_weather_model(self, weather_id: WeatherID) -> bool:
        return weather_id in self.weather_files

    def contains_shape(self, shape_id: ShapeID) -> bool:
        return shape_id in self.shapes

    def to_json_str(self):
        self.hydrus_models = list(self.hydrus_models)
        self.weather_files = list(self.weather_files)
        serialized = jsonify(self)
        self.hydrus_models = set(self.hydrus_models)
        self.weather_files = set(self.weather_files)
        return serialized
