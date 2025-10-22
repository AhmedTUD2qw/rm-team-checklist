// Admin Management JavaScript

let currentDataType = 'categories';
let deleteItemId = null;
let deleteItemType = null;
let currentContext = {
    category: '',
    model: ''
};

// Initialize management interface
document.addEventListener('DOMContentLoaded', function() {
    initializeManagement();
});

function initializeManagement() {
    // Setup tab switching
    setupTabs();
    
    // Load initial data only for categories (lightweight)
    loadData('categories');
    loadCategories();
    
    // Setup form submission
    document.getElementById('dataForm').addEventListener('submit', handleFormSubmit);
    
    // Setup category filters
    setupCategoryFilters();
    
    // Show initial empty state for other tabs
    showEmptyState('models');
    showEmptyState('display_types');
    showEmptyState('pop_materials');
}

function setupTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabName = this.dataset.tab;
            
            // Update active tab button
            tabButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Update active tab content
            tabContents.forEach(content => content.classList.remove('active'));
            document.getElementById(`${tabName}-tab`).classList.add('active');
            
            // Update current data type
            currentDataType = tabName;
            
            // Only load data for categories automatically, others need filter selection
            if (tabName === 'categories') {
                loadData(tabName);
            } else {
                showEmptyState(tabName);
            }
        });
    });
}

function setupCategoryFilters() {
    const filters = ['models-category-filter', 'display-types-category-filter', 'pop-materials-category-filter'];
    
    filters.forEach(filterId => {
        const filter = document.getElementById(filterId);
        if (filter) {
            filter.addEventListener('change', function() {
                const dataType = filterId.split('-')[0] === 'models' ? 'models' : 
                               filterId.split('-')[0] === 'display' ? 'display_types' : 'pop_materials';
                
                if (this.value === '') {
                    // If no filter selected, show empty state
                    showEmptyState(dataType);
                    if (dataType === 'pop_materials') {
                        currentContext.category = '';
                        currentContext.model = '';
                        updateModelFilter(''); // Clear model filter
                    } else {
                        currentContext.category = '';
                    }
                    updateContextIndicator();
                } else {
                    // Load data when filter is selected
                    if (dataType === 'pop_materials') {
                        updateModelFilter(this.value);
                        currentContext.category = this.value;
                        currentContext.model = ''; // Reset model when category changes
                        loadData(dataType, this.value, '');
                    } else {
                        currentContext.category = this.value;
                        loadData(dataType, this.value);
                    }
                }
            });
        }
    });
    
    // Setup model filter for POP materials
    const modelFilter = document.getElementById('pop-materials-model-filter');
    if (modelFilter) {
        modelFilter.addEventListener('change', function() {
            const categoryFilter = document.getElementById('pop-materials-category-filter');
            currentContext.model = this.value;
            
            if (categoryFilter.value === '') {
                // If no category selected, show empty state
                showEmptyState('pop_materials');
                updateContextIndicator();
            } else {
                // Load data with both category and model filters
                loadData('pop_materials', categoryFilter.value, this.value);
            }
        });
    }
}

function loadCategories() {
    fetch('/get_management_data/categories')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateCategoryFilters(data.data);
                updateCategorySelect(data.data);
            }
        })
        .catch(error => console.error('Error loading categories:', error));
}

function updateCategoryFilters(categories) {
    const filters = ['models-category-filter', 'display-types-category-filter', 'pop-materials-category-filter'];
    
    filters.forEach(filterId => {
        const filter = document.getElementById(filterId);
        if (filter) {
            filter.innerHTML = '<option value="">All Categories</option>';
            categories.forEach(category => {
                const option = document.createElement('option');
                option.value = category.name;
                option.textContent = category.name;
                filter.appendChild(option);
            });
        }
    });
}

