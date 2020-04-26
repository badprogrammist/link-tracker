import pytest

from links import InvalidInputData
from links import Link


@pytest.mark.parametrize(
    'links,wrong_url',
    [
        ([Link.from_ts('123', 1)], '123')
    ]
)
def test_attempting_save_incorrect_url(
        in_memory_links_service,
        links,
        wrong_url):
    with pytest.raises(InvalidInputData,
                       match=f'Url "{wrong_url}" is incorrect'):
        in_memory_links_service.visit(links)


def test_handling_repository_error(error_prone_links_service):
    links = [Link.from_ts('ya.ru', 1)]
    with pytest.raises(Exception, match='Some error during saving'):
        error_prone_links_service.visit(links)
