# 📚 Attendance Management System

A web-based **Attendance Management System** built with **Python and Flask** for managing students, recording attendance, and viewing attendance statistics through a clean and responsive web interface.

The system provides a teacher-focused dashboard with authentication, student management, attendance recording, attendance filtering, and database-backed record management.

---

## ✨ Features

### 🔐 Teacher Authentication

- Secure teacher login system
- Session-based authentication using Flask-Login
- Password hashing using Werkzeug
- Protected application routes
- Logout functionality
- Demo teacher account for local testing

### 👥 Student Management

- Add new students
- View all registered students
- Edit student information
- Delete students
- Unique roll number validation
- Store student name, roll number, class, and section
- Automatically remove associated attendance records when a student is deleted

### 📝 Attendance Management

- Mark attendance for multiple students
- Record attendance by date
- Record attendance by subject
- Mark students as:
  - ✅ Present
  - ❌ Absent
- Prevent duplicate attendance records for the same student, date, and subject
- Update existing attendance records when attendance is submitted again

### 📊 Dashboard & Analytics

The dashboard provides a quick overview of the attendance system, including:

- Total number of students
- Today's attendance records
- Number of students present today
- Overall attendance percentage
- Quick access to student and attendance management

### 🔎 Attendance Filtering

Attendance records can be filtered by:

- Subject
- Date
- Attendance status

The system also provides a reset option to clear the applied filters.

### 🎨 User Interface

- Clean and modern web interface
- Responsive layout
- Reusable Jinja2 templates
- Shared navigation and page structure
- Responsive tables
- Interactive forms
- Flash messages for system feedback
- Mobile-friendly layouts

---

## 🛠️ Technology Stack

| Technology | Purpose |
|------------|---------|
| Python | Backend programming |
| Flask | Web application framework |
| Flask-SQLAlchemy | Database ORM |
| Flask-Login | Authentication and session management |
| Werkzeug | Password hashing and security utilities |
| SQLAlchemy | Database interaction |
| SQLite | Local database |
| HTML5 | Frontend structure |
| CSS3 | Frontend styling |
| Jinja2 | Server-side templating |

---

## 🏗️ Application Architecture

The application follows a simple Flask-based web architecture:

```text
                    ┌──────────────────┐
                    │     Browser      │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Flask Routes    │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
       Authentication    Students       Attendance
              │              │              │
              └──────────────┼──────────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ SQLAlchemy ORM   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ SQLite Database   │
                    └──────────────────┘
