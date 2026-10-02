/**
 * Sprouts Box - Shopping Cart & Checkout System
 * Dynamic, professional e-commerce cart interactions
 */

(function () {
    'use strict';

    // Helper: Get CSRF Token
    function getCsrfToken() {
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag && metaTag.content) {
            return metaTag.content;
        }
        const cookieMatch = document.cookie.match(/csrftoken=([^;]+)/);
        return cookieMatch ? cookieMatch[1] : '';
    }

    // Helper: Format Rupee Currency
    function formatCurrency(amount) {
        const num = parseFloat(amount) || 0;
        return '₹' + num.toFixed(2);
    }

    // Active discount tracker
    let appliedDiscount = 0;
    let appliedPromoCode = '';

    // DOM Elements
    const navCartCount = document.getElementById('navCartCount');
    const toastContainer = document.getElementById('sproutsToastContainer');

    // Toast Notification System
    function showToast(message, type = 'success', actionUrl = null, actionText = 'View Basket') {
        if (!toastContainer) return;

        const toast = document.createElement('div');
        toast.className = `sprouts-toast ${type}`;
        
        let actionHtml = '';
        if (actionUrl) {
            actionHtml = `<a href="${actionUrl}" class="toast-action-btn">${actionText} &rarr;</a>`;
        }

        toast.innerHTML = `
            <div class="toast-icon">
                <i data-feather="${type === 'success' ? 'check-circle' : 'alert-circle'}"></i>
            </div>
            <div class="toast-content">
                <div class="toast-message">${message}</div>
                ${actionHtml}
            </div>
            <button class="toast-close" aria-label="Close notification">&times;</button>
        `;

        toastContainer.appendChild(toast);
        if (window.feather) feather.replace();

        // Animate in
        requestAnimationFrame(() => {
            toast.classList.add('show');
        });

        const closeBtn = toast.querySelector('.toast-close');
        function dismiss() {
            toast.classList.remove('show');
            setTimeout(() => {
                if (toast.parentNode) toast.parentNode.removeChild(toast);
            }, 300);
        }

        if (closeBtn) closeBtn.addEventListener('click', dismiss);
        setTimeout(dismiss, 4000);
    }

    // Update Navbar Badge Count
    function updateCartBadge(count) {
        const countVal = parseInt(count, 10) || 0;
        if (navCartCount) {
            navCartCount.textContent = countVal;
            navCartCount.classList.remove('pulse-pop');
            void navCartCount.offsetWidth; // Force reflow
            navCartCount.classList.add('pulse-pop');
        }
    }

    // Recalculate Totals with Promo Code
    function recalculateWithPromo(rawSubtotal, rawShipping) {
        const subtotal = parseFloat(rawSubtotal) || 0;
        const shipping = parseFloat(rawShipping) || 0;
        const discountRow = document.getElementById('discountRow');
        const discountValue = document.getElementById('discountValue');
        const pageGrandTotal = document.getElementById('pageGrandTotal');
        const btnOrderTotal = document.getElementById('btnOrderTotal');

        let finalTotal = subtotal + shipping;

        if (appliedDiscount > 0) {
            finalTotal = Math.max(0, finalTotal - appliedDiscount);
            if (discountRow) discountRow.style.display = 'flex';
            if (discountValue) discountValue.textContent = `-₹${appliedDiscount.toFixed(2)}`;
        } else {
            if (discountRow) discountRow.style.display = 'none';
        }

        const formattedFinalTotal = `₹${finalTotal.toFixed(2)}`;
        if (pageGrandTotal) pageGrandTotal.textContent = formattedFinalTotal;
        if (btnOrderTotal) btnOrderTotal.textContent = formattedFinalTotal;
    }

    // Render Full Cart Page Table from Cart JSON
    function renderFullCartPage(cartData) {
        const tableBody = document.getElementById('cartPageTableBody');
        const pageItemsCount = document.getElementById('pageItemsCount');
        const pageSubtotal = document.getElementById('pageSubtotal');
        const pageShipping = document.getElementById('pageShipping');
        const cartLayoutGrid = document.getElementById('cartLayoutGrid');

        // Free Delivery Progress Update
        const shippingCard = document.getElementById('cartFreeShippingCard');
        if (shippingCard) {
            const progressBar = shippingCard.querySelector('.progress-bar-fill');
            const msgSpan = shippingCard.querySelector('.free-shipping-msg');

            if (progressBar) {
                progressBar.style.width = `${cartData.free_shipping_progress || 0}%`;
            }

            if (msgSpan) {
                if (cartData.has_free_shipping) {
                    msgSpan.className = 'free-shipping-msg text-success';
                    msgSpan.innerHTML = `<i data-feather="check-circle"></i> <strong>FREE Delivery Unlocked!</strong> Your order qualifies for zero shipping charge.`;
                } else if (cartData.cart_count > 0) {
                    msgSpan.className = 'free-shipping-msg';
                    msgSpan.innerHTML = `Add <strong>₹${cartData.amount_needed}</strong> more of farm produce to unlock <strong>FREE Delivery</strong>!`;
                }
            }
        }

        if (!cartLayoutGrid) return;

        // Empty Basket View
        if (!cartData.items || cartData.items.length === 0) {
            // Reload page smoothly to display recommended products grid
            window.location.reload();
            return;
        }

        // Populate Table Rows
        if (tableBody) {
            let rowsHtml = '';
            cartData.items.forEach(item => {
                rowsHtml += `
                    <tr class="cart-table-row" data-product-id="${item.id}">
                        <td class="col-product">
                            <div class="table-product-cell">
                                <div class="table-product-thumb">
                                    <img src="${item.image_url}" alt="${item.name}" onerror="this.src='/static/plugin/images/prod_tomatoes.png'">
                                </div>
                                <div class="table-product-meta">
                                    <h3 class="table-product-name">${item.name}</h3>
                                    <span class="table-product-unit"><i data-feather="tag"></i> Pack: ${item.unit}</span>
                                </div>
                            </div>
                        </td>
                        <td class="col-price">
                            <span class="table-price">${item.formatted_price}</span>
                        </td>
                        <td class="col-qty">
                            <div class="qty-stepper">
                                <button type="button" class="qty-btn qty-minus" data-id="${item.id}" aria-label="Decrease quantity">−</button>
                                <span class="qty-value" data-id="${item.id}">${item.quantity}</span>
                                <button type="button" class="qty-btn qty-plus" data-id="${item.id}" aria-label="Increase quantity">+</button>
                            </div>
                        </td>
                        <td class="col-total">
                            <span class="table-total-price">${item.formatted_total_price}</span>
                        </td>
                        <td class="col-remove">
                            <button type="button" class="table-remove-btn" data-id="${item.id}" title="Remove item" aria-label="Remove item">
                                <i data-feather="x"></i>
                            </button>
                        </td>
                    </tr>
                `;
            });
            tableBody.innerHTML = rowsHtml;
        }

        if (pageItemsCount) pageItemsCount.textContent = `${cartData.cart_count} produce`;
        if (pageSubtotal) pageSubtotal.textContent = cartData.formatted_subtotal;
        if (pageShipping) {
            pageShipping.innerHTML = cartData.has_free_shipping
                ? '<span class="badge-free-delivery">FREE</span>'
                : cartData.formatted_shipping;
        }

        recalculateWithPromo(cartData.subtotal, cartData.shipping);

        if (window.feather) feather.replace();
    }

    // Add to Cart Action
    async function addToCart(productId, productName, btnElement, quantity = 1) {
        if (!productId) return;

        let originalHtml = '';
        if (btnElement) {
            originalHtml = btnElement.innerHTML;
            btnElement.disabled = true;
            btnElement.innerHTML = `<span>Adding...</span>`;
        }

        try {
            const formData = new FormData();
            formData.append('quantity', quantity);

            const response = await fetch(`/cart/add/${productId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            });

            const data = await response.json();

            if (data.success && data.cart) {
                updateCartBadge(data.cart.cart_count);
                renderFullCartPage(data.cart);

                if (btnElement) {
                    btnElement.innerHTML = `<i data-feather="check"></i> <span>Added!</span>`;
                    btnElement.classList.add('btn-added-success');
                    if (window.feather) feather.replace();
                    setTimeout(() => {
                        btnElement.innerHTML = originalHtml;
                        btnElement.classList.remove('btn-added-success');
                        btnElement.disabled = false;
                        if (window.feather) feather.replace();
                    }, 1400);
                }

                showToast(
                    `🌿 Added <strong>${data.product_name || productName}</strong> to basket!`,
                    'success',
                    '/cart/',
                    'Go to Basket'
                );
            } else {
                showToast(data.message || 'Could not add produce to basket.', 'error');
                if (btnElement) {
                    btnElement.innerHTML = originalHtml;
                    btnElement.disabled = false;
                }
            }
        } catch (err) {
            console.error('Error adding to cart:', err);
            showToast('Network error while adding to basket.', 'error');
            if (btnElement) {
                btnElement.innerHTML = originalHtml;
                btnElement.disabled = false;
            }
        }
    }

    // Update Quantity Action
    async function updateQuantity(productId, newQty) {
        try {
            const formData = new FormData();
            formData.append('quantity', newQty);

            const response = await fetch(`/cart/update/${productId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            });

            const data = await response.json();
            if (data.success && data.cart) {
                updateCartBadge(data.cart.cart_count);
                renderFullCartPage(data.cart);
            }
        } catch (err) {
            console.error('Error updating quantity:', err);
        }
    }

    // Remove Item Action
    async function removeItem(productId) {
        try {
            const response = await fetch(`/cart/remove/${productId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();
            if (data.success && data.cart) {
                updateCartBadge(data.cart.cart_count);
                renderFullCartPage(data.cart);
                showToast(data.message || 'Item removed from basket.');
            }
        } catch (err) {
            console.error('Error removing item:', err);
        }
    }

    // Clear Cart Action
    async function clearCart() {
        if (!confirm('Are you sure you want to clear your entire harvest basket?')) return;

        try {
            const response = await fetch('/cart/clear/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();
            if (data.success && data.cart) {
                updateCartBadge(data.cart.cart_count);
                renderFullCartPage(data.cart);
                showToast('Basket cleared.');
            }
        } catch (err) {
            console.error('Error clearing cart:', err);
        }
    }

    // Global Click Handler Delegation
    document.addEventListener('click', function (e) {
        // Add to Cart Button Click
        const addBtn = e.target.closest('.add-to-cart-btn');
        if (addBtn) {
            e.preventDefault();
            const productId = addBtn.getAttribute('data-product-id');
            const productName = addBtn.getAttribute('data-product-name') || 'Produce';
            addToCart(productId, productName, addBtn);
            return;
        }

        // Quantity Plus
        const plusBtn = e.target.closest('.qty-plus');
        if (plusBtn) {
            e.preventDefault();
            const productId = plusBtn.getAttribute('data-id');
            const valEl = plusBtn.parentElement.querySelector('.qty-value');
            const currentQty = parseInt(valEl ? valEl.textContent : '1', 10) || 1;
            updateQuantity(productId, currentQty + 1);
            return;
        }

        // Quantity Minus
        const minusBtn = e.target.closest('.qty-minus');
        if (minusBtn) {
            e.preventDefault();
            const productId = minusBtn.getAttribute('data-id');
            const valEl = minusBtn.parentElement.querySelector('.qty-value');
            const currentQty = parseInt(valEl ? valEl.textContent : '1', 10) || 1;
            updateQuantity(productId, Math.max(0, currentQty - 1));
            return;
        }

        // Remove Item Button
        const removeBtn = e.target.closest('.table-remove-btn');
        if (removeBtn) {
            e.preventDefault();
            const productId = removeBtn.getAttribute('data-id');
            removeItem(productId);
            return;
        }

        // Clear Cart Button
        const clearBtn = e.target.closest('#pageClearCartBtn');
        if (clearBtn) {
            e.preventDefault();
            clearCart();
            return;
        }
    });


    // Dynamic Promo Code System
    const applyPromoBtn = document.getElementById('applyPromoBtn');
    const promoCodeInput = document.getElementById('promoCodeInput');
    const promoFeedback = document.getElementById('promoFeedback');

    if (applyPromoBtn && promoCodeInput) {
        applyPromoBtn.addEventListener('click', function () {
            const code = promoCodeInput.value.trim().toUpperCase();
            if (!code) {
                promoFeedback.style.display = 'block';
                promoFeedback.className = 'promo-feedback error';
                promoFeedback.textContent = 'Please enter a coupon code.';
                return;
            }

            const pageSubtotalEl = document.getElementById('pageSubtotal');
            const currentSubtotal = parseFloat(pageSubtotalEl ? pageSubtotalEl.textContent.replace('₹', '') : '0') || 0;

            if (code === 'SPROUTS10' || code === 'ORGANIC10') {
                appliedDiscount = currentSubtotal * 0.10;
                appliedPromoCode = code;
                promoFeedback.style.display = 'block';
                promoFeedback.className = 'promo-feedback success';
                promoFeedback.innerHTML = `✓ <strong>${code}</strong> applied! 10% farm discount saved (₹${appliedDiscount.toFixed(2)})`;
                applyPromoBtn.textContent = 'Applied';
                applyPromoBtn.disabled = true;
                promoCodeInput.disabled = true;
            } else if (code === 'FRESH50' || code === 'FIRST50') {
                appliedDiscount = 50;
                appliedPromoCode = code;
                promoFeedback.style.display = 'block';
                promoFeedback.className = 'promo-feedback success';
                promoFeedback.innerHTML = `✓ <strong>${code}</strong> applied! ₹50 flat discount saved.`;
                applyPromoBtn.textContent = 'Applied';
                applyPromoBtn.disabled = true;
                promoCodeInput.disabled = true;
            } else {
                promoFeedback.style.display = 'block';
                promoFeedback.className = 'promo-feedback error';
                promoFeedback.textContent = `Invalid code "${code}". Try "SPROUTS10" for 10% off!`;
                return;
            }

            const pageShippingEl = document.getElementById('pageShipping');
            const currentShipping = (pageShippingEl && pageShippingEl.textContent.includes('FREE')) ? 0 : 40;
            recalculateWithPromo(currentSubtotal, currentShipping);
            if (window.feather) feather.replace();
        });
    }

    // Checkout Form Submission - Direct WhatsApp Order
    const checkoutForm = document.getElementById('checkoutForm');
    if (checkoutForm) {
        checkoutForm.addEventListener('submit', async function (e) {
            e.preventDefault();

            // Validate required fields client-side to prevent button getting stuck
            const fullName = document.getElementById('fullName');
            const phoneNumber = document.getElementById('phoneNumber');
            const deliveryAddress = document.getElementById('deliveryAddress');

            if (!fullName || !fullName.value.trim()) {
                alert('Please enter your Full Name.');
                if (fullName) fullName.focus();
                return;
            }
            if (!phoneNumber || !phoneNumber.value.trim()) {
                alert('Please enter your Phone Number.');
                if (phoneNumber) phoneNumber.focus();
                return;
            }
            if (!deliveryAddress || !deliveryAddress.value.trim()) {
                alert('Please enter your Delivery Address.');
                if (deliveryAddress) deliveryAddress.focus();
                return;
            }

            const submitBtn = document.getElementById('submitOrderBtn');
            const origHtml = submitBtn ? submitBtn.innerHTML : '';

            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = `<span>Confirming Harvest Order...</span>`;
            }

            try {
                const formData = new FormData(checkoutForm);
                if (appliedDiscount > 0) {
                    formData.append('promo_code', appliedPromoCode);
                    formData.append('discount_amount', appliedDiscount);
                }

                const response = await fetch(checkoutForm.action, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCsrfToken(),
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: formData
                });

                const data = await response.json();

                if (data.success && data.redirect_url) {
                    showToast('🌱 Order placed! Showing your order details...');

                    // Navigate directly to the Order Details page with 10s auto-redirect window
                    setTimeout(() => {
                        window.location.href = data.redirect_url;
                    }, 200);
                } else {
                    alert(data.error || 'Please fill in all required fields.');
                    if (submitBtn) {
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = origHtml;
                    }
                }
            } catch (err) {
                console.error('Checkout error:', err);
                // Fallback: submit form natively
                checkoutForm.submit();
            }
        });
    }

})();
