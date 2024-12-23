// Initialize Feather icons
feather.replace();

// Pagination state
let currentPage = 1;
let totalPages = 1;
const entriesPerPage = 50;
let allData = [];

// Format time
function formatTime(value, column) {
    const num = parseFloat(value);
    if (column.includes('last_hour')) {
        return `${Math.round(num)} min`;
    } else if (column.includes('last_day') || column.includes('last_week')) {
        const hours = Math.floor(num);
        const minutes = Math.round((num - hours) * 60);
        return hours > 0 ? `${hours}h ${minutes > 0 ? `${minutes}m` : ''}` : `${minutes} min`;
    }
    return value;
}

// DOM elements
const generateBtn = document.getElementById('generateBtn');
const error = document.getElementById('error');
const errorText = document.getElementById('errorText');
const reportInfo = document.getElementById('reportInfo');
const reportId = document.getElementById('reportId');
const statusText = document.getElementById('statusText');
const reportData = document.getElementById('reportData');
const prevPageBtn = document.getElementById('prevPage');
const nextPageBtn = document.getElementById('nextPage');
const pageNumbers = document.getElementById('pageNumbers');
const startEntry = document.getElementById('startEntry');
const endEntry = document.getElementById('endEntry');
const totalEntries = document.getElementById('totalEntries');

// Update pagination controls
function updatePaginationControls() {
    const start = (currentPage - 1) * entriesPerPage + 1;
    const end = Math.min(currentPage * entriesPerPage, allData.length);
    startEntry.textContent = start;
    endEntry.textContent = end;
    totalEntries.textContent = allData.length;

    prevPageBtn.disabled = currentPage === 1;
    nextPageBtn.disabled = currentPage === totalPages;

    pageNumbers.innerHTML = '';
    for (let i = 1; i <= totalPages; i++) {
        const button = document.createElement('button');
        button.textContent = i;
        button.classList.toggle('active', i === currentPage);
        button.addEventListener('click', () => {
            currentPage = i;
            updateTable();
            updatePaginationControls();
        });
        pageNumbers.appendChild(button);
    }
}

// Update the table
function updateTable() {
    const start = (currentPage - 1) * entriesPerPage;
    const end = start + entriesPerPage;
    const pageData = allData.slice(start, end);

    const tableBody = pageData.map(row => `
        <tr>
            ${Object.entries(row).map(([key, value], i) =>
                `<td>${i === 0 ? value : formatTime(value, key)}</td>`
            ).join('')}
        </tr>
    `).join('');
    document.getElementById('tableBody').innerHTML = tableBody;
    feather.replace();
}

// Set loading state
function setLoading(loading) {
    generateBtn.disabled = loading;
    generateBtn.innerHTML = loading
        ? `<i data-feather="loader" class="spinner"></i> Generating Report...`
        : `Generate New Report`;
    feather.replace();
}

// Show error
function showError(message) {
    errorText.textContent = message;
    error.classList.remove('hidden');
}

// Update report display
function updateReportDisplay(data) {
    allData = data;
    totalPages = Math.ceil(data.length / entriesPerPage);
    currentPage = 1;

    // Update table headers
    const headers = Object.keys(data[0]);
    document.getElementById('tableHeader').innerHTML = headers.map(h => `<th>${h.replace(/_/g, ' ')}</th>`).join('');

    // Update table
    updateTable();
    updatePaginationControls();
    reportData.classList.remove('hidden');
}

// Check report status
async function checkReportStatus(id) {
    try {
        const response = await fetch(`http://127.0.0.1:8000/get_report/${id}`);
        const contentType = response.headers.get('content-type');
        if (contentType.includes('text/csv')) {
            const text = await response.text();
            const rows = text.split('\n').map(row => row.split(','));
            const headers = rows[0];
            const data = rows.slice(1).map(row => Object.fromEntries(headers.map((h, i) => [h.trim(), row[i]])));
            statusText.textContent = 'Report generation complete';
            setLoading(false);
            updateReportDisplay(data);
        } else {
            const data = await response.json();
            if (data.status === 'Running') {
                statusText.textContent = 'Report is still generating...';
                setTimeout(() => checkReportStatus(id), 2000);
            }
        }
    } catch (err) {
        showError('Failed to check report status: ' + err.message);
        setLoading(false);
    }
}

// Generate report
async function generateReport() {
    try {
        setLoading(true);
        error.classList.add('hidden');

        const response = await fetch('http://127.0.0.1:8000/get_report', { method: 'POST' });
        const data = await response.json();

        reportId.textContent = data.report_id;
        statusText.textContent = 'Report generation started';
        reportInfo.classList.remove('hidden');

        checkReportStatus(data.report_id);
    } catch (err) {
        showError('Failed to trigger report: ' + err.message);
        setLoading(false);
    }
}

// Event listeners
generateBtn.addEventListener('click', generateReport);
prevPageBtn.addEventListener('click', () => {
    if (currentPage > 1) {
        currentPage--;
        updateTable();
        updatePaginationControls();
    }
});
nextPageBtn.addEventListener('click', () => {
    if (currentPage < totalPages) {
        currentPage++;
        updateTable();
        updatePaginationControls();
    }
});
