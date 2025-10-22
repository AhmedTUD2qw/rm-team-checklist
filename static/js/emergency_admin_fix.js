// Emergency JavaScript Fix
console.log("🚨 Emergency JavaScript Fix Loaded");

function handleFormSubmit(e) {
    console.log("🔧 Emergency handleFormSubmit called");
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
    
    console.log("📤 Sending data:", JSON.stringify(data, null, 2));
    
    fetch('/manage_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        console.log("📥 Response:", data);
        if (data.success) {
            alert('✅ ' + data.message);
            closeModal();
            location.reload();
        } else {
            alert('❌ Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('❌ Error:', error);
        alert('❌ Network error: ' + error.message);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('dataForm');
    if (form) {
        form.removeEventListener('submit', handleFormSubmit);
        form.addEventListener('submit', handleFormSubmit);
        console.log("✅ Emergency form handler attached");
    }
});