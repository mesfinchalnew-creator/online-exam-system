from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os
import pyotp
import qrcode
import io
import base64

app = Flask(__name__)
app.secret_key = 'amu_final_2026'

# --- ዳታቤዝ ግንኙነት (SQLite for simplicity on Render Free Tier) ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///exam.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- ዳታቤዝ ሞዴሎች ---
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
    mfa_secret = db.Column(db.String(32))

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    score = db.Column(db.Integer)
    total = db.Column(db.Integer)
    percentage = db.Column(db.Float)

# ዳታቤዝ ለመፍጠር እና ተማሪዎችን ለመመዝገብ የምንጠቀምበት አዲስ መንገድ
@app.route('/init_db')
def init_db():
    db.create_all()
    
    # የተማሪዎች ዝርዝር
    student_list = [
        {'u': 'mesfin', 's': 'MESFIN2FASECRET1'},
        {'u': 'chere', 's': 'CHERE2FASECRET2'},
        {'u': 'solomon', 's': 'SOLOMON2FASECRET3'},
        {'u': 'abdi', 's': 'ABDI2FASECRET4'},
        {'u': 'bezaye', 's': 'BEZAYE2FASECRET5'}
    ]
    
    for item in student_list:
        if not Student.query.filter_by(username=item['u']).first():
            new_student = Student(username=item['u'], password='123', mfa_secret=item['s'])
            db.session.add(new_student)
    
    # ጥያቄዎችን መመዝገብ
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
    return "Database initialized with Abdi, Bezaye, Chere, Solomon, and Mesfin!"

# --- Routes ---

@app.route('/')
def index(): 
    return render_template('login.html')

@app.route('/setup_2fa/<username>')
def setup_2fa(username):
    student = Student.query.filter_by(username=username).first()
    if not student: return "ተማሪው አልተገኘም"
    
    uri = pyotp.totp.TOTP(student.mfa_secret).provisioning_uri(name=username, issuer_name="AMU_Exam_Security")
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf)
    qr_b64 = base64.b64encode(buf.getvalue()).decode()
    return render_template('setup.html', qr_image=qr_b64, username=username)

@app.route('/login', methods=['POST'])
def login():
    u, p = request.form.get('username'), request.form.get('password')
    student = Student.query.filter_by(username=u, password=p).first()
    if student:
        session['temp_user'] = u
        return redirect(url_for('verify_otp'))
    return "Invalid! <a href='/'>Try again</a>"

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if 'temp_user' not in session: return redirect(url_for('index'))
    
    if request.method == 'POST':
        otp = request.form.get('otp')
        student = Student.query.filter_by(username=session['temp_user']).first()
        totp = pyotp.totp.TOTP(student.mfa_secret)
        
        if totp.verify(otp):
            session['user'] = session.pop('temp_user')
            return redirect(url_for('exam'))
        return "የተሳሳተ ኮድ! <a href='/verify_otp'>እንደገና ይሞክሩ</a>"
    
    return render_template('verify.html')

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
    percentage = round((score / total) * 100, 2) 

    new_result = Result(username=session['user'], score=score, total=total, percentage=percentage)
    db.session.add(new_result)
    db.session.commit()
    return render_template('result.html', score=score, total=total, percentage=percentage)

@app.route('/admin')
def admin():
    if 'user' not in session: return redirect(url_for('index'))
    results = Result.query.all()
    return render_template('admin.html', results=results)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # አፑ ሲነሳ ዳታቤዙን በራሱ ይፈጥራል
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
