from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import date

app = Flask(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO students (name) VALUES (?)", (name,))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_student.html')

@app.route('/mark_attendance', methods=['GET', 'POST'])
def mark_attendance():
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    if request.method == 'POST':
        for student_id, status in request.form.items():
            cursor.execute(
                "INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)",
                (student_id, str(date.today()), status)
            )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    conn.close()
    return render_template('mark_attendance.html', students=students)

@app.route('/view_report')
def view_report():
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT students.name, 
               COUNT(CASE WHEN attendance.status = 'Present' THEN 1 END) AS presents,
               COUNT(CASE WHEN attendance.status = 'Absent' THEN 1 END) AS absents
        FROM students
        LEFT JOIN attendance ON students.id = attendance.student_id
        GROUP BY students.id
    ''')
    report = cursor.fetchall()
    conn.close()
    return render_template('view_report.html', report=report)

if __name__ == '__main__':
    app.run(debug=True)
