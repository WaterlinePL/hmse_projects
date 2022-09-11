# Interface
from abc import ABC, abstractmethod
from typing import List

import numpy as np
from werkzeug.datastructures import FileStorage

from hmse_simulations.hmse_projects.project_metadata import ProjectMetadata
from hmse_simulations.hmse_projects.typing_help import ProjectID, ModflowID, HydrusID, WeatherID, ShapeID


class ProjectDao(ABC):

    @abstractmethod
    def read_metadata(self, project_id: ProjectID) -> ProjectMetadata:
        ...

    @abstractmethod
    def read_all_metadata(self) -> List[ProjectMetadata]:
        ...

    @abstractmethod
    def read_all_names(self) -> List[str]:
        ...

    @abstractmethod
    def save_or_update_metadata(self, metadata: ProjectMetadata) -> None:
        ...

    @abstractmethod
    def delete_project(self, project_id: ProjectID) -> None:
        ...

    @abstractmethod
    def download_project(self, project_id: ProjectID) -> FileStorage:
        ...

    @abstractmethod
    def add_hydrus_model(self, project_id: ProjectID, hydrus_id: ModflowID, archive: FileStorage) -> None:
        ...

    @abstractmethod
    def add_modflow_model(self, project_id: ProjectID, modflow_id: ModflowID, archive: FileStorage) -> None:
        ...

    @abstractmethod
    def delete_hydrus_model(self, project_id: ProjectID, hydrus_id: HydrusID) -> None:
        ...

    @abstractmethod
    def delete_modflow_model(self, project_id: ProjectID, modflow_id: ModflowID) -> None:
        ...

    @abstractmethod
    def add_weather_file(self, project_id: ProjectID, weather_id: WeatherID, weather_file: FileStorage) -> None:
        ...

    @abstractmethod
    def delete_weather_file(self, project_id: ProjectID, weather_file_id: WeatherID) -> None:
        ...

    @abstractmethod
    def save_or_update_shape(self,
                             project_id: ProjectID,
                             shape_id: ShapeID,
                             shape_mask: np.ndarray,
                             color: str) -> None:
        ...

    @abstractmethod
    def get_rch_shapes(self,
                       project_id: ProjectID):
        ...

    @abstractmethod
    def get_shape(self, project_id: ProjectID, shape_id: ShapeID) -> np.ndarray:
        ...

    @abstractmethod
    def delete_shape(self, project_id: ProjectID, shape_id: ShapeID) -> None:
        ...

    @abstractmethod
    def add_modflow_rch_shapes(self, project_id: ProjectID, rch_shapes: List[np.ndarray]):
        ...


project_dao = ProjectDao()
