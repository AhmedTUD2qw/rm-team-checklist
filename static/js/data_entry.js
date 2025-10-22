// Data Entry JavaScript functionality

// Model data structure
const modelData = {
    'OLED': ['S95F', 'S90F', 'S85F'],
    'Neo QLED': ['QN90', 'QN85F', 'QN80F', 'QN70F'],
    'QLED': ['Q8F', 'Q7F'],
    'UHD': ['U8000', '100"/98"'],
    'LTV': ['The Frame'],
    'BESPOKE COMBO': ['WD25DB8995', 'WD21D6400'],
    'BESPOKE Front': ['WW11B1944DGB'],
    'Front': ['WW11B1534D', 'WW90CGC', 'WW4040', 'WW4020'],
    'TL': ['WA19CG6886', 'Local TL'],
    'SBS': ['RS70F'],
    'TMF': ['Bespoke', 'TMF Non-Bespoke', 'TMF'],
    'BMF': ['(Bespoke, BMF)', '(Non-Bespoke, BMF)'],
    'Local TMF': ['Local TMF']
};

// Display type options based on category
const displayTypes = {
    // For TV categories
    'OLED': ['Highlight Zone', 'Fixtures', 'Multi Brand Zone with Space', 'SIS (Endcap)'],
    'Neo QLED': ['Highlight Zone', 'Fixtures', 'Multi Brand Zone with Space', 'SIS (Endcap)'],
    'QLED': ['Highlight Zone', 'Fixtures', 'Multi Brand Zone with Space', 'SIS (Endcap)'],
    'UHD': ['Highlight Zone', 'Fixtures', 'Multi Brand Zone with Space', 'SIS (Endcap)'],
    'LTV': ['Highlight Zone', 'Fixtures', 'Multi Brand Zone with Space', 'SIS (Endcap)'],

    // For Appliance categories
    'BESPOKE COMBO': ['POP Out', 'POP Inner', 'POP'],
    'BESPOKE Front': ['POP Out', 'POP Inner', 'POP'],
    'Front': ['POP Out', 'POP Inner', 'POP'],
    'TL': ['POP Out', 'POP Inner', 'POP'],
    'SBS': ['POP Out', 'POP Inner', 'POP'],
    'TMF': ['POP Out', 'POP Inner', 'POP'],
    'BMF': ['POP Out', 'POP Inner', 'POP'],
    'Local TMF': ['POP Out', 'POP Inner', 'POP']
};

