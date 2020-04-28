"""
Application starting point
"""
import os

import api
import db
import links
import settings
from context import init_context, app_ctx


def init_services():
    """
    Create all services
    :return: None
    """
    links_repo = db.RedisLinksRepository.from_params(
        settings.REDIS_HOST,
        settings.REDIS_PORT,
        settings.REDIS_PASSWORD
    )
    app_ctx.links = links.LinksService(links_repo)

    schemas_path = os.path.join(os.getcwd(), 'api/schemas')
    app_ctx.validator = api.ApiDataValidator(schemas_path)


def before_first_request():
    """
    Before first request callback
    """
    init_context()
    init_services()


app = api.create_app(
    before_first_request=before_first_request
)

if __name__ == "__main__":
    app.run()
