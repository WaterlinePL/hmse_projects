# Interface
import json
import logging
import os
import shutil
from abc import ABC, abstractmethod
from typing import List
from zipfile import ZipFile

import numpy as np
from werkzeug.datastructures import FileStorage

from hmse_simulations.hmse_projects.project_metadata import ProjectMetadata
from hmse_simulations.hmse_projects.typing_help import ProjectID, ModflowID, HydrusID, WeatherID, ShapeID

WORKSPACE_PATH = 'workspace'
METADATA_FILENAME = 'metadata.json'


class ProjectDao(ABC):

    def __init__(self):
        os.makedirs(WORKSPACE_PATH, exist_ok=True)

    @abstractmethod
    def read_metadata(self, project_id: ProjectID) -> ProjectMetadata:
        with open(os.path.join(WORKSPACE_PATH, project_id, METADATA_FILENAME), 'w') as handle:
            return ProjectMetadata(**json.load(handle))

    @abstractmethod
    def read_all_metadata(self) -> List[ProjectMetadata]:
        return [self.read_metadata(project_id) for project_id in self.read_all_names()]

    @abstractmethod
    def read_all_names(self) -> List[str]:
        return os.listdir(WORKSPACE_PATH)

    @abstractmethod
    def save_or_update_metadata(self, metadata: ProjectMetadata) -> None:
        with open(os.path.join(WORKSPACE_PATH, metadata.project_id, METADATA_FILENAME), 'w') as handle:
            json.dump(metadata.to_json_str(), handle, indent=2)
            os.makedirs(os.path.join(ProjectDao.__get_project_path(metadata.project_id), 'modflow'), exist_ok=True)
            os.makedirs(os.path.join(ProjectDao.__get_project_path(metadata.project_id), 'hydrus'), exist_ok=True)
            os.makedirs(os.path.join(ProjectDao.__get_project_path(metadata.project_id), 'weather'), exist_ok=True)
            os.makedirs(os.path.join(ProjectDao.__get_project_path(metadata.project_id), 'shapes'), exist_ok=True)
            os.makedirs(os.path.join(ProjectDao.__get_rch_shapes_path(metadata.project_id)), exist_ok=True)

    @abstractmethod
    def delete_project(self, project_id: ProjectID) -> None:
        try:
            shutil.rmtree(ProjectDao.__get_project_path(project_id))
        except OSError as e:
            logging.error(f"Error occurred during deleting project {project_id}: {str(e)}")

    @abstractmethod
    def download_project(self, project_id: ProjectID) -> str:
        return shutil.make_archive(project_id, 'zip', ProjectDao.__get_project_path(project_id))

    @abstractmethod
    def add_hydrus_model(self, project_id: ProjectID, hydrus_id: HydrusID, archive: FileStorage) -> None:
        archive_path = os.path.join(ProjectDao.__get_project_path(project_id), 'hydrus', archive.filename)
        archive.save(archive_path)
        with ZipFile(archive_path, 'r') as archive_handle:
            hydrus_model_dir = ProjectDao.__get_hydrus_model_path(project_id, hydrus_id)
            os.makedirs(hydrus_model_dir)
            archive_handle.extractall(hydrus_model_dir)
        os.remove(archive_path)

    @abstractmethod
    def add_modflow_model(self, project_id: ProjectID, modflow_id: ModflowID, archive: FileStorage) -> None:
        archive_path = os.path.join(ProjectDao.__get_project_path(project_id), 'modflow', archive.filename)
        archive.save(archive_path)
        with ZipFile(archive_path, 'r') as archive_handle:
            modflow_model_dir = ProjectDao.__get_modflow_model_path(project_id, modflow_id)
            os.makedirs(modflow_model_dir)
            archive_handle.extractall(modflow_model_dir)
        os.remove(archive_path)

    @abstractmethod
    def delete_hydrus_model(self, project_id: ProjectID, hydrus_id: HydrusID) -> None:
        shutil.rmtree(ProjectDao.__get_hydrus_model_path(project_id, hydrus_id))

    @abstractmethod
    def delete_modflow_model(self, project_id: ProjectID, modflow_id: ModflowID) -> None:
        shutil.rmtree(ProjectDao.__get_modflow_model_path(project_id, modflow_id))

    @abstractmethod
    def add_weather_file(self, project_id: ProjectID, weather_id: WeatherID, weather_file: FileStorage) -> None:
        weather_file.save(f"{ProjectDao.__get_weather_model_path(project_id, weather_id)}"
                          f".{weather_file.filename.split('.')[-1]}")

    @abstractmethod
    def delete_weather_file(self, project_id: ProjectID, weather_file_id: WeatherID) -> None:
        os.remove(ProjectDao.__get_weather_model_path(project_id, weather_file_id))

    @abstractmethod
    def save_or_update_shape(self,
                             project_id: ProjectID,
                             shape_id: ShapeID,
                             shape_mask: np.ndarray) -> None:
        np.save(ProjectDao.__get_shape_path(project_id, shape_id), shape_mask)

    @abstractmethod
    def get_rch_shapes(self, project_id: ProjectID):
        return [np.load(ProjectDao.__get_rch_shape_filepath(project_id, shape_id))
                for shape_id in os.listdir(ProjectDao.__get_rch_shapes_path(project_id))]

    @abstractmethod
    def get_shape(self, project_id: ProjectID, shape_id: ShapeID) -> np.ndarray:
        return np.load(ProjectDao.__get_shape_path(project_id, shape_id))

    @abstractmethod
    def delete_shape(self, project_id: ProjectID, shape_id: ShapeID) -> None:
        os.remove(ProjectDao.__get_shape_path(project_id, shape_id))

    @abstractmethod
    def add_modflow_rch_shapes(self, project_id: ProjectID, rch_shapes: List[np.ndarray]):
        for i, mask in enumerate(rch_shapes):
            shape_id = f"rch_shape_{i+1}"
            np.save(ProjectDao.__get_rch_shape_filepath(project_id, shape_id), mask)

    @staticmethod
    def __get_project_path(project_id: ProjectID):
        return os.path.join(WORKSPACE_PATH, project_id)

    @staticmethod
    def __get_modflow_model_path(project_id: ProjectID, modflow_id: ModflowID):
        return os.path.join(ProjectDao.__get_project_path(project_id), 'modflow', modflow_id)

    @staticmethod
    def __get_hydrus_model_path(project_id: ProjectID, hydrus_id: HydrusID):
        return os.path.join(ProjectDao.__get_project_path(project_id), 'hydrus', hydrus_id)

    @staticmethod
    def __get_weather_model_path(project_id: ProjectID, weather_id: WeatherID):
        return os.path.join(ProjectDao.__get_project_path(project_id), 'weather', weather_id)

    @staticmethod
    def __get_shape_path(project_id: ProjectID, shape_id: ShapeID):
        return os.path.join(ProjectDao.__get_project_path(project_id), 'shape', f"{shape_id}.npy")

    @staticmethod
    def __get_rch_shapes_path(project_id: ProjectID):
        return os.path.join(ProjectDao.__get_project_path(project_id), 'rch_shapes')

    @staticmethod
    def __get_rch_shape_filepath(project_id: ProjectID, shape_id: ShapeID):
        return os.path.join(ProjectDao.__get_rch_shapes_path(project_id), f"{shape_id}.npy")


project_dao = ProjectDao()
