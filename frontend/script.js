
const API_URL = "http://127.0.0.1:8000";

// ==============================
// DOM ELEMENTS
// ==============================

const taskList = document.getElementById("task-list");
const projectList = document.getElementById("project-list");
const apiStatus = document.getElementById("api-status");

const totalTasks = document.getElementById("total-tasks");
const totalProjects = document.getElementById("total-projects");
const highPriority = document.getElementById("high-priority");
const pendingTasks = document.getElementById("pending-tasks");


// ==============================
// UTILITY
// ==============================

function createElement(tag, text = "", className = "") {
    const element = document.createElement(tag);

    if (text !== "") {
        element.textContent = text;
    }

    if (className !== "") {
        element.className = className;
    }

    return element;
}


async function readResponse(response) {
    const text = await response.text();

    let data = {};

    if (text) {
        try {
            data = JSON.parse(text);
        } catch {
            data = { detail: text };
        }
    }

    if (!response.ok) {
        let message = "Request failed.";

        if (typeof data.detail === "string") {
            message = data.detail;
        } else if (Array.isArray(data.detail)) {
            message = data.detail
                .map((item) => item.msg || JSON.stringify(item))
                .join("; ");
        }

        throw new Error(message);
    }

    return data;
}


// ==============================
// API STATUS
// ==============================

async function checkApi() {
    try {
        const response = await fetch(`${API_URL}/`);

        if (!response.ok) {
            throw new Error("API unavailable");
        }

        apiStatus.textContent = "API Connected";
        apiStatus.className = "status success";
    } catch (error) {
        apiStatus.textContent = "API Offline";
        apiStatus.className = "status error";

        console.error("API connection failed:", error);
    }
}


// ==============================
// LOAD TASKS
// ==============================

async function loadTasks() {
    try {
        const response = await fetch(`${API_URL}/tasks`);
        const tasks = await readResponse(response);

        displayTasks(tasks);
        updateStatistics(tasks);
    } catch (error) {
        taskList.replaceChildren();

        taskList.appendChild(
            createElement(
                "p",
                `Could not load tasks: ${error.message}`,
                "error"
            )
        );

        console.error("Loading tasks failed:", error);
    }
}


// ==============================
// DISPLAY TASKS
// ==============================

function displayTasks(tasks) {
    taskList.replaceChildren();

    if (!Array.isArray(tasks) || tasks.length === 0) {
        taskList.appendChild(
            createElement("p", "No tasks found.", "muted")
        );
        return;
    }

    tasks.forEach((task) => {
        const taskItem = createElement("div", "", "task-item");
        const taskInfo = createElement("div", "", "task-info");

        const title = createElement("h3", task.title);
        taskInfo.appendChild(title);

        const meta = createElement("div", "", "task-meta");

        meta.appendChild(
            createElement(
                "span",
                task.priority,
                `badge priority-${task.priority}`
            )
        );

        meta.appendChild(
            createElement("span", `Status: ${task.status}`, "badge")
        );

        meta.appendChild(
            createElement("span", `Project: ${task.project_id}`, "badge")
        );

        meta.appendChild(
            createElement(
                "span",
                `Due: ${task.due_date || "Not set"}`,
                "badge"
            )
        );

        taskInfo.appendChild(meta);

        const deleteButton = createElement(
            "button",
            "Delete",
            "delete-button"
        );

        deleteButton.type = "button";

        deleteButton.addEventListener("click", () => {
            deleteTask(task.id);
        });

        taskItem.appendChild(taskInfo);
        taskItem.appendChild(deleteButton);

        taskList.appendChild(taskItem);
    });
}


// ==============================
// DASHBOARD STATISTICS
// ==============================

function updateStatistics(tasks) {
    totalTasks.textContent = tasks.length;

    highPriority.textContent = tasks.filter(
        (task) => task.priority === "high"
    ).length;

    pendingTasks.textContent = tasks.filter(
        (task) => task.status === "pending"
    ).length;
}


// ==============================
// LOAD PROJECTS
// ==============================

