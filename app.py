from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = 'amu_exam_secure_key_2026'

# Database set-up
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///exam_data.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Student model
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    score = db.Column(db.Integer, default=0)

# Question model
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
    
    for name in ['abdi', 'bezaye', 'mesfin', 'chere', 'solomon']:
        db.session.add(Student(username=name, password='123'))
    
    qs = [
        Question(text="OSI model layer for routing?", option_a="Physical", option_b="Network", option_c="Transport", option_d="Data Link", correct_answer="B"),
        Question(text="Port for HTTP?", option_a="21", option_b="25", option_c="80", option_d="443", correct_answer="C"),
        Question(text="Secure remote login protocol?", option_a="Telnet", option_b="SSH", option_c="FTP", option_d="SMTP", correct_answer="B"),
        Question(text="IP stands for?", option_a="Internet Protocol", option_b="Internal Port", option_c="Intranet Path", option_d="Instant Page", correct_answer="A"),
        Question(text="Layer 2 device?", option_a="Router", option_b="Switch", option_c="Hub", option_d="Repeater", correct_answer="B"),
        Question(text="Loopback IP?", option_a="192.168.1.1", option_b="10.0.0.1", option_c="127.0.0.1", option_d="8.8.8.8", correct_answer="C")
    ]
    db.session.add_all(qs)
    db.session.commit()
    return "SUCCESS: Database is ready and clean!"

@app.route('/')
def index(): return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    u, p = request.form.get('username'), request.form.get('password')
    if u == 'admin' and p == 'admin123':
        session['user'] = 'admin'
        return redirect(url_for('admin_panel'))
    
    user_rec = Student.query.filter_by(username=u, password=p).first()
    if user_rec:
        session['user'] = u
        return redirect(url_for('exam'))
    return "Invalid credentials! <a href='/'>Go back</a>"

@app.route('/exam')
def exam():
    if 'user' not in session: return redirect(url_for('index'))
    return render_template('exam.html', questions=Question.query.all())

# --- እዚህ ጋር ነው ውጤቱ እንዲሰላ የተደረገው ---
@app.route('/submit_exam', methods=['POST'])
def submit_exam():
    if 'user' not in session: return redirect(url_for('index'))
    
    questions = Question.query.all()
    score = 0
    
    # እያንዳንዱን የተማሪ መልስ ከዳታቤዙ ጋር ማወዳደር
    for q in questions:
        user_answer = request.form.get(f'q{q.id}')
        if user_answer == q.correct_answer:
            score += 1
    
    user_rec = Student.query.filter_by(username=session['user']).first()
    if user_rec:
        user_rec.score = score
        db.session.commit()
    
    # ውጤቱን ወደ ገጹ መላክ
    return render_template('success.html', score=score, total=len(questions))

@app.route('/admin')
def admin_panel():
    if session.get('user') != 'admin': return "Access Denied!"
    return render_template('admin.html', students=Student.query.all())

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
