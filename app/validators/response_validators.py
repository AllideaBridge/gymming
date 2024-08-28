from functools import wraps

from flask_pydantic import ValidationError


def validate_response(model):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = f(*args, **kwargs)
            try:
                model(**response[0])
                return response
            except ValidationError as e:
                return {"error": str(e)}, 400

        return decorated_function

    return decorator