// POP Material checklist items based on category
const popMaterials = {
    'OLED': [
        'AI topper',
        'Oled Topper',
        'Glare Free',
        'New Topper',
        '165 HZ Side POP',
        'Category POP',
        'Samsung OLED Topper',
        '165 HZ & joy stick indicator',
        'AI Topper Gaming',
        'Side POP',
        'Specs Card',
        'OLED Topper',
        'Why Oled side POP'
    ],

    'Neo QLED': [
        'AI topper',
        'Lockup Topper',
        'Screen POP',
        'New Topper',
        'Glare Free',
        'Specs Card'
    ],

    'QLED': [
        'AI topper',
        'Samsung QLED Topper',
        'Screen POP',
        'New Topper',
        'Specs Card',
        'QLED Topper'
    ],

    'UHD': [
        'UHD topper',
        'Samsung UHD topper',
        'Screen POP',
        'New Topper',
        'Specs Card',
        'AI topper',
        'Samsung Lockup Topper',
        'Inch Logo side POP'
    ],

    'LTV': [
        'Side POP',
        'Matte Display',
        'Category POP',
        'Frame Bezel'
    ],

    'BESPOKE COMBO': [
        'PODs (Door)',
        'POD (Top)',
        'POD (Front)',
        '3 PODs (Top)',
        'AI Home POP',
        'AI Home',
        'AI control panel',
        'Capacity (Kg)',
        'Capacity Dryer',
        'Filter',
        'Ecobuble POP',
        'Ecco Buble',
        'AI Ecco Buble',
        '20 Years Warranty',
        'New Arrival',
        'Samsung Brand/Tech Topper'
    ],

    'BESPOKE Front': [
        'PODs (Door)',
        'POD (Top)',
        'POD (Front)',
        '3 PODs (Top)',
        'AI Home POP',
        'AI Home',
        'AI control panel',
        'Capacity (Kg)',
        'Capacity Dryer',
        'Filter',
        'Ecobuble POP',
        'Ecco Buble',
        'AI Ecco Buble',
        '20 Years Warranty',
        'New Arrival',
        'Samsung Brand/Tech Topper'
    ],

    'Front': [
        'PODs (Door)',
        'POD (Top)',
        'POD (Front)',
        '3 PODs (Top)',
        'AI Home POP',
        'AI Home',
        'AI control panel',
        'Capacity (Kg)',
        'Capacity Dryer',
        'Filter',
        'Ecobuble POP',
        'Ecco Buble',
        'AI Ecco Buble',
        '20 Years Warranty',
        'New Arrival',
        'Samsung Brand/Tech Topper'
    ],

    'TL': [
        'PODs (Door)',
        'POD (Top)',
        'POD (Front)',
        '3 PODs (Top)',
        'AI Home POP',
        'AI Home',
        'AI control panel',
        'Capacity (Kg)',
        'Capacity Dryer',
        'Filter',
        'Ecobuble POP',
        'Ecco Buble',
        'AI Ecco Buble',
        '20 Years Warranty',
        'New Arrival',
        'Samsung Brand/Tech Topper'
    ],

    'SBS': [
        'Samsung Brand/Tech Topper',
        'Main POD',
        '20 Years Warranty',
        'Twin Cooling Plus™',
        'Smart Conversion™',
        'Digital Inverter™',
        'SpaceMax™',
        'Tempered Glass',
        'Power Freeze',
        'Big Vegetable Box',
        'Organize Big Bin'
    ],

    'TMF': [
        'Samsung Brand/Tech Topper',
        '20 Years Warranty',
        'Key features POP',
        'Side POP',
        'Global No.1',
        'Freshness POP',
        'Bacteria Safe Ionizer POP',
        'Gallon Guard POP',
        'Big Vegetables Box POP',
        'Adjustable Pin & Organize POP',
        'Optimal Fresh',
        'Tempered Glass',
        'Gallon Guard',
        'Veg Box',
        'Internal Display',
        'Multi Tray',
        'Foldable Shelf',
        'Active Fresh Filter'
    ],

    'BMF': [
        'Samsung Brand/Tech Topper',
        '20 Years Warranty',
        'Key features POP',
        'Side POP',
        'Global No.1',
        'Led Lighting POP',
        'Full Open Box POP',
        'Big Guard POP',
        'Adjustable Pin',
        'Saves Energy POP',
        'Gentle Lighting',
        'Multi Tray',
        'All-Around Cooling',
        '2 Step Foldable Shelf',
        'Big Fresh Box'
    ],

    'Local TMF': [
        'Samsung Brand/Tech Topper',
        'Key features POP',
        'Side POP',
        'Big Vegetables Box POP'
    ]
};

let modelCounter = 1;

// Initialize data entry functionality
document.addEventListener('DOMContentLoaded', function () {
    initializeDataEntry();
});

function initializeDataEntry() {
    // Load categories first
    loadCategories();

    // Set up event listeners for the first model entry
    setupModelEntry(0);

    // Add model button functionality
    const addModelBtn = document.getElementById('addModelBtn');
    if (addModelBtn) {
        addModelBtn.addEventListener('click', addNewModelEntry);
    }

    // Form submission handling
    const dataEntryForm = document.getElementById('dataEntryForm');
    if (dataEntryForm) {
        dataEntryForm.addEventListener('submit', handleFormSubmission);
    }
}

function loadCategories() {
    fetch('/get_dynamic_data/categories')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const categorySelects = document.querySelectorAll('.category-select');
                categorySelects.forEach(select => {
                    // Keep the default option
                    const defaultOption = select.querySelector('option[value=""]');
                    select.innerHTML = '';
                    if (defaultOption) {
                        select.appendChild(defaultOption);
                    } else {
                        const option = document.createElement('option');
                        option.value = '';
                        option.textContent = 'Select Category';
                        select.appendChild(option);
                    }

                    // Add categories from database
                    data.data.forEach(category => {
                        const option = document.createElement('option');
                        option.value = category;
                        option.textContent = category;
                        select.appendChild(option);
                    });
                });
            }
        })
        .catch(error => {
            console.error('Error loading categories:', error);
        });
}

