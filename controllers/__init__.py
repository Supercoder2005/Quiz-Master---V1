from flask import Flask
from controllers.auth import auth  # Import auth blueprint

app = Flask(__name__)
app.register_blueprint(auth, url_prefix="/auth")  # Register blueprint
