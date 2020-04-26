from enum import IntEnum

import attr


class Statuses(IntEnum):
    SUCCESS = 200
    BAD_REQUEST = 400
    INTERNAL_ERROR = 500


@attr.s(slots=True, frozen=True)
class Status:
    status: str = attr.ib(default='ok')


@attr.s(slots=True, frozen=True)
class Error(Status):
    status: str = attr.ib(default='error')
    message: str = attr.ib(default=None)


def success_response():
    return attr.asdict(Status())


def error_response(message):
    return attr.asdict(Error(message=message))
