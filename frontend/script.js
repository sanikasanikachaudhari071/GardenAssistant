function deleteTask(taskId) {
    const API_BASE_URL = 'http://localhost:8000';
    try {
        console.log('Deleting task:', taskId);
        fetch(`${API_BASE_URL}/api/tasks/${taskId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            console.log('Delete response status:', response.status);
            
            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(`HTTP error! status: ${response.status}`);
                });
            }
            
            return response.json();
        })
        .then(result => {
            console.log('Delete result:', result);
            loadTasks(); // Reload tasks after successful deletion
        })
        .catch(error => {
            console.error('Error deleting task:', error);
            alert('Failed to delete task. Please try again.');
        });
    } catch (error) {
        console.error('Error deleting task:', error);
        alert('Failed to delete task. Please try again.');
    }
}

function updateTask(taskId, completed) {
    const API_BASE_URL = 'http://localhost:8000';
    try {
        console.log('Updating task:', taskId, 'completed:', completed);
        fetch(`${API_BASE_URL}/api/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                completed: completed
            })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(`HTTP error! status: ${response.status}`);
                });
            }
            
            return response.json();
        })
        .then(result => {
            console.log('Update result:', result);
            loadTasks(); // Reload tasks after successful update
        })
        .catch(error => {
            console.error('Error updating task:', error);
            alert('Failed to update task. Please try again.');
        });
    } catch (error) {
        console.error('Error updating task:', error);
        alert('Failed to update task. Please try again.');
    }
}

function loadTasks() {
    const API_BASE_URL = 'http://localhost:8000';
    try {
        console.log('Loading tasks...');
        fetch(`${API_BASE_URL}/api/tasks`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(tasks => {
            console.log('Loaded tasks:', tasks);
            displayTasks(tasks);
        })
        .catch(error => {
            console.error('Error loading tasks:', error);
        });
    } catch (error) {
        console.error('Error loading tasks:', error);
    }
}

function displayTasks(tasks) {
    const taskList = document.getElementById('taskList');
    taskList.innerHTML = '';

    tasks.forEach(task => {
        const taskItem = document.createElement('div');
        taskItem.className = 'task-item';
        taskItem.innerHTML = `
            <div class="task-check">
                <input type="checkbox" 
                       id="task${task.id}" 
                       ${task.completed ? 'checked' : ''}>
                <label for="task${task.id}">${task.title}</label>
            </div>
            <button class="delete-btn">
                <i class="fas fa-trash"></i>
            </button>
        `;
        taskList.appendChild(taskItem);
    });
}

// Main initialization
document.addEventListener('DOMContentLoaded', function() {
    // Mobile Menu Toggle
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const mobileNav = document.querySelector('.mobile-nav');
    let mobileMenuOpen = false;

    mobileMenuBtn.addEventListener('click', function() {
        if (mobileMenuOpen) {
            mobileNav.style.display = 'none';
            mobileMenuOpen = false;
        } else {
            mobileNav.style.display = 'block';
            mobileMenuOpen = true;
        }
    });

    // Task Modal
    const addTaskBtn = document.getElementById('addTaskBtn');
    const taskModal = document.getElementById('taskModal');
    const closeModal = document.querySelector('.close-modal');
    const newTaskForm = document.getElementById('newTaskForm');
    const taskList = document.getElementById('taskList');

    // Open modal
    addTaskBtn.addEventListener('click', function() {
        taskModal.style.display = 'flex';
    });

    // Close modal
    closeModal.addEventListener('click', function() {
        taskModal.style.display = 'none';
    });

    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === taskModal) {
            taskModal.style.display = 'none';
        }
    });

    // Add new task
    newTaskForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const taskName = document.getElementById('taskName').value;
        if (taskName.trim() === '') {
            console.error('Task name cannot be empty');
            return;
        }
        
        console.log('Submitting new task:', taskName);
        addTask(taskName);
        
        // Reset form and close modal
        newTaskForm.reset();
        taskModal.style.display = 'none';
    });

    // Task completion using event delegation
    taskList.addEventListener('change', function(e) {
        if (e.target.type === 'checkbox') {
            const taskId = e.target.id.replace('task', '');
            const completed = e.target.checked;
            updateTask(taskId, completed);
        }
    });
    
    // Delete task using event delegation
    taskList.addEventListener('click', function(e) {
        if (e.target.closest('.delete-btn')) {
            const taskItem = e.target.closest('.task-item');
            const taskId = taskItem.querySelector('input[type="checkbox"]').id.replace('task', '');
            deleteTask(taskId);
        }
    });

    // Responsive adjustments
    function handleResize() {
        if (window.innerWidth > 768) {
            mobileNav.style.display = 'none';
            mobileMenuOpen = false;
        }
    }

    window.addEventListener('resize', handleResize);

    // Add task function
    async function addTask(title) {
        const API_BASE_URL = 'http://localhost:8000';
        try {
            console.log('Adding task:', { title });
            const response = await fetch(`${API_BASE_URL}/api/tasks`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    title: title,
                    completed: false
                })
            });

            console.log('Response status:', response.status);
            
            if (!response.ok) {
                const errorData = await response.json();
                console.error('Error response:', errorData);
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const newTask = await response.json();
            console.log('Successfully added task:', newTask);
            loadTasks(); // Reload tasks after adding
        } catch (error) {
            console.error('Error adding task:', error);
            alert('Failed to add task. Please try again.');
        }
    }

    // Initialize tasks when the page loads
    loadTasks();
});