from cs50 import SQL
from flask import Flask, redirect, render_template, request, session, url_for, flash
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    if "user_id" in session:
        user_type = session.get("user_type")
        return render_template("index.html", user_type=user_type)
    else:
        return render_template("index.html", user_type=None)


@app.route("/search", methods=["POST"])
def search():
    # Get user input from the form
    name = request.form.get("name")
    location = request.form.get("location")
    job_type = request.form.get("job_type")
    company = request.form.get("company")
    # Perform a database query to find matching records
    query = "SELECT * FROM jobs WHERE title LIKE :name AND location LIKE :location AND type LIKE :job_type AND company LIKE :company"
    search_results = db.execute(query, name=f"%{name}%", location=f"%{location}%", job_type=f"%{job_type}%", company=f"%{company}%")
    # Render the search results in a new Booking
    return render_template("search_results.html", search_results=search_results)


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 403)
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["user_type"] = rows[0]["user_type"]  # Store user_type in the session

        return redirect("/dashboard")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/registration_applicant", methods=["GET", "POST"])
def registration_applicant():
    """Register applicant"""
    if request.method == "GET":
        return render_template("registration_applicant.html")

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Check if the name already exists
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=username)
        if len(rows) != 0:
            return apology("username already exists", 400)

        if not username or not password or not confirmation:
            return apology("provide username and/or password", 400)

        if password != confirmation:
            return apology("check password again", 400)

        # Hash the password before storing it in the database
        hashed_password = generate_password_hash(password)
        user_type = "applicant"
        # Store the user in the database
        db.execute("INSERT INTO users (username, hash, user_type) VALUES (:username, :hash, :user_type)",
                   username=username, hash=hashed_password, user_type=user_type)

        # Automatically log in the user after registration
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=username)
        session["user_id"] = rows[0]["id"]

        return redirect("/")

    return render_template("registration_applicant.html")


@app.route("/registration_recruiter", methods=["GET", "POST"])
def registration_recruiter():
    """Register recruiter"""
    if request.method == "GET":
        return render_template("registration_recruiter.html")
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Check if the name already exists
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=username)
        if len(rows) != 0:
            return apology("username already exists", 400)
        if not username or not password or not confirmation:
            return apology("provide username and/or password", 400)
        if password != confirmation:
            return apology("check password again", 400)

        # Hash the password before storing it in the database
        hashed_password = generate_password_hash(password)
        user_type = "recruiter"
        # Store the user in the database
        db.execute("INSERT INTO users (username, hash, user_type) VALUES (:username, :hash, :user_type)",
                   username=username, hash=hashed_password, user_type=user_type)

        # Automatically log in the user after registration
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=username)
        session["user_id"] = rows[0]["id"]

        return redirect("/dashboard")
    return render_template("registration_recruiter.html")


@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    user = db.execute("SELECT * FROM users WHERE id = :id", id=user_id)[0]
    username = user["username"]
    return render_template("dashboard.html", username=username)


@app.route("/create-job", methods=["GET", "POST"])
@login_required
def create_job():
    user_type = session.get("user_type")
    if user_type == "applicant":
        return apology("you're not a recruiter", 400)

    if request.method == "GET":
        user_id = session["user_id"]
        user = db.execute("SELECT * FROM users WHERE id = :id", id=user_id)[0]
        username = user["username"]
        return render_template("create-job.html", username=username)

    if request.method == "POST":
        job_title = request.form.get("job_title")
        company_name = request.form.get("company_name")
        job_type = request.form.get("job_type")
        job_location = request.form.get("job_location")
        job_description = request.form.get("job_description")
        job_status = request.form.get("job_status")

        user_id = session["user_id"]
        user = db.execute("SELECT * FROM users WHERE id = :id", id=user_id)[0]
        username = user["username"]
        posted_by = username

        db.execute("INSERT INTO jobs (title, company, type, location, description, status, posted_by) VALUES "
                   "(?, ?, ?, ?, ?, ?, ?)", job_title, company_name, job_type, job_location, job_description,
                   job_status, posted_by)

        return redirect("/dashboard")


@app.route("/manage-job", methods=["GET", "POST"])
@login_required
def manage_job():
    user_type = session.get("user_type")
    if user_type == "applicant":
        return apology("you're not a recruiter", 400)

    user_id = session["user_id"]
    user = db.execute("SELECT * FROM users WHERE id = :id", id=user_id)[0]
    username = user["username"]

    posted_jobs = db.execute("""SELECT id, title, company, type, location, description, status, applicants
                                FROM jobs
                                WHERE posted_by = :username;
                                """, username=username)

    return render_template("manage-job.html", posted_jobs=posted_jobs, username=username)


