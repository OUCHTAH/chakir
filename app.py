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
    national_id = request.form['national_id']
    ticket_number = request.form['ticket_number']
    amount = request.form['amount']

    # التحقق من أن جميع الحقول مملوءة
    if not name or not national_id or not ticket_number or not amount:
        flash('جميع الحقول يجب أن تكون مملوءة!')
        return redirect(url_for('home'))

    # التحقق من عدم تكرار رقم التذكرة
    for participant in participants:
        if participant['ticket_number'] == ticket_number:
            flash('رقم التذكرة مكرر! يرجى إدخال رقم تذكرة مختلف.')
            return redirect(url_for('home'))

    # إضافة الشخص إلى قائمة المشاركين
    participants.append({'name': name, 'national_id': national_id, 'ticket_number': ticket_number, 'amount': amount})

    # إعادة تحميل الصفحة الرئيسية بعد التسجيل
    flash('تم التسجيل بنجاح!')
    return redirect(url_for('home'))

@app.route('/edit/<ticket_number>', methods=['GET', 'POST'])
@login_required
def edit_participant(ticket_number):
    # البحث عن المشارك باستخدام رقم التذكرة
    participant = next((p for p in participants if p['ticket_number'] == ticket_number), None)
    
    if not participant:
        flash('المشارك غير موجود!')
        return redirect(url_for('home'))

    if request.method == 'POST':
        # تحديث البيانات
        participant['name'] = request.form['name']
        participant['national_id'] = request.form['national_id']
        participant['ticket_number'] = request.form['ticket_number']
        participant['amount'] = request.form['amount']
        
        flash('تم تحديث البيانات بنجاح!')
        return redirect(url_for('home'))

    # عرض النموذج للتعديل
    return render_template('edit_participant.html', participant=participant)

@app.route('/participants', methods=['GET'])
@login_required
def get_participants():
    return jsonify(participants)

if __name__ == '__main__':
    app.run(debug=True)
