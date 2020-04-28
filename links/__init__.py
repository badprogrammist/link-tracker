"""
Links domain
"""
from .db import LinksRepository, LinksRepositoryError
from .exceptions import LinksException, InvalidInputData
from .models import Link
from .service import LinksService, Domains
