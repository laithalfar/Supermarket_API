const API_BASE = '/api/v1';
const toTitleCase = (str) => str ? str.toLowerCase().replace(/(?:^|\s)\w/g, c => c.toUpperCase()) : '-';
let currentSection = 'dashboard';

document.addEventListener('DOMContentLoaded', () => {
    initNav();
    loadSection('dashboard');
    setupModal();

    // Add global listener for the "New Action" button in the header
    const headerAddBtn = document.getElementById('add-entity-btn');
    if (headerAddBtn) {
        headerAddBtn.onclick = () => {
            if (currentSection !== 'dashboard') {
                openEntityModal(currentSection);
            } else {
                showToast('Please select a section first', 'info');
            }
        };
    }
});

function initNav() {
    document.querySelectorAll('.sidebar-nav li').forEach(item => {
        item.addEventListener('click', () => {
            document.querySelector('.sidebar-nav li.active').classList.remove('active');
            item.classList.add('active');
            currentSection = item.dataset.section;
            loadSection(currentSection);
        });
    });
}

function loadSection(section) {
    const area = document.getElementById('content-area');
    area.innerHTML = '<div class="loading-state"><div class="spinner"></div><p>Syncing data...</p></div>';

    switch (section) {
        case 'dashboard': renderDashboard(); break;
        case 'customers': renderEntityTable('customers', 'Customers'); break;
        case 'products': renderEntityTable('products', 'Product Inventory'); break;
        case 'employees': renderEntityTable('employees', 'Staff Members'); break;
        case 'branches': renderEntityTable('branches', 'Store Branches'); break;
        case 'transactions': renderEntityTable('transactions', 'Sales Activity'); break;
    }
}

async function fetchData(endpoint) {
    try {
        const response = await fetch(`${API_BASE}/${endpoint}/`);
        if (!response.ok) throw new Error('Network response was not ok');
        return await response.json();
    } catch (error) {
        console.error('Fetch error:', error);
        showToast('Failed to fetch data', 'error');
        return [];
    }
}