async function loadProjects() {
    try {
        const [projectsResponse, statisticsResponse] = await Promise.all([
            fetch(`${API_URL}/projects`),
            fetch(`${API_URL}/projects/statistics`)
        ]);

        const projects = await readResponse(projectsResponse);
        const statistics = await readResponse(statisticsResponse);

        totalProjects.textContent = projects.length;

        displayProjects(projects, statistics);
    } catch (error) {
        projectList.replaceChildren();

        projectList.appendChild(
            createElement(
                "p",
                `Could not load projects: ${error.message}`,
                "error"
            )
        );

        console.error("Loading projects failed:", error);
    }
}


// ==============================
// DISPLAY PROJECTS
// ==============================

function displayProjects(projects, statistics) {
    projectList.replaceChildren();

    if (!Array.isArray(projects) || projects.length === 0) {
        projectList.appendChild(
            createElement("p", "No projects found.", "muted")
        );
        return;
    }

    projects.forEach((project) => {
        const projectItem = createElement("div", "", "project-item");

        projectItem.appendChild(
            createElement("h3", project.name)
        );

        projectItem.appendChild(
            createElement("p", `Project ID: ${project.id}`)
        );

        projectItem.appendChild(
            createElement("p", `Owner ID: ${project.owner_id}`)
        );

        const stat = statistics.find(
            (item) => item.project_id === project.id
        );

        const taskCount = stat ? stat.task_count : 0;

        projectItem.appendChild(
            createElement("p", `Tasks: ${taskCount}`)
        );

        projectList.appendChild(projectItem);
    });
}


// ==============================
// CREATE PROJECT
// ==============================

const projectForm = document.getElementById("project-form");

projectForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const nameInput = document.getElementById("project-name");
    const ownerInput = document.getElementById("project-owner-id");
    const message = document.getElementById("project-message");

    const name = nameInput.value.trim();
    const ownerId = Number(ownerInput.value);

    message.textContent = "";
    message.className = "";

    if (!name) {
        message.textContent = "Please enter a project name.";
        message.className = "error";
        return;
    }

    if (!Number.isInteger(ownerId) || ownerId < 1) {
        message.textContent = "Please enter a valid owner ID.";
        message.className = "error";
        return;
    }

    const submitButton = projectForm.querySelector(
        'button[type="submit"]'
    );

    submitButton.disabled = true;
    submitButton.textContent = "Creating...";

    try {
        const response = await fetch(`${API_URL}/projects`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify({
                name: name,
                owner_id: ownerId
            })
        });

        const project = await readResponse(response);

        message.textContent =
            `Project "${project.name}" created successfully! ID: ${project.id}`;

        message.className = "success";

        projectForm.reset();

        // Refresh projects and update the project count.
        await loadProjects();

        // Make the new project easy to use in the task forms.
        document.getElementById("task-project-id").value = project.id;
        document.getElementById("quick-project-id").value = project.id;

        // Select the new project ID for future task creation.
        nameInput.focus();
    } catch (error) {
        message.textContent = `Could not create project: ${error.message}`;
        message.className = "error";

        console.error("Project creation failed:", error);
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = "Create Project";
    }
});


// ==============================
// CREATE TASK
// ==============================

document
    .getElementById("task-form")
    .addEventListener("submit", async (event) => {
        event.preventDefault();

        const task = {
            title: document.getElementById("task-title").value.trim(),
            priority: document.getElementById("task-priority").value,
            due_date:
                document.getElementById("task-due-date").value.trim() || null,
            status: document.getElementById("task-status").value,
            project_id: Number(
                document.getElementById("task-project-id").value
            )
        };

        const message = document.getElementById("task-message");
        const submitButton = event.currentTarget.querySelector(
            'button[type="submit"]'
        );

        message.textContent = "";
        message.className = "";

        if (!task.title) {
            message.textContent = "Please enter a task title.";
            message.className = "error";
            return;
        }

        if (!Number.isInteger(task.project_id) || task.project_id < 1) {
            message.textContent = "Please enter a valid project ID.";
            message.className = "error";
            return;
        }

        submitButton.disabled = true;

        try {
            const response = await fetch(`${API_URL}/tasks`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                body: JSON.stringify(task)
            });

            await readResponse(response);

            message.textContent = "Task created successfully.";
            message.className = "success";

            event.currentTarget.reset();

            await Promise.all([
                loadTasks(),
                loadProjects()
            ]);
        } catch (error) {
            message.textContent = error.message;
            message.className = "error";

            console.error("Task creation failed:", error);
        } finally {
            submitButton.disabled = false;
        }
    });


