class AppError(Exception):
    status_code = 400

    def __init__(self, detail: str):
        self.detail = detail

    def __str__(self):
        return self.detail


class NotFoundError(AppError):
    status_code = 404


class PermissionDeniedError(AppError):
    status_code = 403


class BadRequestError(AppError):
    status_code = 400


class WorkoutCreateError(BadRequestError):
    pass
