from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# إعداد Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# إعداد Google Sheets API
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("chakir-441715-e791e6fcbd91.json", scopes=scopes)
client = gspread.authorize(creds)
sheet = client.open("اسم_الملف_في_Google_Sheets").sheet1  # اختر الورقة الخاصة بك

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

# قاعدة بيانات المشاركين
participants = []

@login_manager.user_loader
def load_user(user_id):
    for user in users.values():
        if user.id == int(user_id):
            return user
    return None

@app.route('/')
@login_required
def home():
    total_amount = sum(int(p['amount']) for p in participants)  # حساب إجمالي المبلغ
    participants_sorted = sorted(participants, key=lambda p: p['name'])  # ترتيب المشاركين حسب الاسم
    return render_template('home.html', participants=participants_sorted, total_amount=total_amount)

@app.route('/register', methods=['POST'])
@login_required
def register():
    ticket_number = request.form['ticket_number']
    name = request.form['name']
    national_id = request.form['national_id']
    amount = request.form['amount']

    # التحقق من عدم وجود تكرار في رقم التذكرة
    if any(p['ticket_number'] == ticket_number for p in participants):
        flash('رقم التذكرة موجود بالفعل!')
        return redirect(url_for('home'))

    # إضافة المشارك إلى القاعدة
    participants.append({
        'ticket_number': ticket_number,
        'name': name,
        'national_id': national_id,
        'amount': amount,
        'added_by': current_user.username,
        'registration_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # إضافة تاريخ ووقت التسجيل
    })

    # إضافة البيانات إلى Google Sheets
    sheet.append_row([name, national_id, ticket_number, amount, current_user.username, datetime.now().strftime('%Y-%m-%d %H:%M:%S')])

    flash('تم التسجيل بنجاح!')
    return redirect(url_for('home'))

@app.route('/update/<ticket_number>', methods=['GET', 'POST'])
@login_required
def update(ticket_number):
    # البحث عن المشارك باستخدام رقم التذكرة
    participant = next((p for p in participants if p['ticket_number'] == ticket_number), None)

    if not participant:
        flash('المشارك غير موجود!')
        return redirect(url_for('home'))

    # التأكد من أن المساعد الحالي هو من قام بتسجيل هذا الرقم
    if participant['added_by'] != current_user.username:
        flash('لا يمكنك تعديل هذه البيانات لأنك لم تقم بتسجيلها!')
        return redirect(url_for('home'))

    if request.method == 'POST':
        participant['name'] = request.form['name']
        participant['national_id'] = request.form['national_id']
        participant['amount'] = request.form['amount']
        flash('تم التعديل بنجاح!')
        return redirect(url_for('home'))

    return render_template('update.html', participant=participant)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم تسجيل الخروج بنجاح!')
    return redirect(url_for('login'))

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

if __name__ == '__main__':
    app.run(debug=True)
