// Monaco Editor Configuration

let monacoEditor = null;
let currentConfigId = null;

// Initialize Monaco Editor
require.config({ paths: { vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs' } });

require(['vs/editor/editor.main'], function () {
    monacoEditor = monaco.editor.create(document.getElementById('monaco-editor'), {
        value: '',
        language: 'yaml',
        theme: 'vs',
        automaticLayout: true,
        minimap: { enabled: false },
        scrollBeyondLastLine: false,
        fontSize: 14,
    });
});

// Show new config modal with template
async function showNewConfigModal() {
    const modal = document.getElementById('config-modal');
    modal.classList.add('active');
    
    document.getElementById('modal-title').textContent = 'New Configuration';
    document.getElementById('config-name').value = '';
    currentConfigId = null;
    
    // Load default template
    if (monacoEditor) {
        monacoEditor.setValue('# Loading template...');
    }
}

// Use template
async function useTemplate(templateName) {
    const response = await apiRequest(`/configs/templates/${templateName}`);
    if (!response || !response.ok) return;
    
    const data = await response.json();
    
    const modal = document.getElementById('config-modal');
    modal.classList.add('active');
    
    document.getElementById('modal-title').textContent = `New Config from ${templateName} Template`;
    document.getElementById('config-name').value = `My ${templateName} Config`;
    currentConfigId = null;
    
    if (monacoEditor) {
        monacoEditor.setValue(data.yaml_content);
    }
}

// Edit existing config
async function editConfig(configId) {
    const response = await apiRequest(`/configs/${configId}`);
    if (!response || !response.ok) return;
    
    const config = await response.json();
    
    const modal = document.getElementById('config-modal');
    modal.classList.add('active');
    
    document.getElementById('modal-title').textContent = 'Edit Configuration';
    document.getElementById('config-name').value = config.config_name;
    currentConfigId = configId;
    
    if (monacoEditor) {
        monacoEditor.setValue(config.config_yaml);
    }
}

// Close modal
function closeConfigModal() {
    const modal = document.getElementById('config-modal');
    modal.classList.remove('active');
    document.getElementById('validation-result').style.display = 'none';
}

// Validate config
async function validateConfig() {
    const yamlContent = monacoEditor.getValue();
    const resultDiv = document.getElementById('validation-result');
    
    const response = await apiRequest('/configs/validate', {
        method: 'POST',
        body: JSON.stringify({ yaml_content: yamlContent })
    });
    
    if (response && response.ok) {
        const data = await response.json();
        if (data.valid) {
            resultDiv.className = 'validation-result success';
            resultDiv.textContent = '✓ Configuration is valid!';
        } else {
            resultDiv.className = 'validation-result error';
            resultDiv.textContent = '✗ ' + data.error;
        }
    } else {
        resultDiv.className = 'validation-result error';
        resultDiv.textContent = '✗ Validation failed';
    }
}

// Save config
async function saveConfig() {
    const configName = document.getElementById('config-name').value;
    const yamlContent = monacoEditor.getValue();
    const resultDiv = document.getElementById('validation-result');
    
    if (!configName) {
        resultDiv.className = 'validation-result error';
        resultDiv.textContent = '✗ Please enter a configuration name';
        return;
    }
    
    // Validate first
    const validateResponse = await apiRequest('/configs/validate', {
        method: 'POST',
        body: JSON.stringify({ yaml_content: yamlContent })
    });
    
    if (!validateResponse || !validateResponse.ok) {
        resultDiv.className = 'validation-result error';
        resultDiv.textContent = '✗ Please fix validation errors before saving';
        return;
    }
    
    const validateData = await validateResponse.json();
    if (!validateData.valid) {
        resultDiv.className = 'validation-result error';
        resultDiv.textContent = '✗ ' + validateData.error;
        return;
    }
    
    // Save config
    const endpoint = currentConfigId ? `/configs/${currentConfigId}` : '/configs/create';
    const method = currentConfigId ? 'PUT' : 'POST';
    
    const response = await apiRequest(endpoint, {
        method: method,
        body: JSON.stringify({
            config_name: configName,
            yaml_content: yamlContent
        })
    });
    
    if (response && response.ok) {
        resultDiv.className = 'validation-result success';
        resultDiv.textContent = '✓ Configuration saved successfully!';
        
        setTimeout(() => {
            closeConfigModal();
            loadConfigs();
        }, 1000);
    } else {
        resultDiv.className = 'validation-result error';
        resultDiv.textContent = '✗ Failed to save configuration';
    }
}

// Activate config
async function activateConfig(configId) {
    const response = await apiRequest(`/configs/${configId}/activate`, {
        method: 'POST'
    });
    
    if (response && response.ok) {
        alert('Configuration activated successfully!');
        loadConfigs();
    } else {
        alert('Failed to activate configuration');
    }
}

// Delete config
async function deleteConfig(configId) {
    if (!confirm('Are you sure you want to delete this configuration?')) {
        return;
    }
    
    const response = await apiRequest(`/configs/${configId}`, {
        method: 'DELETE'
    });
    
    if (response && response.ok) {
        loadConfigs();
    } else {
        alert('Failed to delete configuration');
    }
}
