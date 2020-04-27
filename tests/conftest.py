import datetime
import os

import attr
import pytest

import api
import db
import settings
from context import init_context, app_ctx
from links import LinksRepository, Link, LinksService


@attr.s
class InMemoryLinksRepository(LinksRepository):
    _links: list = attr.ib(factory=list)

    def save_link(self, link: Link):
        self._links.append(link)

    def visited_links(self, from_ts: float, to_ts: float):
        return [
            link
            for link in self._links
            if from_ts <= link.visit_ts <= to_ts
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


def init_services():
    if settings.TEST_IN_MEMORY_LINKS_REPOSITORY:
        links_repo = InMemoryLinksRepository()
    else:
        links_repo = db.RedisLinksRepository.from_params(
            settings.REDIS_HOST,
            settings.REDIS_PORT,
            settings.REDIS_PASSWORD
        )
    app_ctx.links = LinksService(links_repo)

    schemas_path = os.path.join(os.getcwd(), 'api/schemas')
    app_ctx.validator = api.ApiDataValidator(schemas_path)


@pytest.fixture
def client():
    init_context()
    init_services()

    app = api.create_app()
    app.config['TESTING'] = True

    with app.test_client() as c:
        yield c