function setupModelEntry(index) {
    const categorySelect = document.getElementById(`category_${index}`);
    const modelSelect = document.getElementById(`model_${index}`);

    if (categorySelect) {
        categorySelect.addEventListener('change', function () {
            handleCategoryChange(index, this.value);
        });
    }

    if (modelSelect) {
        modelSelect.addEventListener('change', function () {
            handleModelChange(index, this.value);
        });
    }

    // Setup branch autocomplete
    setupBranchAutocomplete(index);

    // Setup image upload preview
    setupImageUpload(index);
}

function handleCategoryChange(index, category) {
    const modelSelect = document.getElementById(`model_${index}`);

    // Clear model dropdown
    modelSelect.innerHTML = '<option value="">Select Model</option>';
    modelSelect.disabled = true;

    if (category) {
        // Fetch models from database
        fetch(`/get_dynamic_data/models?category=${encodeURIComponent(category)}`)
            .then(response => response.json())
            .then(data => {
                if (data.success && data.data.length > 0) {
                    data.data.forEach(model => {
                        const option = document.createElement('option');
                        option.value = model;
                        option.textContent = model;
                        modelSelect.appendChild(option);
                    });
                    modelSelect.disabled = false;
                }
            })
            .catch(error => {
                console.error('Error loading models:', error);
            });
    }

    // Hide subsequent sections when category changes
    hideSubsequentSections(index);
}

function handleModelChange(index, model) {
    if (model) {
        showDisplayTypeSection(index);
        showPopMaterialSection(index);
        showImageUploadSection(index);
    } else {
        hideSubsequentSections(index);
    }
}

function showDisplayTypeSection(index) {
    const section = document.querySelector(`[data-index="${index}"] .display-type-section`);
    const select = document.querySelector(`[data-index="${index}"] .display-type-select`);
    const categorySelect = document.getElementById(`category_${index}`);

    if (section && select && categorySelect) {
        const selectedCategory = categorySelect.value;

        // Clear display type options
        select.innerHTML = '<option value="">Select Display Type</option>';

        if (selectedCategory) {
            // Fetch display types from database
            fetch(`/get_dynamic_data/display_types?category=${encodeURIComponent(selectedCategory)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.data.length > 0) {
                        data.data.forEach(type => {
                            const option = document.createElement('option');
                            option.value = type;
                            option.textContent = type;
                            select.appendChild(option);
                        });
                    }
                })
                .catch(error => {
                    console.error('Error loading display types:', error);
                });
        }

        section.style.display = 'block';
    }
}

function showPopMaterialSection(index) {
    const section = document.querySelector(`[data-index="${index}"] .pop-material-section`);
    const container = document.querySelector(`[data-index="${index}"] .checklist-container`);
    const modelSelect = document.getElementById(`model_${index}`);

    if (section && container && modelSelect) {
        const selectedModel = modelSelect.value;

        // Clear existing items
        container.innerHTML = '';

        if (selectedModel) {
            // Fetch POP materials from database by model
            fetch(`/get_dynamic_data/pop_materials?model=${encodeURIComponent(selectedModel)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.data.length > 0) {
                        // Create checklist items
                        data.data.forEach((material, materialIndex) => {
                            const checkboxDiv = document.createElement('div');
                            checkboxDiv.className = 'checkbox-item';

                            const checkbox = document.createElement('input');
                            checkbox.type = 'checkbox';
                            checkbox.id = `pop_${index}_${materialIndex}`;
                            checkbox.name = `pop_materials_${index}`;
                            checkbox.value = material;

                            const label = document.createElement('label');
                            label.htmlFor = `pop_${index}_${materialIndex}`;
                            label.textContent = material;

                            checkboxDiv.appendChild(checkbox);
                            checkboxDiv.appendChild(label);
                            container.appendChild(checkboxDiv);
                        });
                    } else {
                        // Show message if no materials found for this model
                        const noMaterialsDiv = document.createElement('div');
                        noMaterialsDiv.className = 'no-materials-message';
                        noMaterialsDiv.textContent = 'No POP materials configured for this model yet.';
                        container.appendChild(noMaterialsDiv);
                    }
                })
                .catch(error => {
                    console.error('Error loading POP materials:', error);
                });
        }

        section.style.display = 'block';
    }
}

function showImageUploadSection(index) {
    const section = document.querySelector(`[data-index="${index}"] .image-upload-section`);
    if (section) {
        section.style.display = 'block';
    }
}

