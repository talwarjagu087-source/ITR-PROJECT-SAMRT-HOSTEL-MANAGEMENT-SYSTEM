from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "hostel_secret_key"


def get_db_connection():
    conn = sqlite3.connect("hostel.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def login():
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def check_login():

    username = request.form['username']
    password = request.form['password']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    )

    user = cursor.fetchone()
    conn.close()

    if user:

        session['username'] = user['username']
        session['role'] = user['role']

        if user['role'] == 'Admin':
            return redirect('/admin_dashboard')

        elif user['role'] == 'Warden':
            return redirect('/warden_dashboard')

        elif user['role'] == 'Accountant':
            return redirect('/accountant_dashboard')

        elif user['role'] == 'Student':
            return redirect('/student_dashboard')

    return "Invalid Username or Password"

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'role' not in session:
        return redirect('/')

    if session['role'] != 'Admin':
        return render_template('unauthorized.html')

    return render_template('admin_dashboard.html')


@app.route('/warden_dashboard')
def warden_dashboard():
    if 'role' not in session:
        return redirect('/')

    if session['role'] != 'Warden':
        return render_template('unauthorized.html')

    return render_template('warden_dashboard.html')


@app.route('/accountant_dashboard')
def accountant_dashboard():
    if 'role' not in session:
        return redirect('/')

    if session['role'] != 'Accountant':
        return render_template('unauthorized.html')

    return render_template('accountant_dashboard.html')


@app.route('/student_dashboard')
def student_dashboard():
    if 'role' not in session:
        return redirect('/')

    if session['role'] != 'Student':
        return render_template('unauthorized.html')

    return render_template('student_dashboard.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404

@app.route('/students')
def students():

    if 'role' not in session:
        return redirect('/')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    conn.close()

    return render_template("student.html", students=students)

@app.route('/add_student', methods=['POST'])
def add_student():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO students(
            enrollment_no,
            name,
            gender,
            course,
            year,
            phone,
            email,
            address,
            room_no,
            guardian_name,
            guardian_phone,
            admission_date
        )
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
    """,
    (
        request.form['enrollment_no'],
        request.form['name'],
        request.form['gender'],
        request.form['course'],
        request.form['year'],
        request.form['phone'],
        request.form['email'],
        request.form['address'],
        request.form['room_no'],
        request.form['guardian_name'],
        request.form['guardian_phone'],
        request.form['admission_date']
    ))

    conn.commit()
    conn.close()

    return redirect('/students')

@app.route('/rooms')
def rooms():

    if 'role' not in session:
        return redirect('/')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM rooms")
    rooms = cursor.fetchall()

    conn.close()

    return render_template("rooms.html", rooms=rooms)

@app.route('/add_room', methods=['POST'])
def add_room():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO rooms(
            room_no,
            room_type,
            capacity,
            occupied,
            status
        )
        VALUES(?,?,?,?,?)
    """,
    (
        request.form['room_no'],
        request.form['room_type'],
        request.form['capacity'],
        0,
        request.form['status']
    ))

    conn.commit()
    conn.close()

    return redirect('/rooms')


@app.route('/room_allocation')
def room_allocation():

    if 'role' not in session:
        return redirect('/')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM room_allocation")
    allocations = cursor.fetchall()

    conn.close()

    return render_template(
        "room_allocation.html",
        allocations=allocations
    )


@app.route('/allocate_room', methods=['POST'])
def allocate_room():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO room_allocation(
            enrollment_no,
            room_no,
            allocation_date
        )
        VALUES(?,?,?)
    """,
    (
        request.form['enrollment_no'],
        request.form['room_no'],
        request.form['allocation_date']
    ))

    cursor.execute("""
        UPDATE rooms
        SET occupied = occupied + 1
        WHERE room_no=?
    """,
    (request.form['room_no'],))

    conn.commit()
    conn.close()

    return redirect('/room_allocation')

@app.route('/attendance')
def attendance():

    if 'role' not in session:
        return redirect('/')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM attendance")
    attendance_list = cursor.fetchall()

    conn.close()

    return render_template(
        "attendance.html",
        attendance_list=attendance_list
    )


@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO attendance(
        enrollment_no,
        date,
        status
    )
    VALUES(?,?,?)
    """,
    (
        request.form['enrollment_no'],
        request.form['date'],
        request.form['status']
    ))

    conn.commit()
    conn.close()

    return redirect('/attendance')

