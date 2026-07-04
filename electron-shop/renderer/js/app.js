const API_BASE = 'http://127.0.0.1:8000';
let currentUser = null;
let accessToken = localStorage.getItem('accessToken') || null;
let refreshToken = localStorage.getItem('refreshToken') || null;

// API请求封装 - 带JWT token
async function apiRequest(endpoint, options = {}) {
    try {
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers,
        };
        if (accessToken) {
            headers['Authorization'] = `Bearer ${accessToken}`;
        }
        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers,
        });
        const data = await response.json();

        // token过期时自动刷新
        if (response.status === 401 && refreshToken) {
            const refreshed = await refreshAccessToken();
            if (refreshed) {
                headers['Authorization'] = `Bearer ${accessToken}`;
                const retry = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });
                return await retry.json();
            }
        }
        return data;
    } catch (error) {
        console.error('API请求失败:', error);
        return { success: false, message: '网络错误，请检查后端是否启动' };
    }
}

// 刷新token
async function refreshAccessToken() {
    try {
        const response = await fetch(`${API_BASE}/api/token/refresh/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh: refreshToken }),
        });
        if (response.ok) {
            const data = await response.json();
            accessToken = data.access;
            localStorage.setItem('accessToken', accessToken);
            return true;
        }
    } catch (e) {}
    logout();
    return false;
}

// 登录 - 使用JWT token
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const loginType = document.querySelector('input[name="loginType"]:checked').value;

    // 先获取JWT token
    const tokenResult = await fetch(`${API_BASE}/api/token/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
    });

    if (tokenResult.ok) {
        const tokenData = await tokenResult.json();
        accessToken = tokenData.access;
        refreshToken = tokenData.refresh;
        localStorage.setItem('accessToken', accessToken);
        localStorage.setItem('refreshToken', refreshToken);

        // 获取用户信息
        const userData = await apiRequest('/api/users/profile/');

        if (loginType === 'merchant') {
            // 验证是否是商家
            const merchantCheck = await apiRequest('/api/merchants/dashboard/');
            if (merchantCheck.total_goods !== undefined) {
                showPage('merchant');
                loadMerchantDashboard();
            } else {
                document.getElementById('loginError').textContent = '该账号不是商家账号';
                document.getElementById('loginError').classList.remove('d-none');
                logout();
            }
        } else if (loginType === 'admin') {
            window.location.href = `${API_BASE}/admin/`;
        } else {
            currentUser = userData.user;
            document.getElementById('userInfo').textContent = currentUser.username;
            showPage('user');
            showSection('goods');
        }
    } else {
        const err = await tokenResult.json();
        const errorDiv = document.getElementById('loginError');
        errorDiv.textContent = err.detail || err.message || '登录失败';
        errorDiv.classList.remove('d-none');
    }
});

// 用户注册
document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('reg-username').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    const password2 = document.getElementById('reg-password2').value;

    if (password !== password2) {
        const errorDiv = document.getElementById('registerError');
        errorDiv.textContent = '两次密码不一致';
        errorDiv.classList.remove('d-none');
        return;
    }

    const result = await apiRequest('/api/users/register/', {
        method: 'POST',
        body: JSON.stringify({ username, email, password, password2 }),
    });

    if (result.success) {
        // 注册成功后自动获取token
        const tokenResult = await fetch(`${API_BASE}/api/token/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });
        if (tokenResult.ok) {
            const tokenData = await tokenResult.json();
            accessToken = tokenData.access;
            refreshToken = tokenData.refresh;
            localStorage.setItem('accessToken', accessToken);
            localStorage.setItem('refreshToken', refreshToken);
        }
        currentUser = result.user;
        document.getElementById('userInfo').textContent = currentUser.username;
        showPage('user');
        showSection('goods');
    } else {
        const errorDiv = document.getElementById('registerError');
        errorDiv.textContent = result.message || '注册失败';
        errorDiv.classList.remove('d-none');
    }
});

// 商家注册
document.getElementById('merchantRegisterForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const result = await apiRequest('/api/merchants/register/', {
        method: 'POST',
        body: JSON.stringify({
            username: document.getElementById('m-reg-username').value,
            email: document.getElementById('m-reg-email').value,
            password: document.getElementById('m-reg-password').value,
            shop_name: document.getElementById('m-reg-shopname').value,
            contact_phone: document.getElementById('m-reg-phone').value,
            address: document.getElementById('m-reg-address').value,
        }),
    });

    if (result.success) {
        // 自动获取token
        const tokenResult = await fetch(`${API_BASE}/api/token/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: document.getElementById('m-reg-username').value,
                password: document.getElementById('m-reg-password').value,
            }),
        });
        if (tokenResult.ok) {
            const tokenData = await tokenResult.json();
            accessToken = tokenData.access;
            refreshToken = tokenData.refresh;
            localStorage.setItem('accessToken', accessToken);
            localStorage.setItem('refreshToken', refreshToken);
        }
        showPage('merchant');
        loadMerchantDashboard();
    } else {
        const errorDiv = document.getElementById('merchantRegisterError');
        errorDiv.textContent = result.message || '注册失败';
        errorDiv.classList.remove('d-none');
    }
});

