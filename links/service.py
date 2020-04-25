import logging
from typing import List

import attr

from .db import LinksRepository, LinksRepositoryError
from .exceptions import InvalidInputData
from .models import Link, IncorrectUrl


@attr.s(slots=True, frozen=True)
class Status:
    status: str = attr.ib(default='ok')


@attr.s(slots=True, frozen=True)
class Error(Status):
    status: str = attr.ib(default='error')
    message: str = attr.ib(default=None)


@attr.s(slots=True, frozen=True)
class Domains(Status):
    domains: List[str] = attr.ib(factory=list)

    @classmethod
    def from_links(cls, links: List[Link]):
        return cls(domains=[link.domain
                            for link in links])


class LinksService:
    def __init__(self, repository: LinksRepository):
        self._repository = repository
        self._logger = logging.getLogger(__name__)

    def visit(self, links: List[Link]) -> Status:
        try:
            domains = [link.domain for link in links]
        except IncorrectUrl as err:
            self._logger.exception('Could not save visits links')
            return Error(message=str(err))

        try:
            with self._repository as session:
                for link in links:
                    session.save_link(link)
        except LinksRepositoryError as err:
            self._logger.exception('Could not save visits links')
            return Error(message=str(err))

        return Status()

    def visited_domains(self, from_ts: int, to_ts: int) -> Domains:
        if not from_ts or not to_ts:
            raise InvalidInputData('Time delta is incorrect')

        links = self._repository.visited_links(from_ts, to_ts)
        return Domains.from_links(links)
