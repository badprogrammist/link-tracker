"""
Links model classes
"""
from datetime import datetime

import attr
import tldextract

from .exceptions import InvalidInputData


class IncorrectUrl(InvalidInputData):
    pass


@attr.s(slots=True, frozen=True)
class Link:
    """
    Link class
    """
    url: str = attr.ib()
    visit_dt: datetime = attr.ib(kw_only=True,
                                 factory=datetime.now)

    @url.validator
    def _check_url(self, _, value):
        """
        Validate input url
        """
        if not value:
            raise IncorrectUrl('Url is null or empty')

    @classmethod
    def from_ts(cls, url: str, ts: float):
        """
        Build Link from timestamp
        :param url: str
        :param ts: float
        :return: Link
        """
        return cls(
            url,
            visit_dt=datetime.fromtimestamp(ts)
        )

    @property
    def domain(self):
        """
        Extract domain from url
        :return: str
        """
        result = tldextract.extract(self.url)

        if not result.domain or not result.suffix:
            raise IncorrectUrl(f'Url "{self.url}" is incorrect')

        return f'{result.domain}.{result.suffix}'

    @property
    def visit_ts(self):
        """
        Get timestamp
        :return: float
        """
        return self.visit_dt.timestamp()
