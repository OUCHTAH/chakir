from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

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
users = {
    'rachid': User(id=1, username='rachid', password='Rachid123@@'),
    'fanna': User(id=2, username='fanna', password='Rachid124@@'),
    'user1': User(id=3, username='user1', password='Rachid123@@22'),
    'user2': User(id=4, username='user2', password='Rachid123@@33'),
    'user3': User(id=5, username='user3', password='Rachid123@@Use23')
}

# قائمة لتخزين المشاركين
participants = []

# تحميل المستخدم
@login_manager.user_loader
def load_user(user_id):
    for user in users.values():
        if user.id == int(user_id):
            return user
    return None

@app.route('/')
def home():
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
def register():
    # الحصول على البيانات من النموذج
    name = request.form['name']
    id_card = request.form['id_card']
    ticket_number = request.form['ticket_number']
    amount = request.form['amount']

    # التحقق من أن جميع الحقول تم ملؤها
    if not name or not id_card or not ticket_number or not amount:
        flash('جميع الحقول مطلوبة!')
        return redirect(url_for('home'))

    # التحقق من أن رقم التذكرة يحتوي فقط على أرقام
    if not ticket_number.isdigit():
        flash('رقم التذكرة يجب أن يحتوي على أرقام فقط!')
        return redirect(url_for('home'))

    # التحقق من عدم تكرار رقم التذكرة
    for participant in participants:
        if participant['ticket_number'] == ticket_number:
            flash('رقم التذكرة موجود بالفعل!')
            return redirect(url_for('home'))

    # إضافة الشخص إلى قائمة المشاركين
    participants.append({
        'name': name,
        'id_card': id_card,
        'ticket_number': ticket_number,
        'amount': amount
    })

    # إعادة تحميل الصفحة الرئيسية بعد التسجيل
    return render_template('home.html', participants=participants)

@app.route('/participants', methods=['GET'])
def get_participants():
    return jsonify(participants)

if __name__ == '__main__':
    app.run(debug=True)
