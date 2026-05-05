from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = "msc_online_exam_secret"

# Render ዳታቤዝህ ላይ ያለውን 'External Database URL' እዚህ ጋር ቀይረው
app.config['SQLALCHEMY_DATABASE_URI'] = 'የአንተ_ዳታቤዝ_URL_እዚህ_ይግባ'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# የዳታቤዝ ሰንጠረዦች
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    option_a = db.Column(db.String(100), nullable=False)
    option_b = db.Column(db.String(100), nullable=False)
    answer = db.Column(db.String(1), nullable=False)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    # ለጊዜው ተማሪው Login ሲጫን በቀጥታ ወደ ፈተናው እንዲሄድ
    return redirect(url_for('exam'))

@app.route('/exam')
def exam():
    questions = Question.query.all()
    return render_template('exam.html', questions=questions)

if __name__ == "__main__":
    with app.app_context():
        db.create_all() # ሰንጠረዦቹን ዳታቤዝ ውስጥ ይፈጥራል
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
 
