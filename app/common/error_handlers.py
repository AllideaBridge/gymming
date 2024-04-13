from app.common.exceptions import ApplicationError


def register_error_handlers(app):
    @app.errorhandler(ApplicationError)
    def handle_application_error(error):
        return {"message": error.message}, error.status_code

