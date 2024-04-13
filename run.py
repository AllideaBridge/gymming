import os

from app import create_app
from app.common.error_handlers import register_error_handlers

env = os.environ.get('env', 'dev')
app = create_app(env)
register_error_handlers(app)

if __name__ == '__main__':
    app.run(debug=True)
