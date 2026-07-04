// 添加到购物车
function addToCart(goodsId, quantity = 1) {
    fetch('/cart/add/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `goods_id=${goodsId}&quantity=${quantity}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showNotification('已添加到购物车！', 'success');
            const cartBadge = document.querySelector('.navbar .badge');
            if (cartBadge) {
                cartBadge.textContent = data.cart_count;
            }
        } else {
            showNotification(data.message || '添加失败', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('网络错误，请重试', 'danger');
    });
}

// 通知提示
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 80px; right: 20px; z-index: 99999; min-width: 250px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}

// 更新购物车数量
function updateCartItem(itemId, quantity) {
    fetch(`/cart/update/${itemId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `quantity=${quantity}`
    })
    .then(response => {
        if (response.redirected) {
            window.location.reload();
        }
    });
}

// 获取Cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// 数量加减
function changeQuantity(inputId, delta) {
    const input = document.getElementById(inputId);
    let value = parseInt(input.value) + delta;
    if (value < 1) value = 1;
    input.value = value;
}