// 退出登录
function logout() {
    accessToken = null;
    refreshToken = null;
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    currentUser = null;
    showPage('home');
    showHomeSection('goods');
}

// 显示页面
function showPage(page) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(`page-${page}`).classList.add('active');
}

// 用户端显示内容
let currentCategoryId = null;

async function showSection(section) {
    const content = document.getElementById('user-content');
    switch(section) {
        case 'goods': await loadGoods(content); break;
        case 'cart': await loadCart(content); break;
        case 'orders': await loadOrders(content); break;
        case 'profile': await loadProfile(content); break;
    }
}

// 加载商品列表（支持分类筛选）
async function loadGoods(container, categoryId = null) {
    currentCategoryId = categoryId;
    let endpoint = '/api/goods/';
    if (categoryId) {
        endpoint += `?category=${categoryId}`;
    }

    const [goodsResult, categoriesResult] = await Promise.all([
        apiRequest(endpoint),
        apiRequest('/api/categories/')
    ]);

    const goods = goodsResult.results || [];
    const categories = categoriesResult.results || categoriesResult || [];

    container.innerHTML = `
        <div class="mb-4">
            <h4>全部商品</h4>
        </div>
        <div class="mb-4">
            <div class="d-flex flex-wrap gap-2">
                <button class="btn btn-sm ${!currentCategoryId ? 'btn-primary' : 'btn-outline-primary'}" onclick="loadGoods(document.getElementById('user-content'), null)">全部</button>
                ${categories.map(cat => `
                    <button class="btn btn-sm ${currentCategoryId == cat.id ? 'btn-primary' : 'btn-outline-primary'}" onclick="loadGoods(document.getElementById('user-content'), ${cat.id})">
                        ${cat.icon ? `<i class="bi bi-${cat.icon}"></i>` : ''} ${cat.name}
                    </button>
                `).join('')}
            </div>
        </div>
        <div class="row">
            ${goods.length > 0 ? goods.map(item => `
                <div class="col-md-3 mb-4">
                    <div class="card h-100" style="cursor:pointer;" onclick="loadGoodsDetail(document.getElementById('user-content'), ${item.id})">
                        ${item.image
                            ? `<img src="${item.image}" class="card-img-top" style="height: 200px; object-fit: cover;">`
                            : `<div class="card-img-top bg-light d-flex align-items-center justify-content-center" style="height: 200px;"><i class="bi bi-image text-muted" style="font-size: 3rem;"></i></div>`
                        }
                        <div class="card-body">
                            <h6 class="card-title text-truncate">${item.name}</h6>
                            <p class="text-danger fw-bold mb-1">¥${item.price}</p>
                            <small class="text-muted">已售 ${item.sales}</small>
                        </div>
                        <div class="card-footer bg-transparent">
                            <button class="btn btn-outline-primary btn-sm w-100" onclick="event.stopPropagation();addToCart(${item.id})">加入购物车</button>
                        </div>
                    </div>
                </div>
            `).join('') : '<div class="text-center text-muted py-5"><i class="bi bi-inbox" style="font-size: 3rem;"></i><p class="mt-2">该分类暂无商品</p></div>'}
        </div>
    `;
}

