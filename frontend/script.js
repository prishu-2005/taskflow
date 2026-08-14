const API_URL = "http://127.0.0.1:8000";

const taskList = document.getElementById("task-list");
const projectList = document.getElementById("project-list");
const apiStatus = document.getElementById("api-status");

const totalTasks = document.getElementById("total-tasks");
const totalProjects = document.getElementById("total-projects");
const highPriority = document.getElementById("high-priority");
const pendingTasks = document.getElementById("pending-tasks");


// ==============================
// Utility
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
    } catch (error) {
        apiStatus.textContent = "API Offline";
        console.error(error);
    }
}


// ==============================
// LOAD TASKS
// ==============================

async function loadTasks() {
    try {
        const response = await fetch(`${API_URL}/tasks`);

        if (!response.ok) {
            throw new Error("Failed to load tasks");
        }

        const tasks = await response.json();

        displayTasks(tasks);
        updateStatistics(tasks);
    } catch (error) {
        taskList.replaceChildren();

        const message = createElement(
            "p",
            "Could not load tasks. Make sure the FastAPI server is running.",
            "error"
        );

        taskList.appendChild(message);

        console.error(error);
    }
}


// ==============================
// DISPLAY TASKS
// ==============================

function displayTasks(tasks) {
    taskList.replaceChildren();

    if (tasks.length === 0) {
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

        const priority = createElement(
            "span",
            task.priority,
            `badge priority-${task.priority}`
        );

        const status = createElement(
            "span",
            `Status: ${task.status}`,
            "badge"
        );

        const project = createElement(
            "span",
            `Project: ${task.project_id}`,
            "badge"
        );

        const dueDate = createElement(
            "span",
            `Due: ${task.due_date || "Not set"}`,
            "badge"
        );

        meta.appendChild(priority);
        meta.appendChild(status);
        meta.appendChild(project);
        meta.appendChild(dueDate);

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
// STATISTICS
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
        const projectsResponse = await fetch(`${API_URL}/projects`);
        const statisticsResponse = await fetch(
            `${API_URL}/projects/statistics`
        );

        if (!projectsResponse.ok || !statisticsResponse.ok) {
            throw new Error("Failed to load projects");
        }

        const projects = await projectsResponse.json();
        const statistics = await statisticsResponse.json();

        totalProjects.textContent = projects.length;

        displayProjects(projects, statistics);
    } catch (error) {
        projectList.replaceChildren();

        projectList.appendChild(
            createElement(
                "p",
                "Could not load projects.",
                "error"
            )
        );

        console.error(error);
    }
}


// ==============================
// DISPLAY PROJECTS
// ==============================

function displayProjects(projects, statistics) {
    projectList.replaceChildren();

    if (projects.length === 0) {
        projectList.appendChild(
            createElement("p", "No projects found.", "muted")
        );
        return;
    }

    projects.forEach((project) => {
        const projectItem = createElement(
            "div",
            "",
            "project-item"
        );

        const name = createElement("h3", project.name);

        const projectId = createElement(
            "p",
            `Project ID: ${project.id}`
        );

        const ownerId = createElement(
            "p",
            `Owner ID: ${project.owner_id}`
        );

        const stat = statistics.find(
            (item) => item.project_id === project.id
        );

        const taskCount = stat ? stat.task_count : 0;

        const tasks = createElement(
            "p",
            `Tasks: ${taskCount}`
        );

        projectItem.appendChild(name);
        projectItem.appendChild(projectId);
        projectItem.appendChild(ownerId);
        projectItem.appendChild(tasks);

        projectList.appendChild(projectItem);
    });
}


// ==============================
// CREATE TASK
// ==============================

document
    .getElementById("task-form")
    .addEventListener("submit", async (event) => {

        event.preventDefault();

        const task = {
            title: document.getElementById("task-title").value,
            priority: document.getElementById("task-priority").value,
            due_date:
                document.getElementById("task-due-date").value || null,
            status: document.getElementById("task-status").value,
            project_id: Number(
                document.getElementById("task-project-id").value
            )
        };

        const message = document.getElementById("task-message");

        try {
            const response = await fetch(`${API_URL}/tasks`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(task)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    typeof data.detail === "string"
                        ? data.detail
                        : "Could not create task"
                );
            }

            message.textContent = "Task created successfully.";
            message.className = "success";

            document.getElementById("task-form").reset();

            await loadTasks();
            await loadProjects();

        } catch (error) {
            message.textContent = error.message;
            message.className = "error";

            console.error(error);
        }
    });


// ==============================
// AI QUICK ADD
// ==============================

document
    .getElementById("quick-add-form")
    .addEventListener("submit", async (event) => {

        event.preventDefault();

        const description =
            document.getElementById("quick-description").value;

        const projectId = Number(
            document.getElementById("quick-project-id").value
        );

        const message = document.getElementById(
            "quick-add-message"
        );

        try {
            const response = await fetch(
                `${API_URL}/tasks/quick-add`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        description: description,
                        project_id: projectId
                    })
                }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    typeof data.detail === "string"
                        ? data.detail
                        : "Could not quick-add task"
                );
            }

            message.textContent =
                `Task created: ${data.title} (${data.priority})`;

            message.className = "success";

            document.getElementById(
                "quick-add-form"
            ).reset();

            await loadTasks();
            await loadProjects();

        } catch (error) {
            message.textContent = error.message;
            message.className = "error";

            console.error(error);
        }
    });


// ==============================
// SEARCH
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
            const response = await fetch(
                `${API_URL}/tasks/search?title=${encodeURIComponent(title)}`
            );

            if (!response.ok) {
                throw new Error("Search failed");
            }

            const task = await response.json();

            if (!task) {
                taskList.replaceChildren();

                taskList.appendChild(
                    createElement(
                        "p",
                        "No matching task found.",
                        "muted"
                    )
                );

                return;
            }

            displayTasks([task]);

        } catch (error) {
            taskList.replaceChildren();

            taskList.appendChild(
                createElement("p", error.message, "error")
            );

            console.error(error);
        }
    });


// ==============================
// SHOW ALL
// ==============================

document
    .getElementById("show-all-button")
    .addEventListener("click", async () => {
        await loadTasks();
    });


// ==============================
// SORT
// ==============================

document
    .getElementById("sort-button")
    .addEventListener("click", async () => {

        try {
            const response = await fetch(
                `${API_URL}/tasks/sorted`
            );

            if (!response.ok) {
                throw new Error("Could not load sorted tasks");
            }

            const tasks = await response.json();

            displayTasks(tasks);

        } catch (error) {
            taskList.replaceChildren();

            taskList.appendChild(
                createElement("p", error.message, "error")
            );

            console.error(error);
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
        const response = await fetch(
            `${API_URL}/tasks/${taskId}`,
            {
                method: "DELETE"
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                typeof data.detail === "string"
                    ? data.detail
                    : "Could not delete task"
            );
        }

        await loadTasks();
        await loadProjects();

    } catch (error) {
        window.alert(error.message);
        console.error(error);
    }
}


// ==============================
// INITIALIZE
// ==============================

async function initializeApp() {
    await checkApi();
    await loadTasks();
    await loadProjects();
}

initializeApp();