function hideSubsequentSections(index) {
    const modelEntry = document.querySelector(`[data-index="${index}"]`);
    if (modelEntry) {
        const sections = ['.display-type-section', '.pop-material-section', '.image-upload-section'];
        sections.forEach(sectionClass => {
            const section = modelEntry.querySelector(sectionClass);
            if (section) {
                section.style.display = 'none';
            }
        });
    }
}

function setupBranchAutocomplete(index) {
    const branchInput = document.getElementById(`branch_${index}`);
    const shopCodeInput = document.getElementById(`shop_code_${index}`);
    const suggestionsContainer = document.getElementById(`suggestions_${index}`);

    if (!branchInput || !shopCodeInput || !suggestionsContainer) return;

    let currentSuggestions = [];
    let selectedIndex = -1;

    // Handle branch input changes
    branchInput.addEventListener('input', function () {
        const searchTerm = this.value.trim();

        if (searchTerm.length >= 1) {
            fetchBranches(searchTerm, index);
        } else {
            hideSuggestions(index);
        }
    });

    // Handle shop code input changes
    shopCodeInput.addEventListener('input', function () {
        const shopCode = this.value.trim();

        if (shopCode.length >= 2) {
            // Search for branch by shop code
            fetchBranchByCode(shopCode, index);
        }
    });

    // Handle keyboard navigation for branch input
    branchInput.addEventListener('keydown', function (e) {
        const suggestions = suggestionsContainer.querySelectorAll('.autocomplete-suggestion');

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                selectedIndex = Math.min(selectedIndex + 1, suggestions.length - 1);
                updateHighlight(suggestions);
                break;

            case 'ArrowUp':
                e.preventDefault();
                selectedIndex = Math.max(selectedIndex - 1, -1);
                updateHighlight(suggestions);
                break;

            case 'Enter':
                e.preventDefault();
                if (selectedIndex >= 0 && suggestions[selectedIndex]) {
                    const suggestionData = suggestions[selectedIndex].dataset;
                    selectBranch(suggestionData.name, suggestionData.code, index);
                }
                break;

            case 'Escape':
                hideSuggestions(index);
                break;
        }
    });

    // Handle focus and blur
    branchInput.addEventListener('focus', function () {
        if (this.value.trim().length >= 1) {
            fetchBranches(this.value.trim(), index);
        }
    });

    branchInput.addEventListener('blur', function () {
        // Delay hiding to allow clicking on suggestions
        setTimeout(() => hideSuggestions(index), 200);
    });

    function updateHighlight(suggestions) {
        suggestions.forEach((suggestion, idx) => {
            suggestion.classList.toggle('highlighted', idx === selectedIndex);
        });
    }
}

function fetchBranches(searchTerm, index) {
    fetch(`/get_branches?search=${encodeURIComponent(searchTerm)}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showSuggestions(data.branches, index);
            }
        })
        .catch(error => {
            console.error('Error fetching branches:', error);
        });
}

function showSuggestions(branches, index) {
    const suggestionsContainer = document.getElementById(`suggestions_${index}`);
    if (!suggestionsContainer) return;

    suggestionsContainer.innerHTML = '';

    if (branches.length === 0) {
        const noSuggestion = document.createElement('div');
        noSuggestion.className = 'no-suggestions';
        noSuggestion.textContent = 'No existing branches found. Enter branch name and shop code to create new.';
        suggestionsContainer.appendChild(noSuggestion);
    } else {
        branches.forEach(branch => {
            const suggestion = document.createElement('div');
            suggestion.className = 'autocomplete-suggestion';
            suggestion.dataset.name = branch.name;
            suggestion.dataset.code = branch.code;
            suggestion.innerHTML = `<strong>${branch.name}</strong><br><small>Code: ${branch.code}</small>`;

            suggestion.addEventListener('click', function () {
                selectBranch(branch.name, branch.code, index);
            });

            suggestionsContainer.appendChild(suggestion);
        });
    }

    suggestionsContainer.style.display = 'block';
}

function selectBranch(branchName, shopCode, index) {
    const branchInput = document.getElementById(`branch_${index}`);
    const shopCodeInput = document.getElementById(`shop_code_${index}`);

    if (branchInput && shopCodeInput) {
        branchInput.value = branchName;
        shopCodeInput.value = shopCode;
        hideSuggestions(index);
    }
}

function fetchBranchByCode(shopCode, index) {
    fetch(`/get_branch_by_code?code=${encodeURIComponent(shopCode)}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const branchInput = document.getElementById(`branch_${index}`);
                if (branchInput) {
                    branchInput.value = data.branch.name;
                }
            }
        })
        .catch(error => {
            console.error('Error fetching branch by code:', error);
        });
}

