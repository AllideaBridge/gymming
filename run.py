import os

from app import create_app

env = os.environ.get('env', 'dev')
app = create_app(env)

if __name__ == '__main__':
    app.run(debug=True)
