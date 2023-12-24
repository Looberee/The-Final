from models import db
from flask_login import UserMixin

class Admin(UserMixin, db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25))
    email = db.Column(db.String(25), unique=True, nullable=False)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime, nullable=True)
    company = db.Column(db.String(25), default="N/A", nullable=False)
    job = db.Column(db.String(25), default="N/A", nullable=False)
    country = db.Column(db.String(25), default="N/A", nullable=False)
    address = db.Column(db.String(125), default="N/A", nullable=False)
    phone = db.Column(db.String(25), default="N/A", nullable=False)
    priority = db.Column(db.Boolean, default=False)
    

    def __init__(self, name, email, username, password, datetime, priority):
        db.Model.__init__(self)
        self.name = name
        self.email = email
        self.username = username
        self.password = password
        self.date = datetime
        self.priority = priority