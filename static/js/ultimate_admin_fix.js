
// ULTIMATE FIX - Override everything
console.log("🚀 ULTIMATE JavaScript Fix Loaded");

// Complete override of handleFormSubmit
window.handleFormSubmit = function(e) {
    console.log("🔧 ULTIMATE handleFormSubmit called");
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    
    // Get form values
    const itemId = document.getElementById('item-id').value;
    const dataType = document.getElementById('data-type').value;
    const itemName = document.getElementById('item-name').value;
    
    console.log("📊 Form values:", {itemId, dataType, itemName});
    
    // Build data object
    const data = {
        action: itemId ? 'edit' : 'add',
        type: dataType,
        name: itemName.trim()
    };
    
    if (itemId) {
        data.id = parseInt(itemId);
    }
    
    // Handle category_id for models, display_types, pop_materials
    if (dataType === 'models' || dataType === 'display_types') {
        const categorySelect = document.getElementById('item-category');
        if (categorySelect && categorySelect.value) {
            data.category_id = parseInt(categorySelect.value);
            console.log("📊 Category ID:", data.category_id);
        }
    }
    
    // Handle model_id for pop_materials
    if (dataType === 'pop_materials') {
        const modelSelect = document.getElementById('item-model');
        if (modelSelect && modelSelect.value) {
            data.model_id = parseInt(modelSelect.value);
            console.log("📱 Model ID:", data.model_id);
        }
    }
    
    console.log("📤 Final data to send:", JSON.stringify(data, null, 2));
    
    // Validate data before sending
    if (!data.name) {
        alert('❌ Name is required');
        return;
    }
    
    if (dataType !== 'categories' && !data.category_id) {
        alert('❌ Category is required');
        return;
    }
    
    if (dataType === 'pop_materials' && !data.model_id) {
        alert('❌ Model is required');
        return;
    }
    
    // Send request
    fetch('/manage_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        console.log("📥 Response status:", response.status);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        return response.json();
    })
    .then(result => {
        console.log("📥 Response data:", result);
        if (result.success) {
            alert('✅ ' + result.message);
            closeModal();
            // Reload the current tab data
            if (typeof loadData === 'function') {
                loadData(dataType);
            } else {
                location.reload();
            }
        } else {
            alert('❌ Error: ' + result.message);
        }
    })
    .catch(error => {
        console.error('❌ Request failed:', error);
        alert('❌ Request failed: ' + error.message);
    });
};

// Override when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log("🔧 ULTIMATE: DOM loaded, overriding form handler");
    
    const form = document.getElementById('dataForm');
    if (form) {
        // Remove all existing listeners
        const newForm = form.cloneNode(true);
        form.parentNode.replaceChild(newForm, form);
        
        // Add our ultimate handler
        newForm.addEventListener('submit', window.handleFormSubmit);
        console.log("✅ ULTIMATE form handler attached");
    }
    
    // Also override any existing handleFormSubmit function
    setTimeout(() => {
        const form = document.getElementById('dataForm');
        if (form) {
            form.onsubmit = window.handleFormSubmit;
            console.log("✅ ULTIMATE: Form onsubmit overridden");
        }
    }, 1000);
});

// Override after 2 seconds to be absolutely sure
setTimeout(() => {
    const form = document.getElementById('dataForm');
    if (form) {
        form.removeEventListener('submit', handleFormSubmit);
        form.addEventListener('submit', window.handleFormSubmit);
        console.log("✅ ULTIMATE: Final override complete");
    }
}, 2000);