// 加载商品详情页
async function loadGoodsDetail(container, goodsId) {
    const [detail, reviewsResult] = await Promise.all([
        apiRequest(`/api/goods/${goodsId}/`),
        apiRequest(`/api/reviews/${goodsId}/`)
    ]);
    const reviews = reviewsResult.results || reviewsResult || [];

    container.innerHTML = `
        <button class="btn btn-outline-secondary btn-sm mb-3" onclick="loadGoods(document.getElementById('user-content'), currentCategoryId)">
            <i class="bi bi-arrow-left"></i> 返回商品列表
        </button>
        <div class="row">
            <div class="col-md-5">
                ${detail.image
                    ? `<img src="${detail.image}" class="img-fluid rounded" style="max-height:400px;object-fit:cover;">`
                    : `<div class="bg-light d-flex align-items-center justify-content-center rounded" style="height:400px;"><i class="bi bi-image text-muted" style="font-size:5rem;"></i></div>`
                }
            </div>
            <div class="col-md-7">
                <h3>${detail.name}</h3>
                <span class="badge bg-secondary mb-2">${detail.category_name || ''}</span>
                <p class="text-danger fw-bold" style="font-size:1.8rem;">¥${detail.price}</p>
                <p class="text-muted">已售 ${detail.sales} 件 | 库存 ${detail.stock} 件</p>
                <p class="text-muted">评分：${'★'.repeat(Math.round(detail.average_rating || 0))}${'☆'.repeat(5 - Math.round(detail.average_rating || 0))} ${detail.average_rating ? detail.average_rating.toFixed(1) : '暂无'} (${detail.review_count || 0}条评价)</p>
                <button class="btn btn-primary btn-lg" onclick="addToCart(${detail.id})">
                    <i class="bi bi-cart3"></i> 加入购物车
                </button>
                ${detail.description ? `<hr><h6>商品描述</h6><p>${detail.description}</p>` : ''}
            </div>
        </div>
        <hr>
        <h5 class="mb-3">商品评价 (${reviews.length}条)</h5>
        ${reviews.length > 0 ? reviews.map(r => `
            <div class="card mb-2">
                <div class="card-body py-2 px-3">
                    <div class="d-flex justify-content-between align-items-center">
                        <span><strong>${r.username}</strong> <span class="text-warning">${r.rating_stars}</span></span>
                        <small class="text-muted">${r.created_at}</small>
                    </div>
                    ${r.content ? `<p class="mb-0 mt-1">${r.content}</p>` : ''}
                </div>
            </div>
        `).join('') : '<p class="text-muted">暂无评价</p>'}
    `;
}

// 加入购物车
async function addToCart(goodsId) {
    const result = await apiRequest('/api/cart/add/', {
        method: 'POST',
        body: JSON.stringify({ goods_id: goodsId, quantity: 1 }),
    });
    alert(result.message || '操作完成');
}

