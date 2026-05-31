const API_BASE = `http://${window.location.hostname}:5000`;

let loggedInStudent = null;

document.getElementById("registerForm").addEventListener("submit", async function(e) {
  e.preventDefault();

  const data = {
    name: document.getElementById("regName").value,
    email: document.getElementById("regEmail").value,
    college: document.getElementById("regCollege").value,
    password: document.getElementById("regPassword").value
  };

  try {

    const response = await fetch(`${API_BASE}/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    });

    const result = await response.json();

    alert(result.message);

    if (response.ok) {
      document.getElementById("registerForm").reset();
      window.location.href = "#login";
    }

  } catch (error) {

    console.error(error);

    alert("Unable to connect to backend.");

  }
});


document.getElementById("loginForm").addEventListener("submit", async function(e) {

  e.preventDefault();

  const data = {
    email: document.getElementById("loginEmail").value,
    password: document.getElementById("loginPassword").value
  };

  try {

    const response = await fetch(`${API_BASE}/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    });

    const result = await response.json();

    alert(result.message);

    if (response.ok) {

      loggedInStudent = result.student;

      document.getElementById("dashboard")
        .classList.remove("hidden");

      document.getElementById("welcomeText")
        .innerText =
        `Welcome, ${loggedInStudent.name} from ${loggedInStudent.college}`;

      document.getElementById("studentName")
        .value = loggedInStudent.name;

      document.getElementById("loginForm").reset();

      loadProjects();
      loadAssignments();

      window.location.href = "#dashboard";
    }

  } catch (error) {

    console.error(error);

    alert("Unable to connect to backend.");

  }

});


document.getElementById("projectForm").addEventListener("submit", async function(e) {

  e.preventDefault();

  if (!loggedInStudent) {
    alert("Please login first");
    return;
  }

  const data = {
    title: document.getElementById("projectTitle").value,
    description: document.getElementById("projectDescription").value,
    technology: document.getElementById("projectTechnology").value
  };

  try {

    const response = await fetch(`${API_BASE}/projects`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    });

    const result = await response.json();

    alert(result.message);

    if (response.ok) {
      document.getElementById("projectForm").reset();
      loadProjects();
    }

  } catch (error) {

    console.error(error);

    alert("Unable to create project.");

  }

});


document.getElementById("assignmentForm").addEventListener("submit", async function(e) {

  e.preventDefault();

  if (!loggedInStudent) {
    alert("Please login first");
    return;
  }

  const data = {
    student_name: document.getElementById("studentName").value,
    project_title: document.getElementById("assignmentProject").value,
    task: document.getElementById("assignmentTask").value
  };

  try {

    const response = await fetch(`${API_BASE}/assignments`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    });

    const result = await response.json();

    alert(result.message);

    if (response.ok) {

      document.getElementById("assignmentForm").reset();

      document.getElementById("studentName").value =
        loggedInStudent.name;

      loadAssignments();
    }

  } catch (error) {

    console.error(error);

    alert("Unable to submit assignment.");

  }

});


async function loadProjects() {

  try {

    const response = await fetch(`${API_BASE}/projects`);

    const projects = await response.json();

    const list = document.getElementById("projectsList");

    list.innerHTML = "";

    projects.forEach(project => {

      const card = document.createElement("div");

      card.className = "card";

      card.innerHTML = `
        <h4>${project.title}</h4>
        <p>${project.description}</p>
        <p><b>Technology:</b> ${project.technology}</p>
        <small>${project.created_at || ""}</small>
      `;

      list.appendChild(card);

    });

  } catch (error) {

    console.error(error);

  }

}


async function loadAssignments() {

  try {

    const response = await fetch(`${API_BASE}/assignments`);

    const assignments = await response.json();

    const list = document.getElementById("assignmentsList");

    list.innerHTML = "";

    assignments.forEach(assignment => {

      const card = document.createElement("div");

      card.className = "card";

      card.innerHTML = `
        <h4>${assignment.project_title}</h4>
        <p><b>Student:</b> ${assignment.student_name}</p>
        <p>${assignment.task}</p>
        <small>${assignment.submitted_at || ""}</small>
      `;

      list.appendChild(card);

    });

  } catch (error) {

    console.error(error);

  }

}


function logout() {

  loggedInStudent = null;

  document.getElementById("dashboard")
    .classList.add("hidden");

  document.getElementById("welcomeText").innerText = "";

  document.getElementById("studentName").value = "";

  document.getElementById("projectsList").innerHTML = "";

  document.getElementById("assignmentsList").innerHTML = "";

  alert("Logged out successfully");

  window.location.href = "#home";
}
