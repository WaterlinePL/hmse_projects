from typing import List, Dict

import numpy as np
from werkzeug.datastructures import FileStorage

from hmse_simulations.hmse_projects.hmse_hydrological_models.modflow.modflow_metadata import ModflowMetadata
from hmse_simulations.hmse_projects.project_dao import project_dao
from hmse_simulations.hmse_projects.project_metadata import ProjectMetadata
from hmse_simulations.hmse_projects.typing_help import ProjectID, HydrusID, ShapeID, WeatherID, ShapeColor


def get(project_id: ProjectID) -> ProjectMetadata:
    return project_dao.read_metadata(project_id)


def get_all_project_names() -> List[ProjectID]:
    return project_dao.read_all_names()


def save_or_update_metadata(metadata: ProjectMetadata) -> None:
    project_dao.save_or_update_metadata(metadata)


def delete(project_id: ProjectID) -> None:
    project_dao.delete_project(project_id)


def download_project(project_id: ProjectID) -> FileStorage:
    return project_dao.download_project(project_id)


def is_finished(project_id: ProjectID) -> bool:
    return project_dao.read_metadata(project_id).finished


def add_hydrus_model(project_id: ProjectID, hydrus_model: FileStorage):
    metadata = project_dao.read_metadata(project_id)
    hydrus_id = hydrus_model.name
    metadata.add_hydrus_model(hydrus_id)
    project_dao.add_hydrus_model(project_id, hydrus_id, hydrus_model)
    project_dao.save_or_update_metadata(metadata)


def delete_hydrus_model(project_id: ProjectID, hydrus_id: HydrusID):
    metadata = project_dao.read_metadata(project_id)
    metadata.remove_hydrus_model(hydrus_id)
    project_dao.delete_hydrus_model(project_id, hydrus_id)
    project_dao.save_or_update_metadata(metadata)


def set_modflow_model(project_id: ProjectID, modflow_model: FileStorage) -> ModflowMetadata:
    metadata = project_dao.read_metadata(project_id)

    if metadata.modflow_metadata:
        project_dao.delete_modflow_model(project_id, metadata.modflow_metadata.modflow_id)

    modflow_id = modflow_model.filename  # FIXME: perhaps FileStorage.filename
    metadata.set_modflow_metadata(modflow_id)
    project_dao.add_modflow_model(project_id, modflow_id, modflow_model)
    project_dao.save_or_update_metadata(metadata)
    # return modflow_service.analyze_model()    # TODO


def delete_modflow_model(project_id: ProjectID):
    metadata = project_dao.read_metadata(project_id)
    modflow_id = metadata.modflow_metadata.modflow_id
    metadata.remove_modflow_metadata()
    project_dao.delete_modflow_model(project_id, modflow_id)
    project_dao.save_or_update_metadata(metadata)


def add_weather_file(project_id: ProjectID, weather_file: FileStorage):
    metadata = project_dao.read_metadata(project_id)
    weather_id = weather_file.name
    metadata.add_weather_file(weather_id)
    project_dao.add_weather_file(project_id, weather_id, weather_file)
    project_dao.save_or_update_metadata(metadata)


def delete_weather_file(project_id: ProjectID, weather_id: HydrusID):
    metadata = project_dao.read_metadata(project_id)
    metadata.remove_weather_file(weather_id)
    project_dao.delete_weather_file(project_id, weather_id)
    project_dao.save_or_update_metadata(metadata)


def wipe_all_shapes(project_id: ProjectID) -> None:
    metadata = project_dao.read_metadata(project_id)
    for shape_id in metadata.shapes:
        project_dao.delete_shape(project_id, shape_id)


def get_all_shapes(project_id: ProjectID) -> Dict[ShapeID, np.ndarray]:
    metadata = project_dao.read_metadata(project_id)
    shapes = {}
    for shape_id in metadata.shapes.keys():
        shapes[shape_id] = project_dao.get_shape(project_id, shape_id).tolist()
    return shapes


def save_or_update_shape_metadata(project_id: ProjectID, shape_id: ShapeID, shape_color: ShapeColor):
    metadata = project_dao.read_metadata(project_id)
    metadata.add_shape_metadata(shape_id, shape_color)


def save_or_update_shape(project_id: ProjectID, shape_id: ShapeID, shape_mask: np.ndarray, color: str) -> None:
    project_dao.save_or_update_shape(project_id, shape_id, shape_mask, color)


def delete_shape(project_id: ProjectID, shape_id: ShapeID) -> None:
    project_dao.delete_shape(project_id, shape_id)


def map_shape_to_hydrus(project_id: ProjectID, shape_id: ShapeID, hydrus_id: HydrusID):
    metadata = project_dao.read_metadata(project_id)
    metadata.map_shape_to_hydrus(shape_id, hydrus_id)
    project_dao.save_or_update_metadata(metadata)


def map_shape_to_manual_value(project_id: ProjectID, shape_id: ShapeID, value: float):
    metadata = project_dao.read_metadata(project_id)
    metadata.map_shape_to_manual_value(shape_id, value)
    project_dao.save_or_update_metadata(metadata)


def map_hydrus_to_weather_file(project_id: ProjectID, hydrus_id: HydrusID, weather_id: WeatherID):
    metadata = project_dao.read_metadata(project_id)
    metadata.map_hydrus_to_weather(hydrus_id, weather_id)
    project_dao.save_or_update_metadata(metadata)


def remove_shape_mapping(project_id: ProjectID, shape_id: ShapeID):
    metadata = project_dao.read_metadata(project_id)
    metadata.remove_shape_mapping(shape_id)
    project_dao.save_or_update_metadata(metadata)


def remove_weather_hydrus_mapping(project_id: ProjectID, hydrus_id: HydrusID):
    metadata = project_dao.read_metadata(project_id)
    metadata.remove_hydrus_weather_mapping(hydrus_id)
    project_dao.save_or_update_metadata(metadata)
