# Interface
import os
import shutil
from abc import ABC, abstractmethod
from typing import List

import numpy as np
from flask import send_file
from werkzeug.datastructures import FileStorage

from hmse_simulations.hmse_projects.hmse_hydrological_models.modflow.modflow_metadata import ModflowMetadata
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
    def add_hydrus_model(self, project_id: ProjectID,
                         hydrus_id: HydrusID,
                         validated_model_path: os.PathLike) -> None:
        ...

    @abstractmethod
    def add_modflow_model(self, project_id: ProjectID,
                          modflow_id: ModflowID,
                          validated_model_path: os.PathLike) -> None:
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
                             shape_mask: np.ndarray) -> None:
        ...

    @abstractmethod
    def get_rch_shapes(self, project_id: ProjectID):
        ...

    @abstractmethod
    def delete_rch_shapes(self, project_id: ProjectID):
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


class ProjectMock(ProjectDao):

    def delete_rch_shapes(self, project_id: ProjectID):
        pass

    def add_modflow_rch_shapes(self, project_id: ProjectID, rch_shapes: List[np.ndarray]):
        pass

    def get_rch_shapes(self, project_id: ProjectID):
        shape1 = np.zeros((10, 10))
        shape1[7:10, :4] = 1
        shape2 = np.zeros((10, 10))
        shape2[:4, 7:10] = 1
        return {
            "rchShape1": shape1,
            "rchShape2": shape2
        }

    def read_metadata(self, project_id: ProjectID) -> ProjectMetadata:
        return ProjectMetadata(project_id,
                               project_name=project_id,
                               finished=True,
                               lat=10.10,
                               long=34.34,
                               start_date='2020-01-01',
                               spin_up=365,
                               modflow_metadata=ModflowMetadata(
                                   modflow_id="cekcyn-test",
                                   rows=10,
                                   cols=10,
                                   grid_unit='meter',
                                   row_cells=[50] * 10,
                                   col_cells=[20] * 10,
                                   duration=90
                               ),
                               hydrus_models={'las', 'trawa'},
                               weather_files={'weather1', 'weather2'},
                               shapes={'shape1': 'green',
                                       'shape2': 'blue'},
                               hydrus_to_weather={'las': 'weather1'},
                               shapes_to_hydrus={'shape1': 'trawa'},
                               hydrus_durations={'las': 365, 'trawa': 250},
                               weather_files_durations={'weather1': 700, 'weather2': 800},
                               )

    def read_all_metadata(self) -> List[ProjectMetadata]:
        return [ProjectMetadata("sample-project")]

    def read_all_names(self) -> List[ProjectID]:
        return ["sample-project"]

    def save_or_update_metadata(self, metadata: ProjectMetadata) -> None:
        pass

    def delete_project(self, project_id: ProjectID) -> None:
        pass

    def download_project(self, project_id: ProjectID) -> FileStorage:
        return "project.zip"

    def add_hydrus_model(self, project_id: ProjectID, hydrus_id: ModflowID, archive: FileStorage) -> None:
        pass

    def add_modflow_model(self, project_id: ProjectID, modflow_id: ModflowID, archive: FileStorage) -> None:
        pass

    def delete_hydrus_model(self, project_id: ProjectID, hydrus_id: HydrusID) -> None:
        pass

    def delete_modflow_model(self, project_id: ProjectID, modflow_id: ModflowID) -> None:
        pass

    def add_weather_file(self, project_id: ProjectID, weather_id: WeatherID, weather_file: FileStorage) -> None:
        pass

    def delete_weather_file(self, project_id: ProjectID, weather_file_id: WeatherID) -> None:
        pass

    def save_or_update_shape(self,
                             project_id: ProjectID,
                             shape_id: ShapeID,
                             shape_mask: np.ndarray) -> None:
        pass

    def get_shape(self, project_id: ProjectID, shape_id: ShapeID) -> np.ndarray:
        mask = np.zeros((10, 10))
        if shape_id == 'shape1':
            mask[:6, :6] = 1
        elif shape_id == 'shape2':
            mask[6:10, 6:10] = 1
        return mask

    def delete_shape(self, project_id: ProjectID, shape_id: ShapeID) -> None:
        pass


project_dao = ProjectMock()
