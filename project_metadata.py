import copy
import datetime
from dataclasses import dataclass, field
from typing import Optional, Set, Dict, Union

from .hmse_hydrological_models.processing.modflow.modflow_metadata import ModflowMetadata
from .hmse_hydrological_models.processing.typing_help import ModflowID, HydrusID
from .project_exceptions import UnknownShape, UnknownHydrusModel, DuplicateHydrusModel, \
    DuplicateWeatherFile, UnknownWeatherFile
from .simulation_mode import SimulationMode
from .typing_help import WeatherID, ShapeID, ProjectID, ShapeColor


# Is represented as .json file in store, accessed via dao


@dataclass
class ProjectMetadata:
    project_id: ProjectID
    project_name: str

    finished: bool = False
    lat: Optional[float] = None  # latitude of model
    long: Optional[float] = None  # longitude of model
    start_date: Optional[str] = None  # start date of the simulation (YYYY-mm-dd)
    # end_date: Optional[str] = None  # end date of the simulation (YYYY-mm-dd)
    spin_up: int = 0  # how many days of hydrus simulation should be ignored
    modflow_metadata: Optional[ModflowMetadata] = None
    hydrus_models: Set[HydrusID] = field(default_factory=set)  # list of names of folders containing the hydrus models
    weather_files: Set[WeatherID] = field(default_factory=set)
    shapes: Dict[ShapeID, ShapeColor] = field(default_factory=dict)

    hydrus_durations: Dict[HydrusID, int] = field(default_factory=dict)
    weather_files_durations: Dict[WeatherID, int] = field(default_factory=dict)

    shapes_to_hydrus: Dict[ShapeID, Union[HydrusID, float]] = field(default_factory=dict)
    hydrus_to_weather: Dict[HydrusID, WeatherID] = field(default_factory=dict)

    simulation_mode: SimulationMode = SimulationMode.SIMPLE_COUPLING

    def __post_init__(self):
        if isinstance(self.modflow_metadata, dict):
            self.modflow_metadata = ModflowMetadata(**self.modflow_metadata)

        self.hydrus_models = set(self.hydrus_models)
        self.weather_files = set(self.weather_files)
        if isinstance(self.modflow_metadata, dict):
            self.modflow_metadata = ModflowMetadata(**self.modflow_metadata)

    def calculate_end_date(self):
        if self.start_date is None or not self.modflow_metadata:
            return None

        start = datetime.datetime.strptime(self.start_date, "%Y-%m-%d")
        duration = datetime.timedelta(days=self.modflow_metadata.get_duration())
        return (start + duration).strftime("%Y-%m-%d")

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
            raise DuplicateWeatherFile(
                description=f"Weather file with ID {weather_file_id} already present in project!")

    def remove_weather_file(self, weather_file_id: WeatherID):
        try:
            self.weather_files.remove(weather_file_id)
            for hydrus_id, weather_id in self.hydrus_to_weather:
                if weather_id == weather_file_id:
                    del self.hydrus_to_weather[hydrus_id]
        except KeyError:
            raise UnknownWeatherFile(description=f"Cannot delete weather file {weather_file_id} - no such file")

    def add_shape_metadata(self, shape_id: ShapeID, shape_color: ShapeColor):
        self.shapes[shape_id] = shape_color

    def remove_shape_metadata(self, shape_id: ShapeID):
        try:
            del self.shapes[shape_id]
            if shape_id in self.shapes_to_hydrus:
                del self.shapes_to_hydrus[shape_id]
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
        self.hydrus_to_weather[hydrus_id] = weather_id

    def remove_shape_mapping(self, shape_id: ShapeID):
        if not self.contains_shape(shape_id):
            raise UnknownShape(description=f"Cannot unmap shape {shape_id} - no such shape")
        if shape_id in self.shapes_to_hydrus:
            del self.shapes_to_hydrus[shape_id]

    def remove_hydrus_weather_mapping(self, hydrus_id: HydrusID):
        if not self.contains_hydrus_model(hydrus_id):
            raise UnknownHydrusModel(description=f"Cannot unassign weather file from Hydrus model {hydrus_id} "
                                                 f"- no such Hydrus model")
        if hydrus_id in self.hydrus_to_weather:
            del self.hydrus_to_weather[hydrus_id]

    def contains_hydrus_model(self, hydrus_id: HydrusID) -> bool:
        return hydrus_id in self.hydrus_models

    def contains_modflow_model(self, modflow_id: ModflowID) -> bool:
        return modflow_id == self.modflow_metadata.modflow_id

    def contains_weather_model(self, weather_id: WeatherID) -> bool:
        return weather_id in self.weather_files

    def contains_shape(self, shape_id: ShapeID) -> bool:
        return shape_id in self.shapes

    def get_used_hydrus_models(self) -> Set[HydrusID]:
        return {hydrus_id for hydrus_id in self.shapes_to_hydrus.values()
                if isinstance(hydrus_id, str)}

    def to_json_response(self):
        self.hydrus_models = list(self.hydrus_models)
        self.weather_files = list(self.weather_files)
        serialized = copy.deepcopy(self)
        self.hydrus_models = set(self.hydrus_models)
        self.weather_files = set(self.weather_files)
        return serialized
