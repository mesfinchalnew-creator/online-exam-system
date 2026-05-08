from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = 'amu_final_2026'

# Database Setup
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'exam.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Question Table
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500))
    option_a = db.Column(db.String(200))
    option_b = db.Column(db.String(200))
    option_c = db.Column(db.String(200))
    option_d = db.Column(db.String(200))
    correct_answer = db.Column(db.String(1))

# Create DB and 10 Questions
with app.app_context():
    db.create_all()
    if not Question.query.first():
        qs = [
            Question(text="What is the 3rd layer of OSI?", option_a="Physical", option_b="Network", option_c="Session", option_d="Transport", correct_answer="B"),
            Question(text="Which device works at Layer 2?", option_a="Hub", option_b="Router", option_c="Switch", option_d="Repeater", correct_answer="C"),
            Question(text="Standard port for HTTPS?", option_a="80", option_b="21", option_c="443", option_d="25", correct_answer="C"),
            Question(text="IPv4 address size?", option_a="32 bits", option_b="64 bits", option_c="128 bits", option_d="16 bits", correct_answer="A"),
            Question(text="Which one is a Class C IP?", option_a="10.0.0.1", option_b="172.16.0.1", option_c="192.168.1.1", option_d="8.8.8.8", correct_answer="C"),
            Question(text="Which protocol is for Email sending?", option_a="POP3", option_b="SMTP", option_c="HTTP", option_d="FTP", correct_answer="B"),
            Question(text="Full form of LAN?", option_a="Local Area Net", option_b="Local Access Network", option_c="Local Area Network", option_d="Large Area Network", correct_answer="C"),
            Question(text="Which layer provides encryption?", option_a="Application", option_b="Presentation", option_c="Session", option_d="Transport", correct_answer="B"),
            Question(text="MAC address size?", option_a="32 bits", option_b="48 bits", option_c="64 bits", option_d="128 bits", correct_answer="B"),
            Question(text="Which command tests connectivity?", option_a="ipconfig", option_b="tracert", option_c="ping", option_d="netstat", correct_answer="C")
        ]
        db.session.bulk_save_objects(qs)
        db.session.commit()

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    u, p = request.form.get('username'), request.form.get('password')
    if u == 'mesfin' and p == '123':
        session['user'] = u
        return redirect(url_for('exam'))
    return "Wrong! <a href='/'>Back</a>"

@app.route('/exam')
def exam():
    if 'user' not in session: return redirect(url_for('index'))
    return render_template('exam.html', questions=Question.query.all())

@app.route('/submit', methods=['POST'])
def submit():
    if 'user' not in session: return redirect(url_for('index'))
    questions = Question.query.all()
    score = sum(1 for q in questions if request.form.get(str(q.id)) == q.correct_answer)
    return render_template('result.html', score=score, total=len(questions), percentage=(score/len(questions))*100)

@app.route('/admin')
def admin():
    if 'user' not in session: return redirect(url_for('index'))
    return render_template('admin.html', questions=Question.query.all())

# ********* የ LOGOUT ቦታ እዚህ ጋር ነው *********
@app.route('/logout')
def logout():
    session.pop('user', None) # የተጠቃሚውን መረጃ ያስወግዳል
    return redirect(url_for('index')) # ወደ Login ገጽ ይመልሰዋል
# *******************************************

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
