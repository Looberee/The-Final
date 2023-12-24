from models import db

class Candidates(db.Model):
    __tablename__ = 'candidates'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25))
    email = db.Column(db.String(25), unique=True, nullable=False)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(10), nullable=False)
    

    def __init__(self, name, email, username, password, datetime, status):
        db.Model.__init__(self)
        self.name = name
        self.email = email
        self.username = username
        self.password = password
        self.date = datetime
        self.status = status