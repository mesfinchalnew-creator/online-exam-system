import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'amu_secret_key' # ለ Flash መልእክቶች አስፈላጊ ነው
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///exam.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# የተጠቃሚ ሞዴል (User Model)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# የውጤት ሞዴል (Result Model)
class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)

with app.app_context():
    db.create_all()
    # ለመጀመሪያ ጊዜ መፈተኛ የሚሆን ተጠቃሚ መፍጠር (ካለ አይፈጥረውም)
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
        
        # ተጠቃሚውን መፈለግ
        user = User.query.filter_by(username=name).first()
        
        # ስምና ፓስወርድ ትክክል መሆኑን ማረጋገጥ
        if user and user.password == pwd:
            return redirect(url_for('exam', name=name))
        else:
            return "<h3 style='color:red; text-align:center;'>Invalid Username or Password!</h3><a href='/login'>Try Again</a>"
            
    return render_template('login.html')

@app.route('/exam/<name>', methods=['GET', 'POST'])
def exam(name):
    if request.method == 'POST':
        score = 0
        correct_answers = {'q1': 'B', 'q2': 'B', 'q3': 'B', 'q4': 'B', 'q5': 'A'}
        
        for q_id, correct_val in correct_answers.items():
            if request.form.get(q_id) == correct_val:
                score += 20
        
        new_result = Result(student_name=name, score=score)
        db.session.add(new_result)
        db.session.commit()
        
        return render_template('result.html', name=name, score=score)
    return render_template('exam.html', name=name)

@app.route('/admin')
def admin():
    results = Result.query.all()
    return render_template('admin.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
