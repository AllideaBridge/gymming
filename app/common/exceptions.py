class ApplicationError(Exception):
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code


class BadRequestError(ApplicationError):
    def __init__(self):
        super().__init__("Bad Request, Invalid Parameter", 400)