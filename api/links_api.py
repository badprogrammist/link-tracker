from flask import Blueprint, request

import links
from context import app_ctx
from .exceptions import BadRequest
from .statuses import Statuses, success_response, error_response
from .validation import validate

bp = Blueprint('links_api', __name__, url_prefix='/api/v1/linktracker/')


@bp.errorhandler(links.InvalidInputData)
def _handle_invalid_input(ex):
    return (error_response(str(ex)),
            Statuses.BAD_REQUEST)


@bp.errorhandler(links.LinksException)
def _handle_links_error(ex):
    return (error_response(str(ex)),
            Statuses.INTERNAL_ERROR)


def arg(name):
    if name not in request.args:
        raise BadRequest(f'"{name}" argument is required')
    return request.args[name]


@bp.route('/visited_links', methods=['POST'])
@validate('visited_links')
def visit():
    data = request.get_json()
    links_list = [
        links.Link(url)
        for url in data['links']
    ]
    app_ctx.links.visit(links_list)
    return success_response()


@bp.route('/visited_domains', methods=['GET'])
def visited_domains():
    _from = arg('from')
    _to = arg('to')

    domains = app_ctx.links.visited_domains(_from, _to)

    resp = success_response()
    resp['domains'] = list(domains.domains)
    return resp
