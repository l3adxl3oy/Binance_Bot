// Auth Page JavaScript

const API_BASE = '';

// Show/Hide forms
function showLogin() {
    document.getElementById('login-form').classList.add('active');
    document.getElementById('signup-form').classList.remove('active');
}

function showSignup() {
    document.getElementById('login-form').classList.remove('active');
    document.getElementById('signup-form').classList.add('active');
}

// Handle Login
async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const errorDiv = document.getElementById('login-error');
    
    errorDiv.textContent = '';
    
    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Save token to localStorage
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('user_id', data.user_id);
            localStorage.setItem('username', data.username);
            
            // Redirect to dashboard
            window.location.href = '/dashboard';
        } else {
            errorDiv.textContent = data.detail || 'Login failed';
        }
    } catch (error) {
        errorDiv.textContent = 'Network error. Please try again.';
        console.error('Login error:', error);
    }
}

// Handle Signup
async function handleSignup(event) {
    event.preventDefault();
    
    const username = document.getElementById('signup-username').value;
    const email = document.getElementById('signup-email').value;
    const password = document.getElementById('signup-password').value;
    const errorDiv = document.getElementById('signup-error');
    
    errorDiv.textContent = '';
    
    // Basic validation
    if (password.length < 6) {
        errorDiv.textContent = 'Password must be at least 6 characters';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/auth/signup`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Save token to localStorage
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('user_id', data.user_id);
            localStorage.setItem('username', data.username);
            
            // Redirect to dashboard
            window.location.href = '/dashboard';
        } else {
            errorDiv.textContent = data.detail || 'Signup failed';
        }
    } catch (error) {
        errorDiv.textContent = 'Network error. Please try again.';
        console.error('Signup error:', error);
    }
}

// Check if already logged in
if (localStorage.getItem('token')) {
    window.location.href = '/dashboard';
}