function updateCategorySelect(categories) {
    const select = document.getElementById('item-category');
    if (select) {
        select.innerHTML = '<option value="">Select Category</option>';
        categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category.name;
            option.textContent = category.name;
            select.appendChild(option);
        });
    }
}

function loadData(dataType, categoryFilter = '', modelFilter = '') {
    let url = `/get_management_data/${dataType}`;
    const params = new URLSearchParams();
    
    if (categoryFilter) {
        params.append('category', categoryFilter);
        currentContext.category = categoryFilter;
    }
    if (modelFilter) {
        params.append('model', modelFilter);
        currentContext.model = modelFilter;
    }
    
    if (params.toString()) {
        url += `?${params.toString()}`;
    }
    
    // Show loading state
    showLoadingState(dataType);
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateTable(dataType, data.data);
                updateContextIndicator();
            } else {
                showMessage('Error loading data: ' + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error loading data:', error);
            showMessage('Error loading data', 'error');
        });
}

function updateModelFilter(selectedCategory) {
    const modelFilter = document.getElementById('pop-materials-model-filter');
    if (!modelFilter) return;
    
    // Clear current options
    modelFilter.innerHTML = '<option value="">All Models</option>';
    
    if (selectedCategory) {
        // Fetch models for the selected category
        fetch(`/get_management_data/models?category=${encodeURIComponent(selectedCategory)}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    data.data.forEach(model => {
                        const option = document.createElement('option');
                        option.value = model.name;
                        option.textContent = model.name;
                        modelFilter.appendChild(option);
                    });
                }
            })
            .catch(error => {
                console.error('Error loading models:', error);
            });
    }
}

function updateTable(dataType, data) {
    const tableBody = document.querySelector(`#${dataType}-table tbody`);
    if (!tableBody) return;
    
    tableBody.innerHTML = '';
    
    data.forEach(item => {
        const row = document.createElement('tr');
        
        if (dataType === 'categories') {
            row.innerHTML = `
                <td>${item.id}</td>
                <td>${item.name}</td>
                <td>${formatDate(item.created_at || item.created_date)}</td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="editItem('${dataType}', ${item.id}, '${item.name}')">Edit</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteItem('${dataType}', ${item.id})">Delete</button>
                </td>
            `;
        } else if (dataType === 'pop_materials') {
            row.innerHTML = `
                <td>${item.id}</td>
                <td>${item.name}</td>
                <td>${item.model || 'N/A'}</td>
                <td>${item.category || 'N/A'}</td>
                <td>${formatDate(item.created_at || item.created_date)}</td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="editItem('${dataType}', ${item.id}, '${item.name}', '${item.category || ''}', '${item.model || ''}')">Edit</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteItem('${dataType}', ${item.id})">Delete</button>
                </td>
            `;
        } else {
            row.innerHTML = `
                <td>${item.id}</td>
                <td>${item.name}</td>
                <td>${item.category || 'N/A'}</td>
                <td>${formatDate(item.created_at || item.created_date)}</td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="editItem('${dataType}', ${item.id}, '${item.name}', '${item.category || ''}')">Edit</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteItem('${dataType}', ${item.id})">Delete</button>
                </td>
            `;
        }
        
        tableBody.appendChild(row);
    });
}

function formatDate(dateString) {
    if (!dateString || dateString === 'N/A' || dateString === 'null' || dateString === 'undefined') {
        return 'N/A';
    }
    
    try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) {
            return 'N/A';
        }
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    } catch (error) {
        return 'N/A';
    }
}

