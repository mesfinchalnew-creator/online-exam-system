from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = 'amu_exam_key_2026'

# Render ላይ ዳታቤዙን በትክክል እንዲያገኝ
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'exam.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500))
    option_a = db.Column(db.String(200))
    option_b = db.Column(db.String(200))
    option_c = db.Column(db.String(200))
    option_d = db.Column(db.String(200))
    correct_answer = db.Column(db.String(1))

with app.app_context():
    db.create_all()
    if not Question.query.first():
        sample = [
            Question(text="Which protocol is used for secure web browsing?", option_a="HTTP", option_b="FTP", option_c="HTTPS", option_d="SMTP", correct_answer="C"),
            Question(text="What is the main function of a Router?", option_a="Connect devices in LAN", option_b="Determine best path for data", option_c="Store web pages", option_d="Generate IP addresses", correct_answer="B")
        ]
        db.session.bulk_save_objects(sample)
        db.session.commit()

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    user = request.form.get('username')
    pw = request.form.get('password')
    if user == 'mesfin' and pw == '123':
        session['user'] = user
        return redirect(url_for('exam'))
    return "Invalid! <a href='/'>Try again</a>"

@app.route('/exam')
def exam():
    if 'user' not in session: return redirect(url_for('index'))
    questions = Question.query.all()
    return render_template('exam.html', questions=questions)

@app.route('/submit', methods=['POST'])
def submit():
    try:
        questions = Question.query.all()
        score = 0
        for q in questions:
            ans = request.form.get(str(q.id))
            if ans == q.correct_answer: score += 1
        return render_template('result.html', score=score, total=len(questions), percentage=(score/len(questions))*100)
    except Exception as e:
        return f"Error: {str(e)}" # ስህተቱ ምን እንደሆነ እንዲነግረን

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
