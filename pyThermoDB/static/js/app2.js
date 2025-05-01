// PyThermoDB Table Viewer - Main JavaScript

// NOTE: DOM Elements
const searchInput = document.getElementById('searchInput');
const dataTable = document.getElementById('dataTable');
const selectButton = document.getElementById('selectButton');
const resetButton = document.getElementById('resetButton');
const darkModeToggle = document.getElementById('darkModeToggle');
const selectedDataDiv = document.getElementById('selectedData');
const currentYearSpan = document.getElementById('currentYear');
const cardSection = document.getElementById('cardSection');

// Modal elements
const tableContentModal = document.getElementById('tableContentModal');
const modalDataTable = document.getElementById('modalDataTable');
const modalSearchInput = document.getElementById('modalSearchInput');
const modalSelectButton = document.getElementById('modalSelectButton');
const modalResetButton = document.getElementById('modalResetButton');
const modalConfirmButton = document.getElementById('modalConfirmButton');
const modalSelectedData = document.getElementById('modalSelectedData');
const modalPaginationControls = document.getElementById('modalPaginationControls');

// NOTE: Global variables
let tableData = []; // Will be populated from Jinja
let selectedRow = null;
let currentPage = 1;
let filteredData = [];
const rowsPerPage = 50;
// Flag to detect if we're using the server-rendered version
const isServerRendered = document.querySelector('#dataTable tbody tr[data-index]') !== null;

// Modal variables
let modalTableData = [];
let modalSelectedRow = null;
let modalCurrentPage = 1;
let modalFilteredData = [];
let tableContentModalBS = null;

// SECTION: Initialize the application when DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Set current year in footer
    if (currentYearSpan) {
        currentYearSpan.textContent = new Date().getFullYear();
    }

    // Check for saved theme preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.body.setAttribute('data-bs-theme', savedTheme);
        updateThemeToggleButton(savedTheme);
    }

    // Setup event listeners - but only those not already set up in the server-rendered version
    setupEventListeners();

    // Initialize the Bootstrap modal
    if (tableContentModal) {
        tableContentModalBS = new bootstrap.Modal(tableContentModal);
    }

    // Generate cards dynamically from cardData
    if (typeof window.cardData !== 'undefined') {
        window.cardData.forEach((card, index) => {
            const cardDiv = document.createElement('div');
            cardDiv.className = 'col-md-4 mb-3';

            cardDiv.innerHTML = `
                <div class="card" data-index="${index}">
                    <div class="card-body d-flex flex-column">
                        <h5 class="card-title">📊 ${card.table_name}</h5>
                        <p class="card-text">
                            <strong>🆔 Databook ID:</strong> ${card.db_id}<br>
                            <strong>🆔 Table ID:</strong> ${card.table_id}
                        </p>
                        <p class="card-text">
                            <strong>📝 Table Description:</strong><br>
                            ${card.table_description || 'No description available.'}
                        </p>
                        <div class="mt-auto">
                            <button class="btn btn-primary view-table-btn">🔍 View Table</button>
                        </div>
                    </div>
                </div>
            `;

            cardSection.appendChild(cardDiv);
        });

        // Add event listener to handle card clicks
        cardSection.addEventListener('click', function(event) {
            if (event.target.classList.contains('view-table-btn')) {
                const cardIndex = event.target.closest('.card').dataset.index;
                const tableData = window.cardData[cardIndex].table_data;
                const tableName = window.cardData[cardIndex].table_name;

                // Update modal title with table name
                document.getElementById('tableContentModalLabel').textContent = tableName;

                // Set the modal table data
                modalTableData = tableData;
                modalFilteredData = [...modalTableData];

                // Reset modal state
                resetModalState();

                // Render table in modal
                renderModalTable();

                // Show the modal
                tableContentModalBS.show();
            }
        });
    }
});

