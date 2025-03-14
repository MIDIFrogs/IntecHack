from app import init_app
from config import Config

app = init_app()

if __name__ == '__main__':
    app.run(debug=Config.DEBUG)