from werkzeug.exceptions import HTTPException


class ProjectNotFound(HTTPException):
    code = 404
    description = "Project not found!"


class ProjectNotSelected(HTTPException):
    code = 403
    description = "Project not selected!"


class UnknownHydrusModel(HTTPException):
    code = 404
    description = "Unknown Hydrus model!"


class UnknownModflowModel(HTTPException):
    code = 404
    description = "Unknown Modflow model!"


class UnknownShape(HTTPException):
    code = 404
    description = "Unknown shape!"


class UnknownWeatherFile(HTTPException):
    code = 404
    description = "Unknown weather file!"


class DuplicateHydrusModel(HTTPException):
    code = 409
    description = "Hydrus model with same ID already present in project"


class DuplicateModflowModel(HTTPException):
    code = 409
    description = "Modflow model with same ID already present in project"


class DuplicateWeatherFile(HTTPException):
    code = 409
    description = "Weather file with same ID already present in project"
