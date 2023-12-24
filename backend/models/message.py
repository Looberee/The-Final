from flask_sqlalchemy import SQLAlchemy
from models import db
import datetime

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)