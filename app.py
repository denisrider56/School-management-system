from flask import Flask, render_template, request, redirect, session
import pyodbc
import os

app = Flask(__name__)
app.secret_key = "super_secret_key"

# -------- DATABASE CONNECTION --------
DB_PATH = os.path.join(os.getcwd(), "School.accdb")

conn = pyodbc.connect(
    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
    rf'DBQ={DB_PATH};'
)
cursor = conn.cursor()


# -------- LOGIN --------
@app.route('/')
def home():
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == "D-TECH SYSTEMS" and password == "07813660":
            session['user'] = username
            return redirect('/dashboard')
        else:
            error = "Invalid credentials"

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# -------- DASHBOARD --------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    cursor.execute("SELECT COUNT(*) FROM Students")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM (SELECT DISTINCT Class FROM Students)")
    total_classes = cursor.fetchone()[0]

    return render_template(
        'dashboard.html',
        total_students=total_students,
        total_classes=total_classes
    )


# -------- STUDENTS --------
@app.route('/students')
def students():
    if 'user' not in session:
        return redirect('/login')

    cursor.execute("SELECT * FROM Students ORDER BY ID")
    rows = cursor.fetchall()

    students = []
    for row in rows:
        students.append({
            'ID': row[0],
            'Name': row[1],
            'Class': row[2],
            'Age': row[3]
        })

    return render_template('students.html', students=students)


# -------- ADD STUDENT --------
@app.route('/add_student', methods=['POST'])
def add_student():
    name = request.form.get('name')
    class_name = request.form.get('class')
    age = request.form.get('age')

    cursor.execute(
        "INSERT INTO Students (Name, Class, Age) VALUES (?, ?, ?)",
        (name, class_name, age)
    )
    conn.commit()

    return redirect('/students')


# -------- EDIT STUDENT --------
@app.route('/edit_student/<int:id>')
def edit_student(id):
    cursor.execute("SELECT * FROM Students WHERE ID=?", (id,))
    row = cursor.fetchone()

    student = {
        'ID': row[0],
        'Name': row[1],
        'Class': row[2],
        'Age': row[3]
    }

    return render_template('edit_student.html', student=student)


# -------- UPDATE STUDENT --------
@app.route('/update_student/<int:id>', methods=['POST'])
def update_student(id):
    name = request.form.get('name')
    class_name = request.form.get('class')
    age = request.form.get('age')

    cursor.execute(
        "UPDATE Students SET Name=?, Class=?, Age=? WHERE ID=?",
        (name, class_name, age, id)
    )
    conn.commit()

    return redirect('/students')


# -------- DELETE STUDENT --------
@app.route('/delete_student/<int:id>')
def delete_student(id):
    cursor.execute("DELETE FROM Students WHERE ID=?", (id,))
    conn.commit()
    return redirect('/students')


if __name__ == '__main__':
    app.run(debug=True)