// 加载购物车
async function loadCart(container) {
    const result = await apiRequest('/api/cart/');
    const items = result.items || [];

    container.innerHTML = `
        <h4 class="mb-4">购物车</h4>
        ${items.length > 0 ? `
            <table class="table">
                <thead><tr><th>商品</th><th>单价</th><th>数量</th><th>小计</th><th>操作</th></tr></thead>
                <tbody>
                    ${items.map(item => `
                        <tr>
                            <td>${item.goods.name}</td>
                            <td>¥${item.goods.price}</td>
                            <td>${item.quantity}</td>
                            <td class="text-danger">¥${item.subtotal}</td>
                            <td><button class="btn btn-outline-danger btn-sm" onclick="removeCartItem(${item.id})">删除</button></td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
            <div class="text-end">
                <span class="me-3">合计：<span class="text-danger fw-bold">¥${result.total_price}</span></span>
                <button class="btn btn-primary" onclick="showSection('orders')">去结算</button>
            </div>
        ` : '<p class="text-center text-muted">购物车是空的</p>'}
    `;
}

// 移除购物车商品
async function removeCartItem(itemId) {
    await apiRequest(`/api/cart/${itemId}/`, { method: 'DELETE' });
    showSection('cart');
}

// 加载订单列表
async function loadOrders(container) {
    const result = await apiRequest('/api/orders/');
    const orders = result.results || [];

    container.innerHTML = `
        <h4 class="mb-4">我的订单</h4>
        ${orders.length === 0 ? '<p class="text-center text-muted">暂无订单</p>' : ''}
        ${orders.map(order => `
            <div class="card mb-3">
                <div class="card-header d-flex justify-content-between">
                    <span>订单号：${order.order_no}</span>
                    <span class="badge bg-${order.status === 1 ? 'warning' : order.status === 2 ? 'info' : order.status === 3 ? 'primary' : order.status === 4 ? 'success' : 'secondary'}">${order.status_text}</span>
                </div>
                <div class="card-body">
                    <p>合计：<span class="text-danger fw-bold">¥${order.total_amount}</span></p>
                    <p class="text-muted mb-2">${order.created_at}</p>
                    <div class="d-flex gap-2">
                        ${order.status === 3 ? `<button class="btn btn-success btn-sm" onclick="confirmOrder(${order.id})">确认收货</button>` : ''}
                        ${order.status === 4 ? `<button class="btn btn-outline-warning btn-sm" onclick="loadOrderDetailForReview(${order.id})">评价</button>` : ''}
                    </div>
                </div>
            </div>
        `).join('')}
    `;
}

// 确认收货
async function confirmOrder(orderId) {
    if (!confirm('确认已收到商品？')) return;
    const result = await apiRequest(`/api/orders/${orderId}/confirm/`, { method: 'POST' });
    if (result.success) {
        alert('已确认收货');
        showSection('orders');
    } else {
        alert(result.message || '操作失败');
    }
}

// 加载订单详情（用于评价）
async function loadOrderDetailForReview(orderId) {
    const content = document.getElementById('user-content');
    const order = await apiRequest(`/api/orders/${orderId}/`);

    content.innerHTML = `
        <button class="btn btn-outline-secondary btn-sm mb-3" onclick="showSection('orders')">
            <i class="bi bi-arrow-left"></i> 返回订单列表
        </button>
        <h4 class="mb-3">评价订单 ${order.order_no}</h4>
        <div id="review-form-area"></div>
        ${(order.items || []).map(item => `
            <div class="card mb-3" id="review-card-${item.goods}">
                <div class="card-body">
                    <div class="d-flex align-items-center gap-3">
                        ${item.goods_image
                            ? `<img src="${item.goods_image}" style="width:80px;height:80px;object-fit:cover;border-radius:4px;">`
                            : `<div class="bg-light d-flex align-items-center justify-content-center" style="width:80px;height:80px;border-radius:4px;"><i class="bi bi-image text-muted"></i></div>`
                        }
                        <div class="flex-grow-1">
                            <h6 class="mb-1" style="cursor:pointer;" onclick="loadGoodsDetail(document.getElementById('user-content'), ${item.goods})">${item.goods_name}</h6>
                            <small class="text-muted">¥${item.goods_price} × ${item.quantity}</small>
                        </div>
                        <button class="btn btn-outline-primary btn-sm" onclick="showReviewForm(${item.goods}, '${item.goods_name.replace(/'/g, "\\'")}')">评价</button>
                    </div>
                    <div id="review-area-${item.goods}" class="mt-3"></div>
                </div>
            </div>
        `).join('')}
    `;
}

// 显示评价表单
let currentReviewGoodsId = null;
let currentReviewRating = 0;

function showReviewForm(goodsId, goodsName) {
    currentReviewGoodsId = goodsId;
    currentReviewRating = 0;
    const area = document.getElementById(`review-area-${goodsId}`);
    area.innerHTML = `
        <div class="border rounded p-3 bg-light">
            <h6>评价「${goodsName}」</h6>
            <div class="mb-2">
                <label class="form-label">评分：</label>
                <span id="star-rating" class="fs-3" style="cursor:pointer;">
                    ${[1,2,3,4,5].map(i => `<span class="star" data-val="${i}" onclick="setReviewRating(${i})">☆</span>`).join('')}
                </span>
            </div>
            <div class="mb-2">
                <textarea class="form-control" id="reviewContent" rows="2" placeholder="分享你的使用体验（选填）"></textarea>
            </div>
            <div class="d-flex gap-2">
                <button class="btn btn-primary btn-sm" onclick="submitReview()">提交评价</button>
                <button class="btn btn-outline-secondary btn-sm" onclick="document.getElementById('review-area-${goodsId}').innerHTML=''">取消</button>
            </div>
        </div>
    `;
}

function setReviewRating(val) {
    currentReviewRating = val;
    const stars = document.querySelectorAll('#star-rating .star');
    stars.forEach(s => {
        const v = parseInt(s.dataset.val);
        s.textContent = v <= val ? '★' : '☆';
        s.classList.toggle('text-warning', v <= val);
    });
}

async function submitReview() {
    if (currentReviewRating === 0) { alert('请选择评分'); return; }
    const content = document.getElementById('reviewContent').value;
    const result = await apiRequest('/api/reviews/create/', {
        method: 'POST',
        body: JSON.stringify({
            goods_id: currentReviewGoodsId,
            rating: currentReviewRating,
            content: content
        })
    });
    if (result.success) {
        alert('评价成功');
        document.getElementById(`review-area-${currentReviewGoodsId}`).innerHTML = '<span class="text-success"><i class="bi bi-check-circle"></i> 已评价</span>';
    } else {
        alert(result.message || '评价失败');
    }
}

// 加载个人中心
async function loadProfile(container) {
    const result = await apiRequest('/api/users/profile/');
    const user = result.user || {};
    container.innerHTML = `
        <h4 class="mb-4">个人中心</h4>
        <div class="card">
            <div class="card-body">
                <table class="table">
                    <tr><th width="120">用户名</th><td>${user.username || '-'}</td></tr>
                    <tr><th>邮箱</th><td>${user.email || '未设置'}</td></tr>
                    <tr><th>手机号</th><td>${result.phone || '未设置'}</td></tr>
                </table>
            </div>
        </div>
    `;
}

// 商家端加载数据概览
async function loadMerchantDashboard() {
    const content = document.getElementById('merchant-content');
    const result = await apiRequest('/api/merchants/dashboard/');
    document.getElementById('merchantInfo').textContent = result.shop_name || '';

    content.innerHTML = `
        <h4 class="mb-4">数据概览</h4>
        <div class="row mb-4">
            <div class="col-md-3"><div class="card stat-card primary"><div class="card-body"><h6 class="text-muted">商品总数</h6><h3>${result.total_goods || 0}</h3></div></div></div>
            <div class="col-md-3"><div class="card stat-card success"><div class="card-body"><h6 class="text-muted">总销量</h6><h3>${result.total_sales || 0}</h3></div></div></div>
            <div class="col-md-3"><div class="card stat-card warning"><div class="card-body"><h6 class="text-muted">订单总数</h6><h3>${result.total_orders || 0}</h3></div></div></div>
            <div class="col-md-3"><div class="card stat-card info"><div class="card-body"><h6 class="text-muted">总收入</h6><h3>¥${result.total_revenue || 0}</h3></div></div></div>
        </div>
    `;
}

// 商家端切换
function showMerchantSection(section) {
    const content = document.getElementById('merchant-content');
    switch(section) {
        case 'dashboard': loadMerchantDashboard(); break;
        case 'goods': loadMerchantGoods(content); break;
        case 'orders': loadMerchantOrders(content); break;
    }
}

// 加载商家商品
async function loadMerchantGoods(container) {
    const [goodsResult, categoriesResult] = await Promise.all([
        apiRequest('/api/merchants/goods/'),
        apiRequest('/api/categories/')
    ]);
    const goods = goodsResult.results || goodsResult || [];
    const categories = categoriesResult.results || categoriesResult || [];

    container.innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h4>商品管理</h4>
            <button class="btn btn-primary" onclick="showAddGoodsForm()">
                <i class="bi bi-plus-lg"></i> 添加商品
            </button>
        </div>
        <div id="goods-form-area"></div>
        <table class="table">
            <thead><tr><th>图片</th><th>商品</th><th>分类</th><th>售价</th><th>库存</th><th>销量</th><th>状态</th></tr></thead>
            <tbody>
                ${goods.map(item => `
                    <tr>
                        <td>
                            ${item.goods.image
                                ? `<img src="${item.goods.image}" style="width:60px;height:60px;object-fit:cover;border-radius:4px;">`
                                : `<div class="bg-light d-flex align-items-center justify-content-center" style="width:60px;height:60px;border-radius:4px;"><i class="bi bi-image text-muted"></i></div>`
                            }
                        </td>
                        <td>${item.goods.name}</td>
                        <td><span class="badge bg-secondary">${item.goods.category_name || '-'}</span></td>
                        <td>¥${item.goods.price}</td>
                        <td>${item.goods.stock}</td>
                        <td>${item.goods.sales}</td>
                        <td><span class="badge bg-${item.goods.is_active ? 'success' : 'secondary'}">${item.goods.is_active ? '上架' : '下架'}</span></td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;

    window._merchantCategories = categories;
}

// 显示添加商品表单
function showAddGoodsForm() {
    const area = document.getElementById('goods-form-area');
    const categories = window._merchantCategories || [];
    area.innerHTML = `
        <div class="card mb-4">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">添加商品</h5>
                <button class="btn btn-sm btn-outline-secondary" onclick="document.getElementById('goods-form-area').innerHTML=''">取消</button>
            </div>
            <div class="card-body">
                <form id="addGoodsForm" enctype="multipart/form-data">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">商品名称 <span class="text-danger">*</span></label>
                            <input type="text" class="form-control" name="name" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">商品分类 <span class="text-danger">*</span></label>
                            <select class="form-select" name="category" required>
                                <option value="">请选择分类</option>
                                ${categories.map(c => `<option value="${c.id}">${c.name}</option>`).join('')}
                            </select>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">售价 <span class="text-danger">*</span></label>
                            <input type="number" class="form-control" name="price" step="0.01" min="0" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">库存 <span class="text-danger">*</span></label>
                            <input type="number" class="form-control" name="stock" min="0" required>
                        </div>
                        <div class="col-md-12 mb-3">
                            <label class="form-label">商品图片 <span class="text-danger">*</span></label>
                            <input type="file" class="form-control" name="image" accept="image/*" required id="goodsImageInput">
                            <div class="mt-2" id="imagePreview"></div>
                        </div>
                        <div class="col-md-12 mb-3">
                            <label class="form-label">商品描述</label>
                            <textarea class="form-control" name="description" rows="3"></textarea>
                        </div>
                    </div>
                    <button type="submit" class="btn btn-primary">提交</button>
                </form>
            </div>
        </div>
    `;

    document.getElementById('goodsImageInput').addEventListener('change', function(e) {
        const file = e.target.files[0];
        const preview = document.getElementById('imagePreview');
        if (file) {
            const reader = new FileReader();
            reader.onload = function(ev) {
                preview.innerHTML = `<img src="${ev.target.result}" style="max-height:150px;border-radius:4px;">`;
            };
            reader.readAsDataURL(file);
        } else {
            preview.innerHTML = '';
        }
    });

    document.getElementById('addGoodsForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form);
        try {
            let response = await fetch(`${API_BASE}/api/merchants/goods/create/`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${accessToken}` },
                body: formData
            });
            // token过期时自动刷新并重试
            if (response.status === 401 && refreshToken) {
                const refreshed = await refreshAccessToken();
                if (refreshed) {
                    response = await fetch(`${API_BASE}/api/merchants/goods/create/`, {
                        method: 'POST',
                        headers: { 'Authorization': `Bearer ${accessToken}` },
                        body: formData
                    });
                }
            }
            const result = await response.json();
            if (response.ok && result.success) {
                alert('商品添加成功');
                loadMerchantGoods(document.getElementById('merchant-content'));
            } else {
                alert(result.message || JSON.stringify(result) || '添加失败');
            }
        } catch (err) {
            alert('请求失败：' + err.message);
        }
    });
}

// 加载商家订单
async function loadMerchantOrders(container) {
    const result = await apiRequest('/api/merchants/orders/');
    const orders = result.results || result || [];
    container.innerHTML = `
        <h4 class="mb-4">订单管理</h4>
        ${orders.map(order => `
            <div class="card mb-3">
                <div class="card-header d-flex justify-content-between">
                    <span>订单号：${order.order_no}</span>
                    <span class="badge bg-${order.status === 2 ? 'info' : 'secondary'}">${order.status_text}</span>
                </div>
                <div class="card-body">
                    <p>合计：¥${order.total_amount}</p>
                    ${order.status === 2 ? `<button class="btn btn-success btn-sm" onclick="shipOrder(${order.id})">确认发货</button>` : ''}
                </div>
            </div>
        `).join('')}
    `;
}

// 商家发货
async function shipOrder(orderId) {
    const result = await apiRequest(`/api/merchants/orders/${orderId}/ship/`, { method: 'POST' });
    if (result.success) {
        alert('已发货');
        loadMerchantOrders(document.getElementById('merchant-content'));
    }
}

// 首页相关函数
async function showHomeSection(section) {
    const content = document.getElementById('home-content');
    document.querySelectorAll('#page-home .sidebar .nav-link').forEach(link => link.classList.remove('active'));
    if (section === 'goods') {
        document.querySelector('#page-home .sidebar .nav-link:first-child').classList.add('active');
    } else if (section === 'categories') {
        document.querySelector('#page-home .sidebar .nav-link:last-child').classList.add('active');
    }
    switch(section) {
        case 'goods': await loadHomeGoods(content); break;
        case 'categories': await loadHomeCategories(content); break;
    }
}

// 搜索商品
async function searchGoods() {
    const keyword = document.getElementById('searchInput').value.trim();
    if (!keyword) {
        loadHomeGoods(document.getElementById('home-content'));
        return;
    }
    const result = await apiRequest(`/api/goods/?search=${encodeURIComponent(keyword)}`);
    const goods = result.results || [];
    const container = document.getElementById('home-content');
    container.innerHTML = `
        <div class="mb-4">
            <h4>搜索结果：${keyword}</h4>
        </div>
        <div class="row">
            ${goods.length > 0 ? goods.map(item => `
                <div class="col-md-3 mb-4">
                    <div class="card h-100" style="cursor:pointer;" onclick="loadHomeGoodsDetail(document.getElementById('home-content'), ${item.id})">
                        ${item.image
                            ? `<img src="${item.image}" class="card-img-top" style="height: 200px; object-fit: cover;">`
                            : `<div class="card-img-top bg-light d-flex align-items-center justify-content-center" style="height: 200px;"><i class="bi bi-image text-muted" style="font-size: 3rem;"></i></div>`
                        }
                        <div class="card-body">
                            <h6 class="card-title text-truncate">${item.name}</h6>
                            <p class="text-danger fw-bold mb-1">¥${item.price}</p>
                            <small class="text-muted">已售 ${item.sales}</small>
                        </div>
                    </div>
                </div>
            `).join('') : '<div class="col-12 text-center text-muted py-5"><i class="bi bi-inbox" style="font-size: 3rem;"></i><p class="mt-2">未找到相关商品</p></div>'}
        </div>
    `;
}

// 加载首页商品列表
async function loadHomeGoods(container) {
    const goodsResult = await apiRequest('/api/goods/');
    const goods = goodsResult.results || [];

    container.innerHTML = `
        <div class="mb-4">
            <h4>全部商品</h4>
        </div>
        <div class="row">
            ${goods.length > 0 ? goods.map(item => `
                <div class="col-md-3 mb-4">
                    <div class="card h-100" style="cursor:pointer;" onclick="loadHomeGoodsDetail(document.getElementById('home-content'), ${item.id})">
                        ${item.image
                            ? `<img src="${item.image}" class="card-img-top" style="height: 200px; object-fit: cover;">`
                            : `<div class="card-img-top bg-light d-flex align-items-center justify-content-center" style="height: 200px;"><i class="bi bi-image text-muted" style="font-size: 3rem;"></i></div>`
                        }
                        <div class="card-body">
                            <h6 class="card-title text-truncate">${item.name}</h6>
                            <p class="text-danger fw-bold mb-1">¥${item.price}</p>
                            <small class="text-muted">已售 ${item.sales}</small>
                        </div>
                    </div>
                </div>
            `).join('') : '<div class="text-center text-muted py-5"><i class="bi bi-inbox" style="font-size: 3rem;"></i><p class="mt-2">该分类暂无商品</p></div>'}
        </div>
    `;
}

// 加载首页商品详情页
async function loadHomeGoodsDetail(container, goodsId) {
    const [detail, reviewsResult] = await Promise.all([
        apiRequest(`/api/goods/${goodsId}/`),
        apiRequest(`/api/reviews/${goodsId}/`)
    ]);
    const reviews = reviewsResult.results || reviewsResult || [];

    container.innerHTML = `
        <button class="btn btn-outline-secondary btn-sm mb-3" onclick="loadHomeGoods(document.getElementById('home-content'))">
            <i class="bi bi-arrow-left"></i> 返回商品列表
        </button>
        <div class="row">
            <div class="col-md-5">
                ${detail.image
                    ? `<img src="${detail.image}" class="img-fluid rounded" style="max-height:400px;object-fit:cover;">`
                    : `<div class="bg-light d-flex align-items-center justify-content-center rounded" style="height:400px;"><i class="bi bi-image text-muted" style="font-size:5rem;"></i></div>`
                }
            </div>
            <div class="col-md-7">
                <h3>${detail.name}</h3>
                <span class="badge bg-secondary mb-2">${detail.category_name || ''}</span>
                <p class="text-danger fw-bold" style="font-size:1.8rem;">¥${detail.price}</p>
                <p class="text-muted">已售 ${detail.sales} 件 | 库存 ${detail.stock} 件</p>
                <p class="text-muted">评分：${'★'.repeat(Math.round(detail.average_rating || 0))}${'☆'.repeat(5 - Math.round(detail.average_rating || 0))} ${detail.average_rating ? detail.average_rating.toFixed(1) : '暂无'} (${detail.review_count || 0}条评价)</p>
                <button class="btn btn-primary btn-lg" onclick="addToCartFromHome(${detail.id})">
                    <i class="bi bi-cart3"></i> 加入购物车
                </button>
                <small class="text-muted d-block mt-2">登录后可加入购物车</small>
                ${detail.description ? `<hr><h6>商品描述</h6><p>${detail.description}</p>` : ''}
            </div>
        </div>
        <hr>
        <h5 class="mb-3">商品评价 (${reviews.length}条)</h5>
        ${reviews.length > 0 ? reviews.map(r => `
            <div class="card mb-2">
                <div class="card-body py-2 px-3">
                    <div class="d-flex justify-content-between align-items-center">
                        <span><strong>${r.username}</strong> <span class="text-warning">${r.rating_stars}</span></span>
                        <small class="text-muted">${r.created_at}</small>
                    </div>
                    ${r.content ? `<p class="mb-0 mt-1">${r.content}</p>` : ''}
                </div>
            </div>
        `).join('') : '<p class="text-muted">暂无评价</p>'}
    `;
}

// 从首页加入购物车（需要登录）
async function addToCartFromHome(goodsId) {
    if (!accessToken) {
        alert('请先登录后再加入购物车');
        showPage('login');
        return;
    }
    const result = await apiRequest('/api/cart/add/', {
        method: 'POST',
        body: JSON.stringify({ goods_id: goodsId, quantity: 1 }),
    });
    alert(result.message || '操作完成');
}

// 加载首页分类
async function loadHomeCategories(container) {
    const categoriesResult = await apiRequest('/api/categories/');
    const categories = categoriesResult.results || categoriesResult || [];

    container.innerHTML = `
        <div class="mb-4">
            <h4>商品分类</h4>
        </div>
        <div class="row">
            ${categories.length > 0 ? categories.map(cat => `
                <div class="col-md-3 mb-4">
                    <div class="card h-100" style="cursor:pointer;" onclick="loadHomeGoods(document.getElementById('home-content'), ${cat.id})">
                        <div class="card-body text-center">
                            ${cat.icon ? `<i class="bi bi-${cat.icon}" style="font-size: 2rem;"></i>` : ''}
                            <h5 class="mt-2">${cat.name}</h5>
                        </div>
                    </div>
                </div>
            `).join('') : '<div class="text-center text-muted py-5"><p>暂无分类</p></div>'}
        </div>
    `;
}

// 启动时检查已有token
document.addEventListener('DOMContentLoaded', () => {
    // 直接显示首页
    showHomeSection('goods');
    
    // 如果有token，检查是否有效
    if (accessToken) {
        apiRequest('/api/users/profile/').then(data => {
            if (data.user) {
                currentUser = data.user;
                // 可以在这里更新首页显示用户信息
                // 但不自动跳转到用户页面
            }
        });
    }
});
