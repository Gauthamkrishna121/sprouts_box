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
});
