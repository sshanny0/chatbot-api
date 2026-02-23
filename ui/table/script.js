const tableBody = document.getElementById("tableBody");
const addItemBtn = document.getElementById("addItemBtn");
const addRowBtn = document.getElementById("addRowBtn");
const addModal = document.getElementById("addModal");
const cancelAdd = document.getElementById("cancelAdd");
const addForm = document.getElementById("addForm");

let currentPage = 1;
let limit = 10;
let selectedRows = new Set();
let tableData = [];

document.addEventListener("DOMContentLoaded", function () {
  loadData();
  loadCategories();
});

// FETCH DATATABLE
async function loadData(page = 1) {
  try {
    currentPage = page;

    const response = await fetch(
      `http://localhost:8000/crud/list?page=${page}&limit=${limit}`,
    ); // pastikan endpoint benar
    const result = await response.json();

    tableData = result.data; 

    renderTable(tableData);
    renderPagination(result.total, result.page);
  } catch (error) {
    console.error("Error fetching data:", error);
  }
}

// LOAD CATEGORY MODAL
async function loadCategories() {
  try {
    const response = await fetch(`http://localhost:8000/chatbot/categories`);
    const categories = await response.json();

    const newCategory = document.getElementById("newCategory");
    newCategory.innerHTML = '<option value="">Select Category</option>';

    categories.forEach((category) => {
      const option = document.createElement("option");
      option.value = category.category;
      option.textContent = category.category;
      newCategory.appendChild(option);
    });
  } catch (error) {
    console.error("Error loading categories:", error);
  }
}

