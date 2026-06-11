from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import os

app = Flask(__name__)

from prometheus_flask_exporter import PrometheusMetrics
metrics = PrometheusMetrics(app)


def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.environ.get("DB_NAME", "studentresults"),
        user=os.environ.get("DB_USER", "studentuser"),
        password=os.environ.get("DB_PASS", "studentpass"),
        host=os.environ.get("DB_HOST", "db")
    )
    return conn

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/check', methods=['GET', 'POST'])
def check():
    results = None
    error = None
    if request.method == 'POST':
        student_id = request.form['student_id']
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                "SELECT name, subject, score, grade, term, year FROM results WHERE student_id = %s",
                (student_id,)
            )
            results = cur.fetchall()
            cur.close()
            conn.close()
            if not results:
                error = "No results found for this Student ID!"
        except Exception as e:
            error = "Database error. Please try again!"
    return render_template('check.html', results=results, error=error)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    success = None
    if request.method == 'POST':
        student_id = request.form['student_id']
        name = request.form['name']
        subject = request.form['subject']
        score = int(request.form['score'])
        term = request.form['term']
        year = request.form['year']

        if score >= 70:
            grade = 'A'
        elif score >= 60:
            grade = 'B'
        elif score >= 50:
            grade = 'C'
        elif score >= 45:
            grade = 'D'
        else:
            grade = 'F'

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO results (student_id, name, subject, score, grade, term, year) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (student_id, name, subject, score, grade, term, year)
        )
        conn.commit()
        cur.close()
        conn.close()
        success = f"Result for {name} added successfully!"
    return render_template('admin.html', success=success)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
