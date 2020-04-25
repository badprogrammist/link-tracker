import datetime

import attr
import pytest

from links import LinksRepository, Link, LinksService


@attr.s
class InMemoryLinksRepository(LinksRepository):
    _links: list = attr.ib(factory=list)

    def save_link(self, link: Link):
        self._links.append(link)

    def visited_links(self, from_ts: int, to_ts: int):
        from_dt = datetime.datetime.fromtimestamp(from_ts)
        to_dt = datetime.datetime.fromtimestamp(from_ts)

        return [
            link
            for link in self._links
            if from_dt <= link.visit_dt <= to_dt
        ]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return None


class ErrorProneLinksRepository(InMemoryLinksRepository):

    def save_link(self, link: Link):
        raise Exception('Some error during saving')


@pytest.fixture(scope='module')
def in_memory_links_repository():
    return InMemoryLinksRepository()


@pytest.fixture(scope='module')
def in_memory_links_service(in_memory_links_repository):
    return LinksService(in_memory_links_repository)


@pytest.fixture(scope='function')
def error_prone_links_service():
    return LinksService(ErrorProneLinksRepository())
