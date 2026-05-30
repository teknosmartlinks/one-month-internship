from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import time

app = Flask(__name__)
CORS(app)

DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "student_portal")
DB_USER = os.getenv("DB_USER", "portal_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "portal_pass")

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    college = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(100), nullable=False)


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    technology = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Assignment(db.Model):
    __tablename__ = "assignments"

    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    project_title = db.Column(db.String(150), nullable=False)
    task = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)


def initialize_database():
    for _ in range(10):
        try:
            with app.app_context():
                db.create_all()
            print("Database initialized successfully")
            return
        except Exception as e:
            print("Waiting for database...", e)
            time.sleep(3)

    raise Exception("Database connection failed")


initialize_database()


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Student Internship Portal API",
        "status": "running"
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "backend"
    })


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    college = data.get("college")
    password = data.get("password")

    if not name or not email or not college or not password:
        return jsonify({"message": "All fields are required"}), 400

    existing_student = Student.query.filter_by(email=email).first()

    if existing_student:
        return jsonify({"message": "Email already registered"}), 400

    student = Student(
        name=name,
        email=email,
        college=college,
        password=password
    )

    db.session.add(student)
    db.session.commit()

    return jsonify({"message": "Registration successful"}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    student = Student.query.filter_by(email=email, password=password).first()

    if not student:
        return jsonify({"message": "Invalid email or password"}), 401

    return jsonify({
        "message": "Login successful",
        "student": {
            "id": student.id,
            "name": student.name,
            "email": student.email,
            "college": student.college
        }
    })


@app.route("/projects", methods=["GET"])
def get_projects():
    projects = Project.query.order_by(Project.id.desc()).all()

    return jsonify([
        {
            "id": project.id,
            "title": project.title,
            "description": project.description,
            "technology": project.technology,
            "created_at": project.created_at.isoformat()
        }
        for project in projects
    ])


@app.route("/projects", methods=["POST"])
def create_project():
    data = request.get_json()

    title = data.get("title")
    description = data.get("description")
    technology = data.get("technology")

    if not title or not description or not technology:
        return jsonify({"message": "All project fields are required"}), 400

    project = Project(
        title=title,
        description=description,
        technology=technology
    )

    db.session.add(project)
    db.session.commit()

    return jsonify({"message": "Project created successfully"}), 201


@app.route("/assignments", methods=["GET"])
def get_assignments():
    assignments = Assignment.query.order_by(Assignment.id.desc()).all()

    return jsonify([
        {
            "id": assignment.id,
            "student_name": assignment.student_name,
            "project_title": assignment.project_title,
            "task": assignment.task,
            "submitted_at": assignment.submitted_at.isoformat()
        }
        for assignment in assignments
    ])


@app.route("/assignments", methods=["POST"])
def create_assignment():
    data = request.get_json()

    student_name = data.get("student_name")
    project_title = data.get("project_title")
    task = data.get("task")

    if not student_name or not project_title or not task:
        return jsonify({"message": "All assignment fields are required"}), 400

    assignment = Assignment(
        student_name=student_name,
        project_title=project_title,
        task=task
    )

    db.session.add(assignment)
    db.session.commit()

    return jsonify({"message": "Assignment submitted successfully"}), 201


@app.route("/students", methods=["GET"])
def get_students():
    students = Student.query.order_by(Student.id.desc()).all()

    return jsonify([
        {
            "id": student.id,
            "name": student.name,
            "email": student.email,
            "college": student.college
        }
        for student in students
    ])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
