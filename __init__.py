# __init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("./serviceAccountKey.json")
firebase_admin.initialize_app(cred)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'  # Use SQLite for simplicity
db = SQLAlchemy(app)

import routes
import models

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Employee': Employee, 'TimeLog': TimeLog}