async function renderDashboard() {
    const customers = await fetchData('customers');
    const products = await fetchData('products');
    const transactions = await fetchData('transactions');
    const employees = await fetchData('employees');

    const area = document.getElementById('content-area');
    area.innerHTML = `
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-header"><i class="fas fa-users"></i> Total Customers</div>
                <div class="stat-value">${customers.length}</div>
                <div class="stat-trend trend-up"><i class="fas fa-arrow-up"></i> +12% this month</div>
            </div>
            <div class="stat-card">
                <div class="stat-header"><i class="fas fa-box"></i> Active Products</div>
                <div class="stat-value">${products.length}</div>
                <div class="stat-trend"><i class="fas fa-check"></i> Stock healthy</div>
            </div>
            <div class="stat-card">
                <div class="stat-header"><i class="fas fa-receipt"></i> Total Sales</div>
                <div class="stat-value">${transactions.length}</div>
                <div class="stat-trend trend-up"><i class="fas fa-arrow-up"></i> +5% from yesterday</div>
            </div>
            <div class="stat-card">
                <div class="stat-header"><i class="fas fa-id-badge"></i> Active Staff</div>
                <div class="stat-value">${employees.length}</div>
                <div class="stat-trend"><i class="fas fa-circle"></i> Online now</div>
            </div>
        </div>

        <div class="data-table-container">
            <div class="section-header">
                <h3>Recent Activity</h3>
                <button class="btn-mini" onclick="loadSection('dashboard')"><i class="fas fa-sync"></i></button>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Type</th>
                        <th>Amount</th>
                        <th>Time</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${transactions.slice(0, 5).map(t => `
                        <tr>
                            <td>#${t.id}</td>
                            <td>Sale</td>
                            <td>$${t.total}</td>
                            <td>${t.timeOfTransaction ? (t.timeOfTransaction.includes('PT') ? t.timeOfTransaction.replace('PT', '').replace('H', 'h').replace('M', 'm') : t.timeOfTransaction.substring(0, 5)) : 'Recently'}</td>
                            <td>
                                <div class="action-btns">
                                    <button class="btn-mini"><i class="fas fa-eye"></i></button>
                                </div>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

async function renderEntityTable(entity, title) {
    const data = await fetchData(entity);
    const area = document.getElementById('content-area');

    let headers = [];
    if (data.length > 0) {
        headers = Object.keys(data[0]).filter(h => h !== 'model_config' && h !== 'id_column');
    } else {
        // Fallback headers if table is empty
        if (entity === 'employees') headers = ['id', 'name', 'age', 'email', 'role'];
        else if (entity === 'branches') headers = ['id', 'name', 'location', 'size'];
        else if (entity === 'transactions') headers = ['id', 'total', 'dateOfTransaction'];
        else headers = ['id', 'name'];
    }

    area.innerHTML = `
        <div class="data-table-container bounce-in">
            <div class="section-header">
                <h3>${title}</h3>
                <div class="action-btns">
                    <button class="btn-primary" onclick="openEntityModal('${entity}')">
                        <i class="fas fa-plus"></i> Add New
                    </button>
                </div>
            </div>
            <table>
                <thead>
                    <tr>
                        ${headers.map(h => `<th>${h.toUpperCase()}</th>`).join('')}
                        <th>ACTIONS</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.length === 0 ? `<tr><td colspan="${headers.length + 1}" style="text-align:center; padding:40px;">No records found. Click "Add New" to get started.</td></tr>` :
            data.map(row => `
                        <tr>
                            ${headers.map(h => {
                let val = row[h];
                if (typeof val === 'boolean') {
                    return `<td><span class="badge ${val ? 'badge-success' : 'badge-warning'}">${val ? 'Yes' : 'No'}</span></td>`;
                }
                if (h === 'name' || h === 'location' || h === 'role' || h === 'category') {
                    val = toTitleCase(val);
                }
                return `<td>${val === null ? '-' : val}</td>`;
            }).join('')}
                            <td>
                                <div class="action-btns">
                                    <button class="btn-mini" onclick="deleteEntity('${entity}', ${row.id})"><i class="fas fa-trash delete"></i></button>
                                </div>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

function setupModal() {
    const modal = document.getElementById('modal-container');
    const closeBtns = document.querySelectorAll('.close-modal');

    closeBtns.forEach(btn => {
        btn.addEventListener('click', () => modal.classList.add('hidden'));
    });

    window.onclick = (event) => {
        if (event.target == modal) modal.classList.add('hidden');
    };
}

function openEntityModal(entity) {
    const modal = document.getElementById('modal-container');
    const title = document.getElementById('modal-title');
    const form = document.getElementById('entity-form');

    modal.classList.remove('hidden');
    title.innerText = `Add New ${entity.slice(0, -1).toUpperCase()}`;

    // Dynamic form generation based on entity
    let fields = '';
    if (entity === 'customers') {
        fields = `
            <div class="form-group"><label>Name</label><input type="text" name="name" required></div>
            <div class="form-group"><label>Age</label><input type="number" name="age" required></div>
            <div class="form-group"><label>Email</label><input type="email" name="email" required></div>
            <div class="form-group"><label>Membership</label><select name="membership"><option value="true">Yes</option><option value="false">No</option></select></div>
        `;
    } else if (entity === 'products') {
        fields = `
            <div class="form-group"><label>Name</label><input type="text" name="name" required></div>
            <div class="form-group"><label>Stock</label><input type="number" name="stock" required></div>
            <div class="form-group"><label>Sell Price</label><input type="number" step="0.01" name="sellPrice" required></div>
            <div class="form-group"><label>Cost</label><input type="number" step="0.01" name="cost" required></div>
            <div class="form-group"><label>Category ID</label><input type="text" name="category_id" required></div>
            <div class="form-group"><label>Category Name</label><input type="text" name="category" required></div>
        `;
    } else if (entity === 'employees') {
        fields = `
            <div class="form-group"><label>Name</label><input type="text" name="name" required></div>
            <div class="form-group"><label>Age</label><input type="number" name="age" required></div>
            <div class="form-group"><label>Email</label><input type="email" name="email" required></div>
            <div class="form-group"><label>Role</label><select name="role"><option value="CASHIER">Cashier</option><option value="MANAGER">Manager</option><option value="STOCKER">Stocker</option></select></div>
            <div class="form-group"><label>Employment Date</label><input type="date" name="dateOfEmployment" required></div>
        `;
    } else if (entity === 'branches') {
        fields = `
            <div class="form-group"><label>Name</label><input type="text" name="name" required></div>
            <div class="form-group"><label>Location</label><input type="text" name="location" required></div>
            <div class="form-group"><label>Size (sqft)</label><input type="number" name="size" required></div>
            <div class="form-group"><label>Initial Stock</label><input type="number" name="total_stock" value="0"></div>
        `;
    } else if (entity === 'transactions') {
        fields = `
            <div class="form-group"><label>Branch ID</label><input type="number" name="branch_id" required></div>
            <div class="form-group"><label>Customer ID</label><input type="number" name="customer_id"></div>
            <div class="form-group"><label>Employee ID</label><input type="number" name="employee_id" required></div>
            <div class="form-group"><label>Total Amount</label><input type="number" step="0.01" name="total_amount" required></div>
            <div class="form-group"><label>Date</label><input type="date" name="dateOfTransaction" required></div>
            <div class="form-group"><label>Time</label><input type="time" name="timeOfTransaction" required></div>
            <div class="form-group"><label>Final Total</label><input type="number" step="0.01" name="total" required></div>
            <hr>
            <h4>Items (Simplified JSON)</h4>
            <div class="form-group"><label>Details JSON</label>
            <textarea name="details" placeholder='[{"product_id": 1, "quantity": 2, "price": 10.50}]'></textarea></div>
        `;
    }

    form.innerHTML = fields;

    document.getElementById('save-entity-btn').onclick = async () => {
        const formData = new FormData(form);
        const jsonData = {};
        formData.forEach((value, key) => {
            if (['age', 'stock', 'size', 'total_stock', 'branch_id', 'customer_id', 'employee_id'].includes(key)) {
                jsonData[key] = value ? parseInt(value) : null;
            }
            else if (['sellPrice', 'cost', 'total_amount', 'total'].includes(key)) {
                jsonData[key] = value ? parseFloat(value) : 0;
            }
            else if (key === 'membership') jsonData[key] = value === 'true';
            else if (key === 'details' && value) {
                try {
                    jsonData[key] = JSON.parse(value);
                } catch (e) {
                    showToast('Invalid Details JSON format', 'error');
                    throw e;
                }
            }
            else jsonData[key] = value;
        });

        try {
            const res = await fetch(`${API_BASE}/${entity === 'transactions' ? 'transactions' : entity}/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(jsonData)
            });
            if (res.ok) {
                showToast(`Success! ${entity} created.`, 'success');
                modal.classList.add('hidden');
                loadSection(entity);
            } else {
                const err = await res.json();
                const msg = err.detail && Array.isArray(err.detail) ? err.detail[0].msg : (err.detail || 'Creation failed');
                showToast(`Error: ${msg}`, 'error');
            }
        } catch (error) {
            showToast('Failed to save entity', 'error');
        }
    };
}

async function deleteEntity(entity, id) {
    if (!confirm('Are you sure you want to delete this record?')) return;

    try {
        const res = await fetch(`${API_BASE}/${entity}/${id}`, { method: 'DELETE' });
        if (res.ok) {
            showToast('Record deleted');
            loadSection(entity);
        }
    } catch (error) {
        showToast('Delete failed', 'error');
    }
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.style.cssText = `
        background: ${type === 'error' ? '#ef4444' : '#6366f1'};
        padding: 12px 24px;
        margin-top: 10px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        font-weight: 600;
        animation: slideIn 0.3s forwards;
        color: white;
    `;
    toast.innerText = message;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s forwards';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
