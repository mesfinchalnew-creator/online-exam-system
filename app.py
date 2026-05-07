import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Render ላይ PostgreSQL ካለ ይጠቀማል፣ ካልሆነ SQLite ይጠቀማል
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///exam.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# የውጤት መመዝገቢያ ሰንጠረዥ (Table)
class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)

# ዳታቤዙን በራሱ እንዲፈጥር
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

# የአስተዳዳሪ ገጽ (ውጤቶች የሚታዩበት)
@app.route('/admin')
def admin():
    results = Result.query.all()
    return render_template('admin.html', results=results)

@app.route('/exam/<name>', methods=['GET', 'POST'])
def exam(name):
    if request.method == 'POST':
        score = 0
        total_questions = 5
        
        # ትክክለኛ መልሶች (በ exam.html ካሉት ጥያቄዎች ጋር የሚገጥሙ)
        # q1: Transport (B), q2: Forwarding (B), q3: DHCP (B), q4: Secure (B), q5: 192.168 (A)
        correct_answers = {
            'q1': 'B', 
            'q2': 'B', 
            'q3': 'B', 
            'q4': 'B', 
            'q5': 'A'
        }
        
        # የተማሪውን መልስ ከትክክለኛው መልስ ጋር በማነፃፀር ውጤት ማስላት
        for q_id, correct_val in correct_answers.items():
            user_answer = request.form.get(q_id)
            if user_answer == correct_val:
                score += 20  # ለእያንዳንዱ ትክክል መልስ 20 ነጥብ
        
        # ውጤቱን ዳታቤዝ ውስጥ ማስቀመጥ
        new_result = Result(student_name=name, score=score)
        db.session.add(new_result)
        db.session.commit()
        
        # ውጤቱን ለተማሪው ማሳየት
        return f"""
        <div style='text-align:center; margin-top:100px; font-family:sans-serif; background-color:#f4f7f6; padding:50px;'>
            <div style='background:white; display:inline-block; padding:40px; border-radius:15px; box-shadow:0 4px 15px rgba(0,0,0,0.1);'>
                <h2 style='color:#1e3c72;'>ፈተናውን አጠናቀሃል {name}!</h2>
                <h1 style='color:{"#28a745" if score >= 50 else "#dc3545"}; font-size:48px;'>ውጤትህ: {score}%</h1>
                <p style='color:#666;'>ውጤትህ በሲስተሙ ውስጥ በትክክል ተመዝግቧል።</p>
                <br>
                <a href='/login' style='text-decoration:none; background:#2a5298; color:white; padding:10px 20px; border-radius:5px;'>ወደ መጀመሪያ ገጽ ተመለስ</a>
            </div>
        </div>
        """
    
    return render_template('exam.html', name=name)

if __name__ == '__main__':
    app.run(debug=True)
   
