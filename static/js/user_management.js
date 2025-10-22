// User Management JavaScript

let deleteUserId = null;

// Initialize user management
document.addEventListener('DOMContentLoaded', function() {
    initializeUserManagement();
});

function initializeUserManagement() {
    // Setup form submissions
    document.getElementById('userForm').addEventListener('submit', handleUserFormSubmit);
    document.getElementById('passwordForm').addEventListener('submit', handlePasswordFormSubmit);
    
    // Setup password confirmation validation
    document.getElementById('confirm-password').addEventListener('input', validatePasswordConfirmation);
}

function showAddUserModal() {
    document.getElementById('user-modal-title').textContent = 'Add New User';
    document.getElementById('user-id').value = '';
    document.getElementById('user-name').value = '';
    document.getElementById('user-company-code').value = '';
    document.getElementById('user-password').value = '';
    document.getElementById('user-password').required = true;
    document.getElementById('user-is-admin').checked = false;
    document.getElementById('password-help').style.display = 'none';
    
    document.getElementById('userModal').style.display = 'block';
}

function editUser(id, name, companyCode, isAdmin) {
    document.getElementById('user-modal-title').textContent = 'Edit User';
    document.getElementById('user-id').value = id;
    document.getElementById('user-name').value = name;
    document.getElementById('user-company-code').value = companyCode;
    document.getElementById('user-password').value = '';
    document.getElementById('user-password').required = false;
    document.getElementById('user-is-admin').checked = isAdmin;
    document.getElementById('password-help').style.display = 'block';
    
    document.getElementById('userModal').style.display = 'block';
}

function editUserFromButton(button) {
    const id = button.dataset.userId;
    const name = button.dataset.userName;
    const companyCode = button.dataset.userCode;
    const isAdmin = button.dataset.userAdmin === 'True';
    
    editUser(id, name, companyCode, isAdmin);
}

function deleteUser(id, name) {
    deleteUserId = id;
    document.getElementById('delete-user-name').textContent = name;
    document.getElementById('deleteUserModal').style.display = 'block';
}

function deleteUserFromButton(button) {
    const id = button.dataset.userId;
    const name = button.dataset.userName;
    
    deleteUser(id, name);
}

function confirmDeleteUser() {
    if (!deleteUserId) return;
    
    const data = {
        action: 'delete',
        id: deleteUserId
    };
    
    fetch('/manage_user', {
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
            setTimeout(() => {
                location.reload();
            }, 1500);
        } else {
            showMessage('Error: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error deleting user:', error);
        showMessage('Error deleting user', 'error');
    })
    .finally(() => {
        closeDeleteUserModal();
    });
}

function handleUserFormSubmit(e) {
    e.preventDefault();
    
    const userId = document.getElementById('user-id').value;
    const name = document.getElementById('user-name').value;
    const companyCode = document.getElementById('user-company-code').value;
    const password = document.getElementById('user-password').value;
    const isAdmin = document.getElementById('user-is-admin').checked;
    
    // Validation
    if (!name || !companyCode) {
        showMessage('Please fill in all required fields', 'error');
        return;
    }
    
    if (!userId && !password) {
        showMessage('Password is required for new users', 'error');
        return;
    }
    
    if (password && password.length < 6) {
        showMessage('Password must be at least 6 characters long', 'error');
        return;
    }
    
    const data = {
        action: userId ? 'edit' : 'add',
        id: userId || undefined,
        name: name,
        company_code: companyCode,
        password: password || undefined,
        is_admin: isAdmin
    };
    
    fetch('/manage_user', {
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
            closeUserModal();
            setTimeout(() => {
                location.reload();
            }, 1500);
        } else {
            showMessage('Error: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error saving user:', error);
        showMessage('Error saving user', 'error');
    });
}

function showChangePasswordModal() {
    document.getElementById('current-password').value = '';
    document.getElementById('new-password').value = '';
    document.getElementById('confirm-password').value = '';
    document.getElementById('passwordModal').style.display = 'block';
}

