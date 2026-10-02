/**
 * Sprouts Box — Admin Order Delivery Status Quick Controls
 * Provides 1-click status transitions and interactive dropdowns directly in the changelist.
 */

(function () {
    'use strict';

    const STATUS_MAP = {
        pending: {
            bg: '#fef3c7',
            color: '#92400e',
            border: '#fde68a',
            icon: '⏳',
            name: 'Pending Confirmation',
            next: { status: 'confirmed', label: '👉 Confirm', cls: 'btn-step-confirm', title: 'Confirm and prepare order' }
        },
        confirmed: {
            bg: '#e0f2fe',
            color: '#075985',
            border: '#bae6fd',
            icon: '📋',
            name: 'Order Confirmed',
            next: { status: 'out_for_delivery', label: '🚚 Dispatch', cls: 'btn-step-dispatch', title: 'Hand over to delivery partner' }
        },
        out_for_delivery: {
            bg: '#ede9fe',
            color: '#5b21b6',
            border: '#ddd6fe',
            icon: '🚚',
            name: 'Out for Delivery',
            next: { status: 'delivered', label: '✓ Mark Delivered', cls: 'btn-step-delivered', title: 'Mark order successfully delivered' }
        },
        delivered: {
            bg: '#dcfce7',
            color: '#166534',
            border: '#bbf7d0',
            icon: '📦',
            name: 'Delivered',
            next: { status: null, label: '✓ Delivered', cls: 'btn-step-complete', title: 'Order fulfilled' }
        },
        cancelled: {
            bg: '#fee2e2',
            color: '#991b1b',
            border: '#fecaca',
            icon: '❌',
            name: 'Cancelled',
            next: { status: 'pending', label: '↺ Reopen', cls: 'btn-step-reopen', title: 'Reopen cancelled order' }
        }
    };

    // Toast notification manager
    function showToast(message, type = 'success') {
        let toastContainer = document.getElementById('sb-admin-toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'sb-admin-toast-container';
            toastContainer.className = 'sb-toast-container';
            document.body.appendChild(toastContainer);
        }

        const toast = document.createElement('div');
        toast.className = `sb-toast sb-toast-${type}`;
        toast.innerHTML = `
            <span class="sb-toast-icon">${type === 'success' ? '✅' : '⚠️'}</span>
            <span class="sb-toast-text">${message}</span>
            <button type="button" class="sb-toast-close" aria-label="Close">&times;</button>
        `;

        toast.querySelector('.sb-toast-close').addEventListener('click', () => {
            toast.classList.add('fade-out');
            setTimeout(() => toast.remove(), 250);
        });

        toastContainer.appendChild(toast);

        // Auto remove after 3.8s
        setTimeout(() => {
            if (toast.parentElement) {
                toast.classList.add('fade-out');
                setTimeout(() => toast.remove(), 250);
            }
        }, 3800);
    }

    // Close all open popovers
    function closeAllPopovers() {
        document.querySelectorAll('.order-status-popover.show').forEach(pop => {
            pop.classList.remove('show');
            pop.classList.remove('drop-up');
        });
        document.querySelectorAll('.order-status-pill-btn.active').forEach(btn => {
            btn.classList.remove('active');
        });
    }

    // Update row DOM elements when status changes
    function updateRowStatus(orderId, newStatus, statusLabel) {
        const config = STATUS_MAP[newStatus];
        if (!config) return;

        const wrapper = document.getElementById(`order-status-wrapper-${orderId}`);
        const row = wrapper ? wrapper.closest('tr') : null;

        // 1. Update status pill button
        if (wrapper) {
            const btn = wrapper.querySelector('.order-status-pill-btn');
            if (btn) {
                btn.style.backgroundColor = config.bg;
                btn.style.color = config.color;
                btn.style.borderColor = config.border;

                const iconEl = btn.querySelector('.status-icon');
                if (iconEl) iconEl.textContent = config.icon;

                const nameEl = btn.querySelector('.status-name');
                if (nameEl) nameEl.textContent = statusLabel || config.name;
            }

            // 2. Update active item in popover menu
            const popover = wrapper.querySelector('.order-status-popover');
            if (popover) {
                popover.querySelectorAll('.order-status-opt').forEach(opt => {
                    const optStatus = opt.getAttribute('data-status');
                    if (optStatus === newStatus) {
                        opt.classList.add('current');
                        if (!opt.textContent.startsWith('✓')) {
                            opt.textContent = '✓ ' + opt.textContent.replace(/^✓\s*/, '');
                        }
                    } else {
                        opt.classList.remove('current');
                        opt.textContent = opt.textContent.replace(/^✓\s*/, '');
                    }
                });
            }
        }

        // 3. Update quick action step button in that row
        if (row) {
            const actionCell = row.querySelector('.field-delivery_quick_action');
            if (actionCell) {
                const nextStep = config.next;
                if (nextStep && nextStep.status) {
                    const baseUrl = `/admin/store/order/${orderId}/quick-status/${nextStep.status}/`;
                    actionCell.innerHTML = `
                        <a href="${baseUrl}" class="order-step-btn ${nextStep.cls}" title="${nextStep.title}" data-order-id="${orderId}" data-target-status="${nextStep.status}">
                            <span>${nextStep.label}</span>
                        </a>
                    `;
                } else {
                    actionCell.innerHTML = `
                        <span class="order-step-btn ${nextStep ? nextStep.cls : 'btn-step-complete'}">${nextStep ? nextStep.label : '✓ Delivered'}</span>
                    `;
                }
            }

            // Subtle highlight flash on the row
            row.classList.add('row-updated-flash');
            setTimeout(() => row.classList.remove('row-updated-flash'), 1200);
        }
    }

    // Execute AJAX status update
    async function executeStatusChange(url, orderId, newStatus, triggerElement) {
        if (triggerElement) {
            triggerElement.classList.add('is-loading');
        }

        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }

            const data = await response.json();
            if (data.success) {
                updateRowStatus(data.order_id, data.status, data.status_label);
                showToast(`Order <strong>#${data.order_number}</strong> status changed to <strong>${data.status_label}</strong>`, 'success');
            } else {
                window.location.href = url; // Fallback to full page redirect
            }
        } catch (err) {
            console.warn('AJAX status update error, falling back to page reload:', err);
            window.location.href = url;
        } finally {
            if (triggerElement) {
                triggerElement.classList.remove('is-loading');
            }
            closeAllPopovers();
        }
    }

    // Initialize listeners
    function initOrderDeliveryControls() {
        // Delegate status badge button click to open popover
        document.addEventListener('click', function (e) {
            const pillBtn = e.target.closest('.order-status-pill-btn');
            if (pillBtn) {
                e.preventDefault();
                e.stopPropagation();

                const wrapper = pillBtn.closest('.order-status-wrapper');
                if (!wrapper) return;

                const popover = wrapper.querySelector('.order-status-popover');
                if (!popover) return;

                const isAlreadyOpen = popover.classList.contains('show');
                closeAllPopovers();

                if (!isAlreadyOpen) {
                    popover.classList.add('show');
                    pillBtn.classList.add('active');

                    // Check if popover spills off bottom of screen
                    const rect = popover.getBoundingClientRect();
                    const windowHeight = window.innerHeight || document.documentElement.clientHeight;
                    if (rect.bottom > windowHeight - 20) {
                        popover.classList.add('drop-up');
                    } else {
                        popover.classList.remove('drop-up');
                    }
                }
                return;
            }

            // Popover option click (dropdown item)
            const optLink = e.target.closest('.order-status-opt');
            if (optLink) {
                e.preventDefault();
                e.stopPropagation();
                const url = optLink.getAttribute('href');
                const orderId = optLink.getAttribute('data-order-id');
                const targetStatus = optLink.getAttribute('data-status');
                executeStatusChange(url, orderId, targetStatus, optLink);
                return;
            }

            // Quick action step button click in table row
            const stepBtn = e.target.closest('a.order-step-btn');
            if (stepBtn) {
                e.preventDefault();
                e.stopPropagation();
                const url = stepBtn.getAttribute('href');
                const orderId = stepBtn.getAttribute('data-order-id');
                const targetStatus = stepBtn.getAttribute('data-target-status');
                executeStatusChange(url, orderId, targetStatus, stepBtn);
                return;
            }

            // Click outside closes any open popovers
            if (!e.target.closest('.order-status-wrapper')) {
                closeAllPopovers();
            }
        });

        // Close on Escape key
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                closeAllPopovers();
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initOrderDeliveryControls);
    } else {
        initOrderDeliveryControls();
    }
})();