@app.route("/edit-job/<int:job_id>", methods=["GET", "POST"])
@login_required
def edit_job(job_id):
    user_id = session["user_id"]
    user = db.execute("SELECT * FROM users WHERE id = :id", id=user_id)[0]
    username = user["username"]
    # Retrieve job details from the database using job_id
    job = db.execute("SELECT * FROM jobs WHERE id = :job_id", job_id=job_id)

    # Check if the user has permission to edit the job
    if job and job[0]["posted_by"] == username:
        if request.method == "POST":
            # Update the job details in the database based on the form data
            updated_job_title = request.form.get("job_title")
            updated_company_name = request.form.get("company_name")
            updated_job_type = request.form.get("job_type")
            updated_job_location = request.form.get("job_location")
            updated_job_description = request.form.get("job_description")
            updated_job_status = request.form.get("job_status")

            db.execute("""UPDATE jobs
                          SET title = :updated_job_title, 
                              company = :updated_company_name,
                              type = :updated_job_type,
                              location = :updated_job_location,
                              description = :updated_job_description,
                              status = :updated_job_status
                          WHERE id = :job_id""",
                       updated_job_title=updated_job_title, updated_company_name=updated_company_name,
                       updated_job_type=updated_job_type, updated_job_location=updated_job_location,
                       updated_job_description=updated_job_description, updated_job_status=updated_job_status,
                       job_id=job_id)

            return redirect("/manage-job")

        # Render the edit job page with the job details
        return render_template("edit-job.html", job=job[0])

    # If the user doesn't have permission to edit the job, show an error
    return apology("Permission denied", 403)


@app.route("/all-jobs", methods=["GET", "POST"])
def all_jobs():
    if request.method == "GET":
        posted_jobs = db.execute("""SELECT * FROM jobs
                                    WHERE status = "active"
                                    ;""")
        return render_template("all-jobs.html", posted_jobs=posted_jobs)

    else:
        return render_template("all-jobs.html")


@app.route("/job-details/<int:job_id>", methods=["GET", "POST"])
@login_required
def job_details(job_id):
    user_id = session["user_id"]
    user = db.execute("SELECT * FROM users WHERE id = :id", id=user_id)[0]
    username = user["username"]
    user_type = session.get("user_type")

    # Retrieve job details from the database using job_id
    job = db.execute("SELECT * FROM jobs WHERE id = :job_id", job_id=job_id)

    if request.method == "POST":
        if user_type != "applicant":
            flash("Only applicants can apply for jobs.", "warning")
            return redirect('/dashboard')

        # Check if the user has already applied for the job
        previous_application = db.execute(
            "SELECT id FROM applied_jobs WHERE applicant = :user_id AND job_applied = :job_id",
            user_id=user_id, job_id=job_id)

        if previous_application:
            flash("You have already applied for this job.", "warning")
            return redirect('/dashboard')

        application_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.execute(
            "INSERT INTO applied_jobs (applicant, job_applied, apply_time) VALUES (:user_id, :job_id, :application_time)",
            user_id=user_id, job_id=job_id, application_time=application_time)
        db.execute("UPDATE jobs SET applicants = applicants + 1 WHERE id = :job_id", job_id=job_id)
        flash("Application successful!", "success")
        return redirect('/dashboard')

    return render_template("job-details.html", job=job[0], username=username)


@app.route("/manage-application", methods=["GET", "POST"])
@login_required
def manage_application():
    user_type = session.get("user_type")
    if user_type == "recruiter":
        return apology("you're not an applicant", 400)

    user_id = session["user_id"]
    user = db.execute("SELECT * FROM users WHERE id = :id", id=user_id)[0]
    username = user["username"]

    applied_jobs = db.execute("""SELECT jobs.*, applied_jobs.apply_time
                                    FROM jobs
                                    JOIN applied_jobs ON jobs.id = applied_jobs.job_applied
                                    WHERE applied_jobs.applicant = (SELECT id FROM users WHERE username = :username);
                                """, username=username)

    return render_template("manage-application.html", applied_jobs=applied_jobs, username=username)


@app.route("/withdraw-application", methods=["POST"])
@login_required
def withdraw_application():
    user_id = session["user_id"]
    job_id = request.form.get("job_id")

    # Check if the user has applied for the job
    applied_jobs = db.execute(
        "SELECT id FROM applied_jobs WHERE applicant = :user_id AND job_applied = :job_id",
        user_id=user_id, job_id=job_id)
    print("user_id:", user_id)
    print("job_id:", job_id)
    print("applied_jobs:", applied_jobs)

    if applied_jobs:
        application_id = applied_jobs[0]['id']
        print(application_id)

        # Remove the application from the database
        db.execute("DELETE FROM applied_jobs WHERE id = :application_id", application_id=application_id)
        db.execute("UPDATE jobs SET applicants = applicants - 1 WHERE id = :job_id", job_id=job_id)
        flash("Application withdrawn successfully.", "success")
    else:
        flash("Application not found.", "warning")

    return redirect('/dashboard')


if __name__ == "__main__":
    app.run(debug=True)
