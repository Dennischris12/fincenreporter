from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)

class Filing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filing_status = db.Column(db.String(100), nullable=False)
    filing_date = db.Column(db.String(100), nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    transcript_pdf = db.Column(db.LargeBinary)
    
    # Relationship to User
    user = db.relationship('User', backref=db.backref('filings', lazy=True))
