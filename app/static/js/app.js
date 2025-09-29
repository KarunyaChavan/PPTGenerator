// PPT Generator JavaScript Functions

// Slide Builder functionality
class SlideBuilder {
    constructor(initialSlides = [], initialCounter = 0) {
        this.slides = initialSlides;
        this.slideCounter = initialCounter;
        this.initEventListeners();
        this.updateNoSlidesMessage();
    }

    initEventListeners() {
        const addSlideBtn = document.getElementById('add-slide-btn');
        if (addSlideBtn) {
            addSlideBtn.addEventListener('click', () => this.addSlide());
        }

        // Form submission handler
        const presentationForm = document.getElementById('presentation-form');
        if (presentationForm) {
            presentationForm.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }
    }

    addSlide() {
        this.slideCounter++;
        const slideId = `slide-${this.slideCounter}`;
        const slideHTML = this.createSlideHTML(slideId, this.slideCounter);
        const slidesContainer = document.getElementById('slides-container');
        slidesContainer.insertAdjacentHTML('beforeend', slideHTML);
        this.attachSlideEventListeners(slideId);
        this.slides.push({
            id: slideId,
            number: this.slideCounter,
            title: '',
            content: ''
        });
        this.updateSlidesData();
        this.updateNoSlidesMessage();
    }

    createSlideHTML(slideId, slideNumber) {
        return `
            <div class="slide-item" id="${slideId}">
                <div class="slide-header">
                    <div class="d-flex align-items-center">
                        <span class="slide-number">Slide ${slideNumber}</span>
                    </div>
                    <button type="button" class="btn btn-danger btn-sm" onclick="slideBuilder.removeSlide('${slideId}')">
                        Remove
                    </button>
                </div>
                <div class="slide-content">
                    <div class="form-group">
                        <label class="form-label">Slide Title</label>
                        <input type="text" class="form-control slide-title" 
                               placeholder="Enter slide title" 
                               data-slide="${slideId}">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Slide Content</label>
                        <textarea class="form-control slide-content-text" rows="6" 
                                  placeholder="Enter slide content. Use bullet points with • or - for lists." 
                                  data-slide="${slideId}"></textarea>
                        <small class="form-text text-muted">
                            Tip: Use • or - for bullet points, and indent with spaces for sub-bullets
                        </small>
                    </div>
                </div>
            </div>
        `;
    }

    attachSlideEventListeners(slideId) {
        const slideElement = document.getElementById(slideId);
        const titleInput = slideElement.querySelector('.slide-title');
        const contentTextarea = slideElement.querySelector('.slide-content-text');
        
        titleInput.addEventListener('input', () => this.updateSlideData(slideId));
        contentTextarea.addEventListener('input', () => this.updateSlideData(slideId));
    }

    removeSlide(slideId) {
        const slideElement = document.getElementById(slideId);
        if (slideElement) {
            slideElement.remove();
            this.slides = this.slides.filter(slide => slide.id !== slideId);
            this.renumberSlides();
            this.updateSlidesData();
            this.updateNoSlidesMessage();
        }
    }

    renumberSlides() {
        const slideElements = document.querySelectorAll('.slide-item');
        slideElements.forEach((element, index) => {
            const slideNumber = index + 1;
            const numberSpan = element.querySelector('.slide-number');
            numberSpan.textContent = `Slide ${slideNumber}`;
            
            // Update in slides array
            const slideId = element.id;
            const slide = this.slides.find(s => s.id === slideId);
            if (slide) {
                slide.number = slideNumber;
            }
        });
    }

    updateSlideData(slideId) {
        const slideElement = document.getElementById(slideId);
        const title = slideElement.querySelector('.slide-title').value;
        const content = slideElement.querySelector('.slide-content-text').value;
        
        const slide = this.slides.find(s => s.id === slideId);
        if (slide) {
            slide.title = title;
            slide.content = content;
        }
        
        this.updateSlidesData();
    }

