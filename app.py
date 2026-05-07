import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Render ላይ ያለውን PostgreSQL ዳታቤዝ ለመጠቀም
# 'DATABASE_URL' ከሌለ በራሱ 'exam.db' የሚባል ፋይል ይፈጥራል
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///exam.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# የዳታቤዝ ሞዴል (Tables)
class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)

# --- ወሳኝ ክፍል፡ ዳታቤዙን በራሱ እንዲፈጥር የሚያደርግ ---
with app.app_context():
    db.create_all()
# -----------------------------------------------

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('username')
        return redirect(url_for('exam', name=name))
    return render_template('login.html')

@app.route('/exam/<name>', methods=['GET', 'POST'])
def exam(name):
    if request.method == 'POST':
        # እዚህ ጋር ውጤቱን ማስላት ትችላለህ (ለአሁኑ 80 ብለነዋል)
        score = 80 
        new_result = Result(student_name=name, score=score)
        db.session.add(new_result)
        db.session.commit()
        return f"<h1>ደስ የሚል ነው {name}! ውጤትህ {score}% ተመዝግቧል።</h1>"
    return render_template('exam.html', name=name)

@app.route('/admin')
def admin():
    results = Result.query.all()
    return render_template('admin.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
