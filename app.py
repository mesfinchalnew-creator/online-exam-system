from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = 'amu_secret_key'

# Database Configuration
# Render ላይ ዳታቤዙ እንዲሰራ እንዲህ መጻፍ ይሻላል
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'exam.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Question Model
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500))
    option_a = db.Column(db.String(200))
    option_b = db.Column(db.String(200))
    option_c = db.Column(db.String(200))
    option_d = db.Column(db.String(200))
    correct_answer = db.Column(db.String(1))

# Database መፍጠርና ጥያቄዎችን መሙላት
with app.app_context():
    db.create_all()
    if not Question.query.first():
        sample_questions = [
            Question(text="What does IP stand for?", option_a="Internet Protocol", option_b="Internal Port", option_c="Intelligent Process", option_d="Index Page", correct_answer="A"),
            Question(text="Which layer is the OSI model's 3rd layer?", option_a="Physical", option_b="Data Link", option_c="Network", option_d="Transport", correct_answer="C"),
            Question(text="What is the default port for HTTP?", option_a="21", option_b="80", option_c="443", option_d="8080", correct_answer="B"),
            Question(text="Which device works at the Data Link layer?", option_a="Hub", option_b="Repeater", option_c="Switch", option_d="Router", correct_answer="C"),
            Question(text="What is the size of an IPv4 address?", option_a="16 bits", option_b="32 bits", option_c="64 bits", option_d="128 bits", correct_answer="B")
        ]
        db.session.bulk_save_objects(sample_questions)
        db.session.commit()

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if username == 'mesfin' and password == '123':
        session['user'] = username
        return redirect(url_for('exam'))
    return "Invalid Credentials! <a href='/'>Try again</a>"

@app.route('/exam')
def exam():
    if 'user' not in session:
        return redirect(url_for('index'))
    questions = Question.query.all()
    return render_template('exam.html', questions=questions)

@app.route('/submit', methods=['POST'])
def submit():
    if 'user' not in session:
        return redirect(url_for('index'))
    
    questions = Question.query.all()
    score = 0
    total = len(questions)
    
    for q in questions:
        user_ans = request.form.get(str(q.id))
        if user_ans == q.correct_answer:
            score += 1
            
    percentage = (score / total) * 100
    return render_template('result.html', score=score, total=total, percentage=percentage)

# የአድሚን ገጽ
@app.route('/admin')
def admin():
    if 'user' not in session:
        return redirect(url_for('index'))
    questions = Question.query.all()
    return render_template('admin.html', questions=questions)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Render ላይ እንዲሰራ host '0.0.0.0' እና port ከ environment መውሰድ አለበት
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
