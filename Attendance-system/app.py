from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
import os

# ============================================================================
# APPLICATION CONFIGURATION
# ============================================================================

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Initialize login manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# ============================================================================
# DATABASE MODELS
# ============================================================================

class User(db.Model):
    """Teacher/User model for authentication"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='teacher')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


class Student(db.Model):
    """Student model for storing student information"""
    id = db.Column(db.Integer, primary_key=True)
    roll_number = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    class_name = db.Column(db.String(20), nullable=False)
    section = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship with Attendance
    attendances = db.relationship('Attendance', backref='student', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Student {self.roll_number} - {self.name}>'


class Attendance(db.Model):
    """Attendance model for tracking student attendance"""
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(10), nullable=False)  # 'Present' or 'Absent'
    subject = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Attendance {self.student.name} - {self.date} - {self.status}>'


# ============================================================================
# USER LOADER FOR FLASK-LOGIN
# ============================================================================

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ============================================================================
# ROUTES - PUBLIC
# ============================================================================

@app.route('/')
def index():
    """Home page - redirects to dashboard if logged in"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Teacher login page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome back, {user.full_name}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# ============================================================================
# ROUTES - DASHBOARD
# ============================================================================

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard with attendance statistics"""
    total_students = Student.query.count()
    
    # Today's attendance
    today = date.today()
    today_attendance = Attendance.query.filter_by(date=today).count()
    
    # Present count today
    present_today = Attendance.query.filter_by(date=today, status='Present').count()
    
    # Attendance percentage (overall)
    total_attendance = Attendance.query.count()
    total_present = Attendance.query.filter_by(status='Present').count()
    attendance_percentage = round((total_present / total_attendance * 100) if total_attendance > 0 else 0, 2)
    
    return render_template(
        'dashboard.html',
        total_students=total_students,
        today_attendance=today_attendance,
        present_today=present_today,
        attendance_percentage=attendance_percentage
    )


# ============================================================================
# ROUTES - STUDENT MANAGEMENT
# ============================================================================

@app.route('/add_student', methods=['GET', 'POST'])
@login_required
def add_student():
    """Add a new student"""
    if request.method == 'POST':
        roll_number = request.form.get('roll_number')
        name = request.form.get('name')
        class_name = request.form.get('class_name')
        section = request.form.get('section')

        # Check if student already exists
        existing = Student.query.filter_by(roll_number=roll_number).first()
        if existing:
            flash(f'Student with roll number {roll_number} already exists.', 'warning')
            return redirect(url_for('add_student'))

        # Create new student
        student = Student(
            roll_number=roll_number,
            name=name,
            class_name=class_name,
            section=section
        )
        db.session.add(student)
        db.session.commit()

        flash(f'Student {name} added successfully!', 'success')
        return redirect(url_for('view_students'))

    return render_template('add_student.html')


@app.route('/view_students')
@login_required
def view_students():
    """View all students with edit/delete options"""
    students = Student.query.order_by(Student.roll_number).all()
    return render_template('view_students.html', students=students)


@app.route('/edit_student/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_student(id):
    """Edit student details"""
    student = Student.query.get_or_404(id)

    if request.method == 'POST':
        student.roll_number = request.form.get('roll_number')
        student.name = request.form.get('name')
        student.class_name = request.form.get('class_name')
        student.section = request.form.get('section')

        db.session.commit()
        flash('Student updated successfully!', 'success')
        return redirect(url_for('view_students'))

    return render_template('edit_student.html', student=student)


@app.route('/delete_student/<int:id>')
@login_required
def delete_student(id):
    """Delete student (cascades to attendance records)"""
    student = Student.query.get_or_404(id)
    
    # Check if student has attendance records
    attendance_count = Attendance.query.filter_by(student_id=id).count()
    
    db.session.delete(student)
    db.session.commit()
    
    flash(f'Student {student.name} deleted successfully! ({attendance_count} attendance records removed)', 'success')
    return redirect(url_for('view_students'))


# ============================================================================
# ROUTES - ATTENDANCE MANAGEMENT
# ============================================================================

@app.route('/take_attendance', methods=['GET', 'POST'])
@login_required
def take_attendance():
    """Mark attendance for all students"""
    students = Student.query.order_by(Student.roll_number).all()

    if request.method == 'POST':
        subject = request.form.get('subject')
        attendance_date = request.form.get('date')
        
        if not subject:
            flash('Please enter a subject.', 'warning')
            return render_template('take_attendance.html', students=students)

        # Parse date
        if attendance_date:
            att_date = datetime.strptime(attendance_date, '%Y-%m-%d').date()
        else:
            att_date = date.today()

        # Check if attendance already exists for this date
        for student in students:
            status = request.form.get(f'attendance_{student.id}')
            if status:
                # Check if attendance already exists
                existing = Attendance.query.filter_by(
                    student_id=student.id,
                    date=att_date,
                    subject=subject
                ).first()
                
                if existing:
                    existing.status = status
                else:
                    attendance = Attendance(
                        student_id=student.id,
                        date=att_date,
                        status=status,
                        subject=subject
                    )
                    db.session.add(attendance)

        db.session.commit()
        flash(f'Attendance for {att_date} marked successfully!', 'success')
        return redirect(url_for('view_attendance'))

    return render_template('take_attendance.html', students=students)


@app.route('/view_attendance')
@login_required
def view_attendance():
    """View attendance records with filters"""
    # Get all distinct subjects and dates for filtering
    subjects = db.session.query(Attendance.subject).distinct().all()
    dates = db.session.query(Attendance.date).distinct().order_by(Attendance.date.desc()).limit(30).all()
    
    # Get filter parameters
    filter_subject = request.args.get('subject', '')
    filter_date = request.args.get('date', '')
    filter_status = request.args.get('status', '')
    
    # Build query
    query = Attendance.query.join(Student)
    
    if filter_subject:
        query = query.filter(Attendance.subject == filter_subject)
    if filter_date:
        query = query.filter(Attendance.date == datetime.strptime(filter_date, '%Y-%m-%d').date())
    if filter_status:
        query = query.filter(Attendance.status == filter_status)
    
    records = query.order_by(Attendance.date.desc(), Student.roll_number).all()
    
    return render_template(
        'view_attendance.html',
        records=records,
        subjects=subjects,
        dates=dates,
        filter_subject=filter_subject,
        filter_date=filter_date,
        filter_status=filter_status
    )


# ============================================================================
# MAIN APPLICATION ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
        
        # Create default teacher account if it doesn't exist
        if not User.query.filter_by(username='teacher').first():
            teacher = User(
                username='teacher',
                full_name='Teacher',
                role='teacher'
            )
            teacher.set_password('teacher123')
            db.session.add(teacher)
            db.session.commit()
            print('Default teacher account created: teacher / teacher123')

    app.run(debug=True, host='127.0.0.1', port=5000)
