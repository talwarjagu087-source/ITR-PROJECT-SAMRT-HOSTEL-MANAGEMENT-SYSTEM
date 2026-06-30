from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import urllib.parse

app = Flask(__name__)
app.secret_key = 'super_secret_hostel_erp_key'

# --- Safe Password Encoding for database@123 ---
raw_password = "database@123"
safe_password = urllib.parse.quote_plus(raw_password)

# --- MySQL Production Database Connection Configuration ---
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:{safe_password}@localhost/hostel_erp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==========================================
# 1. DATABASE RELATIONAL SCHEMAS (MODELS)
# ==========================================

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='student', nullable=False)  # admin, accountant, student, warden

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    enrollment_no = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10))
    course = db.Column(db.String(100))
    year = db.Column(db.String(20))
    phone = db.Column(db.String(15))
    email = db.Column(db.String(100))
    address = db.Column(db.String(255))
    room_no = db.Column(db.String(20))
    guardian_name = db.Column(db.String(100))
    guardian_phone = db.Column(db.String(15))
    admission_date = db.Column(db.String(20))

class Room(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    room_no = db.Column(db.String(20), unique=True, nullable=False)
    room_type = db.Column(db.String(20), nullable=False)  # Single, Double, Triple
    capacity = db.Column(db.Integer, default=1)
    occupied = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='Available')  # Available, Occupied, Maintenance

class RoomAllocation(db.Model):
    __tablename__ = 'room_allocations'
    id = db.Column(db.Integer, primary_key=True)
    enrollment_no = db.Column(db.String(50), nullable=False)
    room_no = db.Column(db.String(20), nullable=False)
    allocation_date = db.Column(db.String(20), nullable=False)

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    enrollment_no = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # Present, Absent, Leave

class Fee(db.Model):
    __tablename__ = 'fees'
    id = db.Column(db.Integer, primary_key=True)
    enrollment_no = db.Column(db.String(50), nullable=False)
    total_fee = db.Column(db.Float, nullable=False, default=0.0)
    paid_fee = db.Column(db.Float, nullable=False, default=0.0)
    balance_fee = db.Column(db.Float, nullable=False, default=0.0)
    payment_date = db.Column(db.String(20), nullable=False)
    payment_mode = db.Column(db.String(20), nullable=False)

class Complaint(db.Model):
    __tablename__ = 'complaints'
    id = db.Column(db.Integer, primary_key=True)
    enrollment_no = db.Column(db.String(50), nullable=False)
    complaint = db.Column(db.Text, nullable=False)
    complaint_date = db.Column(db.String(20))
    status = db.Column(db.String(20), default='Pending')

class Notice(db.Model):
    __tablename__ = 'notices'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    notice_date = db.Column(db.String(20))

class Visitor(db.Model):
    __tablename__ = 'visitors'
    id = db.Column(db.Integer, primary_key=True)
    visitor_name = db.Column(db.String(100), nullable=False)
    student_enrollment = db.Column(db.String(50), nullable=False)
    relation = db.Column(db.String(50))
    phone = db.Column(db.String(15))
    visit_date = db.Column(db.String(20))
    in_time = db.Column(db.String(20))
    out_time = db.Column(db.String(20))


# ==========================================
# 2. APPLICATION ROUTING PIPELINES
# ==========================================

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


# --- INTERFACE AUTHENTICATION ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            return redirect(url_for('dashboard'))
        
        flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/student_register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('student_register'))
            
        new_user = User(username=username, password=password, role='student')
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    return "<h2>Student Registration Page</h2><form method='POST'>Username: <input type='text' name='username'><br>Password: <input type='password' name='password'><br><button type='submit'>Register</button></form>"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# --- MULTI-ROLE CORE ROUTER INTERFACES ---

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    role = session.get('role')
    if role == 'admin':
        return render_template('admin_dashboard.html')
    elif role == 'accountant':
        return render_template('accountant_dashboard.html')
    elif role == 'warden':
        return render_template('warden_dashboard.html')
    elif role == 'student':
        return render_template('student_dashboard.html')
    
    return redirect(url_for('login'))


# --- SECURITY MANAGEMENT SYSTEM ---

