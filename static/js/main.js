document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const loadingOverlay = document.getElementById('loading-overlay');
    const resultsContainer = document.getElementById('results-container');
    const uploadCard = document.getElementById('upload-card');
    const sheetTabs = document.getElementById('sheet-tabs');
    const activeContent = document.getElementById('active-sheet-content');
    const processBtn = document.getElementById('process-btn');

    let workbookData = null;
    let currentFilename = null;
    let currentRunId = null;

    // Click to upload
    dropZone.addEventListener('click', () => fileInput.click());

    // Drag and drop events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
    });

    dropZone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length) handleFileUpload(files[0]);
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) handleFileUpload(e.target.files[0]);
    });

    async function handleFileUpload(file) {
        if (!file.name.match(/\.(xlsx|xls)$/i)) {
            alert('Please upload an Excel file (.xlsx or .xls)');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        showLoading('Analyzing workbook structure...');

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.error) {
                alert(data.error);
                hideLoading();
                return;
            }

            workbookData = data.sheets;
            currentFilename = data.filename;
            currentRunId = data.run_id;
            renderResults();
            hideLoading();
            uploadCard.style.display = 'none';
            resultsContainer.style.display = 'block';

        } catch (error) {
            console.error('Upload failed:', error);
            alert('An error occurred during processing.');
            hideLoading();
        }
    }

    processBtn.addEventListener('click', async () => {
        if (!workbookData) return;

        showLoading('Mapping tables to template using Agentic AI...');

        try {
            const response = await fetch('/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    sheets: workbookData,
                    filename: currentFilename,
                    run_id: currentRunId
                })
            });

            const data = await response.json();

            if (data.error) {
                alert(data.error);
                hideLoading();
                return;
            }

            hideLoading();
            
            // Create a temporary link to download the file
            const a = document.createElement('a');
            a.href = data.download_url;
            a.download = `processed_${currentFilename}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);

            alert(`Successfully mapped ${data.row_count} rows to the template! Check your downloads.`);
            
            // Reload logs and dashboards in real-time
            if (typeof loadUserHistory === 'function') loadUserHistory();
            if (typeof loadLeadDashboard === 'function') loadLeadDashboard();
            
            // Reset mapping state
            uploadCard.style.display = 'block';
            resultsContainer.style.display = 'none';
            workbookData = null;
            currentFilename = null;
            currentRunId = null;

        } catch (error) {
            console.error('Mapping failed:', error);
            alert('An error occurred during template mapping.');
            hideLoading();
        }
    });

    function renderResults() {
        sheetTabs.innerHTML = '';
        const sheetNames = Object.keys(workbookData);

        sheetNames.forEach((name, index) => {
            const btn = document.createElement('button');
            btn.className = `tab-btn ${index === 0 ? 'active' : ''}`;
            btn.textContent = name;
            btn.addEventListener('click', () => {
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                renderSheetContent(name);
            });
            sheetTabs.appendChild(btn);
        });

        if (sheetNames.length > 0) {
            renderSheetContent(sheetNames[0]);
        }
    }

    function renderSheetContent(sheetName) {
        activeContent.innerHTML = '';
        const sheetObj = workbookData[sheetName];
        const tables = sheetObj.tables || [];
        const metadata = sheetObj.metadata || {};

        if (metadata.start_date || metadata.provider) {
            const metaDiv = document.createElement('div');
            metaDiv.className = 'glass-card metadata-badge';
            metaDiv.style.marginBottom = '1rem';
            metaDiv.innerHTML = `
                <div style="display: flex; gap: 2rem; font-size: 0.9rem;">
                    <span><strong>Provider:</strong> ${metadata.provider || 'N/A'}</span>
                    <span><strong>Validity:</strong> ${metadata.start_date || 'N/A'} to ${metadata.expiration_date || 'N/A'}</span>
                    <span><strong>Commodity:</strong> ${metadata.commodity || 'N/A'}</span>
                </div>
            `;
            activeContent.appendChild(metaDiv);
        }

        if (!tables || tables.length === 0) {
            activeContent.innerHTML = '<div class="glass-card" style="text-align:center">No tables discovered in this sheet.</div>';
            return;
        }

        tables.forEach((table, idx) => {
            const card = document.createElement('div');
            card.className = 'table-card';
            
            let headerHtml = '';
            if (table.headers && table.headers.length > 0) {
                headerHtml = `<thead><tr>${table.headers.map(h => `<th>${h}</th>`).join('')}</tr></thead>`;
            }

            let rowsHtml = '';
            if (table.data && table.data.length > 0) {
                rowsHtml = `<tbody>${table.data.map(row => `<tr>${row.map(cell => `<td>${cell || ''}</td>`).join('')}</tr>`).join('')}</tbody>`;
            }

            const tableName = table.name || `Table ${idx + 1}`;

            card.innerHTML = `
                <div class="table-header">
                    <h3>${tableName} <span class="badge">${table.type || 'Data'}</span></h3>
                    <small style="color: var(--text-muted)">Location: ${table.range || 'Unknown'}</small>
                </div>
                <div class="data-table-wrapper">
                    <table>
                        ${headerHtml}
                        ${rowsHtml}
                    </table>
                </div>
            `;
            activeContent.appendChild(card);
        });
    }

    function showLoading(text) {
        document.getElementById('loading-text').textContent = text;
        loadingOverlay.style.display = 'flex';
    }

    function hideLoading() {
        loadingOverlay.style.display = 'none';
    }
});
