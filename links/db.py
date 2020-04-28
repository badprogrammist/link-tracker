"""
Links Base Repository
"""
from abc import ABC, abstractmethod
from typing import List

from links.models import Link
from .exceptions import LinksException


class LinksRepositoryError(LinksException):
    pass


class LinksRepository(ABC):
    """
    Repository base class
    """
    def __init__(self):
        pass

    @abstractmethod
    def save_link(self, link: Link):
        """
        Save link into database
        :param link: Link
        :return: None
        """
        pass

    @abstractmethod
    def visited_links(self,
                      from_ts: float,
                      to_ts: float) -> List[Link]:
        """
        Fetch visited links
        :param from_ts: begin timestamp
        :param to_ts: end timestamp
        :return: list pf Links
        """
        pass

    @abstractmethod
    def __enter__(self):
        """
        Start transaction
        :return: session
        """
        return self

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Commit or rollback transaction
        """
        return None