@app.route('/fees')
def fees():

    if 'role' not in session:
        return redirect('/')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM fees")
    fees = cursor.fetchall()

    conn.close()

    return render_template("fees.html", fees=fees)


@app.route('/add_fee', methods=['POST'])
def add_fee():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO fees(
        enrollment_no,
        total_fee,
        paid_fee,
        balance_fee,
        payment_date,
        payment_mode
    )
    VALUES(?,?,?,?,?,?)
    """,
    (
        request.form['enrollment_no'],
        request.form['total_fee'],
        request.form['paid_fee'],
        request.form['balance_fee'],
        request.form['payment_date'],
        request.form['payment_mode']
    ))

    conn.commit()
    conn.close()

    return redirect('/fees')

@app.route('/complaints')
def complaints():

    if 'role' not in session:
        return redirect('/')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM complaints")
    complaints = cursor.fetchall()

    conn.close()

    return render_template(
        "complaints.html",
        complaints=complaints
    )


@app.route('/add_complaint', methods=['POST'])
def add_complaint():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO complaints(
        enrollment_no,
        complaint,
        complaint_date,
        status
    )
    VALUES(?,?,?,?)
    """,
    (
        request.form['enrollment_no'],
        request.form['complaint'],
        request.form['complaint_date'],
        request.form['status']
    ))

    conn.commit()
    conn.close()

    return redirect('/complaints')

@app.route('/notice')
def notice():

    if 'role' not in session:
        return redirect('/')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM notices")
    notices = cursor.fetchall()

    conn.close()

    return render_template("notice.html", notices=notices)


@app.route('/add_notice', methods=['POST'])
def add_notice():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO notices(
        title,
        description,
        notice_date
    )
    VALUES(?,?,?)
    """,
    (
        request.form['title'],
        request.form['description'],
        request.form['notice_date']
    ))

    conn.commit()
    conn.close()

    return redirect('/notice')

@app.route('/reports')
def reports():

    if 'role' not in session:
        return redirect('/')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM rooms")
    total_rooms = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(paid_fee) FROM fees")
    total_fees = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM complaints")
    total_complaints = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "reports.html",
        total_students=total_students,
        total_rooms=total_rooms,
        total_fees=total_fees,
        total_complaints=total_complaints
    )

@app.route('/profile')
def profile():

    if 'username' not in session:
        return redirect('/')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=?",
        (session['username'],)
    )

    user = cursor.fetchone()

    conn.close()

    return render_template(
        "profile.html",
        user=user
    )

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():

    if 'username' not in session:
        return redirect('/')

    if request.method == 'POST':

        new_password = request.form['new_password']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE users SET password=? WHERE username=?",
            (new_password, session['username'])
        )

        conn.commit()
        conn.close()

        return redirect('/profile')

    return render_template("change_password.html")

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO users(
            username,
            password,
            role
        )
        VALUES(?,?,?)
        """,
        (
            request.form['username'],
            request.form['password'],
            request.form['role']
        ))

        conn.commit()
        conn.close()

        return redirect('/user')

    return render_template("register.html")

@app.route('/idcard/<enrollment_no>')
def idcard(enrollment_no):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE enrollment_no=?",
        (enrollment_no,)
    )

    student = cursor.fetchone()

    conn.close()

    return render_template(
        "idcard.html",
        student=student,
        issue_date="2026-06-27"
    )

@app.route('/fee_receipt/<enrollment_no>')
def fee_receipt(enrollment_no):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM fees WHERE enrollment_no=?",
        (enrollment_no,)
    )

    fee = cursor.fetchone()

    conn.close()

    return render_template(
        "fee_receipt.html",
        fee=fee
    )