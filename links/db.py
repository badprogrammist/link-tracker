from abc import ABC, abstractmethod
from typing import List

from links.models import Link


class LinksRepositoryError(Exception):
    pass


class LinksRepository(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def save_link(self, link: Link):
        pass

    @abstractmethod
    def visited_links(self,
                      from_ts: float,
                      to_ts: float) -> List[Link]:
        pass

    @abstractmethod
    def __enter__(self):
        return self

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        return None
