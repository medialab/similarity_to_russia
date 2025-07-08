/**
 * CSV Text Annotation Tool - JavaScript
 * Handles user interactions, API calls, and visual feedback
 */

class AnnotationApp {
    constructor() {
        this.currentData = null;
        this.isLoading = false;
        
        // Initialize the application
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadAvailableFiles();
        this.updateProgress();
    }
    
    setupEventListeners() {
        // Keyboard shortcuts
        document.addEventListener('keydown', (event) => {
            if (this.isLoading) return;
            
            // Only handle shortcuts if annotation interface is visible
            const annotationInterface = document.getElementById('annotationInterface');
            if (annotationInterface.style.display === 'none') return;
            
            switch(event.key) {
                case 'ArrowLeft':
                    event.preventDefault();
                    this.annotate(0); // No
                    break;
                case 'ArrowRight':
                    event.preventDefault();
                    this.annotate(1); // Yes
                    break;
                case 'Escape':
                    this.goToFileSelection();
                    break;
            }
        });
        
        // Prevent default behavior for arrow keys to avoid page scrolling
        document.addEventListener('keydown', (event) => {
            if (['ArrowLeft', 'ArrowRight'].includes(event.key)) {
                event.preventDefault();
            }
        });
    }
    
    async loadAvailableFiles() {
        try {
            this.showStatusMessage('Loading files...', 'info');
            const response = await fetch('/api/files');
            const files = await response.json();
            
            this.displayFileList(files);
            this.hideStatusMessage();
        } catch (error) {
            console.error('Error loading files:', error);
            this.showStatusMessage('Error loading files', 'error');
        }
    }
    
    displayFileList(files) {
        const fileList = document.getElementById('fileList');
        
        if (files.length === 0) {
            fileList.innerHTML = `
                <div class="loading">
                    No CSV files found in the data folder.<br>
                    Please add CSV files with a 'content' column.
                </div>
            `;
            return;
        }
        
        fileList.innerHTML = files.map(file => `
            <div class="file-item" onclick="app.loadFile('${file}')">
                📄 ${file}
            </div>
        `).join('');
    }
    
