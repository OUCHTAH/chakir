from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret_key'  # مفتاح سري لتخزين الجلسات

login_manager = LoginManager()
login_manager.init_app(app)

# اسم الملف الذي سيتم تخزين البيانات فيه
excel_file = "قائمة_المسجلين.xlsx"

# تحميل البيانات من ملف Excel إذا كان موجودًا
if os.path.exists(excel_file):
    registrants = pd.read_excel(excel_file).to_dict(orient="records")
else:
    registrants = []

# تعريف المستخدم (User) بشكل بسيط
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# قائمة المستخدمين (تخصيص أسماء المستخدمين وكلمات المرور للمساعدين)
users = {
    'mohammed': {'password': 'password123'},
    'ahmed': {'password': 'ahmedpassword'}
}

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # تحقق من بيانات المستخدم
        if username in users and users[username]['password'] == password:
            user = User(id=username)
            login_user(user)
            return redirect(url_for('index'))
        else:
            return "بيانات الدخول غير صحيحة"
    return render_template('login.html')

@app.route('/')
@login_required
def index():
    return render_template('index.html', registrants=registrants)

@app.route('/add', methods=['POST'])
@login_required
def add_registrant():
    name = request.form['name']
    phone = request.form['phone']
    national_id = request.form['national_id']
    ticket_number = request.form['ticket_number']
    payment = request.form['payment']
    seller_name = current_user.id  # اسم المستخدم الذي قام بالإدخال
    sale_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # الوقت والتاريخ الحالي

    # التحقق من أن جميع الحقول مكتملة وأن المبلغ هو 300
    if name and phone and national_id and ticket_number and payment == '300':
        # التحقق من عدم تكرار رقم التذكرة
        if any(reg['رقم التذكرة'] == ticket_number for reg in registrants):
            return "رقم التذكرة موجود بالفعل، يرجى إدخال رقم مختلف."

        # إضافة المسجل الجديد إلى القائمة
        new_registrant = {
            "الاسم": name,
            "الهاتف": phone,
            "رقم البطاقة الوطنية": national_id,
            "رقم التذكرة": ticket_number,
            "المبلغ المدفوع": payment,
            "اسم الشخص الذي باع التذكرة": seller_name,  # إضافة اسم الشخص
            "التاريخ والوقت": sale_datetime  # إضافة الوقت والتاريخ
        }
        registrants.append(new_registrant)

        # تحديث ملف Excel فورًا عند إضافة المسجل الجديد
        df = pd.DataFrame(registrants)
        df.to_excel(excel_file, index=False)

        return redirect(url_for('index'))
    else:
        return "الرجاء التأكد من إدخال جميع الحقول بشكل صحيح وأن المبلغ المدفوع هو 300 درهم."

@app.route('/edit/<int:index>', methods=['GET', 'POST'])
@login_required
def edit_registrant(index):
    registrant = registrants[index]

    # التحقق من أن الشخص الذي يحاول التعديل هو نفسه الذي باع التذكرة
    if registrant['اسم الشخص الذي باع التذكرة'] != current_user.id:
        return "ليس لديك صلاحية لتعديل هذه التذكرة."

    if request.method == 'POST':
        # الحصول على البيانات المعدلة من النموذج
        registrant['الاسم'] = request.form['name']
        registrant['الهاتف'] = request.form['phone']
        registrant['رقم البطاقة الوطنية'] = request.form['national_id']
        registrant['رقم التذكرة'] = request.form['ticket_number']
        registrant['المبلغ المدفوع'] = request.form['payment']

        # تحديث ملف Excel بعد تعديل البيانات
        df = pd.DataFrame(registrants)
        df.to_excel(excel_file, index=False)

        return redirect(url_for('index'))

    return render_template('edit.html', registrant=registrant)

@app.route('/export')
@login_required
def export_to_excel():
    if registrants:
        df = pd.DataFrame(registrants)
        df.to_excel(excel_file, index=False)
        return "تم تصدير القائمة إلى ملف Excel!"
    else:
        return "لا توجد بيانات لتصديرها."

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
