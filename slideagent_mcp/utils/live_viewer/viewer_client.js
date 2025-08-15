class LiveViewer {
    constructor() {
        this.sections = [];
        this.slideElements = new Map();
        this.init();
    }

    async init() {
        await this.updateStatus();
        setInterval(() => this.updateStatus(), 500);
    }

    async updateStatus() {
        try {
            const response = await fetch('/api/status');
            const status = await response.json();
            
            this.sections = status.sections;
            this.renderSections();
            this.updateProgress(status.completedSlides, status.totalSlides);
            
            // Update stats
            document.getElementById('slide-count').textContent = 
                status.completedSlides + '/' + status.totalSlides;
            document.getElementById('section-count').textContent = 
                status.sections.length;
            document.getElementById('last-update').textContent = 
                new Date().toLocaleTimeString();
            
            // Always hide the no-sections message since we show empty agent rows
            document.getElementById('no-sections').style.display = 'none';
        } catch (err) {
            console.error('Error updating status:', err);
        }
    }

    renderSections() {
        const container = document.getElementById('sections-container');
        
        this.sections.forEach(section => {
            let sectionRow = document.getElementById(`section-${section.number}`);
            
            if (!sectionRow) {
                // Create new section row
                sectionRow = document.createElement('div');
                sectionRow.className = 'section-row';
                sectionRow.id = `section-${section.number}`;
                
                const completed = section.slides.filter(s => s.status === 'completed').length;
                const total = section.slides.length;
                
                const labelText = section.isAgent ? 
                    `🤖 AI Agent ${section.number}` : 
                    `🤖 AI Analyst ${section.number}`;
                const titleText = section.isAgent ? 
                    `Working on "${section.title}" Sections` : 
                    `Working on "${section.title}" Section`;
                
                sectionRow.innerHTML = `
                    <div class="section-header">
                        <div>
                            <div class="section-label">${labelText}</div>
                            <div class="section-title">${titleText}</div>
                        </div>
                        <div class="section-progress" id="section-progress-${section.number}">
                            ${completed}/${total} slides
                        </div>
                    </div>
                    <div class="slides-row" id="slides-row-${section.number}">
                        <!-- Slides will be added here -->
                    </div>
                `;
                
                container.appendChild(sectionRow);
            } else {
                // Update progress
                const completed = section.slides.filter(s => s.status === 'completed').length;
                const total = section.slides.length;
                const progressEl = document.getElementById(`section-progress-${section.number}`);
                if (progressEl) {
                    progressEl.textContent = `${completed}/${total} slides`;
                }
            }
            
            // Render slides for this section
            this.renderSectionSlides(section);
        });
    }

    renderSectionSlides(section) {
        const slidesRow = document.getElementById(`slides-row-${section.number}`);
        if (!slidesRow) return;
        
        section.slides.forEach(slide => {
            const slideId = `slide-${slide.file}`;
            let slideEl = this.slideElements.get(slideId);
            
            if (!slideEl) {
                // Create new slide element
                slideEl = document.createElement('div');
                slideEl.className = `slide-container ${slide.status}`;
                slideEl.id = slideId;
                
                if (slide.status === 'waiting') {
                    slideEl.innerHTML = `
                        <div class="waiting-number">${slide.number}</div>
                        <div class="waiting-text">Waiting</div>
                    `;
                } else if (slide.status === 'completed') {
                    slideEl.className += ' new-slide';
                    slideEl.innerHTML = `
                        <div class="slide-number-overlay">Slide ${slide.number}</div>
                        <iframe class="slide-iframe" src="/${slide.file}?t=${Date.now()}"></iframe>
                    `;
                    slideEl.onclick = () => window.open(`/${slide.file}`, '_blank');
                }
                
                slidesRow.appendChild(slideEl);
                this.slideElements.set(slideId, slideEl);
            } else if (slide.status === 'completed' && slideEl.classList.contains('waiting')) {
                // Update from waiting to completed
                slideEl.className = 'slide-container completed new-slide';
                slideEl.innerHTML = `
                    <div class="slide-number-overlay">Slide ${slide.number}</div>
                    <iframe class="slide-iframe" src="/${slide.file}?t=${Date.now()}"></iframe>
                `;
                slideEl.onclick = () => window.open(`/${slide.file}`, '_blank');
                
                // Scroll the row to show the new slide
                slidesRow.scrollLeft = slideEl.offsetLeft - 20;
            }
        });
    }

    updateProgress(completed, total) {
        const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;
        const fill = document.getElementById('progress-fill');
        fill.style.width = percentage + '%';
        fill.textContent = percentage > 0 ? percentage + '%' : '';
    }
}

// Initialize viewer when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new LiveViewer());
} else {
    new LiveViewer();
}