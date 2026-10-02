/**
 * Sprouts Box Control Center - Product & Inventory Media Preview Assistant
 */
document.addEventListener('DOMContentLoaded', function () {
    // 1. Live Client-Side Image Upload Preview in Product Add/Change Form
    const imageInput = document.getElementById('id_image');
    if (imageInput) {
        // Container wrapping the file input
        const formRow = imageInput.closest('.form-row') || imageInput.parentElement;

        // Create container for live preview
        let previewBox = document.createElement('div');
        previewBox.className = 'live-upload-preview-box';
        previewBox.style.display = 'none';
        formRow.appendChild(previewBox);

        imageInput.addEventListener('change', function (e) {
            const file = e.target.files && e.target.files[0];
            if (file) {
                if (!file.type.startsWith('image/')) {
                    previewBox.style.display = 'block';
                    previewBox.innerHTML = `
                        <div class="live-preview-alert error">
                            <span>⚠️ Selected file is not an image (${file.type || 'unknown type'}).</span>
                        </div>
                    `;
                    return;
                }

                const reader = new FileReader();
                reader.onload = function (event) {
                    const fileSizeKb = (file.size / 1024).toFixed(1);
                    previewBox.style.display = 'flex';
                    previewBox.innerHTML = `
                        <div class="live-preview-thumb-wrap">
                            <img src="${event.target.result}" alt="New Upload Preview" class="live-preview-img" />
                        </div>
                        <div class="live-preview-meta">
                            <div class="live-badge-ready">
                                <span class="dot-pulse"></span> Ready to upload on Save
                            </div>
                            <strong class="live-preview-name">${file.name}</strong>
                            <span class="live-preview-size">${fileSizeKb} KB &bull; ${file.type}</span>
                            <button type="button" class="btn-clear-preview" id="btnClearImageChoice">✕ Cancel change</button>
                        </div>
                    `;

                    // Handle cancel choice
                    const clearBtn = document.getElementById('btnClearImageChoice');
                    if (clearBtn) {
                        clearBtn.addEventListener('click', function () {
                            imageInput.value = '';
                            previewBox.style.display = 'none';
                            previewBox.innerHTML = '';
                        });
                    }
                };
                reader.readAsDataURL(file);
            } else {
                previewBox.style.display = 'none';
                previewBox.innerHTML = '';
            }
        });
    }

    // 2. Interactive Lightbox / Modal for List Display Thumbnails
    document.querySelectorAll('.admin-table-thumb').forEach(function (thumb) {
        thumb.style.cursor = 'zoom-in';
        thumb.addEventListener('click', function (e) {
            e.stopPropagation();
            const src = thumb.getAttribute('src');
            const alt = thumb.getAttribute('alt') || 'Product Image';
            if (!src) return;

            let modal = document.getElementById('admin-image-lightbox');
            if (!modal) {
                modal = document.createElement('div');
                modal.id = 'admin-image-lightbox';
                modal.className = 'admin-lightbox-modal';
                modal.innerHTML = `
                    <div class="lightbox-backdrop"></div>
                    <div class="lightbox-dialog">
                        <button type="button" class="lightbox-close" aria-label="Close">&times;</button>
                        <img src="" alt="" class="lightbox-img" />
                        <div class="lightbox-caption"></div>
                    </div>
                `;
                document.body.appendChild(modal);

                modal.querySelector('.lightbox-backdrop').addEventListener('click', function () {
                    modal.classList.remove('open');
                });
                modal.querySelector('.lightbox-close').addEventListener('click', function () {
                    modal.classList.remove('open');
                });
                document.addEventListener('keydown', function (evt) {
                    if (evt.key === 'Escape' && modal.classList.contains('open')) {
                        modal.classList.remove('open');
                    }
                });
            }

            modal.querySelector('.lightbox-img').src = src;
            modal.querySelector('.lightbox-caption').textContent = alt;
            modal.classList.add('open');
        });
    });

    // 3. Dynamic Changelist Table Enhancements
    const resultTable = document.getElementById('result_list');
    if (resultTable) {
        const actionCounter = document.querySelector('.action-counter');
        const saveBtn = document.querySelector('input[name="_save"]');

        function updateActionCounter() {
            const checkedBoxes = resultTable.querySelectorAll('tbody input.action-select:checked');
            if (actionCounter) {
                if (checkedBoxes.length > 0) {
                    actionCounter.classList.add('has-selection');
                } else {
                    actionCounter.classList.remove('has-selection');
                }
            }
        }

        function markUnsaved() {
            if (saveBtn && !saveBtn.classList.contains('save-pending')) {
                saveBtn.classList.add('save-pending');
                saveBtn.value = '💾 Save Changes (Unsaved)';
            }
        }

        // Row checkbox click listener
        resultTable.querySelectorAll('tbody input.action-select').forEach(function (chk) {
            const row = chk.closest('tr');
            if (chk.checked && row) row.classList.add('row-checked');

            chk.addEventListener('change', function () {
                if (row) {
                    if (chk.checked) {
                        row.classList.add('row-checked');
                    } else {
                        row.classList.remove('row-checked');
                    }
                }
                updateActionCounter();
            });
        });

        // Header select all toggle
        const selectAllToggle = document.getElementById('action-toggle');
        if (selectAllToggle) {
            selectAllToggle.addEventListener('change', function () {
                setTimeout(function () {
                    resultTable.querySelectorAll('tbody tr').forEach(function (row) {
                        const chk = row.querySelector('input.action-select');
                        if (chk && chk.checked) {
                            row.classList.add('row-checked');
                        } else {
                            row.classList.remove('row-checked');
                        }
                    });
                    updateActionCounter();
                }, 50);
            });
        }

        // Live interactive stock toggle sync
        resultTable.querySelectorAll('td.field-is_available input[type="checkbox"]').forEach(function (chk) {
            chk.addEventListener('change', function () {
                const row = chk.closest('tr');
                if (!row) return;

                const badgeCell = row.querySelector('.field-availability_badge');
                if (badgeCell) {
                    if (chk.checked) {
                        badgeCell.innerHTML = '<span class="status-badge in-stock"><span class="badge-dot green"></span>In Stock</span>';
                    } else {
                        badgeCell.innerHTML = '<span class="status-badge out-of-stock"><span class="badge-dot red"></span>Out of Stock</span>';
                    }
                }
                markUnsaved();
            });
        });

        // Live price and unit inline edit dirty indicator
        resultTable.querySelectorAll('td.field-price input, td.field-unit input').forEach(function (input) {
            input.addEventListener('input', function () {
                input.classList.add('field-dirty');
                markUnsaved();
            });
        });

        // Search bar enhancements
        const searchInput = document.getElementById('searchbar');
        if (searchInput) {
            if (!searchInput.getAttribute('placeholder')) {
                searchInput.setAttribute('placeholder', 'Search produce by name, description, category, or slug…');
            }
        }
    }
});
