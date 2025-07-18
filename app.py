from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, session
import base64, cv2, numpy as np, csv, os
from io import BytesIO
from fpdf import FPDF
from recognizer.face_utilits import (
    ensure_db, save_student, get_embedding, reset_students_table,
    load_students, mark_attendance, get_all_classes, add_class, remove_class
)
from recognizer.reset_snapshots import run as reset_snapshots
from recognizer.reset_csv import run as reset_csv
from recognizer.recognize import recognize_frame_by_class
from config import SNAPSHOT_DIR

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def index():
    students = load_students()
    classes = get_all_classes()
    students_by_class = {}
    for student in students:
        class_name = student[2]
        students_by_class.setdefault(class_name, []).append(student)
    return render_template('index.html', students_by_class=students_by_class, classes=classes)

@app.route('/students')
def students():
    students = load_students()
    classes = get_all_classes()
    return render_template('students.html', students=students, classes=classes)

@app.route('/students_db')
def students_db():
    selected_class = request.args.get('class', 'All')
    classes = get_all_classes()
    students = load_students()
    if selected_class != 'All':
        students = [s for s in students if s[2] == selected_class]
    return render_template('students_db.html', students=students, classes=classes, selected_class=selected_class)


@app.route('/students_db/pdf')
def students_db_pdf():
    selected_class = request.args.get('class', 'All')
    students = load_students()
    if selected_class != 'All':
        students = [s for s in students if s[2] == selected_class]
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    title = f"Student Database: {selected_class}" if selected_class != 'All' else "Student Database: All"
    pdf.cell(0, 10, title, ln=True, align='C')
    pdf.ln(5)
    col_width = pdf.w / 4
    headers = ["ID", "Name", "Class"]
    for header in headers:
        pdf.cell(col_width, 10, header, border=1)
    pdf.ln()
    if not students:
        pdf.cell(col_width * len(headers), 10, "No students found.", border=1)
        pdf.ln()
    else:
        for row in students:
            for item in row:
                pdf.cell(col_width, 10, str(item), border=1)
            pdf.ln()
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    pdf_output = BytesIO(pdf_bytes)
    pdf_output.seek(0)
    pdf_name = f"students_db_{selected_class}.pdf" if selected_class != 'All' else "students_db_all.pdf"
    return send_file(pdf_output, as_attachment=True, download_name=pdf_name, mimetype='application/pdf')



@app.route('/add_student', methods=['GET', 'POST'])
def add_student_route():
    classes = get_all_classes()
    selected_class = session.get('selected_class', classes[0] if classes else '')
    if request.method == 'POST':
        data = request.get_json()
        name = data['name']
        class_name = data['class_name']
        session['selected_class'] = class_name
        image_data = data['image'].split(",")[1]
        img_bytes = base64.b64decode(image_data)
        img_array = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        embedding = get_embedding(frame)
        if embedding is not None:
            save_student(name, class_name, embedding)
            os.makedirs(SNAPSHOT_DIR, exist_ok=True)
            cv2.imwrite(os.path.join(SNAPSHOT_DIR, f"{name}.jpg"), frame)
            return jsonify({'status': 'Student added!'})
        else:
            return jsonify({'status': 'Face not found!'})
    return render_template('add_student.html', classes=classes, selected_class=selected_class)

@app.route('/recognize', methods=['GET', 'POST'])
def recognize():
    classes = get_all_classes()
    selected_class = session.get('selected_class', classes[0] if classes else '')
    if request.method == 'POST':
        data = request.get_json()
        class_name = data.get('class_name', '').strip()
        session['selected_class'] = class_name
        image_data = data['image'].split(",")[1]
        img_bytes = base64.b64decode(image_data)
        img_array = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        result = recognize_frame_by_class(frame, class_name)
        return jsonify({'status': result})
    return render_template('recognize.html', classes=classes, selected_class=selected_class)

@app.route('/manage_classes', methods=['GET', 'POST'])
def manage_classes():
    message = ''
    if request.method == 'POST':
        if 'add' in request.form:
            add_class(request.form['class_name'].strip())
            message = 'Class added!'
        elif 'remove' in request.form:
            remove_class(request.form['remove_class'])
            message = 'Class removed!'
    classes = get_all_classes()
    return render_template('manage_classes.html', classes=classes, message=message)

@app.route('/reset_db')
def reset_db():
    reset_students_table()
    flash("Student database has been cleared!")
    return redirect(url_for('index'))

@app.route('/reset_snapshots')
def reset_photos():
    reset_snapshots()
    flash("Snapshots folder has been cleared!")
    return redirect(url_for('index'))

@app.route('/reset_csv')
def reset_csv_route():
    reset_csv()
    flash("Attendance CSV has been reset!")
    return redirect(url_for('index'))

@app.route('/attendance')
def attendance():
    selected_class = request.args.get('class', 'All')
    attendance_list = []
    headers = ["Name", "Class", "Date", "Time"]
    classes = get_all_classes()
    if os.path.exists('database/attendance.csv'):
        with open('database/attendance.csv', newline='') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader, headers)
            for row in reader:
                if len(row) >= 4:
                    if selected_class == 'All' or row[1] == selected_class:
                        attendance_list.append(row)
    return render_template('attendance.html', attendance=attendance_list, headers=headers, classes=classes, selected_class=selected_class)

@app.route('/attendance/pdf')
def attendance_pdf():
    selected_class = request.args.get('class', 'All')
    attendance_list = []
    headers = ["Name", "Class", "Date", "Time"]
    if os.path.exists('database/attendance.csv'):
        with open('database/attendance.csv', newline='') as csvfile:
            reader = csv.reader(csvfile)
            headers_from_file = next(reader, None)
            for row in reader:
                if len(row) >= 4 and (selected_class == 'All' or row[1] == selected_class):
                    attendance_list.append(row)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    title = f"Attendance Report: {selected_class}" if selected_class != 'All' else "Attendance Report: All"
    pdf.cell(0, 10, title, ln=True, align='C')
    pdf.ln(5)
    col_width = pdf.w / (len(headers) + 1)
    for header in headers:
        pdf.cell(col_width, 10, header, border=1)
    pdf.ln()
    if not attendance_list:
        pdf.cell(col_width * len(headers), 10, "No attendance records found.", border=1)
        pdf.ln()
    else:
        for row in attendance_list:
            for item in row:
                pdf.cell(col_width, 10, str(item), border=1)
            pdf.ln()
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    pdf_output = BytesIO(pdf_bytes)
    pdf_output.seek(0)
    pdf_name = f"attendance_{selected_class}.pdf" if selected_class != 'All' else "attendance_all.pdf"
    return send_file(pdf_output, as_attachment=True, download_name=pdf_name, mimetype='application/pdf')

if __name__ == '__main__':
    ensure_db()
    app.run(debug=True)