// ==============================
// AI QUICK ADD
// ==============================

document
    .getElementById("quick-add-form")
    .addEventListener("submit", async (event) => {
        event.preventDefault();

        const description = document
            .getElementById("quick-description")
            .value
            .trim();

        const projectId = Number(
            document.getElementById("quick-project-id").value
        );

        const message = document.getElementById("quick-add-message");
        const submitButton = event.currentTarget.querySelector(
            'button[type="submit"]'
        );

        message.textContent = "";
        message.className = "";

        if (!description) {
            message.textContent = "Please describe your task.";
            message.className = "error";
            return;
        }

        if (!Number.isInteger(projectId) || projectId < 1) {
            message.textContent = "Please enter a valid project ID.";
            message.className = "error";
            return;
        }

        submitButton.disabled = true;

        try {
            const response = await fetch(`${API_URL}/tasks/quick-add`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                body: JSON.stringify({
                    description: description,
                    project_id: projectId
                })
            });

            const task = await readResponse(response);

            message.textContent =
                `Task created: ${task.title} (${task.priority})`;

            message.className = "success";

            event.currentTarget.reset();

            await Promise.all([
                loadTasks(),
                loadProjects()
            ]);
        } catch (error) {
            message.textContent = error.message;
            message.className = "error";

            console.error("AI Quick Add failed:", error);
        } finally {
            submitButton.disabled = false;
        }
    });


// ==============================
// SEARCH TASKS
// ==============================

document
    .getElementById("search-button")
    .addEventListener("click", async () => {
        const title = document
            .getElementById("search-input")
            .value
            .trim();

        if (!title) {
            await loadTasks();
            return;
        }

        try {
            const url =
                `${API_URL}/tasks/search?title=${encodeURIComponent(title)}`;

            const response = await fetch(url);
            const task = await readResponse(response);

            displayTasks(task ? [task] : []);
        } catch (error) {
            taskList.replaceChildren();

            taskList.appendChild(
                createElement("p", error.message, "error")
            );

            console.error("Task search failed:", error);
        }
    });


// ==============================
// SHOW ALL TASKS
// ==============================

document
    .getElementById("show-all-button")
    .addEventListener("click", async () => {
        document.getElementById("search-input").value = "";
        await loadTasks();
    });


// ==============================
// SORT TASKS
// ==============================

document
    .getElementById("sort-button")
    .addEventListener("click", async () => {
        try {
            const response = await fetch(`${API_URL}/tasks/sorted`);
            const tasks = await readResponse(response);

            displayTasks(tasks);
        } catch (error) {
            taskList.replaceChildren();

            taskList.appendChild(
                createElement("p", error.message, "error")
            );

            console.error("Task sorting failed:", error);
        }
    });


// ==============================
// DELETE TASK
// ==============================

async function deleteTask(taskId) {
    const confirmed = window.confirm(
        "Are you sure you want to delete this task?"
    );

    if (!confirmed) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/tasks/${taskId}`, {
            method: "DELETE"
        });

        await readResponse(response);

        await Promise.all([
            loadTasks(),
            loadProjects()
        ]);
    } catch (error) {
        window.alert(`Could not delete task: ${error.message}`);
        console.error("Task deletion failed:", error);
    }
}


// ==============================
// INITIALIZE APPLICATION
// ==============================

async function initializeApp() {
    await checkApi();

    await Promise.all([
        loadTasks(),
        loadProjects()
    ]);
}

initializeApp();

