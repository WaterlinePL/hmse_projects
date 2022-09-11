from dataclasses import dataclass, field
from typing import List, Optional, Set, Dict, Union

# Is represented as .json file in store, accessed via dao
from flask import jsonify

from hmse_simulations.hmse_projects.hmse_hydrological_models.modflow.modflow_metadata import ModflowMetadata
from hmse_simulations.hmse_projects.project_exceptions import UnknownShape, UnknownHydrusModel, DuplicateHydrusModel, \
    DuplicateWeatherFile, UnknownWeatherFile
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

    def __post_init__(self):
        self.hydrus_models = set(self.hydrus_models)
        self.weather_files = set(self.weather_files)

    def set_modflow_metadata(self, modflow_metadata: ModflowMetadata):
        self.modflow_metadata = modflow_metadata

    def remove_modflow_metadata(self):
        self.modflow_metadata = None

    def add_hydrus_model(self, hydrus_id: HydrusID):
        if hydrus_id not in self.hydrus_models:
            self.hydrus_models.add(hydrus_id)
        else:
            raise DuplicateHydrusModel(description=f"Hydrus model with ID {hydrus_id} already present in project!")

    def remove_hydrus_model(self, hydrus_id: HydrusID):
        try:
            self.hydrus_models.remove(hydrus_id)
        except KeyError:
            raise UnknownHydrusModel(description=f"Cannot delete model {hydrus_id} - no such model")

    def add_weather_file(self, weather_file_id: WeatherID):
        if weather_file_id not in self.weather_files:
            self.weather_files.add(weather_file_id)
        else:
            raise DuplicateWeatherFile(description=f"Weather file with ID {weather_file_id} already present in project!")

    def remove_weather_file(self, weather_file_id: WeatherID):
        try:
            self.weather_files.remove(weather_file_id)
        except KeyError:
            raise UnknownWeatherFile(description=f"Cannot delete weather file {weather_file_id} - no such file")

    def add_shape_metadata(self, shape_id: ShapeID, shape_color: ShapeColor):
        self.shapes[shape_id] = shape_color

    def remove_shape_metadata(self, shape_id: ShapeID):
        try:
            del self.shapes[shape_id]
        except KeyError:
            raise UnknownShape(description=f"Cannot delete shape {shape_id} - no such shape!")

    def map_shape_to_hydrus(self, shape_id: ShapeID, hydrus_id: HydrusID):
        if not self.contains_shape(shape_id):
            raise UnknownShape(description=f"Cannot map shape {shape_id} - no such shape")
        if not self.contains_hydrus_model(hydrus_id):
            raise UnknownHydrusModel(description=f"Cannot map shape {shape_id} to Hydrus model {hydrus_id} "
                                                 f"- no such Hydrus model")
        self.shapes_to_hydrus[shape_id] = hydrus_id

    def map_shape_to_manual_value(self, shape_id: ShapeID, value: float):
        if not self.contains_shape(shape_id):
            raise UnknownShape(description=f"Cannot map shape {shape_id} - no such shape")
        self.shapes_to_hydrus[shape_id] = value

    def map_hydrus_to_weather(self, hydrus_id: HydrusID, weather_id: WeatherID):
        if not self.contains_hydrus_model(hydrus_id):
            raise UnknownHydrusModel(description=f"Cannot assign weather file to Hydrus model {hydrus_id} "
                                                 f"- no such Hydrus model")
        if not self.contains_weather_model(weather_id):
            raise UnknownWeatherFile(description=f"Cannot assign weather file {weather_id} to Hydrus model "
                                                 f"- no such weather file")
        self.shapes_to_hydrus[hydrus_id] = weather_id

    def remove_shape_mapping(self, shape_id: ShapeID):
        if not self.contains_shape(shape_id):
            raise UnknownShape(description=f"Cannot unmap shape {shape_id} - no such shape")
        del self.shapes_to_hydrus[shape_id]

    def remove_hydrus_weather_mapping(self, hydrus_id: HydrusID):
        if not self.contains_hydrus_model(hydrus_id):
            raise UnknownHydrusModel(description=f"Cannot unassign weather file from Hydrus model {hydrus_id} "
                                                 f"- no such Hydrus model")
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
