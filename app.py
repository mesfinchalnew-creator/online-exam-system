from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = 'amu_final_fixed_2026'

# ዳታቤዝ ግንኙነት
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///exam_fixed.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ሞዴሎች
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500))
    a = db.Column(db.String(200))
    b = db.Column(db.String(200))
    c = db.Column(db.String(200))
    d = db.Column(db.String(200))
    correct = db.Column(db.String(1))

# ዳታቤዝ መቀስቀሻ - አሁን 6 ጥያቄዎችን ይዟል
@app.route('/init_db')
def init_db():
    db.drop_all()
    db.create_all()
    
    # ተማሪዎችን መመዝገብ
    students = ['abdi', 'bezaye', 'mesfin', 'chere', 'solomon']
    for s in students:
        new_s = Student(username=s, password='123')
        db.session.add(new_s)
    
    # 6 ጥያቄዎች (ለ Presentation የሚሆኑ)
    qs = [
        Question(text="Which layer of the OSI model is responsible for routing?", a="Physical", b="Network", c="Transport", d="Data Link", correct="B"),
        Question(text="What is the standard port for HTTP?", a="21", b="25", c="80", d="443", correct="C"),
        Question(text="Which protocol is used for secure remote login?", a="Telnet", b="SSH", c="FTP", d="SMTP", correct="B"),
        Question(text="What does IP stand for in networking?", a="Internet Protocol", b="Internal Port", c="Intranet Path", d="Instant Page", correct="A"),
        Question(text="Which device operates at Layer 2 of the OSI model?", a="Router", b="Switch", c="Hub", d="Repeater", correct="B"),
        Question(text="What is the loopback IP address for a local host?", a="192.168.1.1", b="10.0.0.1", c="127.0.0.1", d="8.8.8.8", correct="C")
    ]
    db.session.add_all(qs)
    db.session.commit()
    return "SUCCESS: Database Fixed with 6 Networking Questions!"

@app.route('/')
def index(): return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    u, p = request.form.get('username'), request.form.get('password')
    student = Student.query.filter_by(username=u, password=p).first()
    if student:
        session['user'] = u
        return redirect(url_for('exam'))
    return "Error: Invalid Credentials! <a href='/'>Try Again</a>"

@app.route('/exam')
def exam():
    if 'user' not in session: return redirect(url_for('index'))
    return render_template('exam.html', questions=Question.query.all())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
