from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os
import pyotp  # 2FA ኮድ ለማመንጨት (ይህንን 'pip install pyotp' ብለህ መጫን አለብህ)

app = Flask(__name__)
app.secret_key = 'amu_exam_secure_key_2026'

basedir = os.path.abspath(os.path.dirname(__file__))
if not os.path.exists(os.path.join(basedir, 'instance')):
    os.makedirs(os.path.join(basedir, 'instance'))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'exam_data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

SHARED_2FA_SECRET = "JBSWY3DPEHPK3PXP" 

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
    return "SUCCESS: Database is ready with 2FA setup!"

@app.route('/')
def index(): return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    u, p = request.form.get('username'), request.form.get('password')
    user_rec = Student.query.filter_by(username=u, password=p).first()
    
    if user_rec:
        # ፓስወርድ ልክ ከሆነ በቀጥታ ወደ ፈተና ከመሄድ ይልቅ 2FA እንዲያልፍ እናደርጋለን
        session['temp_user'] = u 
        return redirect(url_for('verify_2fa'))
    return "Invalid credentials! <a href='/'>Go back</a>"

# --- አዲሱ የ 2FA ማረጋገጫ ክፍል ---
@app.route('/verify_2fa', methods=['GET', 'POST'])
def verify_2fa():
    if 'temp_user' not in session: return redirect(url_for('index'))
    
    if request.method == 'POST':
        user_code = request.form.get('2fa_code')
        totp = pyotp.TOTP(SHARED_2FA_SECRET)
        
        if totp.verify(user_code): # ኮዱ ልክ ከሆነ
            session['user'] = session.pop('temp_user')
            return redirect(url_for('exam'))
        else:
            return "Invalid 2FA Code! <a href='/verify_2fa'>Try again</a>"
            
    return render_template('verify_2fa.html')

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
