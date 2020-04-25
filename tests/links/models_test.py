import pytest

from links.models import Link, IncorrectUrl


@pytest.mark.parametrize(
    'url',
    [None, '']
)
def test_link_attrs_validation(url):
    with pytest.raises(IncorrectUrl, match='Url is null or empty'):
        Link(url)


@pytest.mark.parametrize(
    'url,exp',
    [
        ('https://stackoverflow.com/questions/11828270/how-to-exit-the-vim-editor',
         'stackoverflow.com'),
        ('https://ya.ru', 'ya.ru'),
        ('https://ya.ru?q=123', 'ya.ru'),
        ('funbox.ru', 'funbox.ru')
    ]
)
def test_domain_extracting(url, exp):
    assert Link(url).domain == exp


@pytest.mark.parametrize(
    'url',
    ['123']
)
def test_domain_extracting_from_invalid_url(url):
    with pytest.raises(IncorrectUrl,
                       match=f'Url "{url}" is incorrect'):
        Link(url).domain
