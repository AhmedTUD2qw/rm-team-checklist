// Enhanced admin management functions

function updateItem(dataType, id, newData) {
    // Show loading state
    const loadingToast = showToast('Saving changes...', 'info');
    
    fetch(`/update_${dataType}/${id}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(newData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Refresh data
            loadData(dataType);
            showToast('Changes saved successfully!', 'success');
            
            // If updating category, refresh dependent data
            if (dataType === 'categories') {
                loadData('models');
                loadData('display_types');
            }
        } else {
            showToast(data.message || 'Error saving changes', 'error');
        }
    })
    .catch(error => {
        console.error('Update error:', error);
        showToast('Error saving changes', 'error');
    })
    .finally(() => {
        // Remove loading toast
        if (loadingToast) loadingToast.remove();
    });
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
    
    return toast;
}

// Add these styles to your CSS
const style = document.createElement('style');
style.textContent = `
.toast {
    position: fixed;
    bottom: 20px;
    right: 20px;
    padding: 12px 24px;
    border-radius: 4px;
    color: white;
    z-index: 1000;
    animation: fadeIn 0.3s ease;
}

.toast-info {
    background-color: #2196F3;
}

.toast-success {
    background-color: #4CAF50;
}

.toast-error {
    background-color: #F44336;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
`;

document.head.appendChild(style);