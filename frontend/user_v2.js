const API_BASE = '/api/v1';
const toTitleCase = (str) => str ? str.toLowerCase().replace(/(?:^|\s)\w/g, c => c.toUpperCase()) : '-';
let cart = [];
let selectedBranch = null;

let currentUser = null;

document.addEventListener('DOMContentLoaded', () => {
    // Session check
    const userStr = localStorage.getItem('user');
    if (!userStr) {
        window.location.href = '/';
        return;
    }
    currentUser = JSON.parse(userStr);

    console.log("SuperVibe User Portal Loaded");
    console.log("Current User from LocalStorage:", currentUser);

    if (!currentUser.access_token) {
        console.error("EROROR: No access_token found in currentUser!");
        showToast("Authentication token missing. Please log in again.", "error");
    }

    loadBranches();
    initCartUI();
});

function logout() {
    localStorage.removeItem('user');
    window.location.href = '/';
}

async function loadBranches() {
    const list = document.getElementById('branch-list');
    list.innerHTML = '<div class="spinner"></div>';

    try {
        console.log("Fetching branches with token:", currentUser.access_token ? "PRESENT" : "MISSING");
        const res = await fetch(`${API_BASE}/branches/`, {
            headers: {
                'Authorization': 'Bearer ' + currentUser.access_token,
                'X-Debug-Source': 'user.js'
            }
        });
        console.log("Branch fetch response status:", res.status);
        const branches = await res.json();

        list.innerHTML = branches.map(b => `
            <div class="card" onclick="selectBranch(${b.id}, '${toTitleCase(b.name)}')">
                <i class="fas fa-store" style="font-size: 2rem; color: #6366f1; margin-bottom: 1rem"></i>
                <h3>${toTitleCase(b.name)}</h3>
                <p style="color: #94a3b8">${toTitleCase(b.location)}</p>
            </div>
        `).join('');
    } catch (e) {
        showToast('Failed to load branches', 'error');
    }
}

async function selectBranch(id, name) {
    selectedBranch = { id, name };
    document.getElementById('current-branch-name').innerText = `Shopping at ${name}`;
    showView('product-selection');
    loadProducts();
}

async function loadProducts() {
    const list = document.getElementById('product-list');
    list.innerHTML = '<div class="spinner"></div>';

    try {
        const res = await fetch(`${API_BASE}/products/`, {
            headers: { 'Authorization': 'Bearer ' + currentUser.access_token }
        });
        const products = await res.json();

        list.innerHTML = products.map(p => {
            const price = typeof p.sellPrice === 'string' ? parseFloat(p.sellPrice) : p.sellPrice;
            return `
                <div class="item-card card">
                    <h4>${toTitleCase(p.name)}</h4>
                    <div class="price">$${price.toFixed(2)}</div>
                    <div style="font-size:0.8rem; color: #94a3b8; margin-bottom:1rem">Stock: ${p.stock}</div>
                    <button class="btn-primary" onclick="addToCart(${p.id}, '${toTitleCase(p.name)}', ${price}, this)">
                        <i class="fas fa-plus"></i> Add
                    </button>
                </div>
            `;
        }).join('');
    } catch (e) {
        showToast('Failed to load products', 'error');
    }
}

function addToCart(id, name, price, btn) {
    const existing = cart.find(i => i.id === id);
    if (existing) {
        existing.quantity++;
    } else {
        cart.push({ id, name, price, quantity: 1 });
    }

    // Quick feedback animation
    if (btn) {
        const original = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-check"></i> Added';
        btn.style.background = '#10b981';
        setTimeout(() => {
            btn.innerHTML = original;
            btn.style.background = '';
        }, 800);
    }

    updateCartUI();
    showToast(`${name} added to cart`);
}

function updateCartUI() {
    const count = cart.reduce((acc, i) => acc + i.quantity, 0);
    document.getElementById('cart-count').innerText = count;

    const total = cart.reduce((acc, i) => acc + (i.price * i.quantity), 0);
    document.getElementById('cart-total').innerText = `$${total.toFixed(2)}`;

    const list = document.getElementById('cart-items-list');
    list.innerHTML = cart.map(i => `
        <div class="cart-item">
            <div>
                <div style="font-weight:600">${i.name}</div>
                <div style="font-size:0.8rem; color:#94a3b8">${i.quantity} x $${i.price.toFixed(2)}</div>
            </div>
            <div style="font-weight:800">$${(i.price * i.quantity).toFixed(2)}</div>
        </div>
    `).join('');
}

function initCartUI() {
    const cartBtn = document.getElementById('cart-btn');
    const closeBtn = document.getElementById('close-cart');
    const overlay = document.getElementById('cart-overlay');
    const checkoutBtn = document.getElementById('checkout-btn');

    cartBtn.onclick = () => overlay.classList.add('open');
    closeBtn.onclick = () => overlay.classList.remove('open');

    checkoutBtn.onclick = handleCheckout;
}

async function handleCheckout() {
    if (cart.length === 0) return showToast('Cart is empty', 'error');

    const total = cart.reduce((acc, i) => acc + (i.price * i.quantity), 0);
    const now = new Date();

    const payload = {
        branch_id: selectedBranch.id,
        employee_id: currentUser.role !== 'customer' ? currentUser.id : null,
        customer_id: currentUser.role === 'customer' ? currentUser.id : null,
        total_amount: total,
        total: total,
        dateOfTransaction: now.toISOString().split('T')[0],
        timeOfTransaction: now.toTimeString().split(' ')[0],
        details: cart.map(i => ({
            product_id: i.id,
            quantity: i.quantity,
            price: i.price
        }))
    };

    try {
        const res = await fetch(`${API_BASE}/transactions/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + currentUser.access_token
            },
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            showToast('Checkout multi-success! Your order is placed.', 'success');
            cart = [];
            updateCartUI();
            document.getElementById('cart-overlay').classList.remove('open');
            showView('branch-selection');
        } else {
            showToast('Checkout failed', 'error');
        }
    } catch (e) {
        showToast('Network error during checkout', 'error');
    }
}

function showView(viewId) {
    document.querySelectorAll('.view-section').forEach(v => v.classList.remove('active'));
    document.getElementById(viewId).classList.add('active');
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.style.cssText = `
        background: ${type === 'error' ? '#ef4444' : (type === 'success' ? '#10b981' : '#6366f1')};
        padding: 12px 24px; margin-top: 10px; border-radius: 8px; color: white;
        font-weight: 600; animation: slideIn 0.3s forwards;
    `;
    toast.innerText = message;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s forwards';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
