from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# إعداد Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# نموذج المستخدم
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password_hash = generate_password_hash(password)

# قاعدة بيانات بسيطة للمستخدمين
users = {'admin': User(id=1, username='admin', password='password')}

@login_manager.user_loader
def load_user(user_id):
    for user in users.values():
        if user.id == int(user_id):
            return user
    return None

# قائمة لتخزين المشاركين
participants = []

@app.route('/')
def home():
    # عرض الصفحة الرئيسية مع عرض المشاركين المسجلين
    return render_template('home.html', participants=participants)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('تم تسجيل الدخول بنجاح!')
            return redirect(url_for('dashboard'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم تسجيل الخروج بنجاح!')
    return redirect(url_for('login'))

@app.route('/register', methods=['POST'])
@login_required
def register():
    # الحصول على البيانات من النموذج
    name = request.form['name']
    email = request.form['email']
    amount = request.form['amount']

    # إضافة الشخص إلى قائمة المشاركين
    participants.append({'name': name, 'email': email, 'amount': amount})

    # إعادة تحميل الصفحة الرئيسية بعد التسجيل
    return render_template('home.html', participants=participants)

@app.route('/participants', methods=['GET'])
@login_required
def get_participants():
    # إعادة قائمة المشاركين كـ JSON
    return jsonify(participants)

if __name__ == '__main__':
    app.run(debug=True)
