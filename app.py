import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///exam.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Database Models ---

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    option_a = db.Column(db.String(200), nullable=False)
    option_b = db.Column(db.String(200), nullable=False)
    answer = db.Column(db.String(1), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, default=0)

# --- Routes ---

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    if username:
        new_user = User(username=username)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('exam', user_id=new_user.id))
    return redirect(url_for('index'))

@app.route('/exam/<int:user_id>')
def exam(user_id):
    questions = Question.query.all()
    return render_template('exam.html', questions=questions, user_id=user_id)

@app.route('/submit/<int:user_id>', methods=['POST'])
def submit(user_id):
    user = User.query.get(user_id)
    questions = Question.query.all()
    score = 0
    for q in questions:
        user_answer = request.form.get(f'question_{q.id}')
        if user_answer == q.answer:
            score += 1
    
    user.score = score
    db.session.commit()
    # AMU Title እዚህ ጋር ተጨምሯል
    return f"<h1>AMU Student Online Examination System</h1><h3>Congratulations, {user.username}!</h3><p>Your score: {score} out of {len(questions)}</p><br><a href='/admin'>View All Results</a>"

@app.route('/admin')
def admin():
    users = User.query.all()
    return render_template('admin.html', users=users)

# --- Database Seeding ---

def seed_questions():
    # በስህተት የነበረችው 'S' ተወግዳለች
    if Question.query.first() is None:
        questions = [
            Question(text="What does SDN stand for?", option_a="Software Defined Networking", option_b="System Data Network", answer="A"),
            Question(text="Which layer is the OSPF protocol located in?", option_a="Data Link Layer", option_b="Network Layer", answer="B"),
            Question(text="Which wireless standard is known as Wi-Fi 6?", option_a="802.11ax", option_b="802.11ac", answer="A"),
            Question(text="In mobile networking, what does 'Handoff' mean?", option_a="Connecting to a VPN", option_b="Transferring a call from one cell to another", answer="B"),
            Question(text="Which of the following is a threat to SDN controllers?", option_a="DDoS attacks", option_b="Physical cable theft", answer="A"),
            Question(text="What is the primary goal of Ethical Hacking?", option_a="To find and fix security vulnerabilities", option_b="To find bugs for money", answer="A")
        ]
        db.session.add_all(questions)
        db.session.commit()
        print("Questions added successfully!")

# --- App Execution ---

if __name__ == "__main__":
    with app.app_context():
        # db.drop_all() 
        db.create_all()
        seed_questions()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
