from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
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

# قاعدة بيانات بسيطة للمستخدمين (المساعدين)
users = {
    'rachid': User(id=1, username='rachid', password='Rachid123@@'),
    'fanna': User(id=2, username='fanna', password='Rachid124@@'),
    'user1': User(id=3, username='user1', password='Rachid123@@22'),
    'user2': User(id=4, username='user2', password='Rachid123@@33'),
    'user3': User(id=5, username='user3', password='Rachid123@@Use23')
}

@login_manager.user_loader
def load_user(user_id):
    for user in users.values():
        if user.id == int(user_id):
            return user
    return None

# قائمة لتخزين المشاركين
participants = []

@app.route('/')
@login_required
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
            return redirect(url_for('home'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم تسجيل الخروج بنجاح!')
    return redirect(url_for('login'))

@app.route('/register', methods=['POST'])
@login_required
def register():
    # التحقق من المدخلات
    ticket_number = request.form['ticket_number']
    name = request.form['name']
    email = request.form['email']
    amount = request.form['amount']

    # التحقق إذا كان رقم التذكرة موجودًا مسبقًا
    if any(p['ticket_number'] == ticket_number for p in participants):
        flash('رقم التذكرة موجود بالفعل')
        return redirect(url_for('home'))

    # إضافة الشخص إلى قائمة المشاركين
    participants.append({
        'ticket_number': ticket_number,
        'name': name,
        'email': email,
        'amount': amount,
        'added_by': current_user.username  # إضافة من قام بالتسجيل
    })

    flash('تم تسجيل الشخص بنجاح!')
    return redirect(url_for('home'))

@app.route('/update/<ticket_number>', methods=['GET', 'POST'])
@login_required
def update(ticket_number):
    # العثور على المشارك بناءً على رقم التذكرة
    participant = next((p for p in participants if p['ticket_number'] == ticket_number), None)
    
    if participant and current_user.username != participant['added_by']:
        flash('لا يمكنك تعديل هذه التذكرة لأنها لم تُسجل بواسطة حسابك.')
        return redirect(url_for('home'))

    if request.method == 'POST':
        # تعديل البيانات إذا كان النموذج صحيحًا
        participant['name'] = request.form['name']
        participant['email'] = request.form['email']
        participant['amount'] = request.form['amount']
        flash('تم تعديل التذكرة بنجاح!')
        return redirect(url_for('home'))

    return render_template('update.html', participant=participant)

if __name__ == '__main__':
    app.run(debug=True)
