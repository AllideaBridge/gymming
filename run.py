import os

from app import create_app

env = os.environ.get('env', 'dev')
app = create_app(env)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True,debug=True)
