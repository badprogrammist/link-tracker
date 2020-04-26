import logging
from typing import Set, List

import attr

from .db import LinksRepository, LinksRepositoryError
from .exceptions import InvalidInputData
from .models import Link, IncorrectUrl


@attr.s(slots=True, frozen=True)
class Domains:
    domains: Set[str] = attr.ib(factory=set,
                                converter=set)

    @classmethod
    def from_links(cls, links: List[Link]):
        return cls(domains={link.domain
                            for link in links})


class LinksService:
    def __init__(self, repository: LinksRepository):
        self._repository = repository
        self._logger = logging.getLogger(__name__)

    def visit(self, links: List[Link]):
        try:
            for link in links:
                link.domain
        except IncorrectUrl:
            self._logger.exception('Could not save visits links')
            raise

        try:
            with self._repository as session:
                for link in links:
                    session.save_link(link)
        except LinksRepositoryError:
            self._logger.exception('Could not save visits links')
            raise

    def visited_domains(self, from_ts: float, to_ts: float) -> Domains:
        if not from_ts or not to_ts:
            raise InvalidInputData('Time delta is incorrect')

        links = self._repository.visited_links(from_ts, to_ts)
        return Domains.from_links(links)