    updateSlidesData() {
        const slidesDataField = document.getElementById('slides_data');
        if (slidesDataField) {
            const slidesData = this.slides.map(slide => ({
                title: slide.title,
                content: slide.content
            }));
            slidesDataField.value = JSON.stringify(slidesData);
        }
    }

    updateNoSlidesMessage() {
        const noSlidesMessage = document.getElementById('no-slides-message');
        if (noSlidesMessage) {
            if (this.slides.length === 0) {
                noSlidesMessage.style.display = 'block';
            } else {
                noSlidesMessage.style.display = 'none';
            }
        }
    }

    handleFormSubmit(e) {
        // Validate that at least one slide exists
        if (this.slides.length === 0) {
            e.preventDefault();
            showAlert('Please add at least one slide to your presentation.', 'error');
            return false;
        }

        // Validate that all slides have titles
        const invalidSlides = this.slides.filter(slide => !slide.title.trim());
        if (invalidSlides.length > 0) {
            e.preventDefault();
            showAlert('Please provide titles for all slides.', 'error');
            return false;
        }

        // Update slides data one final time
        this.updateSlidesData();
        
        // Show loading spinner
        showLoadingSpinner();
        
        return true;
    }
}

// Alert system
function showAlert(message, type = 'info') {
    const alertsContainer = document.getElementById('alerts-container');
    if (!alertsContainer) return;
    
    const alertHTML = `
        <div class="alert alert-${type} alert-dismissible">
            ${message}
            <button type="button" class="btn-close" onclick="this.parentElement.remove()">×</button>
        </div>
    `;
    
    alertsContainer.insertAdjacentHTML('afterbegin', alertHTML);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        const alertElement = alertsContainer.querySelector('.alert');
        if (alertElement) {
            alertElement.remove();
        }
    }, 5000);
}

// Loading spinner
function showLoadingSpinner() {
    const submitBtn = document.querySelector('button[type="submit"]');
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<div class="spinner"></div> Generating Presentation...';
    }
}

function hideLoadingSpinner() {
    const submitBtn = document.querySelector('button[type="submit"]');
    if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Generate Presentation';
    }
}

// Confirmation dialogs
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Form validation helpers
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize slide builder if on create page
    if (document.getElementById('slides-container')) {
        window.slideBuilder = new SlideBuilder();
    }
    
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
    
    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.classList.add('is-invalid');
                    isValid = false;
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showAlert('Please fill in all required fields.', 'error');
            }
        });
    });
    
    // Real-time validation
    const inputs = document.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.hasAttribute('required') && !this.value.trim()) {
                this.classList.add('is-invalid');
            } else {
                this.classList.remove('is-invalid');
            }
        });
        
        input.addEventListener('input', function() {
            if (this.classList.contains('is-invalid') && this.value.trim()) {
                this.classList.remove('is-invalid');
            }
        });
    });
});

// Admin functions
function approvePresentation(presentationId) {
    confirmAction('Are you sure you want to approve this presentation?', () => {
        document.getElementById('action').value = 'approve';
        document.getElementById('admin-review-form').submit();
    });
}

function rejectPresentation(presentationId) {
    confirmAction('Are you sure you want to reject this presentation?', () => {
        document.getElementById('action').value = 'reject';
        document.getElementById('admin-review-form').submit();
    });
}

function rollbackVersion(presentationId, versionNumber) {
    const message = `Are you sure you want to rollback to version ${versionNumber}? This will reset the presentation status to pending.`;
    confirmAction(message, () => {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/admin/presentation/${presentationId}/rollback/${versionNumber}`;
        document.body.appendChild(form);
        form.submit();
    });
}

function toggleUserStatus(userId) {
    confirmAction('Are you sure you want to toggle this user\'s status?', () => {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/admin/user/${userId}/toggle-status`;
        document.body.appendChild(form);
        form.submit();
    });
}