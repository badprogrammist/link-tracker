from datetime import datetime

import attr
import tldextract

from .exceptions import InvalidInputData


class IncorrectUrl(InvalidInputData):
    pass


@attr.s(slots=True, frozen=True)
class Link:
    url: str = attr.ib()
    visit_dt: datetime = attr.ib(kw_only=True,
                                 factory=datetime.now)

    @url.validator
    def _check_url(self, _, value):
        if not value:
            raise IncorrectUrl('Url is null or empty')

    @classmethod
    def from_ts(cls, url: str, ts: int):
        return cls(
            url,
            visit_dt=datetime.fromtimestamp(ts)
        )

    @property
    def domain(self):
        result = tldextract.extract(self.url)

        if not result.domain or not result.suffix:
            raise IncorrectUrl(f'Url "{self.url}" is incorrect')

        return f'{result.domain}.{result.suffix}'