function showAddModal(dataType) {
    document.getElementById('modal-title').textContent = `Add ${getDataTypeLabel(dataType)}`;
    document.getElementById('data-type').value = dataType;
    document.getElementById('item-id').value = '';
    document.getElementById('item-name').value = '';
    document.getElementById('item-category').value = '';
    
    // Show/hide fields based on data type
    const categoryGroup = document.getElementById('category-group');
    const modelGroup = document.getElementById('model-group');
    
    if (dataType === 'categories') {
        categoryGroup.style.display = 'none';
        modelGroup.style.display = 'none';
        document.getElementById('item-category').required = false;
        document.getElementById('item-model').required = false;
    } else if (dataType === 'pop_materials') {
        categoryGroup.style.display = 'block';
        modelGroup.style.display = 'block';
        document.getElementById('item-category').required = true;
        document.getElementById('item-model').required = true;
        
        // Auto-fill category and model if we're in a filtered context
        if (currentContext.category) {
            document.getElementById('item-category').value = currentContext.category;
            
            // Load models for the current category
            loadModelsForCategory(currentContext.category, currentContext.model);
            
            // If we have a specific model context, select it
            if (currentContext.model) {
                setTimeout(() => {
                    document.getElementById('item-model').value = currentContext.model;
                }, 200);
            }
        }
        
        // Setup category change listener for model loading
        setupCategoryModelListener();
    } else {
        categoryGroup.style.display = 'block';
        modelGroup.style.display = 'none';
        document.getElementById('item-category').required = true;
        document.getElementById('item-model').required = false;
        
        // Auto-fill category if we're in a filtered context
        if (currentContext.category) {
            document.getElementById('item-category').value = currentContext.category;
        }
    }
    
    document.getElementById('dataModal').style.display = 'block';
    focusNameField();
}

function editItem(dataType, id, name, category = '', model = '') {
    document.getElementById('modal-title').textContent = `Edit ${getDataTypeLabel(dataType)}`;
    document.getElementById('data-type').value = dataType;
    document.getElementById('item-id').value = id;
    document.getElementById('item-name').value = name;
    document.getElementById('item-category').value = category;
    
    // Show/hide fields based on data type
    const categoryGroup = document.getElementById('category-group');
    const modelGroup = document.getElementById('model-group');
    
    if (dataType === 'categories') {
        categoryGroup.style.display = 'none';
        modelGroup.style.display = 'none';
        document.getElementById('item-category').required = false;
        document.getElementById('item-model').required = false;
    } else if (dataType === 'pop_materials') {
        categoryGroup.style.display = 'block';
        modelGroup.style.display = 'block';
        document.getElementById('item-category').required = true;
        document.getElementById('item-model').required = true;
        
        // Load models for the selected category and set the model
        if (category) {
            loadModelsForCategory(category, model);
        }
        
        // Setup category change listener for model loading
        setupCategoryModelListener();
    } else {
        categoryGroup.style.display = 'block';
        modelGroup.style.display = 'none';
        document.getElementById('item-category').required = true;
        document.getElementById('item-model').required = false;
    }
    
    document.getElementById('dataModal').style.display = 'block';
    focusNameField();
}

function deleteItem(dataType, id) {
    deleteItemId = id;
    deleteItemType = dataType;
    document.getElementById('deleteModal').style.display = 'block';
}

function confirmDelete() {
    if (!deleteItemId || !deleteItemType) return;
    
    const data = {
        action: 'delete',
        type: deleteItemType,
        id: deleteItemId
    };
    
    fetch('/manage_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage(data.message, 'success');
            
            // Reload data with current filters preserved
            reloadCurrentData(deleteItemType);
            
            // Refresh filters and related data after deletion
            if (deleteItemType === 'categories') {
                loadCategories();
                refreshAllFilters();
                // Clear context if deleted category was selected
                if (currentContext.category) {
                    currentContext.category = '';
                    currentContext.model = '';
                    updateContextIndicator();
                }
            } else if (deleteItemType === 'models') {
                refreshModelFilters();
            }
        } else {
            showMessage('Error: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error deleting item:', error);
        showMessage('Error deleting item', 'error');
    })
    .finally(() => {
        closeDeleteModal();
    });
}

function handleFormSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const itemId = formData.get('item-id') || document.getElementById('item-id').value;
    const dataType = formData.get('data-type') || document.getElementById('data-type').value;
    const itemName = formData.get('item-name') || document.getElementById('item-name').value;
    const itemCategory = formData.get('item-category') || document.getElementById('item-category').value;
    
    const data = {
        action: itemId ? 'edit' : 'add',
        type: dataType,
        name: itemName
    };
    
    if (itemId) {
        data.id = itemId;
    }
    
    if (dataType !== 'categories') {
        data.category_id = itemCategory;
        
        if (dataType === 'pop_materials') {
            const itemModel = document.getElementById('item-model').value;
            data.model_id = itemModel;
        }
    }
    
    fetch('/manage_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage(data.message, 'success');
            
            // Close modal first for better UX
            closeModal();
            
            // Reload data to show changes with current filters
            reloadCurrentData(currentDataType);
            
            // Highlight the saved item (if it's an edit)
            const itemId = document.getElementById('item-id').value;
            if (itemId) {
                setTimeout(() => {
                    highlightSavedItem(itemId);
                }, 500);
            }
            
            // Refresh filters and related data after changes
            if (currentDataType === 'categories') {
                loadCategories();
                // Refresh all dependent data
                refreshAllFilters();
            } else if (currentDataType === 'models') {
                // Refresh model filters in POP materials
                refreshModelFilters();
            }
            
            // Keep focus on the same tab for quick editing
            const activeTab = document.querySelector('.tab-btn.active');
            if (activeTab) {
                activeTab.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        } else {
            showMessage('Error: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error saving data:', error);
        showMessage('Error saving data', 'error');
    });
}

function closeModal() {
    document.getElementById('dataModal').style.display = 'none';
}

function closeDeleteModal() {
    document.getElementById('deleteModal').style.display = 'none';
    deleteItemId = null;
    deleteItemType = null;
}

function getDataTypeLabel(dataType) {
    const labels = {
        'categories': 'Category',
        'models': 'Model',
        'display_types': 'Display Type',
        'pop_materials': 'POP Material'
    };
    return labels[dataType] || dataType;
}

function setupCategoryModelListener() {
    const categorySelect = document.getElementById('item-category');
    const modelSelect = document.getElementById('item-model');
    
    if (categorySelect && modelSelect) {
        categorySelect.addEventListener('change', function() {
            loadModelsForCategory(this.value);
        });
    }
}

