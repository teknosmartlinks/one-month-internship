from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

students = []
projects = [
    {
        "id": 1,
        "title": "Frontend Website Containerization",
        "description": "Build and run frontend website using Docker and Nginx."
    },
    {
        "id": 2,
        "title": "Backend API with Python Flask",
        "description": "Create REST APIs using Python Flask and Docker."
    },
    {
        "id": 3,
        "title": "Database and Multi-Container Integration",
        "description": "Connect frontend, backend, and database using Docker Compose."
    },
    {
        "id": 4,
        "title": "Ansible Automation and Monitoring",
        "description": "Automate deployment using Ansible and Python monitoring scripts."
    }
]

submissions = []


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Student Internship Portal Backend API",
        "status": "running"
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "backend",
        "timestamp": datetime.now().isoformat()
    })


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    college = data.get("college")
    password = data.get("password")

    if not name or not email or not college or not password:
        return jsonify({"error": "All fields are required"}), 400

    student = {
        "id": len(students) + 1,
        "name": name,
        "email": email,
        "college": college
    }

    students.append(student)

    return jsonify({
        "message": "Student registered successfully",
        "student": student
    }), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    return jsonify({
        "message": "Login successful",
        "email": email
    })


@app.route("/projects", methods=["GET"])
def get_projects():
    return jsonify(projects)


@app.route("/submit-task", methods=["POST"])
def submit_task():
    data = request.get_json()

    student_name = data.get("student_name")
    project_id = data.get("project_id")
    task_description = data.get("task_description")

    if not student_name or not project_id or not task_description:
        return jsonify({"error": "student_name, project_id and task_description are required"}), 400

    submission = {
        "id": len(submissions) + 1,
        "student_name": student_name,
        "project_id": project_id,
        "task_description": task_description,
        "submitted_at": datetime.now().isoformat()
    }

    submissions.append(submission)

    return jsonify({
        "message": "Task submitted successfully",
        "submission": submission
    }), 201


@app.route("/submissions", methods=["GET"])
def get_submissions():
    return jsonify(submissions)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
