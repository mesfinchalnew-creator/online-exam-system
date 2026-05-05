from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = "msc_online_exam_secret"

# ያንተን External Database URL እዚህ ጋር በነጠላ ሰረዝ ውስጥ አስገባ
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://mesfin:x5xs9y1K2SlyfOezIcjun5wYfXYTOgBN@dpg-d7sq55d7vvec73c8grl0-a.oregon-postgres.render.com/exam_db_p2xo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# የዳታቤዝ ሰንጠረዦች
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    option_a = db.Column(db.String(100), nullable=False)
    option_b = db.Column(db.String(100), nullable=False)
    answer = db.Column(db.String(1), nullable=False)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    return redirect(url_for('exam'))

@app.route('/exam')
def exam():
    all_questions = Question.query.all()
    return render_template('exam.html', questions=all_questions)

# ጥያቄዎችን ወደ ዳታቤዝ ለመጨመር የሚረዳ ተግባር
def seed_questions():
    if Question.query.first() is None:
        q1 = Question(text="What does SDN stand for?", option_a="Software Defined Networking", option_b="System Data Network", answer="A")
        q2 = Question(text="Which layer is the OSPF protocol located in?", option_a="Data Link Layer", option_b="Network Layer", answer="B")
        db.session.add_all([q1, q2])
        db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_questions() # ጥያቄዎቹን ይጨምራል
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
