from typing import List

import attr
import redis

from links import (LinksRepository,
                   Link,
                   LinksRepositoryError)


@attr.s(slots=True)
class RedisLinksRepository(LinksRepository):
    _redis_client = attr.ib()
    _in_pipeline: bool = attr.ib(kw_only=True,
                                 default=False)

    @classmethod
    def from_params(cls, host, port, pwd):
        redis_client = redis.Redis(host=host,
                                   port=port,
                                   password=pwd)
        return cls(redis_client)

    @staticmethod
    def _link_key(link: Link) -> str:
        return f'{hash(link.url)}:{link.visit_dt.timestamp()}'

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

    _LINK_INFO = lambda k: f'link:{k}:info'
    _LINKS_TIMESERIES = 'link:timeseries'

    def save_link(self, link: Link):
        key = RedisLinksRepository._link_key(link)
        self._redis_client.hmset(
            self._LINK_INFO(key),
            self._serialize_link(link)
        )
        self._redis_client.zadd(
            self._LINKS_TIMESERIES,
            {key: link.visit_ts}
        )

    def visited_links(self, from_ts: float, to_ts: float) -> List[Link]:
        if self._in_pipeline:
            raise LinksRepositoryError(
                'Attempt to fetch link in session')

        keys = self._redis_client.zrangebyscore(
            self._LINKS_TIMESERIES,
            from_ts,
            to_ts
        )

        pipe = self._redis_client.pipeline()
        for key in keys:
            pipe.hgetall(self._LINK_INFO(key))
        links_data = pipe.execute()

        return [
            self._deserialize_link(info)
            for info in links_data
        ]

    def __enter__(self):
        if self._in_pipeline:
            raise LinksRepositoryError(
                'The links repository is already in session')

        pipe = self._redis_client.pipeline()
        return RedisLinksRepository(pipe, in_pipeline=True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._in_pipeline:
            self._redis_client.execute()
