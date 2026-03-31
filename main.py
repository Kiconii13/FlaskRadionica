from flask import Flask

from models import db
from routes import register_routes

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'tajna'

db.init_app(app)

with app.app_context():
    db.create_all()

# Registruj sve blueprint rute iz routes paketa
register_routes(app)

if __name__ == '__main__':
    app.run(debug=True)