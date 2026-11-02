from flask import Flask, render_template, redirect, request, url_for, flash
from config import Config
from flask_mysqldb import MySQL

app = Flask(__name__)

# config
app.config.from_object(Config)
app.secret_key = "change-this-to-something-random"  # required for flash/session
mysql = MySQL(app)


@app.route("/")
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM student")
    students = cur.fetchall()
    cur.close()
    return render_template("index.html", students=students)


@app.route("/add", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        course = request.form["course"].strip()

        if not name or not email or not course:
            flash("All fields are required.", "danger")
            return render_template("add.html")

        cur = mysql.connection.cursor()
        try:
            cur.execute(
                "INSERT INTO student(name, email, course) VALUES(%s, %s, %s)",
                (name, email, course),
            )
            mysql.connection.commit()
            flash("Student added successfully.", "success")
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Error adding student: {e}", "danger")
            return render_template("add.html")
        finally:
            cur.close()

        return redirect(url_for("index"))

    # GET request: show the form
    return render_template("add.html")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_student(id):
    cur = mysql.connection.cursor()

    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        course = request.form["course"].strip()

        try:
            cur.execute(
                "UPDATE student SET name=%s, email=%s, course=%s WHERE id=%s",
                (name, email, course, id),
            )
            mysql.connection.commit()
            flash("Student updated successfully.", "success")
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Error updating student: {e}", "danger")
            return redirect(url_for("edit_student", id=id))
        finally:
            cur.close()

        return redirect(url_for("index"))

    cur.execute("SELECT * FROM student WHERE id=%s", (id,))
    student = cur.fetchone()
    cur.close()

    if student is None:
        flash("Student not found.", "danger")
        return redirect(url_for("index"))

    return render_template("edit.html", student=student)


@app.route("/delete/<int:id>", methods=["POST"])
def delete_student(id):
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM student WHERE id=%s", (id,))
        mysql.connection.commit()
        flash("Student deleted successfully.", "danger")
    except Exception as e:
        mysql.connection.rollback()
        flash(f"Error deleting student: {e}", "danger")
    finally:
        cur.close()

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