@app.route('/profile')
def view_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('profile.html', user=session)

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        user = User.query.get(session['user_id'])
        if user and user.password == old_password:
            if new_password == confirm_password:
                user.password = new_password
                db.session.commit()
                flash('Password updated successfully!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('New passwords do not match!', 'danger')
        else:
            flash('Incorrect current password!', 'danger')
            
    return render_template('change_password.html')


# --- SYSTEM USERS CONFIGURATION ---

@app.route('/users')
def view_users():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    all_users = User.query.all()
    return render_template('user.html', users=all_users)


# --- REGISTERED STUDENT CONTROL PIPELINES ---

@app.route('/students')
def view_students():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    student_list = Student.query.all()
    return render_template('student.html', students=student_list)

@app.route('/add_student', methods=['POST'])
def add_student():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    new_student = Student(
        enrollment_no=request.form.get('enrollment_no'),
        name=request.form.get('name'),
        gender=request.form.get('gender'),
        course=request.form.get('course'),
        year=request.form.get('year'),
        phone=request.form.get('phone'),
        email=request.form.get('email'),
        address=request.form.get('address'),
        room_no=request.form.get('room_no'),
        guardian_name=request.form.get('guardian_name'),
        guardian_phone=request.form.get('guardian_phone'),
        admission_date=request.form.get('admission_date')
    )
    db.session.add(new_student)
    db.session.commit()
    flash('Student profile indexed successfully.', 'success')
    return redirect(url_for('view_students'))

@app.route('/delete_student/<enrollment_no>')
def delete_student(enrollment_no):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    student = Student.query.filter_by(enrollment_no=enrollment_no).first_or_404()
    db.session.delete(student)
    db.session.commit()
    flash('Student record removed from tracking registry.', 'info')
    return redirect(url_for('view_students'))


# --- IDENTITY CARD GENERATION ---

@app.route('/idcard')
@app.route('/idcard/<enrollment_no>')
def view_idcard(enrollment_no=None):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    student_record = None
    if enrollment_no:
        student_record = Student.query.filter_by(enrollment_no=enrollment_no).first()
        
    if not student_record:
        student_record = Student(
            enrollment_no="STU-SAMPLE", name="Test Student Profile", 
            course="Technical Science Engineering", room_no="A-101", phone="9999999999"
        )
        
    current_date = datetime.now().strftime("%Y-%m-%d")
    return render_template('idcard.html', student=student_record, issue_date=current_date)


# --- ROOM STRUCTURAL LOGISTICS TRACKING ---

@app.route('/rooms')
def view_rooms():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    room_list = Room.query.all()
    return render_template('rooms.html', rooms=room_list)

@app.route('/add_room', methods=['POST'])
def add_room():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    new_room = Room(
        room_no=request.form.get('room_no'),
        room_type=request.form.get('room_type'),
        capacity=int(request.form.get('capacity') or 1),
        occupied=0,
        status=request.form.get('status')
    )
    db.session.add(new_room)
    db.session.commit()
    return redirect(url_for('view_rooms'))

@app.route('/room_allocation')
def view_allocations():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    allocations = RoomAllocation.query.all()
    return render_template('room_allocation.html', allocations=allocations)

@app.route('/allocate_room', methods=['POST'])
def allocate_room():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    enrollment_no = request.form.get('enrollment_no')
    room_no = request.form.get('room_no')
    
    room = Room.query.filter_by(room_no=room_no).first()
    if room:
        room.occupied += 1
        if room.occupied >= room.capacity:
            room.status = 'Occupied'
            
    allocation = RoomAllocation(
        enrollment_no=enrollment_no,
        room_no=room_no,
        allocation_date=request.form.get('allocation_date')
    )
    
    student = Student.query.filter_by(enrollment_no=enrollment_no).first()
    if student:
        student.room_no = room_no
        
    db.session.add(allocation)
    db.session.commit()
    return redirect(url_for('view_allocations'))


# --- DAILY ATTENDANCE INTERFACES ---

@app.route('/attendance')
def view_attendance():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    attendance_list = Attendance.query.all()
    return render_template('attendance.html', attendance_list=attendance_list)

@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    attendance = Attendance(
        enrollment_no=request.form.get('enrollment_no'),
        date=request.form.get('date'),
        status=request.form.get('status')
    )
    db.session.add(attendance)
    db.session.commit()
    return redirect(url_for('view_attendance'))


# --- ACCOUNTING & FISCAL MANAGEMENT ---

@app.route('/fees')
def view_fees():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    fees_list = Fee.query.all()
    return render_template('fees.html', fees=fees_list)

@app.route('/add_fee', methods=['POST'])
def add_fee():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    enrollment_no = request.form.get('enrollment_no')
    new_fee = Fee(
        enrollment_no=enrollment_no,
        total_fee=float(request.form.get('total_fee') or 0),
        paid_fee=float(request.form.get('paid_fee') or 0),
        balance_fee=float(request.form.get('balance_fee') or 0),
        payment_date=request.form.get('payment_date'),
        payment_mode=request.form.get('payment_mode')
    )
    db.session.add(new_fee)
    db.session.commit()
    return redirect(url_for('generate_fee_receipt', enrollment_no=enrollment_no))

@app.route('/fee_receipt')
@app.route('/fee_receipt/<enrollment_no>')
def generate_fee_receipt(enrollment_no=None):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    fee_record = None
    if enrollment_no:
        fee_record = Fee.query.filter_by(enrollment_no=enrollment_no).order_by(Fee.id.desc()).first()
        
    if not fee_record:
        fee_record = Fee(enrollment_no="N/A", total_fee=0, paid_fee=0, balance_fee=0, payment_date="-", payment_mode="-")
        
    return render_template('fee_recepit.html', fee=fee_record)


# --- HELP DESK & COMPLAINT TRACKING ---

@app.route('/complaints')
def view_complaints():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    complaints_list = Complaint.query.all()
    return render_template('complaints.html', complaints=complaints_list)

@app.route('/add_complaint', methods=['POST'])
def add_complaint():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    complaint = Complaint(
        enrollment_no=request.form.get('enrollment_no'),
        complaint=request.form.get('complaint'),
        complaint_date=request.form.get('complaint_date'),
        status=request.form.get('status')
    )
    db.session.add(complaint)
    db.session.commit()
    return redirect(url_for('view_complaints'))


# --- DIGITAL BULLETIN (NOTICE) INTERFACES ---

@app.route('/notice')
def view_notices():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    notices_list = Notice.query.all()
    return render_template('notice.html', notices=notices_list)

@app.route('/add_notice', methods=['POST'])
def add_notice():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    notice = Notice(
        title=request.form.get('title'),
        description=request.form.get('description'),
        notice_date=request.form.get('notice_date')
    )
    db.session.add(notice)
    db.session.commit()
    return redirect(url_for('view_notices'))


# --- VISITOR ENTRY REGISTER ---

@app.route('/visitors')
def visitor_register():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    visitors_list = Visitor.query.all()
    return render_template('visitors.html', visitors=visitors_list)

@app.route('/add_visitor', methods=['POST'])
def add_visitor():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    visitor = Visitor(
        visitor_name=request.form.get('visitor_name'),
        student_enrollment=request.form.get('student_enrollment'),
        relation=request.form.get('relation'),
        phone=request.form.get('phone'),
        visit_date=request.form.get('visit_date'),
        in_time=request.form.get('in_time'),
        out_time=request.form.get('out_time')
    )
    db.session.add(visitor)
    db.session.commit()
    return redirect(url_for('visitor_register'))


# --- BUSINESS REPORTS & LEDGERS ---

@app.route('/reports')
def financial_reports():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    total_students = Student.query.count()
    total_rooms = Room.query.count()
    total_complaints = Complaint.query.count()
    
    all_fees = Fee.query.all()
    total_fees = sum(f.paid_fee for f in all_fees)
    
    return render_template(
        'reports.html', 
        total_students=total_students, 
        total_rooms=total_rooms, 
        total_fees=total_fees, 
        total_complaints=total_complaints
    )


# --- SYSTEM ERROR ROUTING ---

@app.route('/unauthorized')
def unauthorized():
    return render_template('unauthorized.html'), 401

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# ==========================================
# 3. SCHEMA COMPILATION & SEED ENGINE
# ==========================================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Seed core default logins
        if not User.query.filter_by(username='admin').first():
            db.session.add(User(username='admin', password='admin123', role='admin'))
            
        if not User.query.filter_by(username='accountant').first():
            db.session.add(User(username='accountant', password='acc123', role='accountant'))

        if not User.query.filter_by(username='student').first():
            db.session.add(User(username='student', password='student123', role='student'))

        if not User.query.filter_by(username='warden').first():
            db.session.add(User(username='warden', password='warden123', role='warden'))
            
        db.session.commit()
        print("--> ERP Database initialized. Baseline user nodes structurally seeded.")

    app.run(debug=True)
