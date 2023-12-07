# models.py
from myapp import db
from datetime import datetime

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class TimeLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clock_in_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    clock_out_time = db.Column(db.DateTime)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)