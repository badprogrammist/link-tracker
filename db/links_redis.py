"""
Links repository for redis
"""
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
    """
    Links repository for redis
    """
    _redis_client = attr.ib()
    _pipeline = attr.ib(init=False, default=None)

    @classmethod
    def from_params(cls, host, port, pwd):
        """
        Build repository
        :param host: redis host
        :param port: redis port
        :param pwd: redis password
        :return: LinksRepository
        """
        redis_client = redis.Redis(host=host,
                                   port=port,
                                   password=pwd,
                                   decode_responses=True)
        return cls(redis_client)

    @staticmethod
    def _link_key(link: Link) -> str:
        """
        Build redis key for Link
        :param link: Link
        :return: str
        """
        digest = zlib.crc32(link.url.encode())
        return f'{digest}:{link.visit_dt.timestamp()}'

    @staticmethod
    def _serialize_link(link: Link) -> dict:
        """
        Convert Link to dict
        :param link: Link
        :return: dict
        """
        return {
            'url': link.url,
            'ts': link.visit_ts
        }

    @staticmethod
    def _deserialize_link(info: dict) -> Link:
        """
        Convert dict to Link
        :param info: dict
        :return: Link
        """
        return Link.from_ts(
            info['url'],
            float(info['ts']))

    def save_link(self, link: Link):
        """
        Save Link into redis
        :param link: Link
        :return: None
        """
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
        """
        Fetch visited links
        :param from_ts: begin timestamp
        :param to_ts: end timestamp
        :return: list pf Links
        """
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
        """
        Start a new pipeline
        :return: LinkRepository
        """
        if self._pipeline:
            raise LinksRepositoryError(
                'The links repository is already in session')

        self._pipeline = self._redis_client.pipeline()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Commit pipeline
        """
        if self._pipeline:
            self._pipeline.execute()
            self._pipeline = None

    @property
    def _client(self):
        """
        Define and return appropriate redis client
        :return: Redis client
        """
        if self._pipeline:
            return self._pipeline
        return self._redis_client