function renderTable(data) {
  tableBody.innerHTML = "";

  if (!data || data.length === 0) {
    emptyState.style.display = "block";
    return;
  }

  emptyState.style.display = "none";

  data.forEach((row) => {
    const tr = document.createElement("tr");
    tr.setAttribute("data-id", row.id);

    // Check if this row is selected
    const isSelected = selectedRows.has(row.id);
    const hasLink = row.hyperlink && row.tag;

    tr.innerHTML = `
                        <td>
                            <input type="checkbox" class="row-select" ${isSelected ? "checked" : ""} data-id="${row.id}">
                        </td>
                        <td>${row.id}</td>
                        <td class="editable-cell" data-field="question">
                            <p>${row.question}</p>
                        </td>
                        <td class="editable-cell" data-field="category">
                            <p>${row.category}</p>
                        </td>
                        </td>
                        <td class="editable-cell" data-field="answer">
                            <p>${row.answer}
                            ${
                              hasLink
                                ? `<a href="${row.hyperlink}" target="_blank">${row.tag}</a>`
                                : ""
                            }
                            </p>
                        
                        </td>
                        <td>
                            <span class="status ${row.status.toLowerCase()}">
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

  attachCheckboxEvents();

  // Show/hide delete selected button
  deleteSelectedBtn.style.display =
    selectedRows.size > 0 ? "inline-flex" : "none";
}

function attachCheckboxEvents() {
  document.querySelectorAll(".row-select").forEach((checkbox) => {
    checkbox.addEventListener("change", function () {
      const id = parseInt(this.dataset.id);

      if (this.checked) {
        selectedRows.add(id);
      } else {
        selectedRows.delete(id);
      }
    });
  });
}

function renderPagination(total, currentPage) {
  const pagination = document.getElementById("pagination");
  pagination.innerHTML = "";

  const totalPages = Math.ceil(total / limit);

  // Previous Button
  const prevBtn = document.createElement("button");
  prevBtn.innerText = "«";
  prevBtn.disabled = currentPage === 1;
  prevBtn.onclick = () => loadData(currentPage - 1);
  pagination.appendChild(prevBtn);

  for (let i = 1; i <= totalPages; i++) {
    const btn = document.createElement("button");
    btn.innerText = i;
    btn.style.margin = "5px";

    if (i === currentPage) {
      btn.style.background = "#179ed3";
      btn.style.color = "white";
    }

    btn.addEventListener("click", () => {
      loadData(i);
    });

    pagination.appendChild(btn);
  }

  // Next Button
  const nextBtn = document.createElement("button");
  nextBtn.innerText = "»";
  nextBtn.disabled = currentPage === totalPages;
  nextBtn.onclick = () => loadData(currentPage + 1);
  pagination.appendChild(nextBtn);
}

function updateRow(id, updatedData) {
  id = Number(id);

  const index = tableData.findIndex((row) => row.id === id);

  if (index !== -1) {
    tableData[index] = { ...tableData[index], ...updatedData };
    renderTable(tableData);
  }
}
// Delete row by ID
function deleteRow(id) {
  tableData = tableData.filter((row) => row.id !== id);
  selectedRows.delete(id);
  renderTable();
}

// Delete selected rows
function deleteSelectedRows() {
  if (selectedRows.size === 0) return;

  if (
    confirm(
      `Are you sure you want to delete ${selectedRows.size} selected row(s)?`,
    )
  ) {
    tableData = tableData.filter((row) => !selectedRows.has(row.id));
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
  const filteredData = tableData.filter(
    (row) =>
      row.name.toLowerCase().includes(lowerCaseQuery) ||
      row.email.toLowerCase().includes(lowerCaseQuery) ||
      row.department.toLowerCase().includes(lowerCaseQuery) ||
      row.position.toLowerCase().includes(lowerCaseQuery) ||
      row.status.toLowerCase().includes(lowerCaseQuery),
  );

  renderTable(filteredData);
}

// Open modal for adding/editing
function openModal(rowId = null) {
  if (rowId) {
    // Editing existing row
    isEditing = true;
    editingRowId = rowId;
    modalTitle.textContent = "Edit Row";

    const row = tableData.find((r) => r.id === rowId);
    if (row) {
      newQuestion.value = row.question;
      newCategory.value = row.category;
      newAnswer.value = row.answer;
      newHyperlink.value = row.hyperlink;
      newTag.value = row.tag;
      newStatus.value = row.status;
    }
  } else {
    // Adding new row
    isEditing = false;
    editingRowId = null;
    modalTitle.textContent = "Add New Row";
    addForm.reset();
  }

  addModal.style.display = "flex";
}

// Event listener for search input
// MODAL BUTTON
addRowBtn.addEventListener("click", function () {
  openModal();
});

cancelAdd.addEventListener("click", () => {
  addModal.style.display = "none";
  addForm.reset();
});

window.addEventListener("click", (e) => {
  if (e.target === addModal) {
    addModal.style.display = "none";
  }
});

// LISTENER FOR SUBMIT, EDITING
addForm.addEventListener("submit", async function (e) {
  e.preventDefault();

  const formData = {
    question: newQuestion.value,
    category: newCategory.value,
    answer: newAnswer.value,
    hyperlink: newHyperlink.value,
    tag: newTag.value,
    status: newStatus.value,
  };

  try {
    if (isEditing && editingRowId !== null) {
      // 🔥 UPDATE MODE
      await fetch(
        `http://localhost:8000/crud/update/${editingRowId}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(formData),
        }
      );
    } else {
      // 🔥 ADD MODE
      await fetch("http://localhost:8000/crud/add", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });
    }

    addModal.style.display = "none";
    addForm.reset();

    isEditing = false;
    editingRowId = null;

    await loadData(currentPage);

  } catch (error) {
    console.error("Error submitting form:", error);
  }
});

// Table body event delegation
tableBody.addEventListener("click", function (e) {
  const target = e.target;
  const row = target.closest("tr");
  if (!row) return;

  const rowId = parseInt(row.getAttribute("data-id"));

  // Edit button click
  if (target.closest(".edit-btn")) {
    openModal(rowId);
  }

  // Delete button click
  if (target.closest(".delete-btn")) {
    if (confirm("Are you sure you want to delete this row?")) {
      deleteRow(rowId);
    }
  }

  // Row checkbox click
  if (target.classList.contains("row-select")) {
    const isChecked = target.checked;

    if (isChecked) {
      selectedRows.add(rowId);
    } else {
      selectedRows.delete(rowId);
      selectAllCheckbox.checked = false;
    }

    deleteSelectedBtn.style.display =
      selectedRows.size > 0 ? "inline-flex" : "none";
  }
});
