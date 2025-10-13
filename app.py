from flask import Flask
from model import db
from route.user_route import users_route
from route.task_route import tasks_route

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///task_management.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "123456"

db.init_app(app)

app.register_blueprint(users_route)
app.register_blueprint(tasks_route)

with app.app_context():
    db.create_all()


app.run(debug=True)
