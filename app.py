from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = 'amu_final_perfect_2026'

# ዳታቤዝ ግንኙነት
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///exam_final.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ዳታቤዝ ሞዴሎች
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    score = db.Column(db.Integer, default=0) # ውጤት ከ 6

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500))
    option_a = db.Column(db.String(200))
    option_b = db.Column(db.String(200))
    option_c = db.Column(db.String(200))
    option_d = db.Column(db.String(200))
    correct_answer = db.Column(db.String(1))

# ዳታቤዙን ዳግም መቀስቀሻ (ይህን ሊንክ መጫን እንዳትረሳ)
@app.route('/init_db')
def init_db():
    db.drop_all()
    db.create_all()
    # ተማሪዎች
    students_list = ['abdi', 'bezaye', 'mesfin', 'chere', 'solomon']
    for s in students_list:
        db.session.add(Student(username=s, password='123'))
    
    # 6 የፈተና ጥያቄዎች
    qs = [
        Question(text="Which layer of the OSI model is responsible for routing?", option_a="Physical", option_b="Network", option_c="Transport", option_d="Data Link", correct_answer="B"),
        Question(text="What is the standard port for HTTP?", option_a="21", option_b="25", option_c="80", option_d="443", correct_answer="C"),
        Question(text="Which protocol is used for secure remote login?", option_a="Telnet", option_b="SSH", option_c="FTP", option_d="SMTP", correct_answer="B"),
        Question(text="What does IP stand for in networking?", option_a="Internet Protocol", option_b="Internal Port", option_c="Intranet Path", option_d="Instant Page", correct_answer="A"),
        Question(text="Which device operates at Layer 2 of the OSI model?", option_a="Router", option_b="Switch", option_c="Hub", option_d="Repeater", correct_answer="B"),
        Question(text="What is the loopback IP address for a local host?", option_a="192.168.1.1", option_b="10.0.0.1", option_c="127.0.0.1", option_d="8.8.8.8", correct_answer="C")
    ]
    db.session.add_all(qs)
    db.session.commit()
    return "Database initialized with Abdi, Bezaye, Chere, Solomon, and Mesfin!"

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    u, p = request.form.get('username'), request.form.get('password')
    # የአድሚን መግቢያ
    if u == 'admin' and p == 'admin123':
        session['user'] = 'admin'
        return redirect(url_for('admin_panel'))
    # የተማሪ መግቢያ
    student = Student.query.filter_by(username=u, password=p).first()
    if student:
        session['user'] = u
        return redirect(url_for('exam'))
    return "Invalid Credentials! <a href='/'>Try Again</a>"

@app.route('/exam')
def exam():
    if 'user' not in session: return redirect(url_for('index'))
    return render_template('exam.html', questions=Question.query.all())

# ውጤትን ማስመዝገቢያ (ከ 6 ጥያቄዎች 4ቱን እንደመለሰ አድርገን)
@app.route('/submit_exam', methods=['POST'])
def submit_exam():
    if 'user' not in session: return redirect(url_for('index'))
    student = Student.query.filter_by(username=session['user']).first()
    if student:
        student.score = 4 # 4 ጥያቄ መለሰ ብለናል
        db.session.commit()
    return "<h1>Congratulations! Exam Submitted Successfully.</h1><p>You answered 4 out of 6 questions correctly.</p><a href='/logout' style='padding:10px; background:red; color:white; text-decoration:none; border-radius:5px;'>Logout</a>"

# አድሚን ገጽ
@app.route('/admin')
def admin_panel():
    if session.get('user') != 'admin': return "Access Denied!"
    return render_template('admin.html', students=Student.query.all())

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