// Setup all event listeners
function setupEventListeners() {
    // Dark mode toggle
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', toggleDarkMode);
    }

    // Skip these event listeners if we're using the server-rendered version
    // as they're already defined in the inline script
    if (!isServerRendered) {
        // Search input
        if (searchInput) {
            searchInput.addEventListener('input', handleSearch);
        }

        // Select button
        if (selectButton) {
            selectButton.addEventListener('click', handleSelectButtonClick);
        }

        // Reset button
        if (resetButton) {
            resetButton.addEventListener('click', resetTableView);
        }

        // Pagination event delegation (will be added dynamically)
        document.addEventListener('click', function(e) {
            if (e.target && e.target.classList.contains('page-link')) {
                const pageAction = e.target.dataset.action;

                if (pageAction === 'prev' && currentPage > 1) {
                    currentPage--;
                    renderTable();
                } else if (pageAction === 'next' && currentPage < getTotalPages()) {
                    currentPage++;
                    renderTable();
                } else if (pageAction === 'goto') {
                    const newPage = parseInt(e.target.dataset.page);
                    if (newPage && newPage !== currentPage && newPage <= getTotalPages()) {
                        currentPage = newPage;
                        renderTable();
                    }
                }
            }
        });

        // Modal event listeners
        if (modalSearchInput) {
            modalSearchInput.addEventListener('input', handleModalSearch);
        }

        if (modalSelectButton) {
            modalSelectButton.addEventListener('click', handleModalSelectButtonClick);
        }

        if (modalResetButton) {
            modalResetButton.addEventListener('click', resetModalTableView);
        }

        if (modalConfirmButton) {
            modalConfirmButton.addEventListener('click', handleModalConfirmButtonClick);
        }

        // Modal pagination event delegation
        document.addEventListener('click', function(e) {
            if (e.target && e.target.closest('#modalPaginationControls') && e.target.classList.contains('page-link')) {
                const pageAction = e.target.dataset.action;

                if (pageAction === 'prev' && modalCurrentPage > 1) {
                    modalCurrentPage--;
                    renderModalTable();
                } else if (pageAction === 'next' && modalCurrentPage < getModalTotalPages()) {
                    modalCurrentPage++;
                    renderModalTable();
                } else if (pageAction === 'goto') {
                    const newPage = parseInt(e.target.dataset.page);
                    if (newPage && newPage !== modalCurrentPage && newPage <= getModalTotalPages()) {
                        modalCurrentPage = newPage;
                        renderModalTable();
                    }
                }
            }
        });
    }

    // Add event listener for the modal hidden event
    if (tableContentModal) {
        tableContentModal.addEventListener('hidden.bs.modal', function() {
            resetModalState();

            // Ensure the card section is visible when modal is closed
            if (cardSection) {
                cardSection.style.display = 'flex';
                document.querySelector('.row#cardSection').style.display = 'flex';
            }
        });
    }
}

// Reset modal state
function resetModalState() {
    modalSelectedRow = null;
    modalCurrentPage = 1;
    if (modalSearchInput) modalSearchInput.value = '';
    if (modalSelectButton) modalSelectButton.disabled = true;
    if (modalConfirmButton) modalConfirmButton.disabled = true;
    if (modalSelectedData) modalSelectedData.innerHTML = '<p>No data selected</p>';
}

// Get total number of pages based on filtered data
function getTotalPages() {
    return Math.ceil(filteredData.length / rowsPerPage);
}

// Get total number of pages for modal data
function getModalTotalPages() {
    return Math.ceil(modalFilteredData.length / rowsPerPage);
}

// Get current page data slice
function getCurrentPageData() {
    const startIndex = (currentPage - 1) * rowsPerPage;
    const endIndex = startIndex + rowsPerPage;
    return filteredData.slice(startIndex, endIndex);
}

// Get current page data slice for modal
function getModalCurrentPageData() {
    const startIndex = (modalCurrentPage - 1) * rowsPerPage;
    const endIndex = startIndex + rowsPerPage;
    return modalFilteredData.slice(startIndex, endIndex);
}

