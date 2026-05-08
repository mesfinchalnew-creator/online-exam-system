import os
from flask import Flask, render_template, request, redirect, url_for

# Render ላይ PostgreSQL ካለ ይጠቀማል፣ ካልሆነ SQLite ይጠቀማል
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'amu_exam_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///exam.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)

# Create Database and Default User
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='mesfin').first():
        test_user = User(username='mesfin', password='123')
        db.session.add(test_user)
        db.session.commit()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('username')
        pwd = request.form.get('password')
        
        user = User.query.filter_by(username=name).first()
        
        if user and user.password == pwd:
            return redirect(url_for('exam', name=name))
        else:
            # የተሳሳተ መረጃ ሲገባ የሚመጣ መልዕክት
            return "<h3 style='color:red; text-align:center; margin-top:50px;'>Invalid Username or Password!</h3><br><center><a href='/login'>Try Again</a></center>"
            
    return render_template('login.html')

@app.route('/exam/<name>', methods=['GET', 'POST'])
def exam(name):
    if request.method == 'POST':
        correct_count = 0
        total_questions = 5
        
        # Networking Answer Key
        correct_answers = {
            'q1': 'B', 
            'q2': 'B', 
            'q3': 'B', 
            'q4': 'B', 
            'q5': 'A'
        }
        
        for q_id, correct_val in correct_answers.items():
            user_answer = request.form.get(q_id)
            if user_answer == correct_val:
                correct_count += 1
        
        # ውጤትን በፐርሰንት ማስላት
        score_percentage = int((correct_count / total_questions) * 100)
        
        # ውጤቱን መመዝገብ
        new_result = Result(student_name=name, score=score_percentage)
        db.session.add(new_result)
        db.session.commit()
        
        # ውጤቱን በሁለቱም መንገድ (ቁጥር እና %) ማሳያ
        return f"""
        <div style='text-align:center; margin-top:100px; font-family:sans-serif;'>
            <div style='display:inline-block; border:2px solid #2a5298; padding:50px; border-radius:15px; background:#f9f9f9;'>
                <h2 style='color:#333;'>Congratulations {name}!</h2>
                <hr>
                <h3 style='color:#555;'>You Answered: <span style='color:#2a5298;'>{correct_count} out of {total_questions}</span> Correctly</h3>
                <h1 style='color:{"#28a745" if score_percentage >= 60 else "#dc3545"}; font-size:60px;'>Score: {score_percentage}%</h1>
                <p style='color:#777;'>Your result has been officially recorded.</p>
                <br>
                <a href='/login' style='background:#2a5298; color:white; padding:10px 25px; text-decoration:none; border-radius:5px;'>Log Out</a>
            </div>
        </div>
        """
    return render_template('exam.html', name=name)

@app.route('/admin')
def admin():
    results = Result.query.all()
    return render_template('admin.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
