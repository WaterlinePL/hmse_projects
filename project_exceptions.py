from werkzeug.exceptions import HTTPException


class ProjectNotFound(Exception):
    pass


class ProjectNotSelected(Exception):
    pass


class UnknownHydrusModel(Exception):
    pass


class UnknownModflowModel(Exception):
    pass


class UnknownShape(Exception):
    pass


class UnknownWeatherFile(Exception):
    pass


class DuplicateHydrusModel(HTTPException):
    code = 409
    description = "Hydrus model with same ID already present in project"


class DuplicateModflowModel(HTTPException):
    code = 409
    description = "Modflow model with same ID already present in project"


class DuplicateWeatherFileInProject(HTTPException):
    code = 409
    description = "Weather file with same ID already present in project"
