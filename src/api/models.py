import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask


app = Flask(__name__)
db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return f'<User {self.email}>'

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    status = db.Column(db.String(15), nullable=False)

    def __repr__(self):
        return 'Contact %r>' % self.full_name
    
    def serialize(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "address": self.address,
            "phone": self.phone,
            "status": self.status
        }