function loadModelsForCategory(category, selectedModel = '') {
    const modelSelect = document.getElementById('item-model');
    if (!modelSelect) return;
    
    // Clear current options completely
    modelSelect.innerHTML = '';
    
    // Add default option
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = 'Select Model';
    modelSelect.appendChild(defaultOption);
    
    if (category) {
        fetch(`/get_management_data/models?category=${encodeURIComponent(category)}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Remove duplicates by using a Set
                    const uniqueModels = [];
                    const seenModels = new Set();
                    
                    data.data.forEach(model => {
                        if (!seenModels.has(model.name)) {
                            seenModels.add(model.name);
                            uniqueModels.push(model);
                        }
                    });
                    
                    // Add unique models to select
                    uniqueModels.forEach(model => {
                        const option = document.createElement('option');
                        option.value = model.name;
                        option.textContent = model.name;
                        if (model.name === selectedModel) {
                            option.selected = true;
                        }
                        modelSelect.appendChild(option);
                    });
                }
            })
            .catch(error => {
                console.error('Error loading models:', error);
            });
    }
}

function showMessage(message, type) {
    // Remove existing messages
    const existingMessages = document.querySelectorAll('.flash-message');
    existingMessages.forEach(msg => msg.remove());
    
    // Create new message with icon
    const messageDiv = document.createElement('div');
    messageDiv.className = `flash-message alert alert-${type}`;
    
    const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
    messageDiv.innerHTML = `<span class="message-icon">${icon}</span> ${message}`;
    
    // Add animation class
    messageDiv.style.opacity = '0';
    messageDiv.style.transform = 'translateY(-20px)';
    messageDiv.style.transition = 'all 0.3s ease';
    
    // Insert at top of container
    const container = document.querySelector('.admin-container');
    container.insertBefore(messageDiv, container.firstChild);
    
    // Animate in
    setTimeout(() => {
        messageDiv.style.opacity = '1';
        messageDiv.style.transform = 'translateY(0)';
    }, 10);
    
    // Auto-hide after 4 seconds for success, 6 seconds for errors
    const hideDelay = type === 'success' ? 4000 : 6000;
    setTimeout(() => {
        messageDiv.style.opacity = '0';
        messageDiv.style.transform = 'translateY(-20px)';
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.remove();
            }
        }, 300);
    }, hideDelay);
}

// Close modals when clicking outside
window.addEventListener('click', function(e) {
    const dataModal = document.getElementById('dataModal');
    const deleteModal = document.getElementById('deleteModal');
    
    if (e.target === dataModal) {
        closeModal();
    }
    
    if (e.target === deleteModal) {
        closeDeleteModal();
    }
});

// Keyboard shortcuts for better UX
document.addEventListener('keydown', function(e) {
    // ESC to close modals
    if (e.key === 'Escape') {
        const dataModal = document.getElementById('dataModal');
        const deleteModal = document.getElementById('deleteModal');
        
        if (dataModal && dataModal.style.display === 'block') {
            closeModal();
        }
        if (deleteModal && deleteModal.style.display === 'block') {
            closeDeleteModal();
        }
    }
    
    // Ctrl+S to save form (prevent default browser save)
    if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        const dataModal = document.getElementById('dataModal');
        if (dataModal && dataModal.style.display === 'block') {
            const form = document.getElementById('dataForm');
            if (form) {
                form.dispatchEvent(new Event('submit'));
            }
        }
    }
    
    // Ctrl+N to add new item
    if (e.ctrlKey && e.key === 'n') {
        e.preventDefault();
        showAddModal(currentDataType);
    }
});

// Auto-focus on name field when modal opens
function focusNameField() {
    setTimeout(() => {
        const nameField = document.getElementById('item-name');
        if (nameField) {
            nameField.focus();
            nameField.select();
        }
    }, 100);
}

// Highlight saved item for visual feedback
function highlightSavedItem(itemId) {
    const tableRows = document.querySelectorAll(`#${currentDataType}-table tbody tr`);
    tableRows.forEach(row => {
        const firstCell = row.querySelector('td');
        if (firstCell && firstCell.textContent.trim() === itemId.toString()) {
            row.classList.add('just-saved');
            row.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            // Remove highlight after animation
            setTimeout(() => {
                row.classList.remove('just-saved');
            }, 2000);
        }
    });
}

// Show loading state
function showLoadingState(dataType) {
    const tableBody = document.querySelector(`#${dataType}-table tbody`);
    if (!tableBody) return;
    
    tableBody.innerHTML = '';
    
    const row = document.createElement('tr');
    const colSpan = getColumnCount(dataType);
    
    row.innerHTML = `
        <td colspan="${colSpan}" class="table-loading">
            Loading ${getDataTypeLabel(dataType).toLowerCase()}...
        </td>
    `;
    
    tableBody.appendChild(row);
}

// Show empty state with instruction message
function showEmptyState(dataType) {
    const tableBody = document.querySelector(`#${dataType}-table tbody`);
    if (!tableBody) return;
    
    // Clear current content
    tableBody.innerHTML = '';
    
    // Create instruction row
    const row = document.createElement('tr');
    const colSpan = getColumnCount(dataType);
    
    row.innerHTML = `
        <td colspan="${colSpan}" class="empty-state">
            <div class="empty-state-content">
                <span class="empty-state-icon">🔍</span>
                <p class="empty-state-message">
                    ${getEmptyStateMessage(dataType)}
                </p>
            </div>
        </td>
    `;
    
    tableBody.appendChild(row);
}

function getColumnCount(dataType) {
    switch(dataType) {
        case 'categories': return 4;
        case 'models': return 5;
        case 'display_types': return 5;
        case 'pop_materials': return 6;
        default: return 5;
    }
}

function getEmptyStateMessage(dataType) {
    switch(dataType) {
        case 'models':
            return 'Select a category from the filter above to view models';
        case 'display_types':
            return 'Select a category from the filter above to view display types';
        case 'pop_materials':
            return 'Select a category (and optionally a model) from the filters above to view POP materials';
        default:
            return 'Use the filters above to view data';
    }
}

// Reload data with current filters preserved
function reloadCurrentData(dataType) {
    if (dataType === 'categories') {
        // Categories don't need filters
        loadData(dataType);
    } else if (dataType === 'pop_materials') {
        // For POP materials, use both category and model filters
        const categoryFilter = document.getElementById('pop-materials-category-filter');
        const modelFilter = document.getElementById('pop-materials-model-filter');
        
        if (categoryFilter && categoryFilter.value) {
            loadData(dataType, categoryFilter.value, modelFilter ? modelFilter.value : '');
        } else {
            // No filter selected, show empty state
            showEmptyState(dataType);
        }
    } else {
        // For models and display_types, use category filter
        const filterElement = document.getElementById(`${dataType.replace('_', '-')}-category-filter`);
        
        if (filterElement && filterElement.value) {
            loadData(dataType, filterElement.value);
        } else {
            // No filter selected, show empty state
            showEmptyState(dataType);
        }
    }
}

// Refresh all filters after category changes
function refreshAllFilters() {
    // Reload categories in all filter dropdowns
    loadCategories();
    
    // Clear and reload model filters
    const modelFilter = document.getElementById('pop-materials-model-filter');
    if (modelFilter) {
        modelFilter.innerHTML = '<option value="">All Models</option>';
    }
    
    // If we're currently viewing filtered data, reload it
    if (currentContext.category) {
        setTimeout(() => {
            const categoryFilter = document.getElementById('pop-materials-category-filter');
            if (categoryFilter) {
                categoryFilter.value = currentContext.category;
                updateModelFilter(currentContext.category);
            }
        }, 200);
    }
}

// Refresh model filters after model changes
function refreshModelFilters() {
    // If we're in POP materials and have a category selected, refresh models
    if (currentDataType === 'pop_materials' && currentContext.category) {
        updateModelFilter(currentContext.category);
        
        // If we had a specific model selected, try to maintain it
        if (currentContext.model) {
            setTimeout(() => {
                const modelFilter = document.getElementById('pop-materials-model-filter');
                if (modelFilter) {
                    // Check if the model still exists
                    const modelOption = Array.from(modelFilter.options).find(option => option.value === currentContext.model);
                    if (modelOption) {
                        modelFilter.value = currentContext.model;
                    } else {
                        // Model was deleted or renamed, clear the context
                        currentContext.model = '';
                        updateContextIndicator();
                    }
                }
            }, 300);
        }
    }
}

// Update context indicator
function updateContextIndicator() {
    const indicator = document.getElementById('pop-context-indicator');
    const contextDisplay = document.getElementById('context-display');
    
    if (!indicator || !contextDisplay) return;
    
    if (currentDataType === 'pop_materials' && (currentContext.category || currentContext.model)) {
        let contextText = '';
        
        if (currentContext.model && currentContext.category) {
            contextText = `${currentContext.category} - ${currentContext.model}`;
        } else if (currentContext.category) {
            contextText = `${currentContext.category} (All Models)`;
        }
        
        if (contextText) {
            contextDisplay.textContent = contextText;
            indicator.style.display = 'flex';
        } else {
            indicator.style.display = 'none';
        }
    } else {
        indicator.style.display = 'none';
    }
}