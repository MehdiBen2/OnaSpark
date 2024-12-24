from app import app
from waitress import serve
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    serve(app, host='0.0.0.0', port=port)