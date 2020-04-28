"""
Links Endpoints
"""
from flask import Blueprint, request

import links
from context import app_ctx
from .exceptions import BadRequest
from .statuses import Statuses, success_response, error_response
from .validation import validate

bp = Blueprint('links_api', __name__, url_prefix='/api/v1/linktracker/')


@bp.errorhandler(links.InvalidInputData)
def _handle_invalid_input(ex):
    """
    Prepare 400 bad request error response
    :param ex: exception
    :return: (payload, status)
    """
    return (error_response(str(ex)),
            Statuses.BAD_REQUEST)


@bp.errorhandler(links.LinksException)
def _handle_links_error(ex):
    """
    Prepare unexpected error response
    :param ex: exception
    :return: (payload, status)
    """
    return (error_response(str(ex)),
            Statuses.INTERNAL_ERROR)


def arg(name, cast_type=None):
    """
    Check request argument and cast to type
    :param name: argument's name
    :param cast_type: type to cast
    :return: value
    """
    if name not in request.args:
        raise BadRequest(f'"{name}" argument is required')
    value = request.args[name]

    if cast_type:
        try:
            value = cast_type(value)
        except TypeError:
            raise BadRequest(f'"{name}" argument is incorrect')

    return value


@bp.route('/visited_links', methods=['POST'])
@validate('visited_links')
def visit():
    """
    Endpoint for adding new visited links
    :return: status
    """
    data = request.get_json()
    links_list = [
        links.Link(url)
        for url in data['links']
    ]
    app_ctx.links.visit(links_list)
    return success_response()


@bp.route('/visited_domains', methods=['GET'])
def visited_domains():
    """
    Endpoint for getting visited domain for some timedelta
    :return: domains
    """
    _from = arg('from', cast_type=float)
    _to = arg('to', cast_type=float)

    domains = app_ctx.links.visited_domains(_from, _to)

    resp = success_response()
    resp['domains'] = list(domains.domains)
    return resp
