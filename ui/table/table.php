<html>
<link rel="stylesheet" href="../../public/assets/fonts/fontawesome/css/all.min.css">
<link rel="stylesheet" href="style.css">
<div class="container">
    <div class="header">
        <h1><i class="fas fa-table"></i> Editable Data Table</h1>
        <p>Add, edit, delete, and search table entries with real-time updates</p>
    </div>

    <div class="controls">
        <div class="search-box">
            <i class="fas fa-search"></i>
            <input type="text" id="searchInput" placeholder="Search in table...">
        </div>
        <div>
            <button class="btn btn-success" id="addRowBtn">
                <i class="fas fa-plus-circle"></i> Add New Row
            </button>
            <button class="btn btn-danger" id="deleteSelectedBtn" style="display: none;">
                <i class="fas fa-trash-alt"></i> Delete Selected
            </button>
        </div>
    </div>

    <div class="table-container">
        <table id="dataTable">
            <thead>
                <tr>
                    <th width="50">
                        <input type="checkbox" id="selectAll">
                    </th>
                    <th>ID</th>
                    <th>Question</th>
                    <th>Category</th>
                    <th>Answer</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody id="tableBody">
                <!-- Table rows will be generated here -->
            </tbody>
        </table>

        <div id="emptyState" class="empty-state">
            <i class="fas fa-table"></i>
            <h3>No Data Available</h3>
            <p>Click the "Add New Row" button to add your first entry.</p>
        </div>

        <div id="pagination" class="pagination-container"></div>

    </div>

    <div class="footer">
        <p><i class="fa-solid fa-school" style="color: #007bff;"></i> Help Desk Unit TI &copy; Politeknik Siber dan
            Sandi Negara <i class="fa-solid fa-school" style="color: #007bff;"></i></p>
    </div>
</div>

<!-- Modal for adding/editing rows -->
<div class="modal" id="rowModal">
    <div class="modal-content">
        <div class="modal-header">
            <h3 id="modalTitle">Add New Row</h3>
        </div>
        <form id="rowForm">
            <div class="form-group">
                <label for="inputName">Full Name *</label>
                <input type="text" id="inputName" required>
            </div>
            <div class="form-group">
                <label for="inputEmail">Email Address *</label>
                <input type="email" id="inputEmail" required>
            </div>
            <div class="form-group">
                <label for="inputDepartment">Department *</label>
                <select id="inputDepartment" required>
                    <option value="">Select Department</option>
                    <option value="Engineering">Engineering</option>
                    <option value="Marketing">Marketing</option>
                    <option value="Sales">Sales</option>
                    <option value="HR">Human Resources</option>
                    <option value="Finance">Finance</option>
                    <option value="Operations">Operations</option>
                </select>
            </div>
            <div class="form-group">
                <label for="inputPosition">Position *</label>
                <input type="text" id="inputPosition" required>
            </div>
            <div class="form-group">
                <label for="inputStatus">Status *</label>
                <select id="inputStatus" required>
                    <option value="Active">Active</option>
                    <option value="Inactive">Inactive</option>
                </select>
            </div>
            <div class="modal-actions">
                <button type="button" class="btn btn-danger" id="cancelModalBtn">Cancel</button>
                <button type="submit" class="btn btn-success">Save Row</button>
            </div>
        </form>
    </div>
</div>
<script src="script.js"></script>

</html>