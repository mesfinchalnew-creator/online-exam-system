from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = 'amu_final_2026'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'exam.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Database Models ---
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500))
    option_a = db.Column(db.String(200))
    option_b = db.Column(db.String(200))
    option_c = db.Column(db.String(200))
    option_d = db.Column(db.String(200))
    correct_answer = db.Column(db.String(1))

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))

# --- Database Initialization ---
with app.app_context():
    db.create_all()
    
    # 5 ተማሪዎችን መፍጠር
    if not Student.query.first():
        students = [
            Student(username='mesfin', password='123'),
            Student(username='chere', password='123'),
            Student(username='beza', password='123'),
            Student(username='solomon', password='123'),
            Student(username='abdi', password='123')
        ]
        db.session.bulk_save_objects(students)
        db.session.commit()

    # 6 የኔትዎርኪንግ ጥያቄዎችን መፍጠር
    if not Question.query.first():
        qs = [
            Question(text="Which layer is responsible for routing?", option_a="Data Link", option_b="Network", option_c="Transport", option_d="Physical", correct_answer="B"),
            Question(text="What is the port number for HTTP?", option_a="21", option_b="25", option_c="80", option_d="443", correct_answer="C"),
            Question(text="Which device connects different networks?", option_a="Switch", option_b="Hub", option_c="Bridge", option_d="Router", correct_answer="D"),
            Question(text="IPv4 addresses are how many bits long?", option_a="16", option_b="32", option_c="64", option_d="128", correct_answer="B"),
            Question(text="Which protocol is used to assign IP addresses automatically?", option_a="DNS", option_b="DHCP", option_c="FTP", option_d="SMTP", correct_answer="B"),
            Question(text="What is the 1st layer of the OSI model?", option_a="Physical", option_b="Data Link", option_c="Network", option_d="Application", correct_answer="A")
        ]
        db.session.bulk_save_objects(qs)
        db.session.commit()

# --- Routes ---

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    u = request.form.get('username')
    p = request.form.get('password')
    student = Student.query.filter_by(username=u, password=p).first()
    if student:
        session['user'] = u
        return redirect(url_for('exam'))
    return "Invalid Credentials! <a href='/'>Try again</a>"

@app.route('/exam')
def exam():
    if 'user' not in session: return redirect(url_for('index'))
    return render_template('exam.html', questions=Question.query.all())

@app.route('/submit', methods=['POST'])
def submit():
    if 'user' not in session: return redirect(url_for('index'))
    questions = Question.query.all()
    score = sum(1 for q in questions if request.form.get(str(q.id)) == q.correct_answer)
    total = len(questions)
    return render_template('result.html', score=score, total=total, percentage=(score/total)*100)

@app.route('/admin')
def admin():
    if 'user' not in session: return redirect(url_for('index'))
    return render_template('admin.html', questions=Question.query.all())

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
