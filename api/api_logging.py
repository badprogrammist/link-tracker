"""
Api logging settings
"""
import logging

from flask import request

import settings

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s %(name)s %(filename)s:%(lineno)d %(levelname)s '
           '%(message)s')

handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter(
        '%(asctime)s %(levelname)s %(message)s'))
logger = logging.getLogger('API')
logger.handlers = [handler]
logger.setLevel(settings.LOG_LEVEL)
logger.propagate = False


def log(response):
    """
    Log response
    :param response: Flask Response
    :return: None
    """
    status_code = response.status_code
    content_length = response.content_length

    message = '%s "%s %s %s" %s %s "%s"' % (
        request.remote_addr,
        request.method,
        request.full_path,
        request.environ.get('SERVER_PROTOCOL', '-'),
        status_code,
        content_length,
        request.headers.get('User-Agent')
    )

    if status_code > 499:
        logger.error(message)
    elif status_code in {200, 201}:
        logger.debug(message)
    else:
        logger.info(message)