    async loadFile(filename) {
        if (this.isLoading) return;
        
        try {
            this.isLoading = true;
            this.showStatusMessage(`Loading ${filename}...`, 'info');
            
            const response = await fetch('/api/load_file', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ filename: filename })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showStatusMessage(result.message, 'success');
                this.showAnnotationInterface();
                await this.loadCurrentItem();
            } else {
                this.showStatusMessage(result.message, 'error');
            }
        } catch (error) {
            console.error('Error loading file:', error);
            this.showStatusMessage('Error loading file', 'error');
        } finally {
            this.isLoading = false;
        }
    }
    
    async loadCurrentItem() {
        try {
            const response = await fetch('/api/current_item');
            const data = await response.json();
            
            this.currentData = data;
            
            if (data.has_data && data.item) {
                this.displayCurrentItem(data.item);
                this.updateProgress(data.stats);
            } else {
                this.showCompletionMessage();
            }
        } catch (error) {
            console.error('Error loading current item:', error);
            this.showStatusMessage('Error loading content', 'error');
        }
    }
    
    displayCurrentItem(item) {
        const contentText = document.getElementById('contentText');
        const metadata = document.getElementById('metadata');
        
        // Display content
        contentText.textContent = item.content;
        
        // Display metadata for phrases
        let metadataHtml = `<strong>Phrase ${item.index + 1} of ${item.total}</strong>`;
        
        if (item.metadata.phrase_info) {
            metadataHtml += `<br><strong>Context:</strong> ${item.metadata.phrase_info}`;
        }
        if (item.metadata.headline) {
            metadataHtml += `<br><strong>Article:</strong> ${item.metadata.headline}`;
        }
        if (item.metadata.date_published) {
            metadataHtml += `<br><strong>Published:</strong> ${item.metadata.date_published}`;
        }
        if (item.metadata.url) {
            metadataHtml += `<br><strong>Source:</strong> <a href="${item.metadata.url}" target="_blank" rel="noopener">View Article</a>`;
        }
        
        metadata.innerHTML = metadataHtml;
        
        // Reset button states
        this.resetButtonStates();
        
        // Focus on content area for better UX
        contentText.scrollTop = 0;
    }
    
    async annotate(annotation) {
        if (this.isLoading || !this.currentData || !this.currentData.has_data) return;
        
        try {
            this.isLoading = true;
            
            // Visual feedback
            this.showButtonFeedback(annotation);
            
            const response = await fetch('/api/annotate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ annotation: annotation })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Small delay for visual feedback
                setTimeout(async () => {
                    await this.loadCurrentItem();
                    this.isLoading = false;
                }, 300);
            } else {
                this.showStatusMessage(result.message, 'error');
                this.isLoading = false;
            }
        } catch (error) {
            console.error('Error annotating:', error);
            this.showStatusMessage('Error saving annotation', 'error');
            this.isLoading = false;
        }
    }
    
    showButtonFeedback(annotation) {
        const yesBtn = document.getElementById('yesBtn');
        const noBtn = document.getElementById('noBtn');
        
        // Reset previous states
        yesBtn.classList.remove('clicked');
        noBtn.classList.remove('clicked');
        
        // Add clicked state
        if (annotation === 1) {
            yesBtn.classList.add('clicked');
        } else {
            noBtn.classList.add('clicked');
        }
    }
    
    resetButtonStates() {
        const yesBtn = document.getElementById('yesBtn');
        const noBtn = document.getElementById('noBtn');
        
        yesBtn.classList.remove('clicked');
        noBtn.classList.remove('clicked');
    }
    
    updateProgress(stats = null) {
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        
        if (!stats) {
            progressFill.style.width = '0%';
            progressText.textContent = 'Select a file to begin';
            return;
        }
        
        progressFill.style.width = `${stats.percentage}%`;
        progressText.textContent = `${stats.completed}/${stats.total} phrases annotated (${stats.percentage}%) - ${stats.current_file}`;
    }
    
    showAnnotationInterface() {
        document.getElementById('fileSelection').style.display = 'none';
        document.getElementById('annotationInterface').style.display = 'flex';
        document.getElementById('completionMessage').style.display = 'none';
    }
    
    showCompletionMessage() {
        document.getElementById('fileSelection').style.display = 'none';
        document.getElementById('annotationInterface').style.display = 'none';
        document.getElementById('completionMessage').style.display = 'block';
    }
    
    goToFileSelection() {
        document.getElementById('fileSelection').style.display = 'block';
        document.getElementById('annotationInterface').style.display = 'none';
        document.getElementById('completionMessage').style.display = 'none';
        
        // Refresh file list and progress
        this.loadAvailableFiles();
        this.updateProgress();
    }
    
    async exportAnnotations() {
        try {
            this.showModal('exportModal');
            document.getElementById('exportStatus').textContent = 'Preparing export...';
            
            const response = await fetch('/api/export');
            const result = await response.json();
            
            if (result.success && result.files && result.files.length > 0) {
                const downloadLinks = result.files.map(file => 
                    `<a href="/download/${file}" class="download-link" target="_blank">📥 Download ${file}</a>`
                ).join('<br>');
                
                document.getElementById('exportStatus').innerHTML = `
                    <p>✅ Export completed successfully!</p>
                    <div style="margin-top: 15px;">
                        ${downloadLinks}
                    </div>
                `;
            } else {
                document.getElementById('exportStatus').innerHTML = `
                    <p>⚠️ ${result.message || 'No annotations to export'}</p>
                `;
            }
        } catch (error) {
            console.error('Error exporting:', error);
            document.getElementById('exportStatus').innerHTML = `
                <p>❌ Error exporting annotations</p>
            `;
        }
    }
    
    async resetProgress() {
        if (!confirm('Are you sure you want to reset all annotation progress? This cannot be undone.')) {
            return;
        }
        
        try {
            this.showStatusMessage('Resetting progress...', 'info');
            
            const response = await fetch('/api/reset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showStatusMessage('Progress reset successfully', 'success');
                this.goToFileSelection();
            } else {
                this.showStatusMessage('Error resetting progress', 'error');
            }
        } catch (error) {
            console.error('Error resetting progress:', error);
            this.showStatusMessage('Error resetting progress', 'error');
        }
    }
    
    showModal(modalId) {
        document.getElementById(modalId).style.display = 'flex';
    }
    
    closeModal() {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => modal.style.display = 'none');
    }
    
    showStatusMessage(message, type = 'info') {
        const statusMessage = document.getElementById('statusMessage');
        statusMessage.textContent = message;
        statusMessage.className = `status-message ${type} show`;
        
        // Auto-hide after 3 seconds for success/info messages
        if (type !== 'error') {
            setTimeout(() => {
                this.hideStatusMessage();
            }, 3000);
        }
    }
    
    hideStatusMessage() {
        const statusMessage = document.getElementById('statusMessage');
        statusMessage.classList.remove('show');
    }
}

// Global functions for HTML onclick handlers
function annotate(annotation) {
    app.annotate(annotation);
}

function exportAnnotations() {
    app.exportAnnotations();
}

function resetProgress() {
    app.resetProgress();
}

function goToFileSelection() {
    app.goToFileSelection();
}

function closeModal() {
    app.closeModal();
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new AnnotationApp();
});

// Handle modal clicks (close when clicking outside)
document.addEventListener('click', (event) => {
    if (event.target.classList.contains('modal')) {
        app.closeModal();
    }
});

// Prevent accidental page navigation
window.addEventListener('beforeunload', (event) => {
    if (app && app.currentData && app.currentData.has_data) {
        event.preventDefault();
        event.returnValue = 'You have unsaved annotations. Are you sure you want to leave?';
    }
}); 