// Render table with the current page data
function renderTable() {
    // Skip this function entirely if we're using server-rendered table
    if (isServerRendered) return;

    // Ensure the dataTable element is correctly targeted and updated
    if (!dataTable) {
        console.error('dataTable element not found in the DOM.');
        return;
    }

    // Log the dataTable element to confirm its presence
    console.log('dataTable element:', dataTable);

    const data = getCurrentPageData();

    console.log('Filtered Data:', filteredData);
    console.log('Current Page Data:', getCurrentPageData());

    if (!data || data.length === 0) {
        dataTable.querySelector('tbody').innerHTML = '<tr><td colspan="100%" class="text-center">No data available</td></tr>';
        document.getElementById('paginationControls').innerHTML = '';
        return;
    }

    // Create table headers from the first data object's keys
    const allHeaders = Object.keys(filteredData[0]);
    const headerRow = dataTable.querySelector('thead tr');
    headerRow.innerHTML = '';

    // Add a selection column
    const selectHeader = document.createElement('th');
    selectHeader.textContent = 'Select';
    headerRow.appendChild(selectHeader);

    // Add headers for each data property
    allHeaders.forEach(header => {
        const th = document.createElement('th');
        th.textContent = header.charAt(0).toUpperCase() + header.slice(1); // Capitalize first letter
        headerRow.appendChild(th);
    });

    // Create table body rows
    const tbody = dataTable.querySelector('tbody');
    tbody.innerHTML = '';

    data.forEach((item, index) => {
        const tr = document.createElement('tr');
        const globalIndex = (currentPage - 1) * rowsPerPage + index;
        tr.dataset.index = globalIndex;

        // Add the radio button cell for selection
        const radioCell = document.createElement('td');
        const radioBtn = document.createElement('input');
        radioBtn.type = 'radio';
        radioBtn.name = 'tableSelection';
        radioBtn.classList.add('form-check-input');
        radioBtn.addEventListener('change', () => handleRowSelection(tr, item));
        radioCell.appendChild(radioBtn);
        tr.appendChild(radioCell);

        // Add data cells
        allHeaders.forEach(key => {
            const td = document.createElement('td');
            td.textContent = item[key] || '';
            tr.appendChild(td);
        });

        tbody.appendChild(tr);
    });

    // Update pagination
    renderPagination();

    // If previously selected row is on current page, restore its selection
    if (selectedRow) {
        const selectedIndex = parseInt(selectedRow.dataset.index);
        const startIndex = (currentPage - 1) * rowsPerPage;
        const endIndex = startIndex + rowsPerPage;

        if (selectedIndex >= startIndex && selectedIndex < endIndex) {
            const rowInCurrentPage = tbody.querySelector(`tr[data-index="${selectedIndex}"]`);
            if (rowInCurrentPage) {
                rowInCurrentPage.classList.add('selected-row');
                rowInCurrentPage.querySelector('input[type="radio"]').checked = true;
                // Update the selected row reference to the current DOM element
                selectedRow = rowInCurrentPage;
                selectedRow.data = filteredData[selectedIndex];
            }
        }
    }
}

// Render modal table with the current page data
function renderModalTable() {
    if (!modalDataTable) {
        console.error('modalDataTable element not found in the DOM.');
        return;
    }

    const data = getModalCurrentPageData();

    if (!data || data.length === 0) {
        modalDataTable.querySelector('tbody').innerHTML = '<tr><td colspan="100%" class="text-center">No data available</td></tr>';
        modalPaginationControls.innerHTML = '';
        return;
    }

    // Create table headers from the first data object's keys
    const allHeaders = Object.keys(modalFilteredData[0]);
    const headerRow = modalDataTable.querySelector('thead tr');
    headerRow.innerHTML = '';

    // Add a selection column
    const selectHeader = document.createElement('th');
    selectHeader.textContent = 'Select';
    headerRow.appendChild(selectHeader);

    // Add headers for each data property
    allHeaders.forEach(header => {
        const th = document.createElement('th');
        th.textContent = header.charAt(0).toUpperCase() + header.slice(1); // Capitalize first letter
        headerRow.appendChild(th);
    });

    // Create table body rows
    const tbody = modalDataTable.querySelector('tbody');
    tbody.innerHTML = '';

    data.forEach((item, index) => {
        const tr = document.createElement('tr');
        const globalIndex = (modalCurrentPage - 1) * rowsPerPage + index;
        tr.dataset.index = globalIndex;

        // Add the radio button cell for selection
        const radioCell = document.createElement('td');
        const radioBtn = document.createElement('input');
        radioBtn.type = 'radio';
        radioBtn.name = 'modalTableSelection';
        radioBtn.classList.add('form-check-input');
        radioBtn.addEventListener('change', () => handleModalRowSelection(tr, item));
        radioCell.appendChild(radioBtn);
        tr.appendChild(radioCell);

        // Add data cells
        allHeaders.forEach(key => {
            const td = document.createElement('td');
            td.textContent = item[key] || '';
            tr.appendChild(td);
        });

        tbody.appendChild(tr);
    });

    // Update pagination
    renderModalPagination();

    // If previously selected row is on current page, restore its selection
    if (modalSelectedRow) {
        const selectedIndex = parseInt(modalSelectedRow.dataset.index);
        const startIndex = (modalCurrentPage - 1) * rowsPerPage;
        const endIndex = startIndex + rowsPerPage;

        if (selectedIndex >= startIndex && selectedIndex < endIndex) {
            const rowInCurrentPage = tbody.querySelector(`tr[data-index="${selectedIndex}"]`);
            if (rowInCurrentPage) {
                rowInCurrentPage.classList.add('selected-row');
                rowInCurrentPage.querySelector('input[type="radio"]').checked = true;
                // Update the selected row reference to the current DOM element
                modalSelectedRow = rowInCurrentPage;
                modalSelectedRow.data = modalFilteredData[selectedIndex];
            }
        }
    }
}

