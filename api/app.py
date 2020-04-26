from flask import Flask, request

from .api_logging import logger, log
from .exceptions import BadRequest
from .statuses import error_response, Statuses
from .links_api import bp as links_bp

ALLOWED_REQUEST_TYPES = {
    'POST'
}

ALLOWED_REQUEST_CONTENT_TYPES = {
    "application/json"
}


def check_request_content_type():
    if (request.method in ALLOWED_REQUEST_TYPES
            and request.mimetype not in ALLOWED_REQUEST_CONTENT_TYPES
            and request.data != ''):
        raise BadRequest("This content-type of request is unsupported")


def before_request():
    check_request_content_type()


def after_request(response):
    log(response)
    return response


def create_app(before_first_request=None, teardown_appcontext=None):
    flask_app = Flask(__name__)

    @flask_app.route('/api/v1/linktracker/healthz')
    def healthz():
        return {'status': 'ok'}, 200

    @flask_app.errorhandler(BadRequest)
    def _handle_bad_request(ex):
        return (error_response(str(ex)),
                Statuses.BAD_REQUEST)

    @flask_app.errorhandler(Exception)
    def _handle_error(ex):
        logger.exception("Unexpected exception")
        return (error_response(str(ex)),
                Statuses.INTERNAL_ERROR)

    flask_app.before_request(before_request)
    flask_app.after_request(after_request)

    if before_first_request:
        flask_app.before_first_request(before_first_request)

    if teardown_appcontext:
        flask_app.teardown_appcontext(teardown_appcontext)

    flask_app.register_blueprint(links_bp)

    return flask_app
