# error_handling.py
import logging
from flask import jsonify, request
from werkzeug.exceptions import HTTPException, BadRequest, NotFound, MethodNotAllowed

# Basic logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def error_response(message, status=400, code=None, details=None):
    payload = {"error": {"message": message}}
    if code:
        payload["error"]["code"] = code
    if details is not None:
        payload["error"]["details"] = details
    response = jsonify(payload)
    response.status_code = status
    return response


# Custom exceptions
class ValidationError(Exception):
    def __init__(self, message="Invalid input", details=None):
        super().__init__(message)
        self.details = details


class ObstacleError(Exception):
    def __init__(self, message="Obstacle encountered", obstacle=None):
        super().__init__(message)
        self.obstacle = obstacle


def register_error_handlers(app):
    @app.errorhandler(BadRequest)
    def handle_bad_request(e):
        logger.warning("BadRequest: %s -- data=%s", e, request.get_data(as_text=True))
        return error_response("Malformed JSON or bad request", status=400, details=str(e))

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        logger.info("HTTPException: %s %s", e.code, e.description)
        return error_response(e.description, status=e.code)

    @app.errorhandler(NotFound)
    def handle_not_found(e):
        return error_response("Endpoint not found", status=404)

    @app.errorhandler(MethodNotAllowed)
    def handle_method_not_allowed(e):
        return error_response("Method not allowed on this endpoint", status=405)

    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        logger.debug("ValidationError: %s %s", e, getattr(e, "details", None))
        return error_response(str(e), status=400, details=getattr(e, "details", None))

    @app.errorhandler(ObstacleError)
    def handle_obstacle_error(e):
        logger.info("ObstacleError: %s obstacle=%s", e, getattr(e, "obstacle", None))
        return error_response(str(e), status=409, details={"obstacle": getattr(e, "obstacle", None)})

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.exception("Unhandled exception: %s", e)
        return error_response("Internal server error", status=500)
