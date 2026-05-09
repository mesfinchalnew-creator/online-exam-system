from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = 'amu_secure_2fa_2026'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///exam_final.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

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

@app.route('/init_db')
def init_db():
    db.drop_all()
    db.create_all()
    for s in ['abdi', 'bezaye', 'mesfin', 'chere', 'solomon']:
        db.session.add(Student(username=s, password='123'))
    
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
    return "Database initialized with 2FA enabled!"

@app.route('/')
def index(): return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    u, p = request.form.get('username'), request.form.get('password')
    if u == 'admin' and p == 'admin123':
        session['user'] = 'admin'
        return redirect(url_for('admin_panel'))
    
    student = Student.query.filter_by(username=u, password=p).first()
    if student:
        session['temp_user'] = u # ለጊዜው እዚህ እናቆየው
        return redirect(url_for('verify_2fa')) # ወደ 2FA ገጽ ይሂድ
    return "Invalid! <a href='/'>Try Again</a>"

# --- አዲሱ የ 2FA ማረጋገጫ ገጽ ---
@app.route('/verify_2fa', methods=['GET', 'POST'])
def verify_2fa():
    if 'temp_user' not in session: return redirect(url_for('index'))
    
    if request.method == 'POST':
        otp = request.form.get('otp')
        if otp == '123456': # ለዲሞ የተቀመጠ ኮድ
            session['user'] = session.pop('temp_user')
            return redirect(url_for('exam'))
        else:
            return "Wrong OTP! <a href='/verify_2fa'>Try Again</a>"
            
    return '''
        <div style="text-align:center; margin-top:50px; font-family:Arial;">
            <h2>Two-Factor Authentication</h2>
            <p>Enter the 6-digit code sent to your device (Demo: 123456)</p>
            <form method="POST">
                <input type="text" name="otp" placeholder="Enter Code" required style="padding:10px;"><br><br>
                <button type="submit" style="padding:10px 20px; background:blue; color:white; border:none;">Verify</button>
            </form>
        </div>
    '''

@app.route('/exam')
def exam():
    if 'user' not in session: return redirect(url_for('index'))
    return render_template('exam.html', questions=Question.query.all())

@app.route('/submit_exam', methods=['POST'])
def submit_exam():
    if 'user' not in session: return redirect(url_for('index'))
    student = Student.query.filter_by(username=session['user']).first()
    if student:
        student.score = 4
        db.session.commit()
    return "<h1>Exam Submitted!</h1><a href='/logout'>Logout</a>"

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