function hideSuggestions(index) {
    const suggestionsContainer = document.getElementById(`suggestions_${index}`);
    if (suggestionsContainer) {
        suggestionsContainer.style.display = 'none';
    }
}

function setupImageUpload(index) {
    const imageInput = document.querySelector(`[data-index="${index}"] .image-upload`);
    const previewContainer = document.querySelector(`[data-index="${index}"] .image-preview`);

    if (imageInput && previewContainer) {
        imageInput.addEventListener('change', function (e) {
            const files = e.target.files;
            
            if (validateImageFiles(files)) {
                handleImagePreview(files, previewContainer, index);
            } else {
                // Clear the input if validation fails
                e.target.value = '';
            }
        });
    }
}

// Global array to store selected files for each model entry
let selectedFiles = {};

function handleImagePreview(files, previewContainer, modelIndex) {
    // Initialize array for this model if not exists
    if (!selectedFiles[modelIndex]) {
        selectedFiles[modelIndex] = [];
    }
    
    // Add new files to existing ones
    Array.from(files).forEach(file => {
        if (file.type.startsWith('image/')) {
            selectedFiles[modelIndex].push(file);
        }
    });
    
    // Check total count limit
    if (selectedFiles[modelIndex].length > 10) {
        alert('Maximum 10 images allowed. Keeping first 10 images.');
        selectedFiles[modelIndex] = selectedFiles[modelIndex].slice(0, 10);
    }
    
    // Clear and rebuild preview
    previewContainer.innerHTML = '';
    
    // Add header with count
    if (selectedFiles[modelIndex].length > 0) {
        const header = document.createElement('div');
        header.className = 'preview-header';
        header.innerHTML = `<h5>📷 Selected Images (${selectedFiles[modelIndex].length}/10)</h5>`;
        previewContainer.appendChild(header);
        
        // Create grid container
        const gridContainer = document.createElement('div');
        gridContainer.className = 'image-preview-grid';
        previewContainer.appendChild(gridContainer);
        
        selectedFiles[modelIndex].forEach((file, index) => {
            const reader = new FileReader();
            reader.onload = function (e) {
                const previewDiv = document.createElement('div');
                previewDiv.className = 'image-preview-item';
                previewDiv.dataset.fileIndex = index;

                const img = document.createElement('img');
                img.src = e.target.result;
                img.alt = `Preview ${index + 1}`;
                img.loading = 'lazy';

                const fileName = document.createElement('span');
                fileName.textContent = `${index + 1}. ${file.name}`;
                fileName.className = 'file-name';
                
                const fileSize = document.createElement('span');
                fileSize.textContent = `(${(file.size / 1024 / 1024).toFixed(2)} MB)`;
                fileSize.className = 'file-size';

                const removeBtn = document.createElement('button');
                removeBtn.textContent = '×';
                removeBtn.className = 'remove-image-btn';
                removeBtn.type = 'button';
                removeBtn.onclick = () => removeImageFromSelection(modelIndex, index, previewContainer);

                previewDiv.appendChild(img);
                previewDiv.appendChild(fileName);
                previewDiv.appendChild(fileSize);
                previewDiv.appendChild(removeBtn);
                gridContainer.appendChild(previewDiv);
            };
            reader.readAsDataURL(file);
        });
    }
    
    // Update the file input with current selection
    updateFileInput(modelIndex);
}

function removeImageFromSelection(modelIndex, fileIndex, previewContainer) {
    if (selectedFiles[modelIndex]) {
        selectedFiles[modelIndex].splice(fileIndex, 1);
        handleImagePreview([], previewContainer, modelIndex);
    }
}

function updateFileInput(modelIndex) {
    const fileInput = document.querySelector(`[data-index="${modelIndex}"] .image-upload`);
    if (fileInput && selectedFiles[modelIndex]) {
        // Create new FileList from selected files
        const dt = new DataTransfer();
        selectedFiles[modelIndex].forEach(file => {
            dt.items.add(file);
        });
        fileInput.files = dt.files;
    }
}

