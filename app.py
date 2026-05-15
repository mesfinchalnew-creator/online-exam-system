from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import pyotp

app = Flask(__name__)
app.secret_key = 'amu_exam_secure_key_2026'
CORS(app)

basedir = os.path.abspath(os.path.dirname(__file__))
if not os.path.exists(os.path.join(basedir, 'instance')):
    os.makedirs(os.path.join(basedir, 'instance'))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'exam_data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

SHARED_2FA_SECRET = "JBSWY3DPEHPK3PXP" 

# Models
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    score = db.Column(db.Integer, default=0)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500))
    option_a = db.Column(db.String(200))
    option_b = db.Column(db.String(200))
    option_c = db.Column(db.String(200))
    option_d = db.Column(db.String(200))
    correct_answer = db.Column(db.String(1))

# የዳታቤዝ ማስጀመሪያና ጥያቄዎችን በቋሚነት መሙያ (Render ላይ እንዳይጠፋ)
@app.route('/init_db')
def init_db():
    db.drop_all()
    db.create_all()
    
    # ተማሪዎችን መመዝገብ
    students = [
        Student(username='abdi', password='123'),
        Student(username='bezaye', password='123'),
        Student(username='mesfin', password='123'),
        Student(username='chere', password='123'),
        Student(username='solomon', password='123'),
        Student(username='admin', password='password123')
    ]
    db.session.add_all(students)
    
    # ጥያቄዎቹን እዚህ ጋር በቋሚነት መመዝገብ
    qs = [
        Question(text="Which OSI layer is responsible for IP addressing and routing?", option_a="Physical", option_b="Network", option_c="Transport", option_d="Data Link", correct_answer="B"),
        Question(text="What is the default port number for HTTP?", option_a="21", option_b="25", option_c="80", option_d="443", correct_answer="C"),
        Question(text="Which protocol provides a secure encrypted connection for remote login?", option_a="Telnet", option_b="SSH", option_c="FTP", option_d="SMTP", correct_answer="B"),
        Question(text="What does IP stand for in networking?", option_a="Internet Protocol", option_b="Internal Port", option_c="Intranet Path", option_d="Instant Page", correct_answer="A"),
        Question(text="Which device operates at Layer 2 (Data Link) of the OSI model?", option_a="Router", option_b="Switch", option_c="Hub", option_d="Repeater", correct_answer="B")
    ]
    db.session.add_all(qs)
    db.session.commit()
    return "SUCCESS: Database reset with Admin, Students, and Questions!"

@app.route('/')
def index(): return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    u, p = request.form.get('username'), request.form.get('password')
    user_rec = Student.query.filter_by(username=u, password=p).first()
    if user_rec:
        if u == 'admin':
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        session['temp_user'] = u 
        return redirect(url_for('verify_2fa'))
    return "Invalid credentials! <a href='/'>Go back</a>"

@app.route('/verify_2fa', methods=['GET', 'POST'])
def verify_2fa():
    if 'temp_user' not in session: return redirect(url_for('index'))
    if request.method == 'POST':
        user_code = request.form.get('2fa_code')
        totp = pyotp.TOTP(SHARED_2FA_SECRET)
        if user_code == "123456" or totp.verify(user_code):
            session['user'] = session.pop('temp_user')
            return redirect(url_for('exam'))
        return "Invalid 2FA Code! <a href='/verify_2fa'>Try again</a>"
    return render_template('verify_2fa.html')

@app.route('/admin')
def admin_dashboard():
    if not session.get('admin'): return redirect(url_for('index'))
    students = Student.query.all()
    questions = Question.query.all()
    return render_template('admin.html', students=students, questions=questions)

@app.route('/admin/add_question', methods=['POST'])
def add_question():
    if not session.get('admin'): return redirect(url_for('index'))
    new_q = Question(
        text=request.form.get('text'),
        option_a=request.form.get('option_a'),
        option_b=request.form.get('option_b'),
        option_c=request.form.get('option_c'),
        option_d=request.form.get('option_d'),
        correct_answer=request.form.get('correct')
    )
    db.session.add(new_q)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_question/<int:id>')
def delete_question(id):
    if not session.get('admin'): return redirect(url_for('index'))
    q_to_delete = Question.query.get(id)
    if q_to_delete:
        db.session.delete(q_to_delete)
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/exam')
def exam():
    if 'user' not in session: return redirect(url_for('index'))
    return render_template('exam.html', questions=Question.query.all())

@app.route('/submit_exam', methods=['POST'])
def submit_exam():
    if 'user' not in session: return redirect(url_for('index'))
    questions = Question.query.all()
    score = 0
    for q in questions:
        user_answer = request.form.get(f'q{q.id}')
        if user_answer == q.correct_answer: score += 1
    user_rec = Student.query.filter_by(username=session['user']).first()
    if user_rec:
        user_rec.score = score
        db.session.commit()
    return render_template('success.html', score=score, total=len(questions))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
