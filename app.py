from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = 'amu_admin_fixed_2026'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///exam_final.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ዳታቤዝ ሞዴሎች
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    score = db.Column(db.Integer, default=0) # ውጤት ማስቀመጫ

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500))
    option_a = db.Column(db.String(200))
    option_b = db.Column(db.String(200))
    option_c = db.Column(db.String(200))
    option_d = db.Column(db.String(200))
    correct_answer = db.Column(db.String(1))

@app.route('/init_db')
def init_db():
    db.drop_all()
    db.create_all()
    # ተማሪዎች
    students = ['abdi', 'bezaye', 'mesfin', 'chere', 'solomon']
    for s in students:
        db.session.add(Student(username=s, password='123'))
    # ጥያቄዎች
    qs = [
        Question(text="Which layer of the OSI model is responsible for routing?", option_a="Physical", option_b="Network", option_c="Transport", option_d="Data Link", correct_answer="B"),
        Question(text="What is the standard port for HTTP?", option_a="21", option_b="25", option_c="80", option_d="443", correct_answer="C"),
        Question(text="What does IP stand for in networking?", option_a="Internet Protocol", option_b="Internal Port", option_c="Intranet Path", option_d="Instant Page", correct_answer="A")
    ]
    db.session.add_all(qs)
    db.session.commit()
    return "SUCCESS: Database Ready with Admin Panel!"

@app.route('/')
def index(): return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    u, p = request.form.get('username'), request.form.get('password')
    # Admin Login
    if u == 'admin' and p == 'admin123':
        session['user'] = 'admin'
        return redirect(url_for('admin_panel'))
    # Student Login
    student = Student.query.filter_by(username=u, password=p).first()
    if student:
        session['user'] = u
        return redirect(url_for('exam'))
    return "Error! <a href='/'>Try Again</a>"

@app.route('/exam')
def exam():
    if 'user' not in session: return redirect(url_for('index'))
    return render_template('exam.html', questions=Question.query.all())

@app.route('/submit_exam', methods=['POST'])
def submit_exam():
    if 'user' not in session: return redirect(url_for('index'))
    # ውጤት ማስላት (ለአሁኑ በዘፈቀደ 85 እንስጠው - ለዲሞ እንዲመች)
    student = Student.query.filter_by(username=session['user']).first()
    if student:
        student.score = 85 
        db.session.commit()
    return "<h1>Congratulations! Exam Submitted.</h1><a href='/'>Logout</a>"

# የአድሚን ገጽ (ውጤቶችን በ Table የሚያሳይ)
@app.route('/admin')
def admin_panel():
    if session.get('user') != 'admin': return "Access Denied!"
    students = Student.query.all()
    return render_template('admin.html', students=students)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
