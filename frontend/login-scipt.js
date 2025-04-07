document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const emailError = document.getElementById('emailError');
    const passwordError = document.getElementById('passwordError');
    const togglePassword = document.getElementById('togglePassword');
    const successModal = document.getElementById('successModal');

    // Toggle password visibility
    togglePassword.addEventListener('click', function() {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        
        // Toggle eye icon
        const eyeIcon = this.querySelector('i');
        eyeIcon.classList.toggle('fa-eye');
        eyeIcon.classList.toggle('fa-eye-slash');
    });

    // Form validation
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        let isValid = true;
        
        // Reset error messages
        emailError.textContent = '';
        passwordError.textContent = '';
        
        // Validate email
        if (!emailInput.value) {
            emailError.textContent = 'Email is required';
            isValid = false;
        } else if (!isValidEmail(emailInput.value)) {
            emailError.textContent = 'Please enter a valid email address';
            isValid = false;
        }
        
        // Validate password
        if (!passwordInput.value) {
            passwordError.textContent = 'Password is required';
            isValid = false;
        } else if (passwordInput.value.length < 6) {
            passwordError.textContent = 'Password must be at least 6 characters';
            isValid = false;
        }
        
        // If form is valid, show success modal
        if (isValid) {
            // In a real application, you would send the form data to a server here
            // For this demo, we'll just show the success modal
            successModal.style.display = 'flex';
            
            // Simulate redirect after 2 seconds
            setTimeout(function() {
                window.location.href = 'index.html';
            }, 2000);
        }
    });

    // Email validation helper function
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    // Input focus effects
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.style.borderColor = 'var(--primary-color)';
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.style.borderColor = 'var(--border-color)';
        });
    });
});