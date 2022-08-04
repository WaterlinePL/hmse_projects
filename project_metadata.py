from dataclasses import dataclass, field
from typing import List, Optional


# Is represented as .json file in store, accessed via dao
@dataclass
class ProjectMetadata:
    project_id: str = None                        # name of the project, must match root catalogue
    lat: float = None                       # latitude of model
    long: float = None                      # longitude of model
    start_date: str = None                  # start date of the simulation (YYYY-mm-dd)
    end_date: str = None                    # end date of the simulation (YYYY-mm-dd)
    spin_up: int = None                     # how many days of hydrus simulation should be ignored
    rows: int = None                        # amount of rows in the model grid
    cols: int = None                        # amount of columns in the model grid
    grid_unit: str = None                   # unit in which the model grid size is represented (feet/meters/centimeters)
    row_cells: List[float] = field(default_factory=list)        # heights of the model's consecutive rows
    col_cells: List[float] = field(default_factory=list)        # widths of the model's consecutive columns
    modflow_model: Optional[str] = None                         # name of the folder containing the modflow model
    hydrus_models: List[str] = field(default_factory=list)      # list of names of folders containing the hydrus models

    def remove_modflow_model(self):
        self.modflow_model = None

    def remove_hydrus_model(self, model_name: str):
        self.hydrus_models.remove(model_name)

    def to_json_str(self):
        return self.__dict__