function addNewModelEntry() {
    const container = document.getElementById('modelsContainer');
    const newModelEntry = createModelEntryHTML(modelCounter);

    container.insertAdjacentHTML('beforeend', newModelEntry);
    setupModelEntry(modelCounter);

    modelCounter++;

    // Scroll to the new entry
    const newEntry = document.querySelector(`[data-index="${modelCounter - 1}"]`);
    if (newEntry) {
        newEntry.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

function createModelEntryHTML(index) {
    return `
        <div class="model-entry" data-index="${index}">
            <div class="model-entry-header">
                <h3>Model Entry ${index + 1}</h3>
                <button type="button" class="btn btn-danger btn-sm remove-model-btn" onclick="removeModelEntry(${index})">Remove</button>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label for="branch_${index}">Branch Name:</label>
                    <div class="autocomplete-container">
                        <input type="text" id="branch_${index}" name="branch_${index}" class="branch-input" 
                               placeholder="Type branch name or shop code..." required autocomplete="off">
                        <div class="autocomplete-suggestions" id="suggestions_${index}"></div>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="shop_code_${index}">Shop Code:</label>
                    <input type="text" id="shop_code_${index}" name="shop_code_${index}" class="shop-code-input" 
                           placeholder="Enter shop code..." required autocomplete="off">
                </div>
            </div>
            
            <div class="form-group">
                <label for="category_${index}">Category:</label>
                <select id="category_${index}" name="category_${index}" class="category-select" required>
                    <option value="">Select Category</option>
                    <option value="OLED">OLED</option>
                    <option value="Neo QLED">Neo QLED</option>
                    <option value="QLED">QLED</option>
                    <option value="UHD">UHD</option>
                    <option value="LTV">LTV</option>
                    <option value="BESPOKE COMBO">BESPOKE COMBO</option>
                    <option value="BESPOKE Front">BESPOKE Front</option>
                    <option value="Front">Front</option>
                    <option value="TL">TL</option>
                    <option value="SBS">SBS</option>
                    <option value="TMF">TMF</option>
                    <option value="BMF">BMF</option>
                    <option value="Local TMF">Local TMF</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="model_${index}">Model:</label>
                <select id="model_${index}" name="model_${index}" class="model-select" required disabled>
                    <option value="">Select Model</option>
                </select>
            </div>
            
            <div class="display-type-section" style="display: none;">
                <h4>Display Type</h4>
                <div class="form-group">
                    <select name="display_type_${index}" class="display-type-select" required>
                        <option value="">Select Display Type</option>
                    </select>
                </div>
            </div>
            
            <div class="pop-material-section" style="display: none;">
                <h4>POP Material</h4>
                <div class="checklist-container">
                    <!-- Checklist items will be populated by JavaScript -->
                </div>
            </div>
            
            <div class="image-upload-section" style="display: none;">
                <h4>📸 Image Upload</h4>
                <div class="form-group">
                    <label for="images_${index}" class="file-upload-label">
                        <span class="upload-icon">📁</span>
                        <span class="upload-text">Choose Multiple Images</span>
                        <span class="upload-hint">(JPG, PNG, WEBP - Max 10 images)</span>
                    </label>
                    <input type="file" id="images_${index}" name="images_${index}" multiple accept="image/*,.webp,.avif" 
                           class="image-upload" style="display: none;" max="10">
                    <div class="upload-info">
                        <small>💡 You can select multiple images at once (Ctrl+Click or Shift+Click)</small>
                    </div>
                    <div class="image-preview"></div>
                </div>
            </div>
        </div>
    `;
}

function removeModelEntry(index) {
    const modelEntry = document.querySelector(`[data-index="${index}"]`);
    if (modelEntry && document.querySelectorAll('.model-entry').length > 1) {
        modelEntry.remove();
    } else {
        alert('At least one model entry is required.');
    }
}

function handleFormSubmission(e) {
    e.preventDefault();

    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"]');

    // Show loading state
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Saving...';
    submitBtn.disabled = true;

    // Validate form
    if (!validateForm(form)) {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
        return;
    }

    // Create FormData object
    const formData = new FormData(form);

    // Submit form
    fetch(form.action, {
        method: 'POST',
        body: formData
    })
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            throw new Error('Network response was not ok');
        })
        .then(data => {
            if (data.success) {
                showSuccessMessage('Data saved successfully!');
                form.reset();
                resetFormState();
            } else {
                throw new Error(data.message || 'Failed to save data');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showErrorMessage('Failed to save data. Please try again.');
        })
        .finally(() => {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        });
}

function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('error');
            isValid = false;
        } else {
            field.classList.remove('error');
        }
    });

    if (!isValid) {
        showErrorMessage('Please fill in all required fields.');
    }

    return isValid;
}

