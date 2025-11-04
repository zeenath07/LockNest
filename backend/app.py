from flask import Flask
from backend.routes.user_routes import user_bp
from backend.routes.vault_routes import vault_bp
from backend.routes.intruder_routes import intruder_bp
from backend.routes.lan_routes import lan_bp  # Add this import
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

app.register_blueprint(user_bp, url_prefix='/api/user')
app.register_blueprint(vault_bp, url_prefix='/api/vault')
app.register_blueprint(intruder_bp, url_prefix='/api/intruder')
app.register_blueprint(lan_bp, url_prefix='/api/lan')  # Register LAN blueprint

@app.route('/')
def home():
    return "Welcome to LockNest Backend"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
