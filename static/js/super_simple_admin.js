
// SUPER SIMPLE JavaScript Fix
console.log("🔧 SUPER SIMPLE JavaScript loaded");

// Simple form handler
function handleFormSubmit(e) {
    e.preventDefault();
    console.log("📝 Form submitted");
    
    // Get form elements directly
    const itemId = document.getElementById('item-id').value || '';
    const dataType = document.getElementById('data-type').value || '';
    const itemName = document.getElementById('item-name').value || '';
    
    console.log("Form data:", {itemId, dataType, itemName});
    
    // Build request data
    const data = {
        action: itemId ? 'edit' : 'add',
        type: dataType,
        name: itemName.trim()
    };
    
    if (itemId) {
        data.id = parseInt(itemId);
    }
    
    // Handle category for models/display_types/pop_materials
    if (dataType === 'models' || dataType === 'display_types') {
        const categorySelect = document.getElementById('item-category');
        if (categorySelect && categorySelect.value) {
            data.category_id = parseInt(categorySelect.value);
            console.log("Category ID:", data.category_id);
        } else {
            alert('❌ Please select a category');
            return;
        }
    }
    
    // Handle model for pop_materials
    if (dataType === 'pop_materials') {
        const modelSelect = document.getElementById('item-model');
        if (modelSelect && modelSelect.value) {
            data.model_id = parseInt(modelSelect.value);
            console.log("Model ID:", data.model_id);
        } else {
            alert('❌ Please select a model');
            return;
        }
    }
    
    // Validate
    if (!data.name) {
        alert('❌ Name is required');
        return;
    }
    
    console.log("Sending:", JSON.stringify(data, null, 2));
    
    // Send request
    fetch('/manage_data', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        console.log("Response:", result);
        if (result.success) {
            alert('✅ ' + result.message);
            closeModal();
            location.reload();
        } else {
            alert('❌ ' + result.message);
        }
    })
    .catch(error => {
        console.error("Error:", error);
        alert('❌ Network error');
    });
}

// Attach handler when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log("🔧 Attaching form handler");
    const form = document.getElementById('dataForm');
    if (form) {
        form.onsubmit = handleFormSubmit;
        console.log("✅ Form handler attached");
    }
});