function resetFormState() {
    // Reset to single model entry
    const container = document.getElementById('modelsContainer');
    const firstEntry = container.querySelector('.model-entry');

    // Remove all entries except the first one
    const allEntries = container.querySelectorAll('.model-entry');
    allEntries.forEach((entry, index) => {
        if (index > 0) {
            entry.remove();
        }
    });

    // Reset the first entry
    if (firstEntry) {
        hideSubsequentSections(0);
        const modelSelect = firstEntry.querySelector('.model-select');
        const categorySelect = firstEntry.querySelector('.category-select');

        if (modelSelect) {
            modelSelect.disabled = true;
            modelSelect.innerHTML = '<option value="">Select Model</option>';
        }

        if (categorySelect) {
            categorySelect.selectedIndex = 0;
        }
    }

    modelCounter = 1;
}

function showSuccessMessage(message) {
    showMessage(message, 'success');
}

function showErrorMessage(message) {
    showMessage(message, 'error');
}

function showMessage(message, type) {
    // Remove existing messages
    const existingMessages = document.querySelectorAll('.flash-message');
    existingMessages.forEach(msg => msg.remove());

    // Create new message
    const messageDiv = document.createElement('div');
    messageDiv.className = `flash-message alert alert-${type}`;
    messageDiv.textContent = message;

    // Insert at top of form
    const form = document.getElementById('dataEntryForm');
    form.insertBefore(messageDiv, form.firstChild);

    // Auto-hide after 5 seconds
    setTimeout(() => {
        messageDiv.style.opacity = '0';
        setTimeout(() => {
            messageDiv.remove();
        }, 300);
    }, 5000);
}

// This function is now replaced by removeImageFromSelection

function validateImageFiles(files) {
    const maxFiles = 10;
    const maxSize = 10 * 1024 * 1024; // 10MB per file
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/avif'];
    
    if (files.length > maxFiles) {
        alert(`Maximum ${maxFiles} images allowed. Please select fewer images.`);
        return false;
    }
    
    for (let file of files) {
        if (!allowedTypes.includes(file.type)) {
            alert(`File "${file.name}" is not a supported image format. Please use JPG, PNG, WEBP, or AVIF.`);
            return false;
        }
        
        if (file.size > maxSize) {
            alert(`File "${file.name}" is too large (${(file.size / 1024 / 1024).toFixed(2)}MB). Maximum size is 10MB per image.`);
            return false;
        }
    }
    
    return true;
}

// setupImageUpload function is defined above with the new functionality
// Drag and Drop functionality for images
function setupDragAndDrop(index) {
    const uploadLabel = document.querySelector(`[data-index="${index}"] .file-upload-label`);
    const fileInput = document.querySelector(`[data-index="${index}"] .image-upload`);
    const previewContainer = document.querySelector(`[data-index="${index}"] .image-preview`);
    
    if (!uploadLabel || !fileInput || !previewContainer) return;
    
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadLabel.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });
    
    // Highlight drop area when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadLabel.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        uploadLabel.addEventListener(eventName, unhighlight, false);
    });
    
    // Handle dropped files
    uploadLabel.addEventListener('drop', handleDrop, false);
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    function highlight(e) {
        uploadLabel.style.borderColor = '#007bff';
        uploadLabel.style.backgroundColor = 'rgba(0, 123, 255, 0.1)';
    }
    
    function unhighlight(e) {
        uploadLabel.style.borderColor = 'transparent';
        uploadLabel.style.backgroundColor = '';
    }
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (validateImageFiles(files)) {
            handleImagePreview(files, previewContainer, index);
        }
    }
}

function setupModelEntry(index) {
    const categorySelect = document.getElementById(`category_${index}`);
    const modelSelect = document.getElementById(`model_${index}`);

    if (categorySelect) {
        categorySelect.addEventListener('change', function () {
            handleCategoryChange(index, this.value);
        });
    }

    if (modelSelect) {
        modelSelect.addEventListener('change', function () {
            handleModelChange(index, this.value);
        });
    }

    // Setup branch autocomplete
    setupBranchAutocomplete(index);

    // Setup image upload preview
    setupImageUpload(index);
    
    // Setup drag and drop for images
    setupDragAndDrop(index);
}