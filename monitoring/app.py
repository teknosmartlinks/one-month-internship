from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
import requests
import requests_unixsocket
import psutil
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

PODMAN_SOCKET = os.getenv("PODMAN_SOCKET", "/run/podman/podman.sock")

CONTAINER_NAMES = [
    "student-portal-frontend",
    "student-portal-backend",
    "student-portal-db",
    "student-portal-monitoring"
]

BACKEND_URL = "http://backend:5000/health"
FRONTEND_URL = "http://frontend:80"

DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "student_portal")
DB_USER = os.getenv("DB_USER", "portal_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "portal_pass")


HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
  <title>Container Monitoring Dashboard</title>
  <style>
    body {
      margin: 0;
      font-family: Arial, sans-serif;
      background: #f4f6f9;
      color: #222;
    }

    nav {
      background: #2d145f;
      color: white;
      padding: 20px;
      text-align: center;
    }

    .container {
      padding: 30px;
    }

    .cards {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;
      margin-bottom: 30px;
    }

    .card {
      background: white;
      padding: 25px;
      border-radius: 10px;
      box-shadow: 0 3px 8px #ccc;
      border-top: 5px solid #2d145f;
      text-align: center;
    }

    .card h2 {
      margin: 0;
      color: #2d145f;
    }

    table {
      width: 100%;
      background: white;
      border-collapse: collapse;
      box-shadow: 0 3px 8px #ccc;
      margin-bottom: 30px;
    }

    th, td {
      padding: 14px;
      border-bottom: 1px solid #ddd;
      text-align: left;
    }

    th {
      background: #2d145f;
      color: white;
    }

    .running {
      color: green;
      font-weight: bold;
    }

    .stopped {
      color: red;
      font-weight: bold;
    }

    button {
      background: #ffcc00;
      padding: 12px 25px;
      border: none;
      font-weight: bold;
      border-radius: 5px;
      cursor: pointer;
      margin-bottom: 20px;
    }

    footer {
      background: #2d145f;
      color: white;
      text-align: center;
      padding: 15px;
    }

    @media (max-width: 800px) {
      .cards {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>

<body>

<nav>
  <h1>Tekno Smart Links Inc.</h1>
  <h2>Container Health Monitoring Dashboard</h2>
</nav>

<div class="container">

  <button onclick="loadDashboard()">Refresh Status</button>

  <div class="cards">
    <div class="card">
      <h2 id="totalContainers">0</h2>
      <p>Total Containers</p>
    </div>

    <div class="card">
      <h2 id="runningContainers">0</h2>
      <p>Running Containers</p>
    </div>

    <div class="card">
      <h2 id="stoppedContainers">0</h2>
      <p>Stopped Containers</p>
    </div>
  </div>

  <h2>Application Health</h2>
  <table>
    <thead>
      <tr>
        <th>Service</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody id="healthTable"></tbody>
  </table>

  <h2>Container Status</h2>
  <table>
    <thead>
      <tr>
        <th>Container Name</th>
        <th>Status</th>
        <th>Image</th>
      </tr>
    </thead>
    <tbody id="containerTable"></tbody>
  </table>

  <h2>System Resource Usage</h2>
  <table>
    <thead>
      <tr>
        <th>Metric</th>
        <th>Usage</th>
      </tr>
    </thead>
    <tbody id="systemTable"></tbody>
  </table>

</div>

<footer>
  <p>Tekno Smart Links Inc. | Embracing Technology</p>
</footer>

<script>
async function loadDashboard() {
  const response = await fetch('/api/dashboard');
  const data = await response.json();

  document.getElementById("totalContainers").innerText = data.summary.total;
  document.getElementById("runningContainers").innerText = data.summary.running;
  document.getElementById("stoppedContainers").innerText = data.summary.stopped;

  const healthTable = document.getElementById("healthTable");
  healthTable.innerHTML = "";

  Object.entries(data.health).forEach(([service, status]) => {
    healthTable.innerHTML += `
      <tr>
        <td>${service}</td>
        <td class="${status === 'healthy' || status === 'connected' ? 'running' : 'stopped'}">${status}</td>
      </tr>
    `;
  });

  const containerTable = document.getElementById("containerTable");
  containerTable.innerHTML = "";

  data.containers.forEach(container => {
    containerTable.innerHTML += `
      <tr>
        <td>${container.name}</td>
        <td class="${container.status === 'running' ? 'running' : 'stopped'}">${container.status}</td>
        <td>${container.image}</td>
      </tr>
    `;
  });

  const systemTable = document.getElementById("systemTable");
  systemTable.innerHTML = `
    <tr><td>CPU Usage</td><td>${data.system.cpu}%</td></tr>
    <tr><td>Memory Usage</td><td>${data.system.memory}%</td></tr>
    <tr><td>Disk Usage</td><td>${data.system.disk}%</td></tr>
    <tr><td>Last Updated</td><td>${data.timestamp}</td></tr>
  `;
}

loadDashboard();
setInterval(loadDashboard, 10000);
</script>

</body>
</html>
"""


def get_podman_containers():
    try:
        session = requests_unixsocket.Session()
        socket_encoded = PODMAN_SOCKET.replace("/", "%2F")
        url = f"http+unix://{socket_encoded}/v1.40/containers/json?all=true"

        response = session.get(url, timeout=5)
        containers = response.json()

        result = []

        for expected_name in CONTAINER_NAMES:
            found = False

            for container in containers:
                names = container.get("Names", [])
                clean_names = [name.replace("/", "") for name in names]

                if expected_name in clean_names:
                    found = True
                    result.append({
                        "name": expected_name,
                        "status": container.get("State", "unknown"),
                        "image": container.get("Image", "unknown")
                    })

            if not found:
                result.append({
                    "name": expected_name,
                    "status": "not found",
                    "image": "-"
                })

        return result

    except Exception as e:
        return [
            {
                "name": name,
                "status": f"error: {str(e)}",
                "image": "-"
            }
            for name in CONTAINER_NAMES
        ]


def check_url(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return "healthy"
        return "unhealthy"
    except Exception:
        return "down"


def check_database():
    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            connect_timeout=5
        )
        connection.close()
        return "connected"
    except Exception:
        return "down"


def get_system_usage():
    return {
        "cpu": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage("/").percent
    }


@app.route("/")
def index():
    return render_template_string(HTML_PAGE)


@app.route("/api/dashboard")
def dashboard():
    containers = get_podman_containers()

    running = len([c for c in containers if c["status"] == "running"])
    stopped = len(containers) - running

    return jsonify({
        "summary": {
            "total": len(containers),
            "running": running,
            "stopped": stopped
        },
        "containers": containers,
        "health": {
            "frontend": check_url(FRONTEND_URL),
            "backend": check_url(BACKEND_URL),
            "database": check_database()
        },
        "system": get_system_usage(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "monitoring"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8090)
