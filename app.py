
import random
from datetime import date

from flask import Flask, render_template, request, redirect, url_for, flash

from database import get_connection, init_db, CAMPUSES

app = Flask(__name__)
app.secret_key = "uc-ict-congress-secret-key"  # needed for flash messages


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/registration")
def registration():
    conn = get_connection()
    students = conn.execute(
        "SELECT * FROM Registration ORDER BY idNum"
    ).fetchall()
    conn.close()
    return render_template("registration.html", students=students)


@app.route("/registration/add", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        idNum = request.form["idNum"].strip()
        campus = request.form["campus"]
        studFName = request.form["studFName"].strip()
        studLName = request.form["studLName"].strip()
        amountPaid = request.form["amountPaid"].strip()

        if not idNum or not studFName or not studLName or not amountPaid:
            flash("Please fill in all fields.", "error")
            return render_template("student_form.html", mode="add", form=request.form)

        conn = get_connection()
        existing = conn.execute(
            "SELECT idNum FROM Registration WHERE idNum = ?", (idNum,)
        ).fetchone()
        if existing:
            conn.close()
            flash(f"Student ID {idNum} is already registered.", "error")
            return render_template("student_form.html", mode="add", form=request.form)

        conn.execute(
            """
            INSERT INTO Registration (idNum, campus, studFName, studLName, amountPaid, attended)
            VALUES (?, ?, ?, ?, ?, 'No')
            """,
            (idNum, campus, studFName, studLName, float(amountPaid)),
        )
        conn.commit()
        conn.close()
        flash(f"Student {studFName} {studLName} registered successfully.", "success")
        return redirect(url_for("registration"))

    return render_template("student_form.html", mode="add", form={})


@app.route("/registration/edit/<idNum>", methods=["GET", "POST"])
def edit_student(idNum):
    conn = get_connection()
    student = conn.execute(
        "SELECT * FROM Registration WHERE idNum = ?", (idNum,)
    ).fetchone()

    if student is None:
        conn.close()
        flash("Student record not found.", "error")
        return redirect(url_for("registration"))

    if request.method == "POST":
        campus = request.form["campus"]
        studFName = request.form["studFName"].strip()
        studLName = request.form["studLName"].strip()
        amountPaid = request.form["amountPaid"].strip()

        conn.execute(
            """
            UPDATE Registration
            SET campus = ?, studFName = ?, studLName = ?, amountPaid = ?
            WHERE idNum = ?
            """,
            (campus, studFName, studLName, float(amountPaid), idNum),
        )
        conn.commit()
        conn.close()
        flash(f"Student {idNum} updated successfully.", "success")
        return redirect(url_for("registration"))

    conn.close()
    return render_template("student_form.html", mode="edit", form=student)


@app.route("/registration/delete/<idNum>", methods=["POST"])
def delete_student(idNum):
    conn = get_connection()
    conn.execute("DELETE FROM Registration WHERE idNum = ?", (idNum,))
    conn.commit()
    conn.close()
    flash(f"Student {idNum} removed from the registration list.", "success")
    return redirect(url_for("registration"))


@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    message = None
    message_type = None
    checked_student = None

    if request.method == "POST":
        idNum = request.form.get("idNum", "").strip()
        conn = get_connection()
        student = conn.execute(
            "SELECT * FROM Registration WHERE idNum = ?", (idNum,)
        ).fetchone()

        if student is None:
            message = f'ID # {idNum} is NOT YET REGISTERED.'
            message_type = "error"
        elif student["attended"] == "Yes":
            message = f"Student's Attendance RECORD ALREADY EXISTS."
            message_type = "warning"
            checked_student = student
        else:
            conn.execute(
                "UPDATE Registration SET attended = 'Yes' WHERE idNum = ?", (idNum,)
            )
            conn.commit()
            message = "Student Attendance is SUCCESSFULLY RECORDED."
            message_type = "success"
            checked_student = conn.execute(
                "SELECT * FROM Registration WHERE idNum = ?", (idNum,)
            ).fetchone()
        conn.close()

    conn = get_connection()
    attendees = conn.execute(
        "SELECT * FROM Registration WHERE attended = 'Yes' ORDER BY idNum"
    ).fetchall()
    conn.close()

    return render_template(
        "attendance.html",
        message=message,
        message_type=message_type,
        checked_student=checked_student,
        attendees=attendees,
    )



@app.route("/raffle", methods=["GET", "POST"])
def raffle():
    selected_campuses = request.form.getlist("campus") if request.method == "POST" else CAMPUSES[:]
    winner = None
    error = None

    if request.method == "POST" and "reveal" in request.form:
        if not selected_campuses:
            error = "Please select at least one campus filter."
        else:
            conn = get_connection()
            placeholders = ",".join("?" for _ in selected_campuses)
            candidates = conn.execute(
                f"""
                SELECT * FROM Registration
                WHERE attended = 'Yes' AND campus IN ({placeholders})
                """,
                selected_campuses,
            ).fetchall()
            conn.close()

            if not candidates:
                error = "No eligible (attended) students found for the selected campus filter."
            else:
                winner = random.choice(candidates)

    return render_template(
        "raffle.html",
        campuses=CAMPUSES,
        selected_campuses=selected_campuses,
        winner=winner,
        error=error,
    )



@app.route("/report/campus", methods=["GET", "POST"])
def report_campus():
    selected_campuses = request.form.getlist("campus") if request.method == "POST" else []
    rows = []
    generated = False
    total_collection = 0
    num_registrants = 0
    num_attendees = 0

    if request.method == "POST":
        generated = True
        conn = get_connection()
        if selected_campuses:
            placeholders = ",".join("?" for _ in selected_campuses)
            rows = conn.execute(
                f"SELECT * FROM Registration WHERE campus IN ({placeholders}) ORDER BY idNum",
                selected_campuses,
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM Registration ORDER BY idNum").fetchall()
        conn.close()

        num_registrants = len(rows)
        total_collection = sum(r["amountPaid"] for r in rows)
        num_attendees = sum(1 for r in rows if r["attended"] == "Yes")

    return render_template(
        "report_campus.html",
        campuses=CAMPUSES,
        selected_campuses=selected_campuses,
        rows=rows,
        generated=generated,
        total_collection=total_collection,
        num_registrants=num_registrants,
        num_attendees=num_attendees,
        today=date.today().strftime("%m/%d/%Y"),
    )



@app.route("/report/summary")
def report_summary():
    conn = get_connection()
    summary = []
    total_registered = 0
    total_attended = 0
    total_collection = 0

    for campus in CAMPUSES:
        registered = conn.execute(
            "SELECT COUNT(*) AS c FROM Registration WHERE campus = ?", (campus,)
        ).fetchone()["c"]
        attended = conn.execute(
            "SELECT COUNT(*) AS c FROM Registration WHERE campus = ? AND attended = 'Yes'",
            (campus,),
        ).fetchone()["c"]
        collection = conn.execute(
            "SELECT COALESCE(SUM(amountPaid), 0) AS s FROM Registration WHERE campus = ?",
            (campus,),
        ).fetchone()["s"]

        summary.append(
            {
                "campus": campus,
                "registered": registered,
                "attended": attended,
                "collection": collection,
            }
        )
        total_registered += registered
        total_attended += attended
        total_collection += collection

    conn.close()

    return render_template(
        "report_summary.html",
        summary=summary,
        total_registered=total_registered,
        total_attended=total_attended,
        total_collection=total_collection,
        today=date.today().strftime("%m/%d/%Y"),
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
