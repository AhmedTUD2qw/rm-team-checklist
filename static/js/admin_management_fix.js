// Enhanced admin management with better error handling and data refresh

function updateCategoryFilter(filterId, categorySelect) {
    const filter = document.getElementById(filterId);
    if (filter && categorySelect.value) {
        filter.value = categorySelect.value;
        // Trigger change event to reload data
        filter.dispatchEvent(new Event('change'));
    }
}

function handleFormSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const data = {
        action: form.dataset.action,
        type: currentDataType,
        id: form.dataset.itemId,
        name: formData.get('name'),
        category: formData.get('category'),
        model: formData.get('model')
    };

    showLoadingIndicator();

    fetch('/manage_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            closeModal();
            showSuccessMessage(data.message);

            // Refresh all dependent data
            if (currentDataType === 'categories') {
                loadData('categories').then(() => {
                    // Update category filters and reload related data
                    loadData('models');
                    loadData('display_types');
                    loadCategories();
                });
            } else {
                loadData(currentDataType);
            }
        } else {
            showErrorMessage(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showErrorMessage('An error occurred while saving the data');
    })
    .finally(() => {
        hideLoadingIndicator();
    });
}

function showLoadingIndicator() {
    const indicator = document.createElement('div');
    indicator.id = 'loadingIndicator';
    indicator.className = 'loading-indicator';
    indicator.innerHTML = '<div class="spinner"></div><div>Loading...</div>';
    document.body.appendChild(indicator);
}

function hideLoadingIndicator() {
    const indicator = document.getElementById('loadingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

function showSuccessMessage(message) {
    const toast = showToast(message, 'success');
    setTimeout(() => toast.remove(), 3000);
}

function showErrorMessage(message) {
    const toast = showToast(message, 'error');
    setTimeout(() => toast.remove(), 5000);
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    return toast;
}

// Add to your existing CSS
const style = document.createElement('style');
style.textContent = `
.loading-indicator {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: rgba(255, 255, 255, 0.9);
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    z-index: 1000;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
}

.spinner {
    width: 30px;
    height: 30px;
    border: 3px solid #f3f3f3;
    border-top: 3px solid #3498db;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

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

.toast-success {
    background-color: #4CAF50;
}

.toast-error {
    background-color: #F44336;
}

.toast-info {
    background-color: #2196F3;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
`;

document.head.appendChild(style);