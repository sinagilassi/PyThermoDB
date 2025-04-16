// PyThermoDB Table Viewer - Main JavaScript

// NOTE: DOM Elements
const searchInput = document.getElementById('searchInput');
const dataTable = document.getElementById('dataTable');
const selectButton = document.getElementById('selectButton');
const resetButton = document.getElementById('resetButton');
const darkModeToggle = document.getElementById('darkModeToggle');
const selectedDataDiv = document.getElementById('selectedData');
const currentYearSpan = document.getElementById('currentYear');

// NOTE: Global variables
let tableData = []; // Will be populated from Jinja
let selectedRow = null;
let currentPage = 1;
let filteredData = [];
const rowsPerPage = 50;
// Flag to detect if we're using the server-rendered version
const isServerRendered = document.querySelector('#dataTable tbody tr[data-index]') !== null;

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

    // Get data from global variable that would be set by Jinja
    if (typeof window.tableData !== 'undefined' && !isServerRendered) {
        tableData = window.tableData;
        filteredData = [...tableData];
        renderTable();
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
    }
}

// Get total number of pages based on filtered data
function getTotalPages() {
    return Math.ceil(filteredData.length / rowsPerPage);
}

// Get current page data slice
function getCurrentPageData() {
    const startIndex = (currentPage - 1) * rowsPerPage;
    const endIndex = startIndex + rowsPerPage;
    return filteredData.slice(startIndex, endIndex);
}

// Render table with the current page data
function renderTable() {
    // Skip this function entirely if we're using server-rendered table
    if (isServerRendered) return;

    const data = getCurrentPageData();

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

// Handle the select button click
function handleSelectButtonClick() {
    if (selectedRow && selectedRow.data) {
        // This is where you'd handle the final selection
        // For example, you might send it to a parent window or save it
        // NOTE
        // alert('Data selected: ' + JSON.stringify(selectedRow.data));

        // In a real application, you might do something like:
        // window.opener.receiveSelectedData(selectedRow.data);
        // window.close();
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