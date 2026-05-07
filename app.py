import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///exam.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('username')
        return redirect(url_for('exam', name=name))
    return render_template('login.html')

@app.route('/admin')
def admin():
    results = Result.query.all()
    return render_template('admin.html', results=results)

@app.route('/exam/<name>', methods=['GET', 'POST'])
def exam(name):
    if request.method == 'POST':
        score = 0
        # ትክክለኛ መልሶች ከ HTML 'value' ጋር መግጠም አለባቸው
        correct_answers = {
            'q1': 'B', 
            'q2': 'B', 
            'q3': 'B', 
            'q4': 'B', 
            'q5': 'A'
        }
        
        for q_id, correct_val in correct_answers.items():
            user_answer = request.form.get(q_id) # ከ HTML name="q1" የሚመጣውን ያነባል
            if user_answer == correct_val:
                score += 20
        
        new_result = Result(student_name=name, score=score)
        db.session.add(new_result)
        db.session.commit()
        
        return f"""
        <div style='text-align:center; margin-top:100px; font-family:sans-serif;'>
            <div style='display:inline-block; border:1px solid #ddd; padding:40px; border-radius:10px;'>
                <h2>Congratulations {name}!</h2>
                <h1 style='color:{"#28a745" if score >= 60 else "#dc3545"}; font-size:50px;'>Score: {score}%</h1>
                <p>Your result has been recorded successfully.</p>
                <a href='/login' style='color:#2a5298;'>Back to Home</a>
            </div>
        </div>
        """
    return render_template('exam.html', name=name)

if __name__ == '__main__':
    app.run(debug=True)
