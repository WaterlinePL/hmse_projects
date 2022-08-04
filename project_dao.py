# Interface
from abc import ABC, abstractmethod
from io import BytesIO
from typing import List, Tuple

from hmse_projects.project_metadata import ProjectMetadata


class ProjectDao(ABC):

    @abstractmethod
    def read_metadata(self, project_id: str) -> ProjectMetadata:
        ...

    @abstractmethod
    def read_all_metadata(self) -> List[ProjectMetadata]:
        ...

    @abstractmethod
    def read_all_names(self) -> List[str]:
        ...

    @abstractmethod
    def save_or_update_metadata(self, project: ProjectMetadata) -> None:
        ...

    @abstractmethod
    def delete_project(self, project_id: str) -> None:
        ...

    @abstractmethod
    def download_project(self, project_id: str) -> BytesIO:
        ...

    @abstractmethod
    def add_hydrus_models_to_project(self, project_id: str,
                                     model_names_with_archives: List[Tuple[str, BytesIO]]) -> None:
        ...

    @abstractmethod
    def add_modflow_model_to_project(self, project_id: str, model_name: str, archive: BytesIO) -> None:
        ...

    @abstractmethod
    def remove_hydrus_model_from_project(self, project_id: str, model_name: str) -> None:
        ...

    @abstractmethod
    def remove_modflow_model_from_project(self, project_id: str, model_name: str) -> None:
        ...

    @abstractmethod
    def is_project_finished(self, project_id: str) -> bool:
        ...


project_dao = ProjectDao()
