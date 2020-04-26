import zlib
from typing import List

import attr
import redis

from links import (LinksRepository,
                   Link,
                   LinksRepositoryError)

_LINK_INFO = lambda k: f'link:{k}:info'
_LINKS_TIMESERIES = 'link:timeseries'


@attr.s(slots=True)
class RedisLinksRepository(LinksRepository):
    _redis_client = attr.ib()
    _pipeline = attr.ib(init=False, default=None)

    @classmethod
    def from_params(cls, host, port, pwd):
        redis_client = redis.Redis(host=host,
                                   port=port,
                                   password=pwd,
                                   decode_responses=True)
        return cls(redis_client)

    @staticmethod
    def _link_key(link: Link) -> str:
        digest = zlib.crc32(link.url.encode())
        return f'{digest}:{link.visit_dt.timestamp()}'

    @staticmethod
    def _serialize_link(link: Link) -> dict:
        return {
            'url': link.url,
            'ts': link.visit_ts
        }

    @staticmethod
    def _deserialize_link(info: dict) -> Link:
        return Link.from_ts(
            info['url'],
            float(info['ts']))

    def save_link(self, link: Link):
        key = RedisLinksRepository._link_key(link)
        self._client.hmset(
            _LINK_INFO(key),
            self._serialize_link(link)
        )
        self._client.zadd(
            _LINKS_TIMESERIES,
            {key: link.visit_ts}
        )

    def visited_links(self, from_ts: float, to_ts: float) -> List[Link]:
        if self._pipeline:
            raise LinksRepositoryError(
                'Attempt to fetch link in session')

        keys = self._redis_client.zrangebyscore(
            _LINKS_TIMESERIES,
            from_ts,
            to_ts
        )

        pipe = self._redis_client.pipeline()
        for key in keys:
            pipe.hgetall(_LINK_INFO(key))
        links_data = pipe.execute()

        return [
            self._deserialize_link(info)
            for info in links_data
        ]

    def __enter__(self):
        if self._pipeline:
            raise LinksRepositoryError(
                'The links repository is already in session')

        self._pipeline = self._redis_client.pipeline()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._pipeline:
            self._pipeline.execute()
            self._pipeline = None

    @property
    def _client(self):
        if self._pipeline:
            return self._pipeline
        return self._redis_client
