class ApplicationError(Exception):
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code


class BadRequestError(ApplicationError):
    def __init__(self, message=None):
        super().__init__("Bad Request, Invalid Parameter" if message is None else message, 400)


class UnAuthorizedError(ApplicationError):
    def __init__(self, message=None):
        super().__init__("This Request is UnAuthorized" if message is None else message, 401)