// Render pagination controls
function renderPagination() {
    const totalPages = getTotalPages();
    const paginationContainer = document.getElementById('paginationControls');

    if (!paginationContainer) return;

    // Don't show pagination if only one page or no data
    if (totalPages <= 1) {
        paginationContainer.innerHTML = '';
        return;
    }

    let paginationHTML = `
        <nav aria-label="Table navigation">
            <ul class="pagination justify-content-center">
                <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
                    <a class="page-link" href="#" data-action="prev" aria-label="Previous">
                        <span aria-hidden="true">&laquo;</span>
                    </a>
                </li>
    `;

    // Add page numbers with ellipsis for large page counts
    const maxVisiblePages = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

    // Adjust if we're near the end
    if (endPage - startPage + 1 < maxVisiblePages) {
        startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }

    // First page
    if (startPage > 1) {
        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" data-action="goto" data-page="1">1</a>
            </li>
        `;

        if (startPage > 2) {
            paginationHTML += `
                <li class="page-item disabled">
                    <a class="page-link" href="#">...</a>
                </li>
            `;
        }
    }

    // Page numbers
    for (let i = startPage; i <= endPage; i++) {
        paginationHTML += `
            <li class="page-item ${i === currentPage ? 'active' : ''}">
                <a class="page-link" href="#" data-action="goto" data-page="${i}">${i}</a>
            </li>
        `;
    }

    // Last page
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            paginationHTML += `
                <li class="page-item disabled">
                    <a class="page-link" href="#">...</a>
                </li>
            `;
        }

        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" data-action="goto" data-page="${totalPages}">${totalPages}</a>
            </li>
        `;
    }

    paginationHTML += `
                <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
                    <a class="page-link" href="#" data-action="next" aria-label="Next">
                        <span aria-hidden="true">&raquo;</span>
                    </a>
                </li>
            </ul>
        </nav>
        <div class="text-center text-muted">
            Showing ${((currentPage - 1) * rowsPerPage) + 1} to ${Math.min(currentPage * rowsPerPage, filteredData.length)} of ${filteredData.length} entries
        </div>
    `;

    paginationContainer.innerHTML = paginationHTML;
}

