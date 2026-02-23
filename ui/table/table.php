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

<!-- MODAL QNA BUTTON -->
 <div id="addModal" class="modal">
  <div class="modal-content">
    <h3>Tambah QnA</h3>

    <form id="addForm">
      <label>Question</label>
      <textarea id="newQuestion" required></textarea>

      <label>Category</label>
      <select name="category" id="newCategory">
      </select>

      <label>Answer</label>
      <textarea id="newAnswer" required></textarea>

      <label>Hyperlink</label>
      <input type="text" id="newHyperlink" />

      <label>Tag</label>
      <input type="text" id="newTag" />

      <label>Status</label>
      <select id="newStatus">
        <option value="aktif">Aktif</option>
        <option value="nonaktif">Non-aktif</option>
      </select>

      <div class="modal-actions">
        <button type="button" id="cancelAdd">Cancel</button>
        <button type="submit" class="primary">Save</button>
      </div>
    </form>
  </div>
</div>

<script src="script.js"></script>

</html>