// Dashboard JavaScript

const API_BASE = '';
let currentUser = null;

// Check authentication
function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '/login';
        return null;
    }
    return token;
}

// API request helper
async function apiRequest(endpoint, options = {}) {
    const token = checkAuth();
    if (!token) return null;
    
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...options.headers
    };
    
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers
        });
        
        if (response.status === 401) {
            localStorage.clear();
            window.location.href = '/login';
            return null;
        }
        
        return response;
    } catch (error) {
        console.error('API request error:', error);
        return null;
    }
}

// Load user profile
async function loadProfile() {
    const response = await apiRequest('/auth/me');
    if (!response || !response.ok) return;
    
    const user = await response.json();
    currentUser = user;
    
    // Update UI
    document.getElementById('user-name').textContent = user.username;
    document.getElementById('user-email').textContent = user.email;
    document.getElementById('user-avatar').textContent = user.username[0].toUpperCase();
    
    // Settings tab
    document.getElementById('settings-username').value = user.username;
    document.getElementById('settings-email').value = user.email;
    document.getElementById('settings-created').value = new Date(user.created_at).toLocaleDateString();
}

// Tab navigation
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active from nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(`tab-${tabName}`).classList.add('active');
    
    // Add active to nav item
    event.currentTarget.classList.add('active');
    
    // Load data for specific tabs
    if (tabName === 'configs') {
        loadTemplates();
        loadConfigs();
    } else if (tabName === 'trades') {
        loadTrades();
    } else if (tabName === 'bot') {
        loadBotStatus();
    }
}

// Logout
function handleLogout() {
    localStorage.clear();
    window.location.href = '/login';
}

// Refresh data
function refreshData() {
    loadProfile();
    // Add more refresh functions as needed
}

// Load templates
async function loadTemplates() {
    const response = await apiRequest('/configs/templates');
    if (!response || !response.ok) return;
    
    const templates = await response.json();
    const grid = document.getElementById('template-grid');
    
    grid.innerHTML = templates.templates.map(template => `
        <div class="template-card" onclick="useTemplate('${template}')">
            <h4>${template.charAt(0).toUpperCase() + template.slice(1)} Strategy</h4>
            <p>Click to create a new config based on this template</p>
        </div>
    `).join('');
}

// Load user configs
async function loadConfigs() {
    const response = await apiRequest('/configs/my-configs');
    if (!response || !response.ok) return;
    
    const configs = await response.json();
    const list = document.getElementById('config-list');
    
    if (configs.length === 0) {
        list.innerHTML = '<p class="empty-state">No configurations yet. Create one from a template!</p>';
        return;
    }
    
    list.innerHTML = configs.map(config => `
        <div class="config-item">
            <div class="config-item-info">
                <h4>${config.config_name}</h4>
                <div class="config-item-meta">
                    Version ${config.config_version} • 
                    ${config.is_active ? '<strong>Active</strong>' : 'Inactive'} • 
                    Updated ${new Date(config.updated_at).toLocaleDateString()}
                </div>
            </div>
            <div class="config-item-actions">
                <button class="btn btn-secondary" onclick="editConfig(${config.id})">Edit</button>
                ${!config.is_active ? `<button class="btn btn-primary" onclick="activateConfig(${config.id})">Activate</button>` : ''}
                <button class="btn btn-danger" onclick="deleteConfig(${config.id})">Delete</button>
            </div>
        </div>
    `).join('');
}

// Load trades (placeholder)
function loadTrades() {
    // Will be implemented with bot manager
    console.log('Loading trades...');
}

