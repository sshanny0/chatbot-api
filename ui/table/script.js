document.addEventListener('DOMContentLoaded', function() {
            // Table data - initial sample data
            let tableData = [
                { id: 1, name: "John Smith", email: "john.smith@example.com", department: "Engineering", position: "Software Engineer", status: "Active" },
                { id: 2, name: "Emma Johnson", email: "emma.j@example.com", department: "Marketing", position: "Marketing Manager", status: "Active" },
                { id: 3, name: "Michael Chen", email: "m.chen@example.com", department: "Sales", position: "Sales Executive", status: "Active" },
                { id: 4, name: "Sarah Williams", email: "sarah.w@example.com", department: "HR", position: "HR Specialist", status: "Inactive" },
                { id: 5, name: "Robert Davis", email: "robert.d@example.com", department: "Finance", position: "Financial Analyst", status: "Active" }
            ];

            // DOM elements
            const tableBody = document.getElementById('tableBody');
            const emptyState = document.getElementById('emptyState');
            const searchInput = document.getElementById('searchInput');
            const addRowBtn = document.getElementById('addRowBtn');
            const deleteSelectedBtn = document.getElementById('deleteSelectedBtn');
            const selectAllCheckbox = document.getElementById('selectAll');
            const rowModal = document.getElementById('rowModal');
            const modalTitle = document.getElementById('modalTitle');
            const rowForm = document.getElementById('rowForm');
            const cancelModalBtn = document.getElementById('cancelModalBtn');
            
            // Form inputs
            const inputName = document.getElementById('inputName');
            const inputEmail = document.getElementById('inputEmail');
            const inputDepartment = document.getElementById('inputDepartment');
            const inputPosition = document.getElementById('inputPosition');
            const inputStatus = document.getElementById('inputStatus');

            // Variables for managing row editing
            let isEditing = false;
            let editingRowId = null;
            let selectedRows = new Set();

            // Initialize the table
            function renderTable(data = tableData) {
                tableBody.innerHTML = '';
                
                if (data.length === 0) {
                    emptyState.style.display = 'block';
                    deleteSelectedBtn.style.display = 'none';
                    selectAllCheckbox.checked = false;
                    return;
                }
                
                emptyState.style.display = 'none';
                
                data.forEach(row => {
                    const tr = document.createElement('tr');
                    tr.setAttribute('data-id', row.id);
                    
                    // Check if this row is selected
                    const isSelected = selectedRows.has(row.id);
                    
                    tr.innerHTML = `
                        <td>
                            <input type="checkbox" class="row-select" ${isSelected ? 'checked' : ''} data-id="${row.id}">
                        </td>
                        <td>${row.id}</td>
                        <td class="editable-cell" data-field="name">
                            <input type="text" value="${row.name}" readonly>
                        </td>
                        <td class="editable-cell" data-field="email">
                            <input type="email" value="${row.email}" readonly>
                        </td>
                        <td class="editable-cell" data-field="department">
                            <select readonly>
                                <option value="Engineering" ${row.department === 'Engineering' ? 'selected' : ''}>Engineering</option>
                                <option value="Marketing" ${row.department === 'Marketing' ? 'selected' : ''}>Marketing</option>
                                <option value="Sales" ${row.department === 'Sales' ? 'selected' : ''}>Sales</option>
                                <option value="HR" ${row.department === 'HR' ? 'selected' : ''}>HR</option>
                                <option value="Finance" ${row.department === 'Finance' ? 'selected' : ''}>Finance</option>
                                <option value="Operations" ${row.department === 'Operations' ? 'selected' : ''}>Operations</option>
                            </select>
                        </td>
                        <td class="editable-cell" data-field="position">
                            <input type="text" value="${row.position}" readonly>
                        </td>
                        <td>
                            <span class="status ${row.status === 'Active' ? 'status-active' : 'status-inactive'}">
                                ${row.status}
                            </span>
                        </td>
                        <td>
                            <div class="action-buttons">
                                <button class="icon-btn edit-btn" title="Edit Row">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="icon-btn delete-btn" title="Delete Row">
                                    <i class="fas fa-trash-alt"></i>
                                </button>
                            </div>
                        </td>
                    `;
                    
                    tableBody.appendChild(tr);
                });
                
                // Show/hide delete selected button
                deleteSelectedBtn.style.display = selectedRows.size > 0 ? 'inline-flex' : 'none';
            }

            // Generate a new ID
            function generateNewId() {
                return tableData.length > 0 ? Math.max(...tableData.map(row => row.id)) + 1 : 1;
            }

            // Add new row
            function addRow(rowData) {
                const newId = generateNewId();
                const newRow = { id: newId, ...rowData };
                tableData.push(newRow);
                renderTable();
            }

            // Update existing row
            function updateRow(id, updatedData) {
                const index = tableData.findIndex(row => row.id === id);
                if (index !== -1) {
                    tableData[index] = { ...tableData[index], ...updatedData };
                    renderTable();
                }
            }

            // Delete row by ID
            function deleteRow(id) {
                tableData = tableData.filter(row => row.id !== id);
                selectedRows.delete(id);
                renderTable();
            }

            // Delete selected rows
            function deleteSelectedRows() {
                if (selectedRows.size === 0) return;
                
                if (confirm(`Are you sure you want to delete ${selectedRows.size} selected row(s)?`)) {
                    tableData = tableData.filter(row => !selectedRows.has(row.id));
                    selectedRows.clear();
                    renderTable();
                }
            }

            // Search functionality
            function searchTable(query) {
                if (!query.trim()) {
                    renderTable();
                    return;
                }
                
                const lowerCaseQuery = query.toLowerCase();
                const filteredData = tableData.filter(row => 
                    row.name.toLowerCase().includes(lowerCaseQuery) ||
                    row.email.toLowerCase().includes(lowerCaseQuery) ||
                    row.department.toLowerCase().includes(lowerCaseQuery) ||
                    row.position.toLowerCase().includes(lowerCaseQuery) ||
                    row.status.toLowerCase().includes(lowerCaseQuery)
                );
                
                renderTable(filteredData);
            }

            // Open modal for adding/editing
            function openModal(rowId = null) {
                if (rowId) {
                    // Editing existing row
                    isEditing = true;
                    editingRowId = rowId;
                    modalTitle.textContent = 'Edit Row';
                    
                    const row = tableData.find(r => r.id === rowId);
                    if (row) {
                        inputName.value = row.name;
                        inputEmail.value = row.email;
                        inputDepartment.value = row.department;
                        inputPosition.value = row.position;
                        inputStatus.value = row.status;
                    }
                } else {
                    // Adding new row
                    isEditing = false;
                    editingRowId = null;
                    modalTitle.textContent = 'Add New Row';
                    rowForm.reset();
                }
                
                rowModal.style.display = 'flex';
            }

            // Close modal
            function closeModal() {
                rowModal.style.display = 'none';
                isEditing = false;
                editingRowId = null;
                rowForm.reset();
            }

            // Initialize table with sample data
            renderTable();

            // Event Listeners

            // Search input
            searchInput.addEventListener('input', function() {
                searchTable(this.value);
            });

            // Add row button
            addRowBtn.addEventListener('click', function() {
                openModal();
            });

            // Delete selected button
            deleteSelectedBtn.addEventListener('click', deleteSelectedRows);

            // Select all checkbox
            selectAllCheckbox.addEventListener('change', function() {
                const rowCheckboxes = document.querySelectorAll('.row-select');
                rowCheckboxes.forEach(checkbox => {
                    checkbox.checked = this.checked;
                    const rowId = parseInt(checkbox.getAttribute('data-id'));
                    
                    if (this.checked) {
                        selectedRows.add(rowId);
                    } else {
                        selectedRows.delete(rowId);
                    }
                });
                
                deleteSelectedBtn.style.display = this.checked ? 'inline-flex' : 'none';
            });

            // Table body event delegation
            tableBody.addEventListener('click', function(e) {
                const target = e.target;
                const row = target.closest('tr');
                if (!row) return;
                
                const rowId = parseInt(row.getAttribute('data-id'));
                
                // Edit button click
                if (target.closest('.edit-btn')) {
                    openModal(rowId);
                }
                
                // Delete button click
                if (target.closest('.delete-btn')) {
                    if (confirm('Are you sure you want to delete this row?')) {
                        deleteRow(rowId);
                    }
                }
                
                // Row checkbox click
                if (target.classList.contains('row-select')) {
                    const isChecked = target.checked;
                    
                    if (isChecked) {
                        selectedRows.add(rowId);
                    } else {
                        selectedRows.delete(rowId);
                        selectAllCheckbox.checked = false;
                    }
                    
                    deleteSelectedBtn.style.display = selectedRows.size > 0 ? 'inline-flex' : 'none';
                }
            });

            // Double-click to edit inline
            tableBody.addEventListener('dblclick', function(e) {
                const target = e.target;
                if (!target.classList.contains('editable-cell')) return;
                
                const input = target.querySelector('input, select');
                if (!input) return;
                
                // Make editable
                input.removeAttribute('readonly');
                input.focus();
                
                // Save on blur
                const saveOnBlur = function() {
                    input.setAttribute('readonly', true);
                    
                    const row = input.closest('tr');
                    const rowId = parseInt(row.getAttribute('data-id'));
                    const field = target.getAttribute('data-field');
                    const value = input.value;
                    
                    // Update data
                    const index = tableData.findIndex(row => row.id === rowId);
                    if (index !== -1) {
                        tableData[index][field] = value;
                        
                        // If status field changed, re-render the status badge
                        if (field === 'status') {
                            renderTable();
                        }
                    }
                    
                    input.removeEventListener('blur', saveOnBlur);
                    input.removeEventListener('keydown', saveOnEnter);
                };
                
                // Save on Enter key
                const saveOnEnter = function(e) {
                    if (e.key === 'Enter') {
                        saveOnBlur();
                    }
                };
                
                input.addEventListener('blur', saveOnBlur);
                input.addEventListener('keydown', saveOnEnter);
            });

            // Modal form submission
            rowForm.addEventListener('submit', function(e) {
                e.preventDefault();
                
                const rowData = {
                    name: inputName.value,
                    email: inputEmail.value,
                    department: inputDepartment.value,
                    position: inputPosition.value,
                    status: inputStatus.value
                };
                
                if (isEditing && editingRowId) {
                    updateRow(editingRowId, rowData);
                } else {
                    addRow(rowData);
                }
                
                closeModal();
            });

            // Cancel modal button
            cancelModalBtn.addEventListener('click', closeModal);

            // Close modal when clicking outside
            window.addEventListener('click', function(e) {
                if (e.target === rowModal) {
                    closeModal();
                }
            });
        });