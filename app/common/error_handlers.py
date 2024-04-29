import http.client

from app.common.exceptions import ApplicationError


def register_error_handlers(app):
    @app.errorhandler(ApplicationError)
    def handle_application_error(error):
        return {"message": error.message}, error.status_code

    @app.errorhandler(ValueError)
    def handle_value_error(error):
        return {"message": str(error)}, http.HTTPStatus.BAD_REQUEST

    @app.errorhandler(KeyError)
    def handle_key_error(error):
        return {"message": f"Request Parameter None:{str(error)}"}, http.HTTPStatus.BAD_REQUEST
