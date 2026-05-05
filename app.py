from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = "msc_online_exam_secret" # ለሴኩሪቲ አስፈላጊ ነው

# Render ላይ ኮፒ ያደረግከው External Database URL እዚህ ጋር ይግባ
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@host/db_name'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 1. የተጠቃሚዎች ሰንጠረዥ (User Table)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='student')

# 2. የጥያቄዎች ሰንጠረዥ (Question Table)
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    option_a = db.Column(db.String(100), nullable=False)
    option_b = db.Column(db.String(100), nullable=False)
    answer = db.Column(db.String(1), nullable=False) # 'A' ወይም 'B'

@app.route('/')
def index():
    return "<h1>Online Exam System is Live!</h1><p>ሰንጠረዦቹ በዳታቤዙ ውስጥ ተፈጥረዋል።</p>"

if __name__ == "__main__":
    # ይህ መስመር ሰንጠረዦቹን በራሱ Render ዳታቤዝ ውስጥ ይፈጥራል
    with app.app_context():
        db.create_all()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