function handlePasswordFormSubmit(e) {
    e.preventDefault();
    
    const currentPassword = document.getElementById('current-password').value;
    const newPassword = document.getElementById('new-password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    
    // Validation
    if (!currentPassword || !newPassword || !confirmPassword) {
        showMessage('Please fill in all fields', 'error');
        return;
    }
    
    if (newPassword.length < 6) {
        showMessage('New password must be at least 6 characters long', 'error');
        return;
    }
    
    if (newPassword !== confirmPassword) {
        showMessage('New passwords do not match', 'error');
        return;
    }
    
    const data = {
        current_password: currentPassword,
        new_password: newPassword
    };
    
    fetch('/change_admin_password', {
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
            closePasswordModal();
        } else {
            showMessage('Error: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error changing password:', error);
        showMessage('Error changing password', 'error');
    });
}

function validatePasswordConfirmation() {
    const newPassword = document.getElementById('new-password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    
    if (confirmPassword && newPassword !== confirmPassword) {
        document.getElementById('confirm-password').setCustomValidity('Passwords do not match');
    } else {
        document.getElementById('confirm-password').setCustomValidity('');
    }
}

function closeUserModal() {
    document.getElementById('userModal').style.display = 'none';
}

function closePasswordModal() {
    document.getElementById('passwordModal').style.display = 'none';
}

function closeDeleteUserModal() {
    document.getElementById('deleteUserModal').style.display = 'none';
    deleteUserId = null;
}

function showMessage(message, type) {
    // Remove existing messages
    const existingMessages = document.querySelectorAll('.flash-message');
    existingMessages.forEach(msg => msg.remove());
    
    // Create new message
    const messageDiv = document.createElement('div');
    messageDiv.className = `flash-message alert alert-${type}`;
    messageDiv.textContent = message;
    
    // Insert at top of container
    const container = document.querySelector('.admin-container');
    container.insertBefore(messageDiv, container.firstChild);
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        messageDiv.style.opacity = '0';
        setTimeout(() => {
            messageDiv.remove();
        }, 300);
    }, 5000);
}

// Close modals when clicking outside
window.addEventListener('click', function(e) {
    const userModal = document.getElementById('userModal');
    const passwordModal = document.getElementById('passwordModal');
    const deleteUserModal = document.getElementById('deleteUserModal');
    
    if (e.target === userModal) {
        closeUserModal();
    }
    
    if (e.target === passwordModal) {
        closePasswordModal();
    }
    
    if (e.target === deleteUserModal) {
        closeDeleteUserModal();
    }
});

// Branches Management
let currentBranchUserId = null;

function showBranchesModal(button) {
    const userId = button.dataset.userId;
    const userName = button.dataset.userName;
    
    currentBranchUserId = userId;
    
    document.getElementById('branches-modal-title').textContent = `Manage Branches for ${userName}`;
    document.getElementById('branchesModal').style.display = 'block';
    
    loadUserBranches(userId);
}

function closeBranchesModal() {
    document.getElementById('branchesModal').style.display = 'none';
    currentBranchUserId = null;
}

function loadUserBranches(userId) {
    fetch(`/get_user_branches/${userId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayCurrentBranches(data.user_branches);
                populateAvailableBranches(data.all_branches, data.user_branches);
            } else {
                showMessage('Error loading branches: ' + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error loading branches:', error);
            showMessage('Error loading branches', 'error');
        });
}

function displayCurrentBranches(userBranches) {
    const container = document.getElementById('current-branches-list');
    container.innerHTML = '';
    
    if (userBranches.length === 0) {
        container.innerHTML = '<p class="no-branches">No branches assigned</p>';
        return;
    }
    
    userBranches.forEach(branch => {
        const branchElement = document.createElement('div');
        branchElement.className = 'branch-item';
        branchElement.innerHTML = `
            <span class="branch-name">${branch}</span>
            <button class="btn btn-sm btn-danger" onclick="removeBranchFromUser('${branch}')">
                Remove
            </button>
        `;
        container.appendChild(branchElement);
    });
}

function populateAvailableBranches(allBranches, userBranches) {
    const select = document.getElementById('available-branches-select');
    select.innerHTML = '<option value="">Select a branch to add</option>';
    
    // Filter out branches already assigned to user
    const availableBranches = allBranches.filter(branch => !userBranches.includes(branch));
    
    availableBranches.forEach(branch => {
        const option = document.createElement('option');
        option.value = branch;
        option.textContent = branch;
        select.appendChild(option);
    });
    
    if (availableBranches.length === 0) {
        select.innerHTML = '<option value="">All branches already assigned</option>';
    }
}

function addBranchToUser() {
    const select = document.getElementById('available-branches-select');
    const branchName = select.value;
    
    if (!branchName) {
        showMessage('Please select a branch to add', 'error');
        return;
    }
    
    manageBranch('add', branchName);
}

function removeBranchFromUser(branchName) {
    if (confirm(`Are you sure you want to remove "${branchName}" from this user?`)) {
        manageBranch('remove', branchName);
    }
}

function manageBranch(action, branchName) {
    const data = {
        user_id: currentBranchUserId,
        action: action,
        branch_name: branchName
    };
    
    fetch('/manage_user_branches', {
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
            loadUserBranches(currentBranchUserId); // Reload branches
            
            // Refresh the main table to show updated branches
            setTimeout(() => {
                location.reload();
            }, 1000);
        } else {
            showMessage('Error: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error managing branch:', error);
        showMessage('Error managing branch', 'error');
    });
}

// Close modals when clicking outside
window.addEventListener('click', function(e) {
    const branchesModal = document.getElementById('branchesModal');
    
    if (e.target === branchesModal) {
        closeBranchesModal();
    }
});