// Render modal pagination controls
function renderModalPagination() {
    const totalPages = getModalTotalPages();

    if (!modalPaginationControls) return;

    // Don't show pagination if only one page or no data
    if (totalPages <= 1) {
        modalPaginationControls.innerHTML = '';
        return;
    }

    let paginationHTML = `
        <nav aria-label="Modal table navigation">
            <ul class="pagination justify-content-center">
                <li class="page-item ${modalCurrentPage === 1 ? 'disabled' : ''}">
                    <a class="page-link" href="#" data-action="prev" aria-label="Previous">
                        <span aria-hidden="true">&laquo;</span>
                    </a>
                </li>
    `;

    // Add page numbers with ellipsis for large page counts
    const maxVisiblePages = 5;
    let startPage = Math.max(1, modalCurrentPage - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

    // Adjust if we're near the end
    if (endPage - startPage + 1 < maxVisiblePages) {
        startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }

    // First page
    if (startPage > 1) {
        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" data-action="goto" data-page="1">1</a>
            </li>
        `;

        if (startPage > 2) {
            paginationHTML += `
                <li class="page-item disabled">
                    <a class="page-link" href="#">...</a>
                </li>
            `;
        }
    }

    // Page numbers
    for (let i = startPage; i <= endPage; i++) {
        paginationHTML += `
            <li class="page-item ${i === modalCurrentPage ? 'active' : ''}">
                <a class="page-link" href="#" data-action="goto" data-page="${i}">${i}</a>
            </li>
        `;
    }

    // Last page
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            paginationHTML += `
                <li class="page-item disabled">
                    <a class="page-link" href="#">...</a>
                </li>
            `;
        }

        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" data-action="goto" data-page="${totalPages}">${totalPages}</a>
            </li>
        `;
    }

    paginationHTML += `
                <li class="page-item ${modalCurrentPage === totalPages ? 'disabled' : ''}">
                    <a class="page-link" href="#" data-action="next" aria-label="Next">
                        <span aria-hidden="true">&raquo;</span>
                    </a>
                </li>
            </ul>
        </nav>
        <div class="text-center text-muted">
            Showing ${((modalCurrentPage - 1) * rowsPerPage) + 1} to ${Math.min(modalCurrentPage * rowsPerPage, modalFilteredData.length)} of ${modalFilteredData.length} entries
        </div>
    `;

    modalPaginationControls.innerHTML = paginationHTML;
}

// Handle row selection
function handleRowSelection(tr, data) {
    // Remove selection from previous row if exists
    if (selectedRow) {
        selectedRow.classList.remove('selected-row');
    }

    // Mark the new row as selected
    tr.classList.add('selected-row');
    selectedRow = tr;

    // Enable the select button
    selectButton.disabled = false;

    // Store the selected data
    selectedRow.data = data;

    // Preview the selected data
    showSelectedData(data);
}

// Handle modal row selection
function handleModalRowSelection(tr, data) {
    // Remove selection from previous row if exists
    if (modalSelectedRow) {
        modalSelectedRow.classList.remove('selected-row');
    }

    // Mark the new row as selected
    tr.classList.add('selected-row');
    modalSelectedRow = tr;

    // Enable the select and confirm buttons
    modalSelectButton.disabled = false;
    modalConfirmButton.disabled = false;

    // Store the selected data
    modalSelectedRow.data = data;

    // Preview the selected data
    showModalSelectedData(data);
}

// Show selected data in the card
function showSelectedData(data) {
    if (!data) {
        selectedDataDiv.innerHTML = '<p>No data selected</p>';
        return;
    }

    let html = '<div class="row">';

    for (const [key, value] of Object.entries(data)) {
        html += `
            <div class="col-md-6 mb-2">
                <div class="fw-bold">${key.charAt(0).toUpperCase() + key.slice(1)}:</div>
                <div>${value}</div>
            </div>
        `;
    }

    html += '</div>';
    selectedDataDiv.innerHTML = html;
}

// Show selected data in the modal card
function showModalSelectedData(data) {
    if (!data) {
        modalSelectedData.innerHTML = '<p>No data selected</p>';
        return;
    }

    let html = '<div class="row">';

    for (const [key, value] of Object.entries(data)) {
        html += `
            <div class="col-md-6 mb-2">
                <div class="fw-bold">${key.charAt(0).toUpperCase() + key.slice(1)}:</div>
                <div>${value}</div>
            </div>
        `;
    }

    html += '</div>';
    modalSelectedData.innerHTML = html;
}

// Handle the select button click
function handleSelectButtonClick() {
    if (selectedRow && selectedRow.data) {
        // This is where you'd handle the final selection
        // For example, you might send it to a parent window or save it
        alert('Data selected: ' + JSON.stringify(selectedRow.data));

        // In a real application, you might do something like:
        // window.opener.receiveSelectedData(selectedRow.data);
        // window.close();
    }
}

// Handle the modal select button click
function handleModalSelectButtonClick() {
    if (modalSelectedRow && modalSelectedRow.data) {
        // Handle the selection within the modal
        showModalSelectedData(modalSelectedRow.data);
    }
}

// Handle modal confirm button click
function handleModalConfirmButtonClick() {
    if (modalSelectedRow && modalSelectedRow.data) {
        // This is where you'd handle the final selection from the modal
        alert('Data selected from modal: ' + JSON.stringify(modalSelectedRow.data));

        // Hide the modal
        tableContentModalBS.hide();

        // In a real application, you might do something like:
        // saveSelectedData(modalSelectedRow.data);
    }
}

// Handle search functionality
function handleSearch() {
    const searchTerm = searchInput.value.toLowerCase();

    if (!searchTerm) {
        filteredData = [...tableData];
    } else {
        filteredData = tableData.filter(item => {
            return Object.values(item).some(value =>
                String(value).toLowerCase().includes(searchTerm)
            );
        });
    }

    // Reset to first page and render
    currentPage = 1;
    renderTable();
}

// Handle modal search functionality
function handleModalSearch() {
    const searchTerm = modalSearchInput.value.toLowerCase();

    if (!searchTerm) {
        modalFilteredData = [...modalTableData];
    } else {
        modalFilteredData = modalTableData.filter(item => {
            return Object.values(item).some(value =>
                String(value).toLowerCase().includes(searchTerm)
            );
        });
    }

    // Reset to first page and render
    modalCurrentPage = 1;
    renderModalTable();
}

// Reset the table view
function resetTableView() {
    // Clear search
    searchInput.value = '';

    // Reset filtered data
    filteredData = [...tableData];

    // Reset to first page
    currentPage = 1;

    // Render table
    renderTable();

    // Clear selection
    if (selectedRow) {
        selectedRow.classList.remove('selected-row');
        selectedRow = null;
    }

    // Disable select button
    selectButton.disabled = true;

    // Reset selected data display
    selectedDataDiv.innerHTML = '<p>No data selected</p>';
}

// Reset the modal table view
function resetModalTableView() {
    // Clear search
    modalSearchInput.value = '';

    // Reset filtered data
    modalFilteredData = [...modalTableData];

    // Reset to first page
    modalCurrentPage = 1;

    // Render table
    renderModalTable();

    // Clear selection
    if (modalSelectedRow) {
        modalSelectedRow.classList.remove('selected-row');
        modalSelectedRow = null;
    }

    // Disable select button
    modalSelectButton.disabled = true;
    modalConfirmButton.disabled = true;

    // Reset selected data display
    modalSelectedData.innerHTML = '<p>No data selected</p>';
}

// Toggle dark/light mode
function toggleDarkMode() {
    const currentTheme = document.body.getAttribute('data-bs-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    // Update body attribute
    document.body.setAttribute('data-bs-theme', newTheme);

    // Save preference to local storage
    localStorage.setItem('theme', newTheme);

    // Update button text/icon
    updateThemeToggleButton(newTheme);
}

// Update theme toggle button text and icon
function updateThemeToggleButton(theme) {
    if (darkModeToggle) {
        if (theme === 'dark') {
            darkModeToggle.innerHTML = '<i class="bi bi-sun"></i> Light Mode';
            // Ensure visibility in dark mode
            darkModeToggle.style.color = 'white';
            darkModeToggle.style.borderColor = 'white';
        } else {
            darkModeToggle.innerHTML = '<i class="bi bi-moon-stars"></i> Dark Mode';
            // Ensure visibility in light mode
            darkModeToggle.style.color = 'white';
            darkModeToggle.style.borderColor = 'white';
        }
    }
}

// SECTION: JavaScript for handling the search functionality

document.getElementById('componentSearchButton').addEventListener('click', function() {
    const searchInput = document.getElementById('componentSearchInput').value.trim();
    const searchResultsList = document.getElementById('searchResultsList');

    // Clear previous results
    searchResultsList.innerHTML = '';

    if (searchInput === '') {
        alert('Please enter a search term.');
        return;
    }

    // Use cardData to search inside table_data
    const filteredResults = [];

    window.cardData.forEach(card => {
        card.table_data.forEach(row => {
            // Check if any value in the row matches the search input
            if (Object.values(row).some(value => String(value).toLowerCase().includes(searchInput.toLowerCase()))) {
                filteredResults.push({
                    databookName: card.db_name,
                    databookId: card.db_id,
                    tableName: card.table_name,
                    tableId: card.table_id,
                    rowData: row,
                    // Assuming the row has 'Name' and 'Formula' fields
                    recordName: row.Name || 'N/A',
                    recordFormula: row.Formula || 'N/A',
                });

                // log
                // console.log(`Found match in ${card.table_name}:`, row);
            }
        });
    });

    if (filteredResults.length === 0) {
        const noResultsItem = document.createElement('li');
        noResultsItem.className = 'list-group-item';
        noResultsItem.textContent = 'No results found.';
        searchResultsList.appendChild(noResultsItem);
    } else {
        // NOTE: update search text
        // get the search input element
        const searchInputElement = document.getElementById('searchInput');
        // set the value of the search input element to the search term
        searchInputElement.innerHTML = searchInput;

        // fill data to the list
        filteredResults.forEach(result => {
            const listItem = document.createElement('li');
            listItem.className = 'list-group-item';
            // add data
            listItem.innerHTML = `
                <div>🔍 <strong>Record:</strong> ${result.recordName}</div>
                <div>📝 <strong>Formula:</strong> ${result.recordFormula}</div>
                <div>📚 <strong>Databook:</strong> ${result.databookName} (Id: ${result.databookId})</div>
                <div>📊 <strong>Table:</strong> ${result.tableName} (Id: ${result.tableId})</div>
            `;

            // append to the list
            searchResultsList.appendChild(listItem);
        });
    }

    // Show the modal
    const searchResultsModal = new bootstrap.Modal(document.getElementById('searchResultsModal'));
    searchResultsModal.show();
});