// Load bot status
async function loadBotStatus() {
    try {
        const response = await apiRequest('/bots/status');
        const data = await response.json();
        
        // Update bot status UI
        const statusBadge = document.getElementById('bot-status');
        const statusText = document.getElementById('bot-status-text');
        
        if (data.running) {
            statusBadge.className = 'status-badge running';
            statusBadge.textContent = 'Running';
            statusText.textContent = `Uptime: ${formatUptime(data.uptime_seconds)}`;
            document.getElementById('start-btn').disabled = true;
            document.getElementById('stop-btn').disabled = false;
        } else {
            statusBadge.className = 'status-badge stopped';
            statusBadge.textContent = 'Stopped';
            statusText.textContent = 'Bot is not running';
            document.getElementById('start-btn').disabled = false;
            document.getElementById('stop-btn').disabled = true;
        }
        
        // Update bot info
        if (data.config_name) {
            document.getElementById('bot-config-name').textContent = data.config_name;
        }
        if (data.bot_type) {
            document.getElementById('bot-type').textContent = data.bot_type;
        }
        
    } catch (error) {
        console.error('Failed to load bot status:', error);
    }
}

// Format uptime seconds to readable string
function formatUptime(seconds) {
    if (!seconds) return 'N/A';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
}

// Bot control functions
async function startBot() {
    const startBtn = document.getElementById('start-btn');
    startBtn.disabled = true;
    startBtn.textContent = 'Starting...';
    
    try {
        const response = await apiRequest('/bots/start', {
            method: 'POST',
            body: JSON.stringify({
                bot_type: 'aggressive' // Default to aggressive bot
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('✅ Bot started successfully!');
            loadBotStatus();
        } else {
            alert(`❌ Failed to start bot: ${data.detail || 'Unknown error'}`);
            startBtn.disabled = false;
        }
    } catch (error) {
        alert(`❌ Error starting bot: ${error.message}`);
        startBtn.disabled = false;
    }
    
    startBtn.textContent = 'Start Bot';
}

async function stopBot() {
    if (!confirm('Are you sure you want to stop the bot?')) {
        return;
    }
    
    const stopBtn = document.getElementById('stop-btn');
    stopBtn.disabled = true;
    stopBtn.textContent = 'Stopping...';
    
    try {
        const response = await apiRequest('/bots/stop', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('✅ Bot stopped successfully!');
            loadBotStatus();
        } else {
            alert(`❌ Failed to stop bot: ${data.detail || 'Unknown error'}`);
            stopBtn.disabled = false;
        }
    } catch (error) {
        alert(`❌ Error stopping bot: ${error.message}`);
        stopBtn.disabled = false;
    }
    
    stopBtn.textContent = 'Stop Bot';
}

async function restartBot() {
    if (!confirm('Are you sure you want to restart the bot?')) {
        return;
    }
    
    try {
        const response = await apiRequest('/bots/restart', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('✅ Bot restarted successfully!');
            loadBotStatus();
        } else {
            alert(`❌ Failed to restart bot: ${data.detail || 'Unknown error'}`);
        }
    } catch (error) {
        alert(`❌ Error restarting bot: ${error.message}`);
    }
}

// Save API Keys
async function saveAPIKeys(event) {
    event.preventDefault();
    
    const apiKey = document.getElementById('api-key').value;
    const apiSecret = document.getElementById('api-secret').value;
    const useTestnet = document.getElementById('use-testnet').checked;
    const statusDiv = document.getElementById('api-key-status');
    
    if (!apiKey || !apiSecret) {
        statusDiv.className = 'api-key-status error';
        statusDiv.textContent = 'Please enter both API Key and Secret';
        return;
    }
    
    const response = await apiRequest('/auth/api-keys', {
        method: 'POST',
        body: JSON.stringify({
            api_key: apiKey,
            api_secret: apiSecret,
            use_testnet: useTestnet
        })
    });
    
    if (response && response.ok) {
        statusDiv.className = 'api-key-status success';
        statusDiv.textContent = '✓ API Keys saved successfully!';
        
        // Clear form
        document.getElementById('api-key').value = '';
        document.getElementById('api-secret').value = '';
    } else {
        statusDiv.className = 'api-key-status error';
        statusDiv.textContent = 'Failed to save API keys. Please try again.';
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    loadProfile();
});
