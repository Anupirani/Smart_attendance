# 📚 Smart Attendance Management System

A desktop-based **Smart Attendance Management System** built with Python and Tkinter.

The application allows teachers or administrators to register students, mark attendance for multiple students at once, prevent duplicate attendance, view attendance statistics, search records, and export attendance data to CSV.

---

## ✨ Features

### 👨‍🎓 Student Management

- Add students individually
- Import multiple students from a CSV file
- Store:
  - Student ID
  - Student Name
  - Class
  - Email
- Search students
- View all registered students

### ✅ Smart Attendance

- Mark attendance for a single student or multiple students
- Paste multiple Student IDs at once
- Supports:
  - One ID per line
  - Comma-separated IDs
  - Space-separated IDs
  - Semicolon-separated IDs
  - Excel/tab-separated IDs
- Prevents duplicate attendance on the same day
- Automatically records the current date and time
- Identifies students who are not registered

### 📊 Dashboard

The dashboard displays:

- Total number of students
- Students present today
- Students absent today
- Attendance percentage
- Today's attendance records

### 📋 Attendance Records

- View all attendance records
- View today's attendance
- Search attendance by Student ID
- Export attendance records to CSV

### 💾 Database

The application uses **SQLite** for persistent data storage.

The database is automatically created when the application starts.

---

## 🖥️ Application Preview

The application contains four main sections:

```text
┌─────────────────────────────────────────────────────┐
│             SMART ATTENDANCE SYSTEM                 │
├─────────────────────────────────────────────────────┤
│ Dashboard │ Mark Attendance │ Students │ Records    │
├─────────────────────────────────────────────────────┤
│                                                     │
│                 Dashboard                           │
│                                                     │
│  Total       Present       Absent       Attendance  │
│    50           43            7            86%      │
│                                                     │
│              Today's Attendance                     │
│                                                     │
└─────────────────────────────────────────────────────┘
