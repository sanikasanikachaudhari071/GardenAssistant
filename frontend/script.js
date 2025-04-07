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
        if (taskName.trim() === '') return;
        
        // Create new task item
        const taskId = 'task-' + Date.now();
        const taskItem = document.createElement('div');
        taskItem.className = 'task-item';
        taskItem.innerHTML = `
            <div class="task-check">
                <input type="checkbox" id="${taskId}">
                <label for="${taskId}">${taskName}</label>
            </div>
            <button class="delete-btn"><i class="fas fa-trash"></i></button>
        `;
        
        // Add to task list
        taskList.appendChild(taskItem);
        
        // Reset form and close modal
        newTaskForm.reset();
        taskModal.style.display = 'none';
        
        // Add event listener to new delete button
        addDeleteListeners();
    });

    // Delete task
    function addDeleteListeners() {
        const deleteButtons = document.querySelectorAll('.delete-btn');
        deleteButtons.forEach(button => {
            button.addEventListener('click', function() {
                const taskItem = this.parentElement;
                taskItem.remove();
            });
        });
    }

    // Initialize delete listeners for existing tasks
    addDeleteListeners();

    // Task completion
    taskList.addEventListener('change', function(e) {
        if (e.target.type === 'checkbox') {
            const label = e.target.nextElementSibling;
            if (e.target.checked) {
                label.style.textDecoration = 'line-through';
                label.style.color = '#9ca3af';
            } else {
                label.style.textDecoration = 'none';
                label.style.color = 'var(--text-color)';
            }
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
});