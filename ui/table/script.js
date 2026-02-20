let currentPage = 1;
let limit = 10;
let selectedRows = new Set();

document.addEventListener("DOMContentLoaded", function () {
  loadData();
});

async function loadData(page = 1) {
  try {
    currentPage = page;

    const response = await fetch(
      `http://127.0.0.1:8000/crud/list?page=${page}&limit=${limit}`,
    ); // pastikan endpoint benar
    const result = await response.json();

    renderTable(result.data);
    renderPagination(result.total, result.page);
  } catch (error) {
    console.error("Error fetching data